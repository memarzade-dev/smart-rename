import os
import tempfile
import shutil
from pathlib import Path
import pytest
import yaml
from smart_rename_pro import TextProcessor, FileHandler, ReplaceConfig, DirectoryProcessor, IgnoreFileProcessor, SmartRenameError

@pytest.fixture
def temp_dir():
    """Fixture to create a temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_get_case_pattern():
    """Test case pattern detection."""
    assert TextProcessor.get_case_pattern("source") == "lower"
    assert TextProcessor.get_case_pattern("SOURCE") == "upper"
    assert TextProcessor.get_case_pattern("Source") == "title"
    assert TextProcessor.get_case_pattern("sOuCe") == "custom"
    assert TextProcessor.get_case_pattern("loveYou") == "lower"

def test_apply_case_structure():
    """Test applying case structure to replacement text."""
    assert TextProcessor.apply_case_structure("destination", "lower") == "destination"
    assert TextProcessor.apply_case_structure("destination", "upper") == "DESTINATION"
    assert TextProcessor.apply_case_structure("destination", "title") == "Destination"
    assert TextProcessor.apply_case_structure("destination", "custom", "sOuCe") == "dEsTiNaT"
    assert TextProcessor.apply_case_structure("هدف", "custom", "destination") == "هدف"

def test_is_text_file():
    """Test text file extension detection."""
    config = ReplaceConfig("", "", Path.cwd())
    assert TextProcessor.is_text_file(Path("test.php"), config) is True
    assert TextProcessor.is_text_file(Path("test.txt"), config) is True
    assert TextProcessor.is_text_file(Path("test.jpg"), config) is False
    config_exclude = ReplaceConfig("", "", Path.cwd(), exclude_extensions=[".php"])
    assert TextProcessor.is_text_file(Path("test.php"), config_exclude) is False
    config_include = ReplaceConfig("", "", Path.cwd(), include_extensions=[".txt"])
    assert TextProcessor.is_text_file(Path("test.txt"), config_include) is True
    assert TextProcessor.is_text_file(Path("test.php"), config_include) is False

def test_validate_term():
    """Test validation of search/replace terms."""
    TextProcessor.validate_term("source", "search")
    TextProcessor.validate_term("destination", "replace")
    TextProcessor.validate_term("loveYou", "search")
    TextProcessor.validate_term("هدف", "replace")
    with pytest.raises(SmartRenameError, match=r"Invalid search term.*contains prohibited characters"):
        TextProcessor.validate_term("source:/", "search")
    with pytest.raises(SmartRenameError, match=r"Invalid replace term.*empty"):
        TextProcessor.validate_term(" ", "replace")

def test_process_path_name(temp_dir):
    """Test renaming a file or directory."""
    test_file = temp_dir / "source_config.php"
    test_file.write_text("test", encoding='utf-8')
    
    new_path, renamed = FileHandler.process_path_name(test_file, "source", "destination", dry_run=False)
    assert renamed is True
    assert new_path.name == "destination_config.php"
    assert new_path.exists()

def test_process_path_name_dry_run(temp_dir):
    """Test dry-run mode for path renaming."""
    test_file = temp_dir / "source_config.php"
    test_file.write_text("test", encoding='utf-8')
    
    new_path, renamed = FileHandler.process_path_name(test_file, "source", "destination", dry_run=True)
    assert renamed is True
    assert new_path.name == "destination_config.php"
    assert not new_path.exists()
    assert test_file.exists()

def test_process_path_name_special_chars(temp_dir):
    """Test renaming with special characters."""
    test_dir = temp_dir / "source#payment"
    test_dir.mkdir()
    
    new_path, renamed = FileHandler.process_path_name(test_dir, "source", "destination", dry_run=False)
    assert renamed is True
    assert new_path.name == "destination#payment"
    assert new_path.exists()

def test_process_path_name_non_ascii(temp_dir):
    """Test renaming with non-ASCII characters."""
    test_file = temp_dir / "loveYou_config.txt"
    test_file.write_text("test", encoding='utf-8')
    
    new_path, renamed = FileHandler.process_path_name(test_file, "loveYou", "هدف", dry_run=False)
    assert renamed is True
    assert new_path.name == "هدف_config.txt"
    assert new_path.exists()

def test_process_file_content(temp_dir):
    """Test replacing content in a text file."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("This is a Source payment", encoding='utf-8')
    
    result = FileHandler.process_file_content(test_file, "source", "destination", dry_run=False)
    assert result is True
    assert test_file.read_text(encoding='utf-8') == "This is a Destination payment"

def test_process_file_content_dry_run(temp_dir):
    """Test dry-run mode for content replacement."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("This is a Source payment", encoding='utf-8')
    
    result = FileHandler.process_file_content(test_file, "source", "destination", dry_run=True)
    assert result is True
    assert test_file.read_text(encoding='utf-8') == "This is a Source payment"

def test_process_file_content_non_ascii(temp_dir):
    """Test replacing non-ASCII content."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("پایا چیستا اینچا، loveYou اینجا", encoding='utf-8')
    
    result = FileHandler.process_file_content(test_file, "loveYou", "هدف", dry_run=False)
    assert result is True
    assert test_file.read_text(encoding='utf-8') == "پایا چیستا اینچا، هدف اینجا"

def test_update_path_references(temp_dir):
    """Test updating path references in file content."""
    test_file = temp_dir / "test.php"
    test_file.write_text("require 'source_payments/config.php';", encoding='utf-8')
    
    result = FileHandler.update_path_references(
        test_file, 
        temp_dir / "source_payments", 
        temp_dir / "destination_payments", 
        dry_run=False
    )
    assert result is True
    assert "destination_payments/config.php" in test_file.read_text(encoding='utf-8')

def test_process_directory(temp_dir):
    """Test processing full directory processing."""
    (temp_dir / "source_payments/subdir").mkdir(parents=True)
    test_file = temp_dir / "source_payments/subdir/source_config.txt"
    test_file.write_text("Source payment gateway", encoding='utf-8')
    
    config = ReplaceConfig(
        search_term="source",
        replace_term="destination",
        directory=temp_dir,
        max_workers=2
    )
    
    DirectoryProcessor.process_directory(config)
    
    assert (temp_dir / "destination_payments").exists()
    assert (temp_dir / "destination_payments/subdir").exists()
    assert (temp_dir / "destination_payments/subdir/source_config.txt").exists()
    assert (temp_dir / "destination_payments/subdir/destination_config.txt").read_text(encoding='utf-8') == "Destination payment gateway"

def test_process_directory_non_ascii(temp_dir):
    """Test directory processing with non-ASCII terms."""
    (temp_dir / "loveYou").mkdir(parents=True)
    test_file = temp_dir / "loveYou/subdir/زرین.txt"
    test_file.write_text("loveYou gateway", encoding='utf-8')
    
    config = ReplaceConfig(
        search_term="loveYou",
        replace_term="هدف",
        directory=temp_dir,
        max_workers=2
    )
    
    DirectoryProcessor.process_directory(config)
    
    assert (temp_dir / "هدف").exists()
    assert (temp_dir / "هدف/subdir").exists()
    assert (temp_dir / "هدف/subdir/هدف.txt").exists()
    assert (temp_dir / "هدف/subdir/هدف.txt").read_text(encoding='utf-8') == "هدف gateway"

def test_load_config_file(temp_dir):
    """Test loading configuration from YAML file."""
    config_file = temp_dir / "config.yaml"
    config_data = {
        "search_term": "source",
        "replace_term": "destination",
        "exclude_extensions": [".log"],
        "include_extensions": [".php", ".js"]
    }
    config_file.write_text(yaml.dump(config_data), encoding='utf-8')
    
    loaded_config = load_config_file(config_file)
    assert loaded_config == config_data

def test_ignore_gitignore_files(temp_dir):
    """Test ignoring files specified in .gitignore."""
    gitignore_file = temp_dir / ".gitignore"
    gitignore_file.write_text("*.log\nignored_dir/", encoding='utf-8')
    
    (temp_dir / "ignored_dir").mkdir()
    test_file = temp_dir / "source_config.txt"
    ignored_file = temp_dir / "source.log"
    ignored_dir_file = temp_dir / "ignored_dir/source_config.txt"
    
    test_file.write_text("Source payment", encoding='utf-8')
    ignored_file.write_text("Source payment", encoding='utf-8')
    ignored_dir_file.write_text("Source payment", encoding='utf-8')
    
    config = ReplaceConfig(
        search_term="source",
        replace_term="destination",
        directory=temp_dir,
        max_workers=2
    )
    
    DirectoryProcessor.process_directory(config)
    
    assert (temp_dir / "destination_config.txt").exists()
    assert (temp_dir / "destination_config.txt").read_text(encoding='utf-8') == "Destination payment"
    assert ignored_file.exists()
    assert ignored_dir_file.exists()
    assert ignored_file.read_text(encoding='utf-8') == "Source payment"
    assert ignored_dir_file.read_text(encoding='utf-8') == "Source payment"

def test_invalid_directory(temp_dir):
    """Test handling of invalid directory."""
    config = ReplaceConfig(
        search_term="invalid",
        replace_term="invalid_term",
        directory=Path("/nonexistent/destination"),
        max_workers=1
    )
    with pytest.raises(SmartRenameError, match=r"Directory.*does not exist"):
        DirectoryProcessor.process_directory(config) 