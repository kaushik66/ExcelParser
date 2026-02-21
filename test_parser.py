import pytest
from openpyxl import Workbook

from data_extractor import parse_cell_value, extract_and_parse_data
from schemas import LLMHeaderMapping, ColumnMapping

# ---------------------------------------------------------
# Test deterministic string parsing (parse_cell_value)
# ---------------------------------------------------------

def test_parse_cell_value_standard_numbers():
    assert parse_cell_value(123) == 123.0
    assert parse_cell_value(45.67) == 45.67
    assert parse_cell_value("89.0") == 89.0

def test_parse_cell_value_commas():
    assert parse_cell_value("1,234.56") == 1234.56
    assert parse_cell_value("1,000,000") == 1000000.0

def test_parse_cell_value_percentages():
    assert parse_cell_value("45%") == 0.45
    assert parse_cell_value("100.5%") == 1.005

def test_parse_cell_value_booleans():
    assert parse_cell_value("YES") == 1.0
    assert parse_cell_value("TRUE") == 1.0
    assert parse_cell_value("NO") == 0.0
    assert parse_cell_value("FALSE") == 0.0
    assert parse_cell_value(True) == 1.0
    assert parse_cell_value(False) == 0.0

def test_parse_cell_value_nulls():
    assert parse_cell_value(None) is None
    assert parse_cell_value("") is None
    assert parse_cell_value(" ") is None
    assert parse_cell_value("N/A") is None
    assert parse_cell_value("-") is None
    assert parse_cell_value("NULL") is None
    assert parse_cell_value("NONE") is None

def test_parse_cell_value_invalid_strings():
    assert parse_cell_value("Some random text") is None
    assert parse_cell_value("123 ABC") is None

# ---------------------------------------------------------
# Test data extraction and business logic rules
# ---------------------------------------------------------

@pytest.fixture
def mock_validation_worksheet():
    """Creates a basic openpyxl worksheet in memory for testing."""
    wb = Workbook()
    ws = wb.active
    ws.append(["Coal Consumption", "Misc Notes"])
    return ws

def test_extract_and_parse_happy_path(mock_validation_worksheet):
    mock_validation_worksheet.append(["1,500.25", "Seems fine"])
    
    mapping = LLMHeaderMapping(mappings=[
        ColumnMapping(
            original_header="Coal Consumption",
            canonical_parameter="coal_consumption",
            asset_name="Boiler-1",
            confidence="high"
        ),
        ColumnMapping(
            original_header="Misc Notes",
            canonical_parameter=None,  # Unmapped
            asset_name=None,
            confidence="high"
        )
    ])
    
    response = extract_and_parse_data(worksheet=mock_validation_worksheet, header_row_index=1, mapping_result=mapping)
    
    assert response.status == "success"
    assert len(response.parsed_data) == 1
    assert response.parsed_data[0].param_name == "coal_consumption"
    assert response.parsed_data[0].parsed_value == 1500.25
    assert len(response.unmapped_columns) == 1
    assert len(response.warnings) == 0

def test_negative_value_validation_warning(mock_validation_worksheet):
    mock_validation_worksheet.append([-500.0, "Impossible value"])
    
    mapping = LLMHeaderMapping(mappings=[
        ColumnMapping(
            original_header="Coal Consumption",
            canonical_parameter="coal_consumption",
            asset_name=None,
            confidence="high"
        ),
        ColumnMapping(
            original_header="Misc Notes",
            canonical_parameter=None,
            asset_name=None,
            confidence="high"
        )
    ])
    
    response = extract_and_parse_data(worksheet=mock_validation_worksheet, header_row_index=1, mapping_result=mapping)
    
    # Value should still be extracted
    assert len(response.parsed_data) == 1
    assert response.parsed_data[0].parsed_value == -500.0
    
    # But a warning MUST be generated
    assert len(response.warnings) == 1
    assert "has a negative value (-500.0) for 'coal_consumption'" in response.warnings[0]
