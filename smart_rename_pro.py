"""Smart Rename Pro - A powerful file and content renaming tool.

This module provides functionality for batch renaming files and directories,
including content replacement while preserving case patterns and handling
various file encodings.
"""

import argparse
import datetime
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import chardet
import pathspec
import yaml

# Configure logging with platform-specific log file path
log_dir = Path(os.path.expanduser("~")) / ".smart_rename_pro"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "smart_rename_pro.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class SmartRenameError(Exception):
    """Custom exception for Smart Rename Pro errors."""

    pass


@dataclass
class ReplaceConfig:
    """Configuration for search and replace operation.

    This class holds all configuration parameters needed for the search and replace
    operation, including search terms, directory paths, and processing options.
    """

    search_term: str
    replace_term: str
    directory: Path
    max_workers: int = 4
    config_file: Optional[Path] = None
    exclude_extensions: Optional[List[str]] = None
    include_extensions: Optional[List[str]] = None
    dry_run: bool = False

    def __post_init__(self) -> None:
        """Initialize default values and validate configuration."""
        self.exclude_extensions = self.exclude_extensions or []
        self.include_extensions = self.include_extensions or []
        self.max_workers = max(1, min(self.max_workers, 16))

        # Validate search and replace terms
        TextProcessor.validate_term(self.search_term, "search")
        TextProcessor.validate_term(self.replace_term, "replace")

        # Validate date format if it looks like a date
        if self._looks_like_date(self.search_term) and not self._is_valid_date(
            self.search_term
        ):
            raise SmartRenameError(
                f"Invalid date format in search term: {self.search_term}"
            )
        if self._looks_like_date(self.replace_term) and not self._is_valid_date(
            self.replace_term
        ):
            raise SmartRenameError(
                f"Invalid date format in replace term: {self.replace_term}"
            )

    @staticmethod
    def _looks_like_date(text: str) -> bool:
        """Check if text looks like a date."""
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
            r"\d{4}/\d{2}/\d{2}",  # YYYY/MM/DD
            r"\d{2}-\d{2}-\d{4}",  # DD-MM-YYYY
            r"\d{4}\.\d{2}\.\d{2}",  # YYYY.MM.DD
            r"\d{2}\.\d{2}\.\d{4}",  # DD.MM.YYYY
        ]
        return any(re.search(pattern, text) for pattern in date_patterns)

    @staticmethod
    def _is_valid_date(text: str) -> bool:
        """Validate if text is a valid date."""
        try:
            # Try common date formats
            formats = [
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%Y/%m/%d",
                "%d-%m-%Y",
                "%Y.%m.%d",
                "%d.%m.%Y",
            ]
            for fmt in formats:
                try:
                    datetime.strptime(text, fmt)
                    return True
                except ValueError:
                    continue
            return False
        except Exception:
            return False

    @classmethod
    def load_from_file(cls, config_path: Path) -> "ReplaceConfig":
        """Load configuration from YAML file."""
        try:
            with config_path.open("r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
            return cls(
                search_term=config_data["search_term"],
                replace_term=config_data["replace_term"],
                directory=Path(config_data.get("directory", ".")),
                exclude_extensions=config_data.get("exclude_extensions", []),
                include_extensions=config_data.get("include_extensions", []),
                max_workers=config_data.get("max_workers", 4),
                config_file=config_path,
                dry_run=config_data.get("dry_run", False),
            )
        except Exception as e:
            raise SmartRenameError(f"Error loading config: {str(e)}")


class TextProcessor:
    """Handles text processing and replacement operations."""

    TEXT_EXTENSIONS = (
        # Web and markup
        ".php",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".sass",
        ".less",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".vue",
        ".svelte",
        ".erb",
        ".twig",
        ".blade.php",
        ".phtml",
        ".tpl",
        # Programming
        ".py",
        ".pyw",
        ".ipynb",
        ".r",
        ".rb",
        ".pl",
        ".pm",
        ".sh",
        ".bash",
        ".ps1",
        ".bat",
        ".cmd",
        # Data and config
        ".json",
        ".yaml",
        ".yml",
        ".xml",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
        ".env",
        ".properties",
        # Documentation
        ".md",
        ".markdown",
        ".rst",
        ".tex",
        ".txt",
        ".log",
        ".csv",
        ".tsv",
        ".sql",
        ".graphql",
        # Templates
        ".ejs",
        ".hbs",
        ".mustache",
        ".jade",
        ".pug",
        # Web
        ".asp",
        ".aspx",
        ".jsp",
        ".cfm",
        ".gohtml",
        ".htaccess",
        ".gitignore",
        # Build and package
        ".dockerfile",
        ".lock",
        ".map",
        ".mjs",
        ".cjs",
        ".gql",
        ".proto",
        # Other languages
        ".vbs",
        ".lua",
        ".groovy",
        ".kt",
        ".kts",
        ".dart",
        ".java",
        ".cs",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".vb",
        ".fs",
        ".fsx",
        ".scala",
        ".clj",
        ".cljs",
        ".edn",
        ".erl",
        ".ex",
        ".exs",
        ".elm",
        ".hs",
        ".lhs",
        ".jl",
        ".rs",
        ".go",
        ".mod",
        ".sum",
        ".tf",
        ".tfvars",
        ".bal",
    )

    @staticmethod
    def detect_encoding(file_path: Path) -> str:
        """Detect file encoding using chardet."""
        try:
            with file_path.open("rb") as file:
                raw_data = file.read(10000)  # Read first 10KB for efficiency
                result = chardet.detect(raw_data)
                encoding = result["encoding"] or "utf-8"
                logger.debug(
                    "Detected encoding",
                    extra={
                        "operation": "encoding",
                        "file": str(file_path),
                        "encoding": encoding,
                    },
                )
                return encoding
        except Exception as e:
            logger.warning(
                f"Could not detect encoding for {file_path}: {e}",
                extra={"operation": "encoding", "file": str(file_path)},
            )
            return "utf-8"

    @staticmethod
    def get_case_pattern(matched_text: str) -> str:
        """Determine the case pattern of the matched text."""
        if matched_text.islower():
            return "lower"
        elif matched_text.isupper():
            return "upper"
        elif (
            len(matched_text) > 1
            and matched_text[0].isupper()
            and matched_text[1:].islower()
        ):
            return "title"
        return "custom"

    @staticmethod
    def apply_case_structure(
        text: str, case_pattern: str, reference_text: Optional[str] = None
    ) -> str:
        """Apply the case structure to the replacement text."""
        if case_pattern == "lower":
            return text.lower()
        elif case_pattern == "upper":
            return text.upper()
        elif case_pattern == "title":
            return text[0].upper() + text[1:].lower() if text else text
        elif case_pattern == "custom" and reference_text:
            result = ""
            for i, char in enumerate(text):
                if i < len(reference_text):
                    if reference_text[i].isupper():
                        result += char.upper()
                    elif reference_text[i].islower():
                        result += char.lower()
                    else:
                        result += char
                else:
                    result += char
            return result
        return text

    @classmethod
    def is_text_file(cls, file_path: Path, config: ReplaceConfig) -> bool:
        """Check if a file is a text file based on its extension and config."""
        ext = file_path.suffix.lower()
        if config.include_extensions and ext not in config.include_extensions:
            return False
        if config.exclude_extensions and ext in config.exclude_extensions:
            return False
        return ext in cls.TEXT_EXTENSIONS

    @staticmethod
    def validate_term(term: str, term_type: str) -> None:
        """Validate search or replace term for invalid characters."""
        invalid_chars = r'[<>:"/\\|?*]'
        if re.search(invalid_chars, term):
            raise SmartRenameError(
                f"Invalid {term_type} term '{term}' contains prohibited characters: {invalid_chars}"
            )
        if not term.strip():
            raise SmartRenameError(
                f"{term_type.capitalize()} term cannot be empty or whitespace"
            )


class IgnoreFileProcessor:
    """Handles parsing and applying ignore patterns from .gitignore files."""

    @staticmethod
    def load_gitignore_patterns(directory: Path) -> Optional[pathspec.PathSpec]:
        """Load .gitignore patterns recursively from the directory and its parents."""
        patterns = []
        current_dir = directory
        while current_dir != current_dir.parent:  # Stop at root
            gitignore_path = current_dir / ".gitignore"
            if gitignore_path.exists():
                try:
                    with gitignore_path.open("r", encoding="utf-8") as f:
                        patterns.extend(f.read().splitlines())
                    logger.debug(
                        f"Loaded .gitignore from {gitignore_path}",
                        extra={"operation": "gitignore_load"},
                    )
                except Exception as e:
                    logger.warning(
                        f"Error loading .gitignore from {gitignore_path}: {e}",
                        extra={"operation": "gitignore_load"},
                    )
            current_dir = current_dir.parent
        if patterns:
            return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
        return None

    @staticmethod
    def is_ignored(
        path: Path, directory: Path, spec: Optional[pathspec.PathSpec]
    ) -> bool:
        """Check if a path is ignored based on .gitignore patterns."""
        if spec is None:
            return False
        try:
            rel_path = path.relative_to(directory).as_posix()
            ignored = spec.match_file(rel_path)
            if ignored:
                logger.debug(
                    f"Ignored path: {path}", extra={"operation": "gitignore_check"}
                )
            return ignored
        except ValueError:
            return False


class FileHandler:
    """Handles file and directory name and content replacement operations."""

    @staticmethod
    def process_path_name(
        path: Path, search_term: str, replace_term: str, dry_run: bool
    ) -> Tuple[Path, bool]:
        """Process and rename a file or directory if its name contains the search term."""
        try:
            TextProcessor.validate_term(search_term, "search")
            TextProcessor.validate_term(replace_term, "replace")
            path_name = path.name
            pattern = re.compile(
                r"(?<!\w)" + re.escape(search_term) + r"(?!\w)",
                re.IGNORECASE | re.UNICODE,
            )

            def replacement(match):
                matched_text = match.group(0)
                case_pattern = TextProcessor.get_case_pattern(matched_text)
                return TextProcessor.apply_case_structure(
                    replace_term, case_pattern, matched_text
                )

            new_path_name = pattern.sub(replacement, path_name)
            if new_path_name != path_name:
                new_path = path.parent / new_path_name
                if not dry_run:
                    path.rename(new_path)
                    logger.info(
                        f"Renamed {path} to {new_path}",
                        extra={
                            "operation": "rename_path",
                            "file_size": path.stat().st_size if path.is_file() else 0,
                        },
                    )
                else:
                    logger.info(
                        f"[Dry Run] Would rename {path} to {new_path}",
                        extra={"operation": "dry_run_rename"},
                    )
                return new_path, True
            return path, False
        except Exception as e:
            logger.error(
                f"Error renaming {path}: {e}", extra={"operation": "rename_path"}
            )
            raise SmartRenameError(f"Failed to rename {path}") from e

    @staticmethod
    def process_file_content(
        file_path: Path, search_term: str, replace_term: str, dry_run: bool
    ) -> bool:
        """Process and replace content inside a text file."""
        try:
            TextProcessor.validate_term(search_term, "search")
            TextProcessor.validate_term(replace_term, "replace")
            encoding = TextProcessor.detect_encoding(file_path)
            with file_path.open("r", encoding=encoding, errors="replace") as file:
                content = file.read()
            pattern = re.compile(
                r"(?<!\w)" + re.escape(search_term) + r"(?!\w)",
                re.IGNORECASE | re.UNICODE,
            )

            def replacement(match):
                matched_text = match.group(0)
                case_pattern = TextProcessor.get_case_pattern(matched_text)
                return TextProcessor.apply_case_structure(
                    replace_term, case_pattern, matched_text
                )

            new_content = pattern.sub(replacement, content)
            if new_content != content:
                if not dry_run:
                    with file_path.open("w", encoding=encoding) as file:
                        file.write(new_content)
                    logger.info(
                        f"Updated content in {file_path}",
                        extra={
                            "operation": "update_content",
                            "file_size": file_path.stat().st_size,
                        },
                    )
                else:
                    logger.info(
                        f"[Dry Run] Would update content in {file_path}",
                        extra={"operation": "dry_run_content"},
                    )
                return True
            return False
        except Exception as e:
            logger.error(
                f"Error processing {file_path}: {e}",
                extra={"operation": "update_content"},
            )
            raise SmartRenameError(f"Failed to process {file_path}") from e

    @staticmethod
    def update_path_references(
        file_path: Path, old_path: Path, new_path: Path, dry_run: bool
    ) -> bool:
        """Update references to renamed paths in file content."""
        if not TextProcessor.is_text_file(file_path, ReplaceConfig("", "", Path.cwd())):
            return False
        try:
            encoding = TextProcessor.detect_encoding(file_path)
            with file_path.open("r", encoding=encoding, errors="replace") as file:
                content = file.read()

            old_path_pattern = re.escape(old_path.as_posix()).replace("\\", r"[\\/]")
            pattern = re.compile(old_path_pattern, re.IGNORECASE)
            new_content = pattern.sub(new_path.as_posix().replace("\\", "/"), content)

            if new_content != content:
                if not dry_run:
                    with file_path.open("w", encoding=encoding) as file:
                        file.write(new_content)
                    logger.info(
                        f"Updated path references in {file_path}",
                        extra={
                            "operation": "update_references",
                            "file_size": file_path.stat().st_size,
                        },
                    )
                else:
                    logger.info(
                        f"[Dry Run] Would update path references in {file_path}",
                        extra={"operation": "dry_run_references"},
                    )
                return True
            return False
        except Exception as e:
            logger.error(
                f"Error updating path references in {file_path}: {e}",
                extra={"operation": "update_references"},
            )
            raise SmartRenameError(f"Failed to update references in {file_path}") from e


class DirectoryProcessor:
    """Handles directory processing and file operations."""

    @staticmethod
    def process_directory(config: ReplaceConfig) -> None:
        """Process directory for search and replace operations."""
        renamed_paths: List[Tuple[Path, Path]] = []
        gitignore_spec = IgnoreFileProcessor.load_gitignore_patterns(config.directory)
        summary = {"files_processed": 0, "files_modified": 0, "errors": 0}

        try:
            with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
                futures = []
                for item in config.directory.rglob("*"):
                    if item.is_file() or item.is_dir():
                        futures.append(
                            executor.submit(
                                DirectoryProcessor._process_item,
                                item,
                                config,
                                renamed_paths,
                                gitignore_spec,
                                summary,
                            )
                        )
                for future in futures:
                    future.result()

            logger.info(
                "Processing complete",
                extra={
                    "operation": "complete",
                    "files_processed": summary["files_processed"],
                    "files_modified": summary["files_modified"],
                    "errors": summary["errors"],
                },
            )
        except Exception as e:
            logger.error(
                f"Error processing directory: {e}", extra={"operation": "error"}
            )
            raise SmartRenameError(f"Failed to process directory: {str(e)}")

    @staticmethod
    def _should_process_item(
        item_path: Path, config: ReplaceConfig, gitignore_spec
    ) -> bool:
        """Check if an item should be processed based on configuration."""
        if IgnoreFileProcessor.is_ignored(item_path, config.directory, gitignore_spec):
            return False
        if item_path.is_file() and not TextProcessor.is_text_file(item_path, config):
            return False
        return True

    @staticmethod
    def _process_item(
        item_path: Path,
        config: ReplaceConfig,
        renamed_paths: List[Tuple[Path, Path]],
        gitignore_spec,
        summary: Dict[str, int],
    ) -> None:
        """Process a single item (file or directory)."""
        try:
            if not DirectoryProcessor._should_process_item(
                item_path, config, gitignore_spec
            ):
                return

            summary["files_processed"] += 1
            new_path, renamed = FileHandler.process_path_name(
                item_path, config.search_term, config.replace_term, config.dry_run
            )

            if renamed:
                renamed_paths.append((item_path, new_path))
                summary["files_modified"] += 1

            if item_path.is_file():
                content_modified = FileHandler.process_file_content(
                    new_path, config.search_term, config.replace_term, config.dry_run
                )
                if content_modified:
                    summary["files_modified"] += 1

        except Exception as e:
            logger.error(
                f"Error processing {item_path}: {e}",
                extra={"operation": "process_item", "file": str(item_path)},
            )
            summary["errors"] += 1


def load_config_file(config_file: Path) -> Dict:
    """Load configuration from a YAML file."""
    try:
        with config_file.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            logger.debug(
                f"Loaded config from {config_file}: {config}",
                extra={"operation": "load_config"},
            )
            return config
    except Exception as e:
        logger.error(
            f"Error loading config file {config_file}: {e}",
            extra={"operation": "load_config"},
        )
        raise SmartRenameError(f"Failed to load config file {config_file}") from e


def main() -> None:
    """Execute the main program logic.

    Parse command line arguments, load configuration, and process files
    according to the specified search and replace parameters.
    """
    try:
        parser = argparse.ArgumentParser(
            description="Smart Rename Pro - Batch file and content renaming tool"
        )
        parser.add_argument("--directory", required=True, help="Directory to process")
        parser.add_argument("--search", help="Term to search for")
        parser.add_argument("--replace", help="Term to replace with")
        parser.add_argument(
            "--workers",
            type=int,
            default=4,
            help="Number of parallel workers (1-16)",
            choices=range(1, 17),
        )
        parser.add_argument("--config", help="Path to YAML config file")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without applying them",
        )

        args = parser.parse_args()

        # Initialize config with defaults
        config = ReplaceConfig(
            search_term=args.search or "",
            replace_term=args.replace or "",
            directory=Path(args.directory).resolve(),
            max_workers=args.workers,
            config_file=Path(args.config).resolve() if args.config else None,
            exclude_extensions=None,
            include_extensions=None,
            dry_run=args.dry_run,
        )

        # Load config file if provided
        if config.config_file:
            if not config.config_file.exists():
                raise SmartRenameError(
                    f"Config file {config.config_file} does not exist"
                )
            config_data = load_config_file(config.config_file)
            config.search_term = config.search_term or config_data.get(
                "search_term", ""
            )
            config.replace_term = config.replace_term or config_data.get(
                "replace_term", ""
            )
            config.exclude_extensions = config_data.get("exclude_extensions", [])
            config.include_extensions = config_data.get("include_extensions", [])

        # Validate required parameters
        if not config.search_term or not config.replace_term:
            parser.error(
                "Both --search and --replace terms are required, either via command line or config file"
            )

        TextProcessor.validate_term(config.search_term, "search")
        TextProcessor.validate_term(config.replace_term, "replace")

        DirectoryProcessor.process_directory(config)
    except SmartRenameError as e:
        logger.error(f"Operation failed: {e}", extra={"operation": "main"})
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", extra={"operation": "main"})
        exit(1)


if __name__ == "__main__":
    main()
