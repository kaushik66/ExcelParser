from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# 1. LLM Evaluation & Mapping Schemas
# ---------------------------------------------------------

class ColumnMapping(BaseModel):
    """Mapping for a single extracted column header to a canonical parameter/asset."""
    original_header: str = Field(
        ..., 
        description="The exact column header string extracted from the Excel file."
    )
    canonical_parameter: Optional[str] = Field(
        None, 
        description="The exact 'name' from the Parameter Registry, or null if unmapped."
    )
    asset_name: Optional[str] = Field(
        None, 
        description="The exact 'name' from the Asset Registry detected in the header, or null if none."
    )
    confidence: Literal["high", "medium", "low"] = Field(
        ..., 
        description="Confidence level of the LLM mapping based on context and text similarity."
    )

class LLMHeaderMapping(BaseModel):
    """The strictly structured payload expected back from the LLM when passing in the headers."""
    mappings: List[ColumnMapping] = Field(
        default_factory=list, 
        description="List of all analyzed headers with their canonical mapping attempts."
    )

# ---------------------------------------------------------
# 2. Final API Response Schemas
# ---------------------------------------------------------

class ParsedDataPoint(BaseModel):
    """Represents a successfully mapped and deterministically parsed data cell."""
    row: int = Field(..., description="The 0-indexed row number of the data cell.")
    col: int = Field(..., description="The 0-indexed column number of the data cell.")
    param_name: str = Field(..., description="The canonical parameter name.")
    asset_name: Optional[str] = Field(None, description="The canonical asset name, if extracted.")
    raw_value: str = Field(..., description="The exact raw string representation from the cell.")
    parsed_value: Optional[float] = Field(None, description="The parsed deterministic float value (null for 'N/A').")
    confidence: Literal["high", "medium", "low"] = Field(..., description="Propagated from the LLM's column mapping.")

class UnmappedColumn(BaseModel):
    """Represents a column that was dropped/ignored based on LLM mapping or logic."""
    col: int = Field(..., description="The 0-indexed column number of the unmapped column.")
    header: str = Field(..., description="The raw header of the unmapped column.")
    reason: str = Field(..., description="Reason for ignoring (e.g., 'No matching parameter found').")

class ParseResponse(BaseModel):
    """The master JSON response schema for the /parse FastAPI endpoint."""
    status: str = Field("success", description="Overall execution status ('success' or 'error').")
    header_row: int = Field(..., description="The 0-indexed row number where true headers reside.")
    parsed_data: List[ParsedDataPoint] = Field(default_factory=list)
    unmapped_columns: List[UnmappedColumn] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list, description="Parser warnings (e.g., skipped titles, unparseable cells).")
