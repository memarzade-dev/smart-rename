import os
import pytest
from pathlib import Path
from smart_rename_pro import (
    ReplaceConfig,
    TextProcessor,
    IgnoreFileProcessor,
    FileHandler,
    DirectoryProcessor,
    SmartRenameError
)


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def config(temp_dir):
    """Create a test configuration."""
    return ReplaceConfig(
        search_term="source",
        replace_term="destination",
        directory=temp_dir
    )


def test_get_case_pattern():
    """Test case pattern generation."""
    processor = TextProcessor()
    pattern = processor.get_case_pattern("source")
    assert pattern == "[sS][oO][uU][rR][cC][eE]"


def test_apply_case_structure():
    """Test case structure application."""
    processor = TextProcessor()
    result = processor.apply_case_structure("destination", "Source")
    assert result == "Destination"


def test_process_path_name(temp_dir, config):
    """Test path name processing."""
    handler = FileHandler(config)
    test_file = temp_dir / "source_file.txt"
    test_file.touch()
    
    new_path = handler.process_path_name(test_file)
    assert new_path.name == "destination_file.txt"


def test_process_file_content(temp_dir, config):
    """Test file content processing."""
    handler = FileHandler(config)
    test_file = temp_dir / "test.txt"
    test_file.write_text("This is a source file")
    
    handler.process_file_content(test_file)
    assert test_file.read_text() == "This is a destination file"


def test_update_path_references(temp_dir, config):
    """Test path reference updates."""
    handler = FileHandler(config)
    test_file = temp_dir / "test.txt"
    test_file.write_text(f"Path: {temp_dir / 'source_file.txt'}")
    
    handler.update_path_references(test_file)
    expected_path = str(temp_dir / "destination_file.txt").replace("\\", "/")
    assert expected_path in test_file.read_text()


def test_ignore_gitignore_files(temp_dir, config):
    """Test .gitignore file handling."""
    # Create .gitignore file
    gitignore = temp_dir / ".gitignore"
    gitignore.write_text("*.log\nignored_dir/")
    
    # Create test files
    (temp_dir / "test.log").touch()
    (temp_dir / "ignored_dir").mkdir()
    (temp_dir / "ignored_dir" / "test.txt").touch()
    (temp_dir / "normal.txt").touch()
    
    processor = DirectoryProcessor(config)
    processor.process_directory()
    
    # Check that ignored files were not processed
    assert (temp_dir / "test.log").exists()
    assert (temp_dir / "ignored_dir" / "test.txt").exists()
    assert not (temp_dir / "normal.txt").exists()


def test_process_directory(temp_dir, config):
    """Test directory processing."""
    # Create test files
    (temp_dir / "source1.txt").touch()
    (temp_dir / "source2.txt").touch()
    (temp_dir / "subdir").mkdir()
    (temp_dir / "subdir" / "source3.txt").touch()
    
    processor = DirectoryProcessor(config)
    processor.process_directory()
    
    # Check that files were renamed
    assert not (temp_dir / "source1.txt").exists()
    assert not (temp_dir / "source2.txt").exists()
    assert not (temp_dir / "subdir" / "source3.txt").exists()
    assert (temp_dir / "destination1.txt").exists()
    assert (temp_dir / "destination2.txt").exists()
    assert (temp_dir / "subdir" / "destination3.txt").exists()


def test_dry_run(temp_dir, config):
    """Test dry run mode."""
    config.dry_run = True
    test_file = temp_dir / "source.txt"
    test_file.touch()
    
    processor = DirectoryProcessor(config)
    processor.process_directory()
    
    # Check that files were not actually renamed
    assert (temp_dir / "source.txt").exists()
    assert not (temp_dir / "destination.txt").exists()


def test_error_handling(temp_dir, config):
    """Test error handling."""
    # Create a file that can't be accessed
    test_file = temp_dir / "source.txt"
    test_file.touch()
    
    # Set read-only permissions
    if os.name == 'nt':  # Windows
        os.chmod(test_file, 0o444)
    else:  # Unix-like
        os.chmod(test_file, 0o000)
    
    processor = DirectoryProcessor(config)
    with pytest.raises(SmartRenameError):
        processor.process_directory()
    
    # Restore permissions
    if os.name == 'nt':  # Windows
        os.chmod(test_file, 0o666)
    else:  # Unix-like
        os.chmod(test_file, 0o644)


def test_case_insensitive_rename(temp_dir, config):
    """Test renaming on case-insensitive filesystems."""
    # Create test files with case differences
    (temp_dir / "Source.txt").touch()
    (temp_dir / "source.txt").touch()
    
    processor = DirectoryProcessor(config)
    processor.process_directory()
    
    # Check that files were renamed correctly
    assert not (temp_dir / "Source.txt").exists()
    assert not (temp_dir / "source.txt").exists()
    assert (temp_dir / "Destination.txt").exists()


def test_path_separators(temp_dir, config):
    """Test handling of different path separators."""
    handler = FileHandler(config)
    test_file = temp_dir / "test.txt"
    
    # Test with mixed path separators
    content = f"Path: {temp_dir}\\subdir/source.txt"
    test_file.write_text(content)
    
    handler.update_path_references(test_file)
    expected_path = str(temp_dir / "subdir" / "destination.txt").replace("\\", "/")
    assert expected_path in test_file.read_text() 