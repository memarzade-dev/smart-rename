# Smart Rename

A robust, cross-platform Python script for intelligently renaming files, directories, and updating content in text files within a project directory. Ideal for renaming components in large projects like Laravel, WordPress, or any codebase, with case-sensitive replacements, path reference updates, non-ASCII support, and robust ignore pattern handling.

## Features
- **Smart Renaming**: Renames files and directories, preserving case (e.g., `source` → `destination`, `Source` → `Destination`, `SOURCE` → `DESTINATION`, `loveYou` → `هدف`).
- **Content Replacement**: Updates occurrences in text files (e.g., `source=1` → `destination=1`, `زرینین پال` → `هدف`).
- **Path Reference Updates**: Automatically updates references to renamed paths (e.g., `import source_payments` → `import destination_payments`).
- **Ignore Patterns**: Respects `.gitignore` patterns recursively, skipping files like logs or `.git/`.
- **Dry-Run Mode**: Previews changes without applying them for safety.
- **Cross-Platform**: Compatible with Windows, Linux, and macOS using `pathlib`.
- **File Support**: Processes all common text file formats (`.php`, `.js`, `.py`, `.txt`, etc.).
- **Configuration File**: Supports `.smart-rename.yaml` for custom settings (e.g., exclude/include extensions).
- **Parallel Processing**: Multithreading for efficient processing of large projects.
- **Encoding Handling**: Detects file encodings with `chardet` for robust text processing.
- **Error Handling**: Custom exceptions, detailed logging with file size and operation context.
- **Validation**: Checks for invalid characters in search/replace terms.
- **Logging**: Logs to `rename.log` and console with debug-level details.
- **CI/CD Pipeline**: Automated testing, linting, coverage, and release creation via GitHub Actions.
- **Unit Tests**: Comprehensive tests for case-sensitivity, non-ASCII, special characters, ignore patterns, and dry-run.
- **Docker Support**: Containerized execution environment.
- **Executable Build**: Windows `.exe` for standalone distribution.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/memarzade-dev/smart-rename.git
   cd smart-rename
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure Python 3.8+ is installed:
   - **Windows**: Download from https://www.python.org/downloads/
   - **Linux**: `sudo apt-get install python3.10`
   - **macOS**: `brew install python@3.10`

## Usage

Run the script from the command line:
```bash
python smart_rename_pro.py --directory /path/to/project --search source --replace destination
```

### Non-ASCII Example:
```bash
python smart_rename_pro.py --directory /path/to/project --search "loveYou" --replace "هدف"
```

### Arguments
- `--directory`: Project directory path (required).
- `--search`: Term to search for (optional if using config file).
- `--replace`: Term to replace with (optional if using config file).
- `--workers`: Number of parallel workers (1-16, default: 4).
- `--config`: Path to YAML config file (optional).
- `--dry-run`: Preview changes without applying them (optional).

### Configuration File
Create `.smart-rename.yaml`:
```yaml
search_term: source
replace_term: destination
exclude_extensions:
  - .log
  - .bak
include_extensions:
  - .php
  - .js
  - .txt
```
Run with config:
```bash
python smart_rename_pro.py --directory /path/to/project --config .smart-rename.yaml
```

### Ignore Support
The script respects `.gitignore` patterns recursively. Example:
```
*.log
dist/
.git/
```
Ignored: `rename.log`, `dist/`, `.git/`.

### Dry-Run Mode
Preview changes:
```bash
python smart_rename_pro.py --directory /path/to/project --search source --replace destination --dry-run
```

### Examples
1. **English Rename**:
   ```bash
   python smart_rename_pro.py --directory /path/to/project --search source --replace destination
   ```
   - Renames `source_payments/` to `destination_payments/`.
   - Renames `source_config.php` to `destination_config.php`.
   - Updates `use source_payments;` to `use destination_payments;`.
   - Preserves case: `SourcePayments` → `DestinationPayments`.

2. **Non-ASCII Rename**:
   ```bash
   python smart_rename_pro.py --directory /path/to/project --search "loveYou" --replace "هدف"
   ```
   - Renames `loveYou.txt` to `هدف.txt`.
   - Updates content: `پروژه loveYou` → `پروژه هدف`.

## Docker Setup

1. Build the image:
   ```bash
   docker build -t smart-rename .
   ```
2. Run:
   ```bash
   docker run -v /path/to/project:/source smart-rename --directory /source --search source --replace destination
   ```
3. Non-ASCII:
   ```bash
   docker run -v /path/to/project:/source smart-rename --directory /source --search "loveYou" --replace "هدف"
   ```

## Build Windows Executable

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build:
   ```bash
   pyinstaller --onefile --name smart-rename smart_rename_pro.py
   ```
3. Run:
   ```bash
   .\dist\smart-rename.exe --directory "C:\MyProject" --search source --replace destination
   ```

## Run Tests

Run unit tests:
```bash
pytest tests/ --cov=smart_rename_pro.py --cov-report=html
```
Coverage report: `htmlcov/index.html`

## CI/CD Pipeline

The `.github/workflows/ci.yml` includes:
- Tests on Ubuntu, Windows, macOS with Python 3.8, 3.9, 3.10.
- Linting with `flake8`.
- Coverage with `pytest-cov`.
- Builds `.exe` releases on tagged commits.

View results:
- GitHub Actions: https://github.com/memarzade-dev/smart-rename/actions
- Configure Codecov: Add `CODECOV_TOKEN` to GitHub Secrets.

## Troubleshooting

- **Encoding Errors**: Ensure files use UTF-8 encoding or compatible formats.
- **Permission Issues**: Run with elevated permissions (`sudo` on Linux/macOS, Admin on Windows).
- **Ignored Files**: Check `.gitignore` patterns if files are unexpectedly skipped.
- **Non-ASCII Issues**: Ensure terminal supports Unicode (e.g., PowerShell, UTF-8 enabled).
- **Logs**: Review `rename.log` for detailed error messages and operation details.

## Best Practices
- **Backup**: Back up projects before running the script.
- **Dry-Run**: Always test with `--dry-run` first.
- **Small Batches**: Process large projects in smaller directories for better control.
- **Validate Config**: Ensure `.smart-rename.yaml` is correct before using.
- **Monitor Logs**: Use `rename.log` to track changes and errors.

## Contributing
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "Add feature"`
4. Test: `pytest tests/`
5. Lint: `flake8 .`
6. Push: `git push origin feature/my-feature`
7. Open Pull Request.

## License
MIT License. See [LICENSE](LICENSE).

## Contact
Issues or suggestions: Open a GitHub issue or contact [memarzade-dev](https://github.com/memarzade-dev).
