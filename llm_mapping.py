import json
import logging
import os
from typing import List, Dict, Any
from google import genai
from google.genai import types

from schemas import LLMHeaderMapping

logger = logging.getLogger(__name__)

# Assumes GEMINI_API_KEY is available in the environment variables
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are an expert industrial data mapping AI.
Your task is to analyze a list of messy column headers extracted from a factory's operational Excel spreadsheet and map each header to a strict Canonical Parameter Name and an optional Asset Name.

# Context: Registries
You must ONLY use the exact string values provided in the "name" fields of the following registries for your mappings.

Parameter Registry:
{param_registry}

Asset Registry:
{asset_registry}

# Rules and Instructions
1. Fuzzy Matching (Parameter Mapping): Look at the meaning, units, or common abbreviations in the original header to find the best match in the Parameter Registry. For example, "Coal Consump." or "Coal (MT)" should map to "coal_consumption".
2. Asset Extraction: Often, the asset name or its abbreviation is embedded inside the header. Extract the best matching Asset Name from the Asset Registry if present. For example, "Steam (Boiler 2)" maps to parameter: "steam_generation", asset: "AFBC-2".
3. Unmappable Columns: If a column header represents metadata, comments, notes, empty strings, dates, or simply does not correspond to any known parameter in the registry, you MUST return `null` for `canonical_parameter` and `asset_name`.
4. Confidence Scoring: Assign a confidence score based on mapping quality:
   - "high": The original header is an exact or near-exact semantic match to the parameter.
   - "medium": The header is somewhat ambiguous or uses an unusual abbreviation, but the mapping is likely correct.
   - "low": It's a best guess, or the intent is unclear.
   - For unmappable columns, use "high" confidence if it's clearly a comment/date column, or "low" if you're unsure if it applies.
"""

async def map_headers(
    headers: List[str],
    param_registry: List[Dict[str, Any]],
    asset_registry: List[Dict[str, Any]]
) -> LLMHeaderMapping:
    """
    Sends messy Excel headers to the LLM and maps them to canonical parameters and assets.
    
    Args:
        headers: A list of the raw string headers found in the Excel sheet.
        param_registry: A list of dicts representing the valid parameters.
        asset_registry: A list of dicts representing the valid assets.
        
    Returns:
        LLMHeaderMapping: A strictly typed Pydantic model containing the mappings.
    """
    # Stringify the registries for injection
    param_str = json.dumps(param_registry, indent=2)
    asset_str = json.dumps(asset_registry, indent=2)
    
    # Construct the final system prompt with the registries injected
    formatted_system_prompt = SYSTEM_PROMPT.format(
        param_registry=param_str,
        asset_registry=asset_str
    )
    
    # We pass the raw headers as a JSON array string to the user prompt
    user_prompt = f"Please map the following extracted column headers:\n{json.dumps(headers, indent=2)}"
    
    try:
        # Utilize generativeai's structured output support with Pydantic schemas
        response = await client.aio.models.generate_content(
            model="gemini-3-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=LLMHeaderMapping,
                temperature=0.0,
                system_instruction=formatted_system_prompt
            )
        )
        
        # Parse the JSON string response back into the Pydantic object
        result = LLMHeaderMapping.model_validate_json(response.text)
        return result
        
    except Exception as e:
        logger.error(f"Failed to map headers using Gemini LLM: {e}")
        raise
