// Talks to your FastAPI backend. Change the port here if your backend
// runs somewhere other than 8001.
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export interface FinancialInput {
  company_name: string;
  revenue: number;
  cost_of_goods_sold: number;
  net_income: number;
  current_assets: number;
  current_liabilities: number;
  inventory: number;
  total_assets: number;
  total_liabilities: number;
  total_equity: number;
}

export interface RatioExplanation {
  ratio_name: string;
  explanation: string;
  concern_level: "healthy" | "watch" | "concerning" | string;
}

export interface AnalysisResult {
  id: number;
  input: FinancialInput;
  ratios: Record<string, number | null>;
  analysis: {
    explanations: RatioExplanation[];
    overall_summary: string;
  };
  warnings: string[];
}

export interface AnalysisSummary {
  id: number;
  company_name: string;
  created_at: string;
}

// FastAPI validation errors (422) come back as an array of objects like
// { loc: ["body", "revenue"], msg: "Value error, revenue cannot be negative" }
// rather than a single string. This turns either shape into one readable message.
function extractErrorMessage(body: any, fallbackStatus: number): string {
  if (typeof body.detail === "string") {
    return body.detail;
  }
  if (Array.isArray(body.detail)) {
    return body.detail
      .map((err: any) => {
        const field = Array.isArray(err.loc) ? err.loc[err.loc.length - 1] : "input";
        const msg = (err.msg || "").replace(/^Value error,\s*/, "");
        return `${field}: ${msg}`;
      })
      .join("; ");
  }
  return `Request failed with status ${fallbackStatus}`;
}

export async function analyzeManual(
  input: FinancialInput
): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/analyze/manual/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(extractErrorMessage(body, res.status));
  }

  return res.json();
}

export async function fetchHistory(): Promise<AnalysisSummary[]> {
  const res = await fetch(`${API_BASE}/analyses`);
  if (!res.ok) {
    throw new Error(`Could not load history (status ${res.status})`);
  }
  return res.json();
}

export async function fetchAnalysisById(id: number): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/analyses/${id}`);
  if (!res.ok) {
    throw new Error(`Could not load analysis ${id} (status ${res.status})`);
  }
  return res.json();
}

export function getPdfUrl(id: number): string {
  return `${API_BASE}/analyses/${id}/pdf`;
}
