import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pydantic import ValidationError
import openpyxl
from io import BytesIO

from schemas import ParseResponse
from parser_logic import find_header_row_index
from llm_mapping import map_headers
from data_extractor import extract_and_parse_data

# The Context Registries (Ground Truth)
PARAM_REGISTRY = [
  {"name": "coal_consumption", "display_name": "Coal Consumption", "unit": "MT", "category": "input", "section": "COGEN BOILER"},
  {"name": "steam_generation", "display_name": "Steam Generation", "unit": "T/hr", "category": "output", "section": "COGEN BOILER"},
  {"name": "power_generation", "display_name": "Power Generation", "unit": "MWh", "category": "output", "section": "POWER PLANT"}
]

ASSET_REGISTRY = [
  {"name": "AFBC-1", "display_name": "AFBC Boiler 1", "type": "boiler"},
  {"name": "AFBC-2", "display_name": "AFBC Boiler 2", "type": "boiler"},
  {"name": "TG-1", "display_name": "Turbo Generator 1", "type": "turbine"}
]

app = FastAPI(
    title="Intelligent Excel Parser API",
    description="Maps messy factory data to rigid taxonomy using Gemini and deterministic parsing.",
    version="1.0.0"
)

@app.post("/parse", response_model=ParseResponse)
async def parse_excel_file(file: UploadFile = File(...)):
    """
    Accepts an uploaded .xlsx file, deterministically finds the header row,
    uses Gemini 2.5 Flash to map headers, and extracts the core data.
    """
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Only .xlsx files are supported."
        )
        
    try:
        # Load the file into memory
        contents = await file.read()
        workbook = openpyxl.load_workbook(filename=BytesIO(contents), data_only=True)
        if not workbook.worksheets:
            raise ValueError("The uploaded workbook contains no active worksheets.")
            
        master_parsed_data = []
        master_needs_review = []
        master_unmapped_columns = []
        master_warnings = []
        master_header_row = -1
        
        for worksheet in workbook.worksheets:
            try:
                # 1. Deterministic Header Search
                header_row_index = find_header_row_index(worksheet)
            except ValueError:
                master_warnings.append(f"Sheet '{worksheet.title}' skipped: No valid headers found.")
                continue
            
            # Extract the raw header string values
            # openpyxl uses 1-indexed rows
            raw_headers = []
            for cell in worksheet[header_row_index]:
                val = str(cell.value).strip() if cell.value is not None else ""
                raw_headers.append(val)
                
            # 2. LLM Header Mapping
            mapping_result = await map_headers(
                headers=raw_headers,
                param_registry=PARAM_REGISTRY,
                asset_registry=ASSET_REGISTRY
            )
            
            # 3. Deterministic Data Extraction
            sheet_result = extract_and_parse_data(
                worksheet=worksheet,
                header_row_index=header_row_index,
                mapping_result=mapping_result
            )
            
            if master_header_row == -1:
                master_header_row = sheet_result.header_row
                
            master_parsed_data.extend(sheet_result.parsed_data)
            master_needs_review.extend(sheet_result.needs_review)
            master_unmapped_columns.extend(sheet_result.unmapped_columns)
            master_warnings.extend(sheet_result.warnings)
            
        if master_header_row == -1:
            raise ValueError("No valid sheets with headers found in the workbook.")
            
        return ParseResponse(
            status="success",
            header_row=master_header_row,
            parsed_data=master_parsed_data,
            needs_review=master_needs_review,
            unmapped_columns=master_unmapped_columns,
            warnings=master_warnings
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        # Catch unexpected LLM errors or deep openpyxl parsing faults
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
