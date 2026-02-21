from typing import Any
from openpyxl.worksheet.worksheet import Worksheet


def find_header_row_index(worksheet: Worksheet) -> int:
    """
    Deterministically find the true header row in a messy Excel sheet.
    
    Iterates through the first 20 rows of the worksheet and counts the number
    of string-based cells in each row. The row with the highest count of string
    values (minimum of 2) is considered the header row.
    
    Args:
        worksheet (Worksheet): The openpyxl Worksheet object to analyze.
        
    Returns:
        int: The 1-indexed row number of the true headers.
        
    Raises:
        ValueError: If no suitable header row is found within the first 20 rows.
    """
    max_string_count = 0
    best_row_idx = -1
    
    # Iterate through the first 20 rows (or up to max_row if smaller)
    # openpyxl uses 1-indexed rows
    for row_idx, row in enumerate(worksheet.iter_rows(min_row=1, max_row=20, values_only=True), start=1):
        string_count = 0
        
        # Count string-based cells in the current row
        for value in row:
            if value is not None and isinstance(value, str) and value.strip():
                string_count += 1
                
        # Update the best row if we found a higher string count
        if string_count > max_string_count:
            max_string_count = string_count
            best_row_idx = row_idx
            
    # Check if we met the minimum threshold of 2 string-based cells
    if max_string_count >= 2 and best_row_idx != -1:
        return best_row_idx
        
    raise ValueError("Could not find a valid header row within the first 20 rows.")
