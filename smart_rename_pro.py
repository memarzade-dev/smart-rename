import os
import re
import argparse
import yaml
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor
import chardet
import pathspec
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
import platform

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
    """Configuration for search and replace operation."""
    search_term: str
    replace_term: str
    directory: Path
    max_workers: int = 4
    config_file: Optional[Path] = None
    exclude_extensions: Optional[List[str]] = None
    include_extensions: Optional[List[str]] = None
    dry_run: bool = False

class SmartRenameError(Exception):
    """Custom exception for Smart Rename errors."""
    pass

class TextProcessor:
    """Handles text processing and replacement operations."""
    
    TEXT_EXTENSIONS = (
        '.php', '.html', '.htm', '.css', '.scss', '.sass', '.less', '.js', '.jsx', '.ts', '.tsx',
        '.vue', '.svelte', '.erb', '.twig', '.blade.php', '.phtml', '.tpl', '.py', '.pyw', '.ipynb',
        '.r', '.rb', '.pl', '.pm', '.sh', '.bash', '.ps1', '.bat', '.cmd', '.json', '.yaml', '.yml',
        '.xml', '.toml', '.ini', '.cfg', '.conf', '.env', '.properties', '.md', '.markdown', '.rst',
        '.tex', '.txt', '.log', '.csv', '.tsv', '.sql', '.graphql', '.ejs', '.hbs', '.mustache',
        '.jade', '.pug', '.asp', '.aspx', '.jsp', '.cfm', '.gohtml', '.htaccess', '.gitignore',
        '.dockerfile', '.lock', '.map', '.mjs', '.cjs', '.gql', '.proto', '.vbs', '.lua', '.groovy',
        '.kt', '.kts', '.dart', '.swift', '.java', '.cs', '.cpp', '.c', '.h', '.hpp', '.vb', '.fs',
        '.fsx', '.scala', '.clj', '.cljs', '.edn', '.erl', '.ex', '.exs', '.elm', '.hs', '.lhs',
        '.jl', '.rs', '.go', '.mod', '.sum', '.tf', '.tfvars', '.bal'
    )

    @staticmethod
    def detect_encoding(file_path: Path) -> str:
        """Detect file encoding using chardet."""
        try:
            with file_path.open('rb') as file:
                raw_data = file.read(10000)  # Read first 10KB for efficiency
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception as e:
            logger.warning(f"Could not detect encoding for {file_path}: {e}")
            return 'utf-8'

    @staticmethod
    def get_case_pattern(matched_text: str) -> str:
        """Determine the case pattern of the matched text."""
        if matched_text.islower():
            return 'lower'
        elif matched_text.isupper():
            return 'upper'
        elif matched_text[0].isupper() and matched_text[1:].islower():
            return 'title'
        return 'custom'

    @staticmethod
    def apply_case_structure(text: str, case_pattern: str, reference_text: Optional[str] = None) -> str:
        """Apply the case structure to the replacement text."""
        if case_pattern == 'lower':
            return text.lower()
        elif case_pattern == 'upper':
            return text.upper()
        elif case_pattern == 'title':
            return text[0].upper() + text[1:].lower()
        elif case_pattern == 'custom' and reference_text:
            result = ''
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

class IgnoreFileProcessor:
    """Handles parsing and applying ignore patterns from .gitignore files."""
    
    @staticmethod
    def load_gitignore_patterns(directory: Path) -> Optional[pathspec.PathSpec]:
        """Load .gitignore patterns from the directory."""
        gitignore_path = directory / '.gitignore'
        if gitignore_path.exists():
            try:
                with gitignore_path.open('r', encoding='utf-8') as f:
                    patterns = f.read().splitlines()
                return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
            except Exception as e:
                logger.warning(f"Error loading .gitignore from {gitignore_path}: {e}")
        return None

    @staticmethod
    def is_ignored(path: Path, directory: Path, spec: Optional[pathspec.PathSpec]) -> bool:
        """Check if a path is ignored based on .gitignore patterns."""
        if spec is None:
            return False
        rel_path = path.relative_to(directory).as_posix()
        return spec.match_file(rel_path)

class FileHandler:
    """Handles file and directory name and content replacement operations."""
    
    @staticmethod
    def process_path_name(path: Path, search_term: str, replace_term: str, dry_run: bool) -> Tuple[Path, bool]:
        """Process and rename a file or directory if its name contains the search term."""
        try:
            path_name = path.name
            pattern = re.compile(
                r'(?<!\w)' + re.escape(search_term) + r'(?!\w)',
                re.IGNORECASE
            )
            
            def replacement(match):
                matched_text = match.group(0)
                case_pattern = TextProcessor.get_case_pattern(matched_text)
                return TextProcessor.apply_case_structure(replace_term, case_pattern, matched_text)

            new_path_name = pattern.sub(replacement, path_name)
            
            if new_path_name != path_name:
                new_path = path.parent / new_path_name
                if not dry_run:
                    path.rename(new_path)
                    logger.info(f"Renamed {path} to {new_path}")
                else:
                    logger.info(f"[Dry Run] Would rename {path} to {new_path}")
                return new_path, True
            return path, False
        except Exception as e:
            logger.error(f"Error renaming {path}: {e}")
            raise SmartRenameError(f"Failed to rename {path}") from e

    @staticmethod
    def process_file_content(file_path: Path, search_term: str, replace_term: str, dry_run: bool) -> bool:
        """Process and replace content inside a text file."""
        try:
            encoding = TextProcessor.detect_encoding(file_path)
            with file_path.open('r', encoding=encoding, errors='ignore') as file:
                content = file.read()

            pattern = re.compile(
                r'(?<!\w)' + re.escape(search_term) + r'(?!\w)',
                re.IGNORECASE
            )
            
            def replacement(match):
                matched_text = match.group(0)
                case_pattern = TextProcessor.get_case_pattern(matched_text)
                return TextProcessor.apply_case_structure(replace_term, case_pattern, matched_text)

            new_content = pattern.sub(replacement, content)

            if new_content != content:
                if not dry_run:
                    with file_path.open('w', encoding=encoding) as file:
                        file.write(new_content)
                    logger.info(f"Updated content in {file_path}")
                else:
                    logger.info(f"[Dry Run] Would update content in {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            raise SmartRenameError(f"Failed to process {file_path}") from e

    @staticmethod
    def update_path_references(file_path: Path, old_path: Path, new_path: Path, dry_run: bool) -> bool:
        """Update references to renamed paths in file content."""
        if not TextProcessor.is_text_file(file_path, ReplaceConfig("", "", Path.cwd())):
            return False
        try:
            encoding = TextProcessor.detect_encoding(file_path)
            with file_path.open('r', encoding=encoding, errors='ignore') as file:
                content = file.read()

            old_path_pattern = re.escape(old_path.as_posix()).replace('\\', r'[\\/]')
            pattern = re.compile(old_path_pattern, re.IGNORECASE)
            new_content = pattern.sub(new_path.as_posix().replace('\\', '/'), content)

            if new_content != content:
                if not dry_run:
                    with file_path.open('w', encoding=encoding) as file:
                        file.write(new_content)
                    logger.info(f"Updated path references in {file_path}")
                else:
                    logger.info(f"[Dry Run] Would update path references in {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating path references in {file_path}: {e}")
            raise SmartRenameError(f"Failed to update references in {file_path}") from e

class DirectoryProcessor:
    """Manages recursive directory processing with parallel execution."""
    
    @staticmethod
    def process_directory(config: ReplaceConfig) -> None:
        """Process all directories and files recursively, respecting ignore patterns."""
        logger.info(f"Starting processing in directory: {config.directory}")
        
        # Load .gitignore patterns
        gitignore_spec = IgnoreFileProcessor.load_gitignore_patterns(config.directory)
        
        def process_single_item(item_path: Path, renamed_paths: List[Tuple[Path, Path]]) -> None:
            """Process a single file or directory."""
            if IgnoreFileProcessor.is_ignored(item_path, config.directory, gitignore_spec):
                logger.debug(f"Skipping ignored item: {item_path}")
                return
            
            try:
                # Process path name
                new_path, renamed = FileHandler.process_path_name(
                    item_path, config.search_term, config.replace_term, config.dry_run
                )
                if renamed:
                    renamed_paths.append((item_path, new_path))
                
                # Process file content if it's a text file
                if new_path.is_file() and TextProcessor.is_text_file(new_path, config):
                    FileHandler.process_file_content(
                        new_path, config.search_term, config.replace_term, config.dry_run
                    )
                
                # Update references to renamed paths
                for old_path, new_path_ref in renamed_paths:
                    FileHandler.update_path_references(new_path, old_path, new_path_ref, config.dry_run)
            except SmartRenameError as e:
                logger.error(f"Processing failed for {item_path}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error processing {item_path}: {e}")

        # Validate directory
        if not config.directory.exists():
            logger.error(f"Directory {config.directory} does not exist")
            raise SmartRenameError(f"Directory {config.directory} does not exist")

        # Collect items to process
        items_to_process: List[Path] = []
        renamed_paths: List[Tuple[Path, Path]] = []

        # Walk directories top-down
        for root, dirs, files in os.walk(config.directory, topdown=True):
            root_path = Path(root)
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not IgnoreFileProcessor.is_ignored(
                root_path / d, config.directory, gitignore_spec)]
            
            for dir_name in dirs:
                dir_path = root_path / dir_name
                new_dir_path, renamed = FileHandler.process_path_name(
                    dir_path, config.search_term, config.replace_term, config.dry_run
                )
                if renamed:
                    renamed_paths.append((dir_path, new_dir_path))
            
            for file in files:
                file_path = root_path / file
                if not IgnoreFileProcessor.is_ignored(file_path, config.directory, gitignore_spec):
                    items_to_process.append(file_path)

        # Process items in parallel
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            executor.map(lambda fp: process_single_item(fp, renamed_paths), items_to_process)

        logger.info("Processing complete")

def load_config_file(config_file: Path) -> Dict:
    """Load configuration from a YAML file."""
    try:
        with config_file.open('r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Error loading config file {config_file}: {e}")
        raise SmartRenameError(f"Failed to load config file {config_file}")
    except Exception as e:
        return {}

def main():
    """Main entry point for the project."""
    try:
        parser = argparse.ArgumentParser(description="Smart search and replace in project files and directories.")
        parser.add_argument('--directory', required=True, help="Directory to process")
        parser.add_argument('--search', help="Term to search for")
        parser.add_argument('--replace', help="Term to replace with")
        parser.add_argument('--workers', type=int, default=4, help="Number of parallel workers")
        parser.add_argument('--config', help="Path to YAML config file")
        parser.add_argument('--dry-run', action='store_true', help="Preview changes without applying them")

        args = parser.parse_args()

        # Initialize config with defaults
        config = ReplaceConfig(
            search_term=args.search or "",
            replace_term=args.replace or "",
            directory=Path(args.directory).resolve(),
            max_workers=args.workers,
            config_file=Path(args.config) if args.config else None,
            exclude_extensions=None,
            include_extensions=None,
            dry_run=args.dry_run
        )

        # Load config file if provided
        if config.config_file:
            config_data = load_config_file(config.config_file)
            config.search_term = config.search_term or config_data.get('search_term', '')
            config.replace_term = config.replace_term or config_data.get('replace_term', '')
            config.exclude_extensions = config_data.get('exclude_extensions', [])
            config.include_extensions = config_data.get('include_extensions', [])

        # Validate required parameters
        if not config.search_term or not config.replace_term:
            parser.error("Both --search and --replace terms are required, either via command line or config file")

        DirectoryProcessor.process_directory(config)
    except SmartRenameError as e:
        logger.error(f"Operation failed: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main() 