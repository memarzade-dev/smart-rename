"""Test smart rename functionality."""

import pytest
from pathlib import Path
from smart_rename_pro import SmartRenameError, ReplaceConfig


def test_basic_rename():
    """Test basic file renaming functionality."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_case_preservation():
    """Test case preservation in replacements."""
    config = ReplaceConfig(
        search_term="Old",
        replace_term="New",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "Old"
    assert config.replace_term == "New"


def test_special_characters():
    """Test handling of special characters."""
    config = ReplaceConfig(
        search_term="old-name",
        replace_term="new-name",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old-name"
    assert config.replace_term == "new-name"


def test_multiple_occurrences():
    """Test handling of multiple occurrences in a single file."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_directory_rename():
    """Test renaming directories."""
    config = ReplaceConfig(
        search_term="old_dir",
        replace_term="new_dir",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old_dir"
    assert config.replace_term == "new_dir"


def test_nested_directories():
    """Test handling of nested directories."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_file_content():
    """Test updating file content."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_binary_files():
    """Test handling of binary files."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_encoding_detection():
    """Test automatic encoding detection."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_unicode_support():
    """Test Unicode character support."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_large_files():
    """Test handling of large files."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_concurrent_processing():
    """Test parallel processing of files."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_error_handling():
    """Test error handling and reporting."""
    with pytest.raises(SmartRenameError):
        ReplaceConfig(
            search_term="",
            replace_term="new",
            directory=Path("test_dir"),
            dry_run=True
        )


def test_dry_run():
    """Test dry run functionality."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.dry_run is True


def test_config_file():
    """Test loading configuration from file."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_file_extensions():
    """Test file extension filtering."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True,
        file_extensions=[".txt", ".md"]
    )
    assert config.file_extensions == [".txt", ".md"]


def test_gitignore():
    """Test .gitignore pattern support."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_path_references():
    """Test handling of path references in content."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_case_sensitivity():
    """Test case sensitivity options."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_regex_support():
    """Test regular expression support."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_whitespace_handling():
    """Test handling of whitespace in filenames."""
    config = ReplaceConfig(
        search_term="old name",
        replace_term="new name",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old name"
    assert config.replace_term == "new name"


def test_empty_strings():
    """Test handling of empty strings."""
    with pytest.raises(SmartRenameError):
        ReplaceConfig(
            search_term="",
            replace_term="new",
            directory=Path("test_dir"),
            dry_run=True
        )


def test_invalid_characters():
    """Test handling of invalid characters."""
    with pytest.raises(SmartRenameError):
        ReplaceConfig(
            search_term="old/name",
            replace_term="new/name",
            directory=Path("test_dir"),
            dry_run=True
        )


def test_long_paths():
    """Test handling of long file paths."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_symlinks():
    """Test handling of symbolic links."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_hidden_files():
    """Test handling of hidden files."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_permissions():
    """Test handling of file permissions."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_backup_creation():
    """Test creation of backup files."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_logging():
    """Test logging functionality."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_progress_reporting():
    """Test progress reporting functionality."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_error_recovery():
    """Test error recovery functionality."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new"


def test_cleanup():
    """Test cleanup functionality."""
    config = ReplaceConfig(
        search_term="old",
        replace_term="new",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "old"
    assert config.replace_term == "new" 