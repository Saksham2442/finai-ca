"""
FinAI CA - Backend
Stage 1: ratio math. Stage 2: AI explanations. Stage 4: persistence.
Stage 6: validation. Stage 7: PDF export. Stage 8: authentication.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator, EmailStr
from dotenv import load_dotenv
import pandas as pd
import io

load_dotenv()  # reads GEMINI_API_KEY and JWT_SECRET_KEY into the environment

from ratios import compute_ratios
from ai_explain import explain_ratios
from validation import check_warnings
from pdf_export import generate_pdf
from auth import hash_password, verify_password, create_access_token, get_current_user_id
import database

app = FastAPI(title="FinAI CA - Ratio Engine")

database.init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# ---- Auth models ----

class SignupInput(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, value: str):
        if len(value) < 8:
            raise ValueError("password must be at least 8 characters")
        return value


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str


# ---- Auth routes ----

@app.post("/auth/signup", response_model=TokenResponse)
def signup(payload: SignupInput):
    existing = database.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    user_id = database.create_user(email=payload.email, password_hash=hash_password(payload.password))
    token = create_access_token(user_id=user_id, email=payload.email)
    return TokenResponse(access_token=token, email=payload.email)


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginInput):
    user = database.get_user_by_email(payload.email)
    if not user or not user["password_hash"] or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = create_access_token(user_id=user["id"], email=user["email"])
    return TokenResponse(access_token=token, email=user["email"])


# ---- Financial input ----

class FinancialInput(BaseModel):
    company_name: str = "Untitled"
    revenue: float
    cost_of_goods_sold: float
    net_income: float
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
    data = payload.model_dump()
    data.pop("company_name")
    return data


@app.post("/analyze/manual")
def analyze_manual(payload: FinancialInput, user_id: int = Depends(get_current_user_id)):
    """Manual number entry -> computed ratios (no AI, not saved). Requires login."""
    ratios = compute_ratios(_ratio_fields(payload))
    return {"input": payload.model_dump(), "ratios": ratios}


@app.post("/analyze/csv")
async def analyze_csv(file: UploadFile = File(...), user_id: int = Depends(get_current_user_id)):
    """CSV upload -> computed ratios. Requires login."""
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
def analyze_manual_explain(payload: FinancialInput, user_id: int = Depends(get_current_user_id)):
    """Computes ratios, checks warnings, gets AI explanations, and saves - owned by the logged-in user."""
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
        user_id=user_id,
    )

    return {
        "id": saved_id,
        "input": payload.model_dump(),
        "ratios": ratios,
        "analysis": analysis,
        "warnings": warnings,
    }


@app.get("/analyses")
def get_analyses(user_id: int = Depends(get_current_user_id)):
    """List of this user's past analyses, most recent first."""
    return database.list_analyses(user_id)


@app.get("/analyses/{analysis_id}")
def get_one_analysis(analysis_id: int, user_id: int = Depends(get_current_user_id)):
    """Fetch one full past analysis by id - only if it belongs to the logged-in user."""
    result = database.get_analysis(analysis_id, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@app.get("/analyses/{analysis_id}/pdf")
def download_analysis_pdf(analysis_id: int, user_id: int = Depends(get_current_user_id)):
    """Generate and return a PDF report for a saved analysis - only if owned by this user."""
    result = database.get_analysis(analysis_id, user_id)
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