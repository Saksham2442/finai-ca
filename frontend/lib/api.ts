import { getToken, clearToken } from "@/lib/auth";

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

export interface AuthResponse {
  access_token: string;
  token_type: string;
  email: string;
}

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

async function authedFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const token = getToken();
  const headers = new Headers(options.headers);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    clearToken();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  }

  return res;
}

export async function signup(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(extractErrorMessage(body, res.status));
  }
  return res.json();
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(extractErrorMessage(body, res.status));
  }
  return res.json();
}

export async function analyzeManual(
  input: FinancialInput
): Promise<AnalysisResult> {
  const res = await authedFetch(`/analyze/manual/explain`, {
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
  const res = await authedFetch(`/analyses`);
  if (!res.ok) {
    throw new Error(`Could not load history (status ${res.status})`);
  }
  return res.json();
}

export async function fetchAnalysisById(id: number): Promise<AnalysisResult> {
  const res = await authedFetch(`/analyses/${id}`);
  if (!res.ok) {
    throw new Error(`Could not load analysis ${id} (status ${res.status})`);
  }
  return res.json();
}

export async function downloadPdf(id: number, companyName: string): Promise<void> {
  const res = await authedFetch(`/analyses/${id}/pdf`);
  if (!res.ok) {
    throw new Error(`Could not download PDF (status ${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const slug = companyName.replace(/[^a-zA-Z0-9]/g, "_");
  a.download = `${slug}_financial_analysis.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
