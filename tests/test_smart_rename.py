import os
import pytest
from pathlib import Path
from smart_rename_pro import (
    TextProcessor,
    FileHandler,
    DirectoryProcessor,
    SmartRenameError,
    ReplaceConfig,
)


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def text_processor():
    """Create a TextProcessor instance for testing."""
    return TextProcessor("source", "destination")


def test_get_case_pattern(text_processor):
    """Test case pattern detection."""
    assert text_processor.get_case_pattern("source") == "lower"
    assert text_processor.get_case_pattern("Source") == "title"
    assert text_processor.get_case_pattern("SOURCE") == "upper"
    assert text_processor.get_case_pattern("source_payment") == "snake"
    assert text_processor.get_case_pattern("sourcePayment") == "camel"


def test_apply_case_structure(text_processor):
    """Test case structure application."""
    assert text_processor.apply_case_structure("lower", "destination") == "destination"
    assert text_processor.apply_case_structure("title", "destination") == "Destination"
    assert text_processor.apply_case_structure("upper", "destination") == "DESTINATION"
    assert text_processor.apply_case_structure("snake", "destination") == "destination"
    assert text_processor.apply_case_structure("camel", "destination") == "destination"


def test_validate_term(text_processor):
    """Test term validation."""
    with pytest.raises(SmartRenameError):
        text_processor.validate_term("source/")
    with pytest.raises(SmartRenameError):
        text_processor.validate_term("")
    with pytest.raises(SmartRenameError):
        text_processor.validate_term("source\\")


def test_process_path_name(text_processor):
    """Test path name processing."""
    result = text_processor.process_path_name("source_payment.py")
    assert result == "destination_payment.py"


def test_process_path_name_dry_run(text_processor):
    """Test path name processing in dry run mode."""
    result = text_processor.process_path_name("source_payment.py", dry_run=True)
    assert result == "source_payment.py"


def test_process_path_name_special_chars(text_processor):
    """Test path name processing with special characters."""
    result = text_processor.process_path_name("source-payment.py")
    assert result == "destination-payment.py"


def test_process_file_content(text_processor, temp_dir):
    """Test file content processing."""
    test_file = temp_dir / "test.py"
    test_file.write_text("source = 1\nsource_payment = 2")
    text_processor.process_file_content(test_file)
    assert test_file.read_text() == "destination = 1\ndestination_payment = 2"


def test_process_file_content_dry_run(text_processor, temp_dir):
    """Test file content processing in dry run mode."""
    test_file = temp_dir / "test.py"
    content = "source = 1\nsource_payment = 2"
    test_file.write_text(content)
    text_processor.process_file_content(test_file, dry_run=True)
    assert test_file.read_text() == content


def test_process_directory(text_processor, temp_dir):
    """Test directory processing."""
    (temp_dir / "source_dir").mkdir()
    (temp_dir / "source_dir" / "test.py").write_text("source = 1")
    text_processor.process_directory(temp_dir)
    assert (temp_dir / "destination_dir").exists()
    assert (temp_dir / "destination_dir" / "test.py").read_text() == "destination = 1"


def test_process_directory_non_ascii(text_processor, temp_dir):
    """Test directory processing with non-ASCII content."""
    (temp_dir / "source_dir").mkdir()
    (temp_dir / "source_dir" / "test.py").write_text("source = 'هدف'")
    text_processor.process_directory(temp_dir)
    assert (temp_dir / "destination_dir").exists()
    assert (temp_dir / "destination_dir" / "test.py").read_text() == "destination = 'هدف'"


def test_load_config_file(temp_dir):
    """Test configuration file loading."""
    config_file = temp_dir / ".smart-rename.yaml"
    config_file.write_text("""
    search_term: source
    replace_term: destination
    exclude_extensions:
      - .log
      - .bak
    """)
    config = ReplaceConfig.load_from_file(config_file)
    assert config.search_term == "source"
    assert config.replace_term == "destination"
    assert ".log" in config.exclude_extensions


def test_ignore_gitignore_files(text_processor, temp_dir):
    """Test gitignore pattern handling."""
    (temp_dir / ".gitignore").write_text("*.log\n.git/\n")
    (temp_dir / "test.log").write_text("source = 1")
    text_processor.process_directory(temp_dir)
    assert (temp_dir / "test.log").read_text() == "source = 1"


def test_invalid_directory(text_processor):
    """Test handling of invalid directory."""
    with pytest.raises(SmartRenameError):
        text_processor.process_directory(Path("/nonexistent/path")) 