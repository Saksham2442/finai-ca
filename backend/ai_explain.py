"""
Stage 2: AI explanation layer.

Rule for this whole file: the AI NEVER computes numbers. It only receives
ratios that ratios.py has already calculated, and explains them in plain
English. This keeps the math trustworthy and the AI's job narrow.
"""

import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List

# The client reads GEMINI_API_KEY from the environment automatically —
# never hardcode the key in this file.
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=30_000),  # 30 second timeout, in milliseconds
)

MODEL = "gemini-3.5-flash"  # fast + free-tier friendly; good fit for this task


class RatioExplanation(BaseModel):
    ratio_name: str = Field(description="The name of the financial ratio")
    explanation: str = Field(description="Plain-language explanation, 2-3 sentences, for a small business owner with no finance background")
    concern_level: str = Field(description="One of: 'healthy', 'watch', 'concerning'")


class RatioAnalysis(BaseModel):
    explanations: List[RatioExplanation]
    overall_summary: str = Field(description="2-3 sentence plain-language summary of overall financial health")


def explain_ratios(ratios: dict) -> dict:
    """
    Takes a dict of computed ratios (from ratios.compute_ratios) and returns
    plain-language explanations for each, plus an overall summary.
    """
    prompt = f"""You are helping a small business owner (not an accountant)
understand their financial ratios. Here are their computed ratios:

{json.dumps(ratios, indent=2)}

For each ratio, explain in plain English what it means and whether it's
healthy, worth watching, or concerning. Use general, well-known benchmarks
(e.g. current ratio above 1.5-2 is typically healthy, debt-to-equity above
2 is often a red flag) but keep it simple. Do not give specific investment
or legal advice — just explain what the numbers mean.

If any ratio is null (missing data), skip it rather than explaining a
missing number."""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RatioAnalysis,
        ),
    )

    result = RatioAnalysis.model_validate_json(response.text)
    return result.model_dump()