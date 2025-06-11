import os
import re
import argparse
import yaml
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor
import chardet
from typing import Optional, Tuple, List
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rename.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ReplaceConfig:
    """Configuration for search and replace operation."""
    search_term: str
    replace_term: str
    directory: str
    max_workers: int = 4
    config_file: Optional[str] = None
    exclude_extensions: Optional[List[str]] = None
    include_extensions: Optional[List[str]] = None

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
    def detect_encoding(file_path: str) -> str:
        """Detect file encoding using chardet."""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read(10000)  # Read first 10KB for efficiency
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception as e:
            logger.warning(f"Could not detect encoding for {file_path}: {e}")
            return 'utf-8'

    @staticmethod
    def get_case_pattern(search_term: str, matched_text: str) -> str:
        """Detect the case pattern between search_term and matched_text."""
        if matched_text.islower():
            return "lower"
        elif matched_text.isupper():
            return "upper"
        elif matched_text.istitle():
            return "title"
        else:
            return "custom"

    @staticmethod
    def apply_case_structure(text: str, case_type: str, pattern: str = None) -> str:
        """Apply case structure to text based on pattern."""
        if case_type == "lower":
            return text.lower()
        elif case_type == "upper":
            return text.upper()
        elif case_type == "title":
            return text.title()
        elif case_type == "custom" and pattern:
            # Match the length and case of the reference pattern exactly
            result = []
            for i, char in enumerate(text):
                if i < len(pattern):
                    result.append(char.upper() if pattern[i].isupper() else char.lower())
                else:
                    # If the pattern is shorter, use lower for remaining
                    result.append(char.lower())
            return ''.join(result)
        return text

    @classmethod
    def is_text_file(cls, file_path: str, config: ReplaceConfig) -> bool:
        """Check if a file is a text file based on its extension and config."""
        ext = Path(file_path).suffix.lower()
        if config.include_extensions and ext not in config.include_extensions:
            return False
        if config.exclude_extensions and ext in config.exclude_extensions:
            return False
        return ext in cls.TEXT_EXTENSIONS

class FileHandler:
    """Handles file and directory name and content replacement operations."""
    
    @staticmethod
    def process_path_name(path: str, search_term: str, replace_term: str) -> Tuple[str, bool]:
        """Process a file or directory path name."""
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        
        if search_term.lower() in basename.lower():
            case_pattern = TextProcessor.get_case_pattern(search_term, basename)
            new_basename = basename.replace(search_term, TextProcessor.apply_case_structure(replace_term, case_pattern, search_term))
            new_path = os.path.join(dirname, new_basename)
            try:
                os.rename(path, new_path)
                return new_path, True
            except OSError as e:
                logging.error(f"Error renaming {path}: {e}")
                return path, False
        return path, False

    @staticmethod
    def process_file_content(file_path: str, search_term: str, replace_term: str) -> bool:
        """Process file content and replace search term with replace term."""
        try:
            # Detect file encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'

            # Read file content
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()

            # Use re.sub with a function to handle each match
            def repl(match):
                matched_text = match.group(0)
                case_pattern = TextProcessor.get_case_pattern(search_term, matched_text)
                return TextProcessor.apply_case_structure(replace_term, case_pattern, matched_text)

            new_content, count = re.subn(re.escape(search_term), repl, content, flags=re.IGNORECASE)

            if count > 0:
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(new_content)
                return True
            return False
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")
            return False

    @staticmethod
    def update_path_references(old_path: str, new_path: str, search_term: str, replace_term: str) -> None:
        """Update path references in all text files."""
        root_dir = os.path.dirname(os.path.dirname(old_path))
        # Use a minimal config for extension filtering
        config = ReplaceConfig(search_term, replace_term, root_dir)
        for root, _, files in os.walk(root_dir):
            for file in files:
                if TextProcessor.is_text_file(file, config):
                    file_path = os.path.join(root, file)
                    try:
                        # Detect file encoding
                        with open(file_path, 'rb') as f:
                            raw_data = f.read()
                            result = chardet.detect(raw_data)
                            encoding = result['encoding'] or 'utf-8'

                        # Read file content
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()

                        # Replace old path with new path
                        old_relative = os.path.relpath(old_path, root_dir)
                        new_relative = os.path.relpath(new_path, root_dir)
                        old_relative = old_relative.replace('\\', '/')
                        new_relative = new_relative.replace('\\', '/')
                        if old_relative in content:
                            new_content = content.replace(old_relative, new_relative)
                            with open(file_path, 'w', encoding=encoding) as f:
                                f.write(new_content)
                    except Exception as e:
                        logging.error(f"Error updating references in {file_path}: {e}")

class DirectoryProcessor:
    """Manages recursive directory processing with parallel execution."""
    
    @staticmethod
    def process_directory(config: ReplaceConfig) -> None:
        """Process all directories and files recursively."""
        def process_item(path: str) -> None:
            try:
                # Process path name
                new_path, renamed = FileHandler.process_path_name(path, config.search_term, config.replace_term)
                
                # If renamed, update path references in other files
                if renamed:
                    FileHandler.update_path_references(path, new_path, config.search_term, config.replace_term)
                
                # Process file content if it's a text file
                if os.path.isfile(new_path) and TextProcessor.is_text_file(new_path, config):
                    FileHandler.process_file_content(new_path, config.search_term, config.replace_term)
                
                # Recursively process subdirectories
                if os.path.isdir(new_path):
                    for item in os.listdir(new_path):
                        item_path = os.path.join(new_path, item)
                        process_item(item_path)
            except Exception as e:
                logging.error(f"Error processing {path}: {e}")

        # Start processing from the root directory
        process_item(config.directory)

def load_config_file(config_file: str) -> dict:
    """Load configuration from a YAML file."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Error loading config file {config_file}: {e}")
        return {}

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Smart search and replace in project files and directories.")
    parser.add_argument('--directory', required=True, help="Directory to process")
    parser.add_argument('--search', help="Term to search for")
    parser.add_argument('--replace', help="Term to replace with")
    parser.add_argument('--workers', type=int, default=4, help="Number of parallel workers")
    parser.add_argument('--config', help="Path to YAML config file")

    args = parser.parse_args()

    # Initialize config with defaults
    config = ReplaceConfig(
        search_term=args.search or "",
        replace_term=args.replace or "",
        directory=os.path.abspath(args.directory),
        max_workers=args.workers,
        config_file=args.config,
        exclude_extensions=None,
        include_extensions=None
    )

    # Load config file if provided
    if args.config:
        config_data = load_config_file(args.config)
        config.search_term = config.search_term or config_data.get('search_term', '')
        config.replace_term = config.replace_term or config_data.get('replace_term', '')
        config.exclude_extensions = config_data.get('exclude_extensions', [])
        config.include_extensions = config_data.get('include_extensions', [])

    # Validate required parameters
    if not config.search_term or not config.replace_term:
        parser.error("Both --search and --replace terms are required, either via command line or config file")

    DirectoryProcessor.process_directory(config)

if __name__ == "__main__":
    main() 