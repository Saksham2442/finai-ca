"""
FinAI CA - Backend
Stage 1: ratio math. Stage 2: AI explanations. Stage 4: persistence.
Stage 6: validation. Stage 7: PDF export.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv
import pandas as pd
import io

load_dotenv()  # reads GEMINI_API_KEY from .env into the environment

from ratios import compute_ratios
from ai_explain import explain_ratios
from validation import check_warnings
from pdf_export import generate_pdf
import database

app = FastAPI(title="FinAI CA - Ratio Engine")

database.init_db()  # creates finai.db and the analyses table if they don't exist yet

# Allow the Next.js frontend to call this API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


class FinancialInput(BaseModel):
    """Manual entry input - the numbers a small business owner would actually have on hand."""
    company_name: str = "Untitled"
    revenue: float
    cost_of_goods_sold: float
    net_income: float  # allowed to be negative - a business can post a loss
    current_assets: float
    current_liabilities: float
    inventory: float
    total_assets: float
    total_liabilities: float
    total_equity: float

    @field_validator(
        "revenue", "cost_of_goods_sold", "current_assets", "current_liabilities",
        "inventory", "total_assets", "total_liabilities", "total_equity",
    )
    @classmethod
    def must_be_non_negative(cls, value: float, info):
        if value < 0:
            raise ValueError(f"{info.field_name} cannot be negative")
        return value


def _ratio_fields(payload: FinancialInput) -> dict:
    """The 9 numeric fields ratios.py expects - excludes company_name."""
    data = payload.model_dump()
    data.pop("company_name")
    return data


@app.post("/analyze/manual")
def analyze_manual(payload: FinancialInput):
    """Stage 1 endpoint: manual number entry -> computed ratios (no AI, not saved)."""
    ratios = compute_ratios(_ratio_fields(payload))
    return {"input": payload.model_dump(), "ratios": ratios}


@app.post("/analyze/csv")
async def analyze_csv(file: UploadFile = File(...)):
    """
    Stage 1 endpoint: CSV upload -> computed ratios.
    Expects a single-row CSV with columns matching the 9 numeric fields.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse CSV — check the file format")

    required_cols = [k for k in FinancialInput.model_fields.keys() if k != "company_name"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"CSV is missing columns: {missing}")

    row = df.iloc[0][required_cols].to_dict()
    ratios = compute_ratios(row)
    return {"input": row, "ratios": ratios}


@app.post("/analyze/manual/explain")
def analyze_manual_explain(payload: FinancialInput):
    """
    Stage 2 + 4 + 6 endpoint: computes ratios, checks for suspicious input,
    gets AI explanations, and saves the full result (including warnings) to the database.
    """
    ratio_fields = _ratio_fields(payload)
    warnings = check_warnings(ratio_fields)
    ratios = compute_ratios(ratio_fields)

    try:
        analysis = explain_ratios(ratios)
    except Exception as e:
        error_text = str(e)
        if "DEADLINE_EXCEEDED" in error_text or "504" in error_text:
            detail = "The AI took too long to respond - this usually means you're hitting the free-tier rate limit. Wait about a minute and try again."
        elif "RESOURCE_EXHAUSTED" in error_text or "429" in error_text:
            detail = "Rate limit reached on the free tier. Wait about a minute before trying again."
        else:
            detail = f"AI explanation failed: {error_text}"
        raise HTTPException(status_code=502, detail=detail)

    saved_id = database.save_analysis(
        company_name=payload.company_name,
        input_data=payload.model_dump(),
        ratios=ratios,
        analysis=analysis,
        warnings=warnings,
    )

    return {
        "id": saved_id,
        "input": payload.model_dump(),
        "ratios": ratios,
        "analysis": analysis,
        "warnings": warnings,
    }


@app.get("/analyses")
def get_analyses():
    """Stage 4: list of past analyses, most recent first - for the history view."""
    return database.list_analyses()


@app.get("/analyses/{analysis_id}")
def get_one_analysis(analysis_id: int):
    """Stage 4: fetch one full past analysis by id."""
    result = database.get_analysis(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@app.get("/analyses/{analysis_id}/pdf")
def download_analysis_pdf(analysis_id: int):
    """Stage 7: generate and return a PDF report for a saved analysis."""
    result = database.get_analysis(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    pdf_bytes = generate_pdf(result)
    company_slug = "".join(c if c.isalnum() else "_" for c in result["company_name"])
    filename = f"{company_slug}_financial_analysis.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/health")
def health():
    return {"status": "ok"}