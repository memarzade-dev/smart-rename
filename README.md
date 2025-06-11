# Smart Rename

A professional Python script for intelligently renaming files, directories, and updating content in text files within a project directory. Ideal for renaming components in large projects like Laravel, WordPress, or any codebase, with case-sensitive replacements and path reference updates.

## Features
- **Smart Renaming**: Renames files and directories containing the search term, preserving case (e.g., `source` → `destination`, `Source` → `Destination`, `SOURCE` → `DESTINATION`).
- **Content Replacement**: Updates occurrences of the search term in text file contents, including in variables or concatenated strings (e.g., `source=1` → `destination=1`).
- **Path Reference Updates**: Automatically updates references to renamed files or directories in text files (e.g., `import source_payments` → `import destination_payments`).
- **Ignore Support**: Respects `.gitignore` patterns, skipping files and directories like logs, build artifacts, or `.git/`.
- **Comprehensive File Support**: Processes all common text file formats (`.php`, `.js`, `.py`, `.json`, `.md`, etc.).
- **Configuration File**: Supports a `.smart-rename.yaml` file for customizable settings (e.g., exclude/include extensions).
- **Parallel Processing**: Uses multithreading for efficient processing of large projects.
- **Robust Encoding Handling**: Detects file encodings using `chardet` to handle various text formats.
- **Logging**: Detailed logs saved to `rename.log` and displayed in the console.
- **CI/CD Pipeline**: Automated testing, linting, coverage, and release creation via GitHub Actions.
- **Unit Tests**: Comprehensive tests for key functionalities, including non-ASCII, special characters, and ignore patterns.
- **Docker Support**: Run the script in a containerized environment.
- **Executable Build**: Supports building a Windows `.exe` for easy distribution.

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
3. Ensure Python 3.7+ is installed.

## Usage
Run the script from the command line:
```bash
python smart_rename_pro.py --directory /path/to/project --search source --replace destination
```
### Arguments
- `--directory`: Path to the project directory (required).
- `--search`: Term to search for (optional if using config file).
- `--replace`: Term to replace with (optional if using config file).
- `--workers`: Number of parallel workers (optional, default: 4).
- `--config`: Path to YAML config file (optional).

### Configuration File
Create a `.smart-rename.yaml` file to specify settings:
```yaml
search_term: source
replace_term: destination
exclude_extensions:
  - .log
  - .bak
include_extensions:
  - .php
  - .js
```
Run with config file:
```bash
python smart_rename_pro.py --directory /path/to/project --config .smart-rename.yaml
```

### Ignore Support
The script automatically respects `.gitignore` patterns in the project directory. For example:
```gitignore
*.log
dist/
.git/
```
Files and directories matching these patterns (e.g., `rename.log`, `dist/`, `.git/`) will be skipped during processing.

### Example
To replace `source` with `destination` in a project:
```bash
python smart_rename_pro.py --directory "C:\my_project" --search source --replace destination
```
This will:
- Rename `source_payments` directory to `destination_payments`.
- Rename `source_config.php` to `destination_config.php`.
- Update content like `use source_payments;` to `use destination_payments;`.
- Preserve case: `SourcePayments` → `DestinationPayments`.
- Skip ignored files like `rename.log` or `.git/`.

## Docker Support
Run the script in a Docker container:
1. Build the Docker image:
   ```bash
   docker build -t smart-rename .
   ```
2. Run the container, mounting your project directory:
   ```bash
   docker run -v /path/to/project:/project smart-rename --directory /project --search source --replace destination
   ```

## Building a Windows Executable
To create a standalone `.exe` for Windows:
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Run PyInstaller:
   ```bash
   pyinstaller --onefile --name smart-rename smart_rename_pro.py
   ```
3. Find the executable in the `dist/` directory.
4. Run the `.exe`:
   ```bash
   .\dist\smart-rename.exe --directory "C:\my_project" --search source --replace destination
   ```

## Running Tests
Unit tests are located in the `tests/` directory. To run tests:
```bash
pytest tests/ --cov=smart_rename_pro --cov-report=html
```
This generates a coverage report in `htmlcov/`.

## CI/CD Pipeline
The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:
- Runs unit tests across Python 3.7, 3.8, and 3.9.
- Performs linting with `flake8`.
- Generates code coverage reports with `pytest-cov`.
- Builds and releases the `.exe` for tagged commits.

To view CI/CD results:
1. Push changes to the repository.
2. Check the "Actions" tab on GitHub (`https://github.com/memarzade-dev/smart-rename/actions`).

## Important Notes
- **Backup**: Always back up your project before running the script, as it modifies files and directories directly.
- **Log File**: Check `rename.log` for a detailed record of changes and errors.
- **Windows Compatibility**: Fully compatible with Windows paths; also works on Linux/Mac with appropriate path formats.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-feature`).
3. Commit changes (`git commit -m "Add my feature"`).
4. Run tests (`pytest tests/`).
5. Run linting (`flake8 .`).
6. Push to the branch (`git push origin feature/my-feature`).
7. Open a Pull Request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For issues or suggestions, open an issue on GitHub or contact the maintainer at [memarzade-dev](https://github.com/memarzade-dev).
