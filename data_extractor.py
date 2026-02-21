import logging
from typing import Any, Optional
from openpyxl.worksheet.worksheet import Worksheet

from schemas import LLMHeaderMapping, ParseResponse, ParsedDataPoint, UnmappedColumn

logger = logging.getLogger(__name__)


def parse_cell_value(raw_val: Any) -> Optional[float]:
    """
    Helper function to deterministically parse raw cell values into floats.
    Handles commas, percentages, boolean texts (YES/NO, TRUE/FALSE), and empty/null states.
    """
    if raw_val is None:
        return None
        
    # If openpyxl already parsed it as a number
    if isinstance(raw_val, (int, float)):
        # In python, bool is a subclass of int, so strict checking is helpful if we care,
        # but the float() cast works properly for both.
        if isinstance(raw_val, bool):
            return 1.0 if raw_val else 0.0
        return float(raw_val)
        
    raw_str = str(raw_val).strip().upper()
    
    # Null equivalents
    if raw_str in ("", "N/A", "NULL", "-", "NONE"):
        return None
        
    # Boolean text equivalents
    if raw_str in ("YES", "TRUE"):
        return 1.0
    if raw_str in ("NO", "FALSE"):
        return 0.0
        
    # Remove large number separators
    raw_str = raw_str.replace(",", "")
    
    # Handle percentages
    if "%" in raw_str:
        raw_str = raw_str.replace("%", "")
        try:
            return float(raw_str) / 100.0
        except ValueError:
            return None
            
    # Standard float conversion
    try:
        return float(raw_str)
    except ValueError:
        return None


def extract_and_parse_data(worksheet: Worksheet, header_row_index: int, mapping_result: LLMHeaderMapping) -> ParseResponse:
    """
    Iterates through rows beneath the header row, parsing values deterministically
    based on the LLM mapping results.
    
    Args:
        worksheet (Worksheet): The openpyxl Worksheet object.
        header_row_index (int): 1-indexed row number of the true headers.
        mapping_result (LLMHeaderMapping): The structured response from the LLM.
        
    Returns:
        ParseResponse: structured representation of the parsed excel sheet.
    """
    parsed_data = []
    needs_review = []
    unmapped_columns = []
    warnings = []
    
    # 0-indexed translation for final JSON schema
    zero_indexed_header_row = header_row_index - 1
    if header_row_index > 1:
        warnings.append(f"Row(s) 1 to {header_row_index - 1} appear to be title/metadata rows, skipped.")
        
    # Map out which columns have a canonical parameter to avoid re-checking inside the row loop
    mapped_cols = {}
    seen_mappings = set()
    for col_idx, mapping in enumerate(mapping_result.mappings):
        if mapping.canonical_parameter:
            mapped_cols[col_idx] = mapping
            
            mapping_key = (mapping.canonical_parameter, mapping.asset_name)
            if mapping_key in seen_mappings:
                if mapping.asset_name:
                    warnings.append(f"Duplicate mapping detected: Multiple columns mapped to parameter '{mapping.canonical_parameter}' for asset '{mapping.asset_name}'.")
                else:
                    warnings.append(f"Duplicate mapping detected: Multiple columns mapped to parameter '{mapping.canonical_parameter}'.")
            else:
                seen_mappings.add(mapping_key)
        else:
            unmapped_columns.append(UnmappedColumn(
                sheet_name=worksheet.title,
                col=col_idx,
                header=mapping.original_header,
                reason="No matching parameter found"
            ))
            
    # Iterate through row values skipping the header row
    # start=header_row_index effectively means the first data row will have 0-indexed row mapping
    # since data starts at header_row_index + 1 (1-indexed), which is header_row_index (0-indexed).
    for row_idx, row in enumerate(
        worksheet.iter_rows(min_row=header_row_index + 1, values_only=True), 
        start=header_row_index
    ):
        # Check if the entire row is empty to gracefully skip it
        is_empty_row = all(val is None or (isinstance(val, str) and not val.strip()) for val in row)
        if is_empty_row:
            continue
            
        # Iterate over cells horizontally
        for col_idx, raw_val in enumerate(row):
            # Guard against openpyxl returning more columns than we mapped headers for
            if col_idx >= len(mapping_result.mappings):
                continue
                
            mapping = mapped_cols.get(col_idx)
            # We only extract parsed data if the LLM mapped this column to a known parameter
            if not mapping:
                continue
                
            # Compute parsed value
            parsed_val = parse_cell_value(raw_val)
            
            # Form clean raw representation
            raw_str = str(raw_val).strip() if raw_val is not None else ""
            
            # Physical validation logic for impossible negative values
            if parsed_val is not None and parsed_val < 0:
                if mapping.canonical_parameter in ("coal_consumption", "steam_generation", "power_generation"):
                    warnings.append(f"Validation Warning: Row {row_idx}, Column {col_idx} has a negative value ({parsed_val}) for '{mapping.canonical_parameter}'.")
            
            data_point = ParsedDataPoint(
                sheet_name=worksheet.title,
                row=row_idx,
                col=col_idx,
                param_name=mapping.canonical_parameter,
                asset_name=mapping.asset_name,
                raw_value=raw_str,
                parsed_value=parsed_val,
                confidence=mapping.confidence
            )
            
            if mapping.confidence == "low":
                needs_review.append(data_point)
            else:
                parsed_data.append(data_point)
            
    return ParseResponse(
        status="success",
        header_row=zero_indexed_header_row,
        parsed_data=parsed_data,
        needs_review=needs_review,
        unmapped_columns=unmapped_columns,
        warnings=warnings
    )
