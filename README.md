# Intelligent Excel Data Parser

An AI-driven, full-stack application that deterministically extracts, maps, and validates operational factory data from messy `.xlsx` spreadsheets into a strict parameter taxonomy using Google Gemini and FastAPI.

**Live Demo:** [https://excelparser-ui.onrender.com](https://excelparser-ui.onrender.com)

> ⚠️ **Note:** This project is currently hosted on a free-tier Render instance. If the service has spun down due to inactivity, it may take between **50 seconds to 1 minute** to wake up the server upon your first request.

## Key Features

### 1. Robust AI Header Mapping

The core engine leverages Google's **Gemini 2.5 Flash** model with strict Pydantic Output Structuring to dynamically analyze messy, unformatted spreadsheet columns. It natively maps variations (e.g., "Coal Used (MT)", "Total Coke Consumption") to canonical predefined input/output parameters.

### 2. Multi-Sheet Batch Processing

Simply drop a multi-sheet workbook into the platform, and the pipeline will automatically iterate over all available tabs, skipping empty ones and aggregating results into a singular, cohesive payload.

### 3. Edge-Case Immunity

The deterministic Python engine supplements the LLM mapping with strict logical fail-safes:

- **Duplicate Warnings**: Flags scenarios where multiple Excel columns try to map to the exact same Canonical Parameter and Asset.
- **Physics Validation rules**: Intelligently flags physically impossible data points (e.g., negative fuel consumption or generation) without destroying the data matrix.
- **Low-Confidence Quarantine**: Suspect inferences made by the LLM are routed into a dedicated `needs_review` payload for human inspection rather than tainting the production `parsed_data`.
- **String Parsing Engine**: Converts nasty strings like `"1,234.56"`, `"45%"`, `"YES"`, and `"N/A"` into clean float matrices.

### 4. Developer-First Dashboard

A Next.js (TypeScript, Tailwind) split-screen dashboard provides executives with top-level metric breakdowns, whilst developers are treated to a syntax-highlighted, scrollable JSON interface (with an integrated clipboard tool) to freely inspect the API payloads seamlessly.

---

## Setup & Installation (Local Development)

To run the full-stack system on your machine, you will need a valid `GEMINI_API_KEY`.

### Method A: Docker Compose (Recommended)

The simplest way to boot both the FastAPI backend and Next.js frontend concurrently is via Docker.

1. Create a `.env` file in the root directory and add your API key:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
2. Build and boot the stack:
   ```bash
   docker-compose up --build
   ```
3. The API will boot at `http://127.0.0.1:8000` and the UI dashboard will boot at `http://localhost:3000`.

### Method B: Manual Boot (Python & Node)

If you prefer to run the services explicitly on bare metal, use standard Python and Node package managers.

#### Backend (FastAPI)

```bash
# Initialize a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn main:app --reload
```

#### Frontend (Next.js)

```bash
cd frontend

# Install Node dependencies
npm install

# Optional: Add local fallback if different from :8000
# export NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# Start the dashboard
npm run dev
```

### Generating Test Data

A utility script is included to generate various Excel workbooks for testing the extraction logic locally. Run `python create_test_data.py` to generate the test spreadsheets. The script will automatically create a `/test_files` directory in the root of the project and output `clean_data.xlsx`, `messy_data.xlsx`, `multi_asset.xlsx`, and `complex_multi_sheet.xlsx` directly into it.

---

## Testing

The parsing engine relies on the core deterministic data extractor to structure the chaotic strings found within Excel cells. A comprehensive `pytest` suite is included to guarantee correctness.

```bash
# Ensure you are via the .venv environment
# Run all tests
pytest test_parser.py -v
```
