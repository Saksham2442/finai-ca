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
}

export interface AnalysisSummary {
  id: number;
  company_name: string;
  created_at: string;
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
    throw new Error(body.detail || `Request failed with status ${res.status}`);
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