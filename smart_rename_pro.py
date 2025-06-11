import argparse
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import chardet
import yaml
import pathspec


# Configure logging with platform-specific log file path
log_file = Path("rename.log").resolve()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ReplaceConfig:
    """Configuration for search and replace operations."""
    search_term: str
    replace_term: str
    directory: Path
    max_workers: int = 4
    config_file: Optional[Path] = None
    exclude_extensions: List[str] = None
    include_extensions: List[str] = None
    dry_run: bool = False


class SmartRenameError(Exception):
    """Custom exception for smart rename operations."""
    pass


class TextProcessor:
    """Handles text processing operations."""

    @staticmethod
    def get_case_pattern(search_term: str) -> str:
        """Generate case-insensitive pattern for search term."""
        return ''.join(f'[{c.lower()}{c.upper()}]' if c.isalpha() else c
                      for c in search_term)

    @staticmethod
    def apply_case_structure(text: str, pattern: str) -> str:
        """Apply case structure from pattern to text."""
        result = []
        for i, char in enumerate(text):
            if i < len(pattern):
                if pattern[i].isupper():
                    result.append(char.upper())
                else:
                    result.append(char.lower())
            else:
                result.append(char)
        return ''.join(result)


class IgnoreFileProcessor:
    """Handles .gitignore file processing."""

    def __init__(self, directory: Path):
        self.directory = directory
        self.spec = None
        self.load_ignore_patterns()

    def load_ignore_patterns(self) -> None:
        """Load ignore patterns from .gitignore file."""
        gitignore_path = self.directory / '.gitignore'
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    patterns = f.readlines()
                self.spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)
            except Exception as e:
                logger.warning(f"Error loading .gitignore from {gitignore_path}: {e}")
                self.spec = pathspec.PathSpec([])
        else:
            self.spec = pathspec.PathSpec([])

    def is_ignored(self, path: Path) -> bool:
        """Check if a path should be ignored."""
        if self.spec is None:
            return False
        try:
            # Convert path to POSIX-style for consistent matching
            rel_path = path.relative_to(self.directory).as_posix()
            return self.spec.match_file(rel_path)
        except ValueError:
            # Path is not relative to directory
            return False


class FileHandler:
    """Handles file operations."""

    def __init__(self, config: ReplaceConfig):
        self.config = config
        self.text_processor = TextProcessor()
        self.case_pattern = self.text_processor.get_case_pattern(
            config.search_term
        )

    def process_path_name(self, path: Path) -> Optional[Path]:
        """Process and rename a file or directory path."""
        if self.config.search_term.lower() not in path.name.lower():
            return None

        new_name = path.name.replace(
            self.config.search_term,
            self.config.replace_term
        )
        new_name = self.text_processor.apply_case_structure(
            new_name,
            self.case_pattern
        )
        new_path = path.parent / new_name

        if not self.config.dry_run:
            try:
                # Handle case-insensitive filesystems (Windows)
                if path.exists() and new_path.exists() and path.name.lower() == new_path.name.lower():
                    temp_path = path.parent / f"{new_path.stem}_temp{new_path.suffix}"
                    path.rename(temp_path)
                    temp_path.rename(new_path)
                else:
                    path.rename(new_path)
                logger.info(f"Renamed: {path} -> {new_path}")
            except Exception as e:
                logger.error(f"Error renaming {path} -> {new_path}")
                raise SmartRenameError(f"Failed to rename {path}") from e
        else:
            logger.info(f"Would rename: {path} -> {new_path}")

        return new_path

    def process_file_content(self, file_path: Path) -> None:
        """Process and update file content."""
        if not file_path.is_file():
            return

        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'

            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()

            if self.config.search_term.lower() not in content.lower():
                return

            new_content = content.replace(
                self.config.search_term,
                self.config.replace_term
            )
            new_content = self.text_processor.apply_case_structure(
                new_content,
                self.case_pattern
            )

            if not self.config.dry_run:
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(new_content)
                logger.info(f"Updated content in: {file_path}")
            else:
                logger.info(f"Would update content in: {file_path}")

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise SmartRenameError(f"Failed to process {file_path}") from e

    def update_path_references(self, file_path: Path) -> None:
        """Update path references in file content."""
        if not file_path.is_file():
            return

        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'

            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()

            old_path = str(file_path)
            new_path = str(self.process_path_name(file_path))
            if new_path and old_path != new_path:
                # Handle both forward and backward slashes in paths
                old_path_pattern = re.escape(old_path).replace('\\', r'[\\/]')
                new_path_posix = str(Path(new_path).as_posix())
                new_content = re.sub(old_path_pattern, new_path_posix, content)
                
                if not self.config.dry_run:
                    with open(file_path, 'w', encoding=encoding) as f:
                        f.write(new_content)
                    logger.info(f"Updated path references in: {file_path}")
                else:
                    logger.info(f"Would update path references in: {file_path}")

        except Exception as e:
            logger.error(f"Error updating references in {file_path}: {str(e)}")
            raise SmartRenameError(
                f"Failed to update references in {file_path}"
            ) from e


class DirectoryProcessor:
    """Handles directory processing operations."""

    def __init__(self, config: ReplaceConfig):
        self.config = config
        self.file_handler = FileHandler(config)
        self.ignore_processor = IgnoreFileProcessor(config.directory)

    def should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed based on extensions."""
        if self.ignore_processor.is_ignored(file_path):
            return False

        if self.config.exclude_extensions:
            if file_path.suffix.lower() in self.config.exclude_extensions:
                return False

        if self.config.include_extensions:
            return file_path.suffix.lower() in self.config.include_extensions

        return True

    def process_file(self, file_path: Path) -> None:
        """Process a single file."""
        try:
            if not self.should_process_file(file_path):
                return

            self.file_handler.process_file_content(file_path)
            self.file_handler.update_path_references(file_path)

        except Exception as e:
            logger.error(f"Processing failed for {file_path}: {str(e)}")
            raise SmartRenameError(f"Failed to process {file_path}") from e

    def process_directory(self) -> None:
        """Process all files in the directory."""
        logger.info(f"Starting processing in directory: {self.config.directory}")

        try:
            # Ensure directory exists
            if not self.config.directory.exists():
                raise SmartRenameError(f"Directory {self.config.directory} does not exist")

            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                for file_path in self.config.directory.rglob('*'):
                    if file_path.is_file():
                        executor.submit(self.process_file, file_path)

            logger.info("Processing complete")

        except Exception as e:
            logger.error(f"Directory processing failed: {str(e)}")
            raise SmartRenameError("Directory processing failed") from e


def load_config(config_file: Path) -> ReplaceConfig:
    """Load configuration from YAML file."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        return ReplaceConfig(**config_data)
    except Exception as e:
        raise SmartRenameError(f"Failed to load config: {str(e)}") from e


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Smart file renaming and content replacement tool'
    )
    parser.add_argument(
        '--directory',
        type=str,
        required=True,
        help='Directory to process'
    )
    parser.add_argument(
        '--search',
        type=str,
        required=True,
        help='Term to search for'
    )
    parser.add_argument(
        '--replace',
        type=str,
        required=True,
        help='Term to replace with'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )

    args = parser.parse_args()

    try:
        if args.config:
            config = load_config(Path(args.config))
        else:
            config = ReplaceConfig(
                search_term=args.search,
                replace_term=args.replace,
                directory=Path(args.directory).resolve(),
                dry_run=args.dry_run
            )

        processor = DirectoryProcessor(config)
        processor.process_directory()

    except SmartRenameError as e:
        logger.error(f"Error: {str(e)}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        exit(1)


if __name__ == '__main__':
    main() 