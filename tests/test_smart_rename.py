import os
import tempfile
import shutil
from pathlib import Path
import pytest
import yaml
from smart_rename_pro import TextProcessor, FileHandler, ReplaceConfig, DirectoryProcessor, load_config_file, IgnoreFileProcessor

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_get_case_pattern():
    """Test case pattern detection."""
    assert TextProcessor.get_case_pattern("source") == "lower"
    assert TextProcessor.get_case_pattern("SOURCE") == "upper"
    assert TextProcessor.get_case_pattern("Source") == "title"
    assert TextProcessor.get_case_pattern("sOuRcE") == "custom"
    assert TextProcessor.get_case_pattern("پرداخت") == "custom"

def test_apply_case_structure():
    """Test case structure application."""
    assert TextProcessor.apply_case_structure("destination", "lower") == "destination"
    assert TextProcessor.apply_case_structure("destination", "upper") == "DESTINATION"
    assert TextProcessor.apply_case_structure("destination", "title") == "Destination"
    assert TextProcessor.apply_case_structure("destination", "custom", "sOuRcE") == "dEsTiNaTion"
    assert TextProcessor.apply_case_structure("پرداخت", "custom", "sOuRcE") == "پRdAcHت"

def test_is_text_file():
    """Test text file extension detection."""
    config = ReplaceConfig("", "", "")
    assert TextProcessor.is_text_file("test.php", config) is True
    assert TextProcessor.is_text_file("test.txt", config) is True
    assert TextProcessor.is_text_file("test.jpg", config) is False
    config_exclude = ReplaceConfig("", "", "", exclude_extensions=[".php"])
    assert TextProcessor.is_text_file("test.php", config_exclude) is False
    config_include = ReplaceConfig("", "", "", include_extensions=[".txt"])
    assert TextProcessor.is_text_file("test.txt", config_include) is True
    assert TextProcessor.is_text_file("test.php", config_include) is False

def test_process_path_name(temp_dir):
    """Test renaming a file or directory."""
    test_file = os.path.join(temp_dir, "source_config.php")
    with open(test_file, 'w') as f:
        f.write("test")
    
    new_path, renamed = FileHandler.process_path_name(test_file, "source", "destination")
    assert renamed is True
    assert os.path.basename(new_path) == "destination_config.php"
    assert os.path.exists(new_path)

def test_process_path_name_special_chars(temp_dir):
    """Test renaming with special characters."""
    test_dir = os.path.join(temp_dir, "source#payment")
    os.makedirs(test_dir)
    
    new_path, renamed = FileHandler.process_path_name(test_dir, "source", "destination")
    assert renamed is True
    assert os.path.basename(new_path) == "destination#payment"
    assert os.path.exists(new_path)

def test_process_path_name_non_ascii(temp_dir):
    """Test renaming with non-ASCII search term."""
    test_file = os.path.join(temp_dir, "پرداخت_config.php")
    with open(test_file, 'w') as f:
        f.write("test")
    
    new_path, renamed = FileHandler.process_path_name(test_file, "پرداخت", "هدف")
    assert renamed is True
    assert os.path.basename(new_path) == "هدف_config.php"
    assert os.path.exists(new_path)

def test_process_file_content(temp_dir):
    """Test replacing content in a text file."""
    test_file = os.path.join(temp_dir, "test.txt")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("This is a Source payment")
    
    result = FileHandler.process_file_content(test_file, "Source", "Destination")
    assert result is True
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert content == "This is a Destination payment"

def test_process_file_content_non_ascii(temp_dir):
    """Test replacing non-ASCII content."""
    test_file = os.path.join(temp_dir, "test.txt")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("این یک پرداخت است")
    
    result = FileHandler.process_file_content(test_file, "پرداخت", "هدف")
    assert result is True
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert content == "این یک هدف است"

def test_update_path_references(temp_dir):
    """Test updating path references in file content."""
    test_file = os.path.join(temp_dir, "test.php")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("require 'source_payments/config.php';")
    
    result = FileHandler.update_path_references(
        test_file, 
        os.path.join(temp_dir, "source_payments"), 
        os.path.join(temp_dir, "destination_payments")
    )
    assert result is True
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "destination_payments/config.php" in content

def test_process_directory(temp_dir):
    """Test full directory processing."""
    # Create test structure
    os.makedirs(os.path.join(temp_dir, "source_payments/subdir"))
    test_file = os.path.join(temp_dir, "source_payments/subdir", "source_config.php")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("Source payment gateway")
    
    config = ReplaceConfig(
        search_term="source",
        replace_term="destination",
        directory=temp_dir,
        max_workers=1
    )
    
    DirectoryProcessor.process_directory(config)
    
    # Check directory rename
    assert os.path.exists(os.path.join(temp_dir, "destination_payments/subdir"))
    # Check file rename
    assert os.path.exists(os.path.join(temp_dir, "destination_payments/subdir", "destination_config.php"))
    # Check content
    with open(os.path.join(temp_dir, "destination_payments/subdir", "destination_config.php"), 'r', encoding='utf-8') as f:
        content = f.read()
    assert content == "Destination payment gateway"

def test_load_config_file(temp_dir):
    """Test loading configuration from YAML file."""
    config_file = os.path.join(temp_dir, ".smart-rename.yaml")
    config_data = {
        "search_term": "source",
        "replace_term": "destination",
        "exclude_extensions": [".log"],
        "include_extensions": [".php", ".txt"]
    }
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config_data, f)
    
    loaded_config = load_config_file(config_file)
    assert loaded_config == config_data

def test_ignore_gitignore_files(temp_dir):
    """Test ignoring files specified in .gitignore."""
    # Create .gitignore
    gitignore_file = os.path.join(temp_dir, ".gitignore")
    with open(gitignore_file, 'w', encoding='utf-8') as f:
        f.write("*.log\nignored_dir/")
    
    # Create test structure
    os.makedirs(os.path.join(temp_dir, "ignored_dir"))
    test_file = os.path.join(temp_dir, "source_config.php")
    ignored_file = os.path.join(temp_dir, "source.log")
    ignored_dir_file = os.path.join(temp_dir, "ignored_dir", "source_config.php")
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("Source payment")
    with open(ignored_file, 'w', encoding='utf-8') as f:
        f.write("Source payment")
    with open(ignored_dir_file, 'w', encoding='utf-8') as f:
        f.write("Source payment")
    
    config = ReplaceConfig(
        search_term="source",
        replace_term="destination",
        directory=temp_dir,
        max_workers=1
    )
    
    DirectoryProcessor.process_directory(config)
    
    # Check that non-ignored file was processed
    assert os.path.exists(os.path.join(temp_dir, "destination_config.php"))
    with open(os.path.join(temp_dir, "destination_config.php"), 'r', encoding='utf-8') as f:
        content = f.read()
    assert content == "Destination payment"
    
    # Check that ignored files were not processed
    assert os.path.exists(ignored_file)
    assert os.path.exists(ignored_dir_file)
    with open(ignored_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert content == "Source payment"
    with open(ignored_dir_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert content == "Source payment"

def test_utf16_encoding(temp_dir):
    """Test handling of UTF-16 encoded files."""
    test_file = os.path.join(temp_dir, "test.txt")
    with open(test_file, 'w', encoding='utf-16') as f:
        f.write("Source payment")
    
    result = FileHandler.process_file_content(test_file, "Source", "Destination")
    assert result is True
    with open(test_file, 'r', encoding='utf-16') as f:
        content = f.read()
    assert content == "Destination payment"

def test_nested_directory_structure(temp_dir):
    """Test processing deeply nested directory structure."""
    # Create a deep directory structure
    deep_path = os.path.join(temp_dir, "source", "payments", "gateway", "config")
    os.makedirs(deep_path)
    
    # Create files at different levels
    files = [
        os.path.join(temp_dir, "source", "index.php"),
        os.path.join(temp_dir, "source", "payments", "gateway.php"),
        os.path.join(deep_path, "settings.php")
    ]
    
    for file_path in files:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Source configuration")
    
    config = ReplaceConfig(
        search_term="source",
        replace_term="destination",
        directory=temp_dir,
        max_workers=1
    )
    
    DirectoryProcessor.process_directory(config)
    
    # Verify directory structure was renamed
    assert os.path.exists(os.path.join(temp_dir, "destination", "payments", "gateway", "config"))
    
    # Verify files were renamed and content updated
    for old_path, new_path in [
        (os.path.join(temp_dir, "source", "index.php"), 
         os.path.join(temp_dir, "destination", "index.php")),
        (os.path.join(temp_dir, "source", "payments", "gateway.php"),
         os.path.join(temp_dir, "destination", "payments", "gateway.php")),
        (os.path.join(deep_path, "settings.php"),
         os.path.join(temp_dir, "destination", "payments", "gateway", "config", "settings.php"))
    ]:
        assert os.path.exists(new_path)
        with open(new_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == "Destination configuration"

def test_special_characters_in_content(temp_dir):
    """Test handling of special characters in file content."""
    test_file = os.path.join(temp_dir, "test.txt")
    special_content = "source-payment@example.com\nsource_payment\nsource#payment"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(special_content)
    
    result = FileHandler.process_file_content(test_file, "source", "destination")
    assert result is True
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    expected_content = "destination-payment@example.com\ndestination_payment\ndestination#payment"
    assert content == expected_content

def test_case_preservation(temp_dir):
    """Test preservation of case patterns in replacements."""
    test_file = os.path.join(temp_dir, "test.txt")
    case_content = "SOURCE\nSource\nsource\nsOuRcE"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(case_content)
    
    result = FileHandler.process_file_content(test_file, "source", "destination")
    assert result is True
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    expected_content = "DESTINATION\nDestination\ndestination\ndEsTiNaTion"
    assert content == expected_content 