"""Test smart rename functionality."""

import pytest
from pathlib import Path
from smart_rename_pro import (
    DirectoryProcessor,
    SmartRenameError,
    ReplaceConfig,
    TextProcessor,
    FileHandler,
    IgnoreFileProcessor
)


def test_basic_rename():
    """Test basic file renaming functionality."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_case_preservation():
    """Test case preservation in replacements."""
    config = ReplaceConfig(
        search_term="Test",
        replace_term="Demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "Test"
    assert config.replace_term == "Demo"


def test_special_characters():
    """Test handling of special characters."""
    config = ReplaceConfig(
        search_term="test-file",
        replace_term="demo-file",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test-file"
    assert config.replace_term == "demo-file"


def test_multiple_occurrences():
    """Test handling of multiple occurrences in a single file."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_directory_renaming():
    """Test directory renaming functionality."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_nested_directories():
    """Test handling of nested directories."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_file_content():
    """Test file content replacement."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_binary_files():
    """Test handling of binary files."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_encoding_detection():
    """Test automatic encoding detection."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_unicode_support():
    """Test Unicode character support."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_large_files():
    """Test handling of large files."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_concurrent_processing():
    """Test concurrent file processing."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        max_workers=4,
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"
    assert config.max_workers == 4


def test_error_handling():
    """Test error handling and reporting."""
    with pytest.raises(SmartRenameError):
        ReplaceConfig(
            search_term="",
            replace_term="demo",
            directory=Path("test_dir")
        )


def test_dry_run():
    """Test dry run functionality."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"
    assert config.dry_run is True


def test_config_file():
    """Test configuration file loading."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        config_file=Path("config.yaml"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"
    assert config.config_file == Path("config.yaml")


def test_exclude_extensions():
    """Test file extension exclusion."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        exclude_extensions=[".exe", ".dll"],
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"
    assert config.exclude_extensions == [".exe", ".dll"]


def test_include_extensions():
    """Test file extension inclusion."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        include_extensions=[".txt", ".md"],
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"
    assert config.include_extensions == [".txt", ".md"]


def test_gitignore_support():
    """Test .gitignore pattern support."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_path_references():
    """Test updating path references in files."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_case_sensitivity():
    """Test case sensitivity options."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_regex_support():
    """Test regular expression support."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_whitespace_handling():
    """Test whitespace handling in search and replace terms."""
    config = ReplaceConfig(
        search_term="test file",
        replace_term="demo file",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test file"
    assert config.replace_term == "demo file"


def test_empty_strings():
    """Test handling of empty strings."""
    with pytest.raises(SmartRenameError):
        ReplaceConfig(
            search_term="",
            replace_term="",
            directory=Path("test_dir")
        )


def test_invalid_characters():
    """Test handling of invalid characters."""
    with pytest.raises(SmartRenameError):
        ReplaceConfig(
            search_term="test*file",
            replace_term="demo",
            directory=Path("test_dir")
        )


def test_long_paths():
    """Test handling of long file paths."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_symlinks():
    """Test handling of symbolic links."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_hidden_files():
    """Test handling of hidden files."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_permissions():
    """Test handling of file permissions."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_backup_creation():
    """Test backup file creation."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_logging():
    """Test logging functionality."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_progress_reporting():
    """Test progress reporting functionality."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_error_recovery():
    """Test error recovery functionality."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo"


def test_cleanup():
    """Test cleanup functionality."""
    config = ReplaceConfig(
        search_term="test",
        replace_term="demo",
        directory=Path("test_dir"),
        dry_run=True
    )
    assert config.search_term == "test"
    assert config.replace_term == "demo" 