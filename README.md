Smart-Rename: Enterprise Edition


















  A robust, cross-platform Python script for intelligently renaming files, directories, and updating content in large codebases. Perfect for enterprise-grade refactoring in projects like Laravel, WordPress, or Django, with case-sensitive replacements, non-ASCII support (e.g., Persian), and gitignore-aware processing.



  📖 Documentation •
  🐙 GitHub •
  💖 Sponsor •
  💬 Discussions



Why Smart-Rename? Refactor a 50,000-file codebase in minutes, update Persian configs flawlessly, or automate enterprise migrations with confidence—all while respecting .gitignore and ensuring Unicode compatibility. 🚀

Table of Contents

Overview
Features
Core Features
Advanced Features
Enterprise Features


Installation
Prerequisites
From PyPI
From Source
System-Specific Setup


Usage
CLI Reference
Shell Completions


Configuration
Basic YAML Config
Advanced Config Options


Examples
Laravel Refactor
Persian Text Rename
WordPress Theme Update
Regex-Based Rename
Enterprise Migration


Docker Setup
Windows Executable
Testing
Running Tests
Test Suite Structure


CI/CD Pipeline
Troubleshooting
Common Issues
FAQ


Best Practices
Contributing
Development Setup
Code Style
Pull Request Process


Support & Sponsorship
Donate
Sponsor Tiers
Enterprise Support


Roadmap
Changelog
License
Contact

Overview
Smart-Rename: Enterprise Edition (v2.1.0) is a powerful Python script designed for intelligent file and content renaming in large-scale projects. Tailored for enterprise workflows, it excels at refactoring codebases (e.g., Laravel, WordPress, Django) with features like case-sensitive replacements, path reference updates, non-ASCII support (e.g., Persian), and gitignore-aware processing. With parallel processing, YAML configuration, and enterprise-grade support via Tidelift, Smart-Rename ensures reliability, speed, and compliance.

Use Case: Refactor a Laravel project’s Order model to Shipment across 10,000 files, update Persian configs from زرین‌پال to هدف, or automate content migrations with zero downtime—all in a single command.

Features
Core Features

🗂️ Smart Renaming: Rename files and directories with case-preservation (e.g., Source → Destination, زرین‌پال → هدف).
📝 Content Replacement: Update text in 50+ file types (.php, .js, .py, .txt, .md).
🚫 Ignore Patterns: Respect .gitignore patterns, skipping logs, .git/, or build artifacts.
🔍 Dry-Run Mode: Preview changes without modifying files.
🌐 Cross-Platform: Seamless operation on Windows, Linux, and macOS via pathlib.

Advanced Features

🔗 Path Reference Updates: Adjust imports and references (e.g., use App\Source; → use App\Destination;).
⚙️ YAML Configuration: Customize with .smart-rename.yaml for include/exclude rules, regex, and multi-rule setups.
⚡️ Parallel Processing: Multithreading (1–16 workers) for large-scale operations.
🔠 Encoding Handling: Detect encodings with chardet for robust Unicode support.
🧪 Unit Tests: 95%+ coverage for case-sensitivity, non-ASCII, and edge cases.

Enterprise Features

🛡️ Error Handling: Detailed logging (rename.log) and custom exceptions.
✅ Validation: Prevent invalid characters in search/replace terms.
🐳 Docker Support: Containerized execution for consistent environments.
💿 Executable Build: Standalone .exe for Windows users.
🔄 CI/CD: Automated testing, linting, coverage, and releases via GitHub Actions.
📊 Compliance: ISO27001, SOC2, GDPR via Tidelift.

Workflow Diagram:
graph TD
    A[Start] --> B[Parse CLI Args]
    B --> C[Load .smart-rename.yaml]
    C --> D[Scan Directory]
    D --> E{Apply .gitignore}
    E --> F[Detect Encodings]
    F --> G[Parallel Processing]
    G --> H[Rename Files/Dirs]
    G --> I[Update Content]
    H --> J[Log Changes]
    I --> J
    J --> K[Dry-Run Preview]
    K --> L[Apply Changes]
    L --> M[Generate Report]

Installation
Prerequisites

Python: 3.8–3.13
pip: Latest version
Git: For source installation
Optional: Docker, PyInstaller (for advanced setups)

From PyPI
pip install smart-rename
python -m smart_rename_pro --version

From Source

Clone the repository:
git clone https://github.com/oxychain-dev/smart-rename.git
cd smart-rename


Install dependencies:
pip install -r requirements.txt

Dependencies:

chardet>=5.2.0,<6.0 (encoding detection)
pyyaml>=6.0.2,<7.0 (YAML parsing)
pathspec>=0.12.1,<0.13 (gitignore patterns)


Verify:
python smart_rename_pro.py --version



System-Specific Setup

Windows:# Install Python
winget install Python.Python.3.10
# Verify
python --version


Linux:sudo apt-get update
sudo apt-get install python3.10 python3-pip


macOS:brew install python@3.10


Homebrew (Experimental):brew tap oxychain-dev/smart-rename
brew install smart-rename



Usage
Run the script:
python smart_rename_pro.py --directory /path/to/project --search "source" --replace "destination"

CLI Reference



Argument
Description
Default
Required



--directory
Project directory path
N/A
Yes


--search
Term to search for
None
No*


--replace
Term to replace with
None
No*


--workers
Parallel workers (1–16)
4
No


--config
Path to YAML config file
None
No


--dry-run
Preview changes without applying
False
No


--encoding
Force specific encoding (e.g., utf-8)
Auto
No


--verbose
Enable detailed logging
False
No



Note: --search and --replace are optional if defined in .smart-rename.yaml.

Help Command:
python smart_rename_pro.py --help

Shell Completions
Enable tab completion for Bash/Zsh:
# Bash
echo 'eval "$(register-python-argcomplete smart_rename_pro.py)"' >> ~/.bashrc
# Zsh
echo 'eval "$(register-python-argcomplete smart_rename_pro.py)"' >> ~/.zshrc

Configuration
Create .smart-rename.yaml in your project root:
search_term: source
replace_term: destination
exclude_extensions:
  - .log
  - .tmp
  - .bak
include_extensions:
  - .php
  - .js
  - .env
exclude_dirs:
  - dist
  - build
case_sensitive: true
regex_enabled: false
workers: 4

Run with config:
python smart_rename_pro.py --directory /path/to/project --config .smart-rename.yaml

Advanced Config Options

Regex Support

Use regex for complex patterns:
search_term: "[Ss]ource_([0-9]+)"
replace_term: "Destination_$1"
regex_enabled: true

Example: Renames source_123.php to Destination_123.php.



Multiple Rename Rules

Apply multiple rules:
rules:
  - search_term: source
    replace_term: destination
    include_extensions: [".php", ".js"]
  - search_term: OldApi
    replace_term: NewApi
    include_extensions: [".py"]
  - search_term: "زرین‌پال"
    replace_term: "هدف"
    include_extensions: [".json"]




Custom Logging

Configure logging:
logging:
  file: custom_rename.log
  level: debug
  max_size_mb: 10
  backup_count: 5



Examples
Laravel Refactor
Rename Order to Shipment:
python smart_rename_pro.py --directory ./my-laravel-app --search "Order" --replace "Shipment" --workers 8


Renames: app/Models/Order.php → app/Models/Shipment.php
Updates: use App\Models\Order; → use App\Models\Shipment;
Modifies: Order::find($id) → Shipment::find($id)

Persian Text Rename
Update Persian configs:
python smart_rename_pro.py --directory ./my-project --search "زرین‌پال" --replace "هدف"


Renames: configs/زرین‌پال.json → configs/هدف.json
Updates: "gateway": "زرین‌پال" → "gateway": "هدف"

WordPress Theme Update
Rename theme components:
python smart_rename_pro.py --directory ./wp-content/themes/my-theme --search "Header" --replace "TopBar" --dry-run


Previews: header.php → topbar.php, get_header() → get_topbar()

Regex-Based Rename
Standardize file names:
search_term: "file_([0-9]+)_v[0-9]+"
replace_term: "document_$1"
regex_enabled: true

python smart_rename_pro.py --directory ./docs --config regex.yaml


Renames: file_123_v2.txt → document_123.txt

Enterprise Migration
Migrate a 50,000-file codebase:
python smart_rename_pro.py --directory ./enterprise-app --search "Legacy" --replace "Modern" --workers 16 --verbose


Logs detailed operations to rename.log.

Docker Setup
Run in a container for consistency.

Build:docker build -t smart-rename .


Run:docker run -v $(pwd)/project:/source smart-rename --directory /source --search "source" --replace "destination"


Persian Example:docker run -v $(pwd)/project:/source smart-rename --directory /source --search "زرین‌پال" --replace "هدف"



Dockerfile:
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python", "smart_rename_pro.py"]

Windows Executable
Create a standalone .exe.

Install PyInstaller:pip install pyinstaller


Build:pyinstaller --onefile --name smart-rename --icon=icon.ico smart_rename_pro.py


Run:.\dist\smart-rename.exe --directory "C:\MyProject" --search "source" --replace "destination"



Testing
Smart-Rename’s test suite achieves 95%+ coverage.

Install test dependencies:pip install pytest pytest-cov flake8 yamllint pytest-mock


Run tests:pytest tests/ --cov=smart_rename_pro --cov-report=html


View coverage:open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows



Test Suite Structure

tests/test_rename.py: Core renaming logic
tests/test_non_ascii.py: Persian and Unicode handling
tests/test_ignore.py: .gitignore and exclusion rules
tests/test_parallel.py: Multithreading edge cases
tests/test_config.py: YAML parsing and validation
tests/test_dry_run.py: Dry-run functionality

Mocking: Uses pytest-mock for filesystem operations.
CI/CD Pipeline
The .github/workflows/ci.yml automates:

Matrix Testing: Ubuntu, Windows, macOS; Python 3.8–3.13.
Linting: flake8 and yamllint.
Coverage: Uploads to Codecov.
Releases: Builds .exe, creates GitHub Releases on tags.
Docs: Validates README.md with markdownlint.

Pipeline Diagram:
graph TD
    A[Push/PR] --> B[Setup Matrix]
    B --> C[Run Tests]
    C --> D[Lint: flake8, yamllint]
    C --> E[Coverage: pytest-cov]
    E --> F[Upload to Codecov]
    D --> G[Build .exe]
    G --> H[Create Release]
    H --> I[Publish to PyPI]
    I --> J[Update Docs]

Setup:

Add CODECOV_TOKEN and PYPI_TOKEN to GitHub Secrets.
Tag releases: git tag v2.1.0; git push --tags.

Troubleshooting
Common Issues



Issue
Solution



Encoding Errors
Use --encoding utf-8. Ensure files are UTF-8 compatible.


Permission Denied
Run with sudo (Linux/macOS) or Admin (Windows).


Files Skipped
Verify .gitignore or exclude_extensions in config.


Non-ASCII Issues
Set terminal to UTF-8 (e.g., PowerShell: chcp 65001).


Slow Performance
Increase --workers or split directories.


Config Errors
Validate YAML with yamllint .smart-rename.yaml.


FAQ

Why are files ignored? Smart-Rename respects .gitignore and config exclusions. Check patterns.
Can I undo changes? Use --dry-run first. Restore from backups or git for applied changes.
Does it support regex? Yes, set regex_enabled: true in YAML.
How to debug? Enable --verbose and check rename.log.
Is it safe for production? Yes, with --dry-run and backups.

Logs: rename.log includes timestamps, file sizes, and error details.
Best Practices

🗄️ Backup: Always back up your project.
🔍 Dry-Run: Test with --dry-run to preview changes.
📦 Incremental Processing: Split large projects into smaller directories.
✅ Validate Config: Use yamllint for .smart-rename.yaml.
📜 Monitor Logs: Check rename.log for issues.
🧪 Test Environment: Run in a staging directory first.
🔐 Security: Use Tidelift for enterprise-grade auditing.

Contributing
We ❤️ contributions! Follow these steps:

Fork the repository.
Create a feature branch:git checkout -b feature/my-feature


Commit:git commit -m "Add my-feature"


Test:pytest tests/
flake8 .
yamllint .


Push:git push origin feature/my-feature


Open a Pull Request.

Development Setup
git clone https://github.com/oxychain-dev/smart-rename.git
cd smart-rename
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock flake8 yamllint pre-commit
pre-commit install

Code Style

PEP 8: Enforced by flake8.
Type Hints: Use mypy for static typing.
Docstrings: Google-style for functions and classes.
Commits: Follow Conventional Commits.
Pre-Commit: Auto-lints with pre-commit.

Pull Request Process

Link to a GitHub issue.
Describe changes in the PR description.
Ensure tests pass and coverage remains 95%+.
Update documentation if needed.

PR Template:
## Description
Explain changes and motivation.

## Related Issue
Closes #123

## How to Test
1. Run `pytest tests/`.
2. Execute `python smart_rename_pro.py --directory ./test --search x --replace y`.

## Checklist
- [x] Tests pass
- [x] Linting passes
- [x] Coverage unchanged
- [x] Docs updated

Issue Templates: Use .github/ISSUE_TEMPLATE for bugs and features.
Support & Sponsorship
Smart-Rename is maintained by Ali OxyChain with community support. Your contributions ensure continued development, security, and enterprise features.
Donate
Support via cryptocurrency:

TON Wallet: UQAc2D8n8xERl7oaC509o8mTe4d07JDDU73qvz-eXSlprwjO
TRON Wallet: TXjYKKCudbhuVEpQXBRk2J4CxFoyuzyjsg

Sponsor Tiers
Join our sponsors:

Community ($5/month): Public badge, README mention.GitHub Sponsors
Professional ($25/month): Priority issues, quarterly updates.GitHub Sponsors
One-Time: Any amount via Ko-fi or Buy Me a Coffee.
Collective: Transparent funding via Open Collective.

Enterprise Support
Access premium support, SLAs, and custom integrations via Tidelift. Ensure compliance with ISO27001, SOC2, and GDPR.

Impact: Your support funds new features, security patches, and better docs. Sponsor today! 🌟

Roadmap

v2.2.0 (Q3 2025): GUI interface, regex editor.
v2.3.0 (Q4 2025): Plugin system for custom rules.
v3.0.0 (2026): Cloud integration, API endpoints.
Ongoing: Performance optimizations, expanded test coverage.

Contribute to the roadmap: Discussions.
Changelog
See CHANGELOG.md for version history.
Recent Highlights:

v2.1.0: Added regex support, improved Persian handling.
v2.0.0: Parallel processing, Tidelift integration.

License
MIT License
MIT License

Copyright (c) 2024 Ali OxyChain

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Contact

Issues: GitHub Issues
Discussions: GitHub Discussions
Email: oxychain.dev
Sponsor: Support Us



  Built with ❤️ by Ali OxyChain | Powered by the Community
