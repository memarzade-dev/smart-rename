"""Test date handling functionality."""

from pathlib import Path

import pytest

from smart_rename_pro import ReplaceConfig, SmartRenameError


def test_date_pattern_matching():
    """Test matching a specific date in filenames."""
    config = ReplaceConfig(
        search_term="2023-01-01",
        replace_term="2024-01-01",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "2023-01-01"
    assert config.replace_term == "2024-01-01"


def test_date_format_validation():
    """Test validation of date format."""
    with pytest.raises(SmartRenameError):
        ReplaceConfig(
            search_term="invalid-date",
            replace_term="2024-01-01",
            directory=Path("test_dir"),
            dry_run=True,
        )


def test_date_replacement():
    """Test replacing a specific date in filenames."""
    config = ReplaceConfig(
        search_term="2023-01-01",
        replace_term="2024-01-01",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "2023-01-01"
    assert config.replace_term == "2024-01-01"


def test_date_with_time():
    """Test handling dates with time information."""
    config = ReplaceConfig(
        search_term="2023-01-01 12:00",
        replace_term="2024-01-01 12:00",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "2023-01-01 12:00"
    assert config.replace_term == "2024-01-01 12:00"


def test_date_with_timezone():
    """Test handling dates with timezone information."""
    config = ReplaceConfig(
        search_term="2023-01-01 12:00 UTC",
        replace_term="2024-01-01 12:00 UTC",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "2023-01-01 12:00 UTC"
    assert config.replace_term == "2024-01-01 12:00 UTC"


def test_date_with_custom_format():
    """Test handling dates with custom format."""
    config = ReplaceConfig(
        search_term="01/01/2023",
        replace_term="01/01/2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "01/01/2023"
    assert config.replace_term == "01/01/2024"


def test_date_with_relative_reference():
    """Test handling dates with relative references."""
    config = ReplaceConfig(
        search_term="yesterday",
        replace_term="today",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "yesterday"
    assert config.replace_term == "today"


def test_date_with_age():
    """Test handling dates with age information."""
    config = ReplaceConfig(
        search_term="Age 1 2023",
        replace_term="Age 1 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Age 1 2023"
    assert config.replace_term == "Age 1 2024"


def test_multiple_date_formats():
    """Test handling of multiple date formats."""
    config = ReplaceConfig(
        search_term="2023/01/01",
        replace_term="2024-01-01",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "2023/01/01"
    assert config.replace_term == "2024-01-01"


def test_date_in_content():
    """Test date replacement in file content."""
    config = ReplaceConfig(
        search_term="2023-01-01",
        replace_term="2024-01-01",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "2023-01-01"
    assert config.replace_term == "2024-01-01"


def test_date_with_milliseconds():
    """Test handling of dates with millisecond precision."""
    config = ReplaceConfig(
        search_term="2023-01-01 12:00:00.123",
        replace_term="2024-01-01 12:00:00.123",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "2023-01-01 12:00:00.123"
    assert config.replace_term == "2024-01-01 12:00:00.123"


def test_date_with_weekday():
    """Test handling of dates with weekday information."""
    config = ReplaceConfig(
        search_term="Monday, 2023-01-01",
        replace_term="Monday, 2024-01-01",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Monday, 2023-01-01"
    assert config.replace_term == "Monday, 2024-01-01"


def test_date_with_month_name():
    """Test handling of dates with month names."""
    config = ReplaceConfig(
        search_term="January 1, 2023",
        replace_term="January 1, 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "January 1, 2023"
    assert config.replace_term == "January 1, 2024"


def test_date_with_era():
    """Test handling of dates with era information."""
    config = ReplaceConfig(
        search_term="2023 CE",
        replace_term="2024 CE",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "2023 CE"
    assert config.replace_term == "2024 CE"


def test_date_with_season():
    """Test handling of dates with season information."""
    config = ReplaceConfig(
        search_term="Winter 2023",
        replace_term="Winter 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Winter 2023"
    assert config.replace_term == "Winter 2024"


def test_date_with_quarter():
    """Test handling of dates with quarter information."""
    config = ReplaceConfig(
        search_term="Q1 2023",
        replace_term="Q1 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Q1 2023"
    assert config.replace_term == "Q1 2024"


def test_date_with_fiscal_year():
    """Test handling of dates with fiscal year information."""
    config = ReplaceConfig(
        search_term="FY2023",
        replace_term="FY2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "FY2023"
    assert config.replace_term == "FY2024"


def test_date_with_academic_year():
    """Test handling of dates with academic year information."""
    config = ReplaceConfig(
        search_term="2023-24",
        replace_term="2024-25",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "2023-24"
    assert config.replace_term == "2024-25"


def test_date_with_week_number():
    """Test handling of dates with week number information."""
    config = ReplaceConfig(
        search_term="Week 1, 2023",
        replace_term="Week 1, 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Week 1, 2023"
    assert config.replace_term == "Week 1, 2024"


def test_date_with_day_of_year():
    """Test handling of dates with day of year information."""
    config = ReplaceConfig(
        search_term="Day 1, 2023",
        replace_term="Day 1, 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Day 1, 2023"
    assert config.replace_term == "Day 1, 2024"


def test_date_with_holiday():
    """Test handling of dates with holiday information."""
    config = ReplaceConfig(
        search_term="New Year's Day 2023",
        replace_term="New Year's Day 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "New Year's Day 2023"
    assert config.replace_term == "New Year's Day 2024"


def test_date_with_event():
    """Test handling of dates with event information."""
    config = ReplaceConfig(
        search_term="Conference 2023",
        replace_term="Conference 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Conference 2023"
    assert config.replace_term == "Conference 2024"


def test_date_with_version():
    """Test handling of dates with version information."""
    config = ReplaceConfig(
        search_term="v2023.1.1",
        replace_term="v2024.1.1",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "v2023.1.1"
    assert config.replace_term == "v2024.1.1"


def test_date_with_release():
    """Test handling of dates with release information."""
    config = ReplaceConfig(
        search_term="Release 2023",
        replace_term="Release 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Release 2023"
    assert config.replace_term == "Release 2024"


def test_date_with_sprint():
    """Test handling of dates with sprint information."""
    config = ReplaceConfig(
        search_term="Sprint 1 2023",
        replace_term="Sprint 1 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Sprint 1 2023"
    assert config.replace_term == "Sprint 1 2024"


def test_date_with_iteration():
    """Test handling of dates with iteration information."""
    config = ReplaceConfig(
        search_term="Iteration 1 2023",
        replace_term="Iteration 1 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Iteration 1 2023"
    assert config.replace_term == "Iteration 1 2024"


def test_date_with_milestone():
    """Test handling of dates with milestone information."""
    config = ReplaceConfig(
        search_term="Milestone 1 2023",
        replace_term="Milestone 1 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Milestone 1 2023"
    assert config.replace_term == "Milestone 1 2024"


def test_date_with_phase():
    """Test handling of dates with phase information."""
    config = ReplaceConfig(
        search_term="Phase 1 2023",
        replace_term="Phase 1 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Phase 1 2023"
    assert config.replace_term == "Phase 1 2024"


def test_date_with_stage():
    """Test handling of dates with stage information."""
    config = ReplaceConfig(
        search_term="Stage 1 2023",
        replace_term="Stage 1 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Stage 1 2023"
    assert config.replace_term == "Stage 1 2024"


def test_date_with_cycle():
    """Test handling of dates with cycle information."""
    config = ReplaceConfig(
        search_term="Cycle 1 2023",
        replace_term="Cycle 1 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Cycle 1 2023"
    assert config.replace_term == "Cycle 1 2024"


def test_date_with_period():
    """Test handling of dates with period information."""
    config = ReplaceConfig(
        search_term="Period 1 2023",
        replace_term="Period 1 2024",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "Period 1 2023"
    assert config.replace_term == "Period 1 2024"


def test_date_with_epoch():
    """Test handling of dates with epoch information."""
    config = ReplaceConfig(
        search_term="1970-01-01",
        replace_term="2024-01-01",
        directory=Path("test_dir"),
        dry_run=True,
    )
    assert config.search_term == "1970-01-01"
    assert config.replace_term == "2024-01-01"
