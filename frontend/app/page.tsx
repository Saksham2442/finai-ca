"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import UploadForm from "@/components/UploadForm";
import RatioLedger from "@/components/RatioLedger";
import HistoryList from "@/components/HistoryList";
import {
  analyzeManual,
  fetchHistory,
  fetchAnalysisById,
  type AnalysisResult,
  type AnalysisSummary,
  type FinancialInput,
} from "@/lib/api";
import { isLoggedIn, getEmail, clearToken } from "@/lib/auth";

export default function Home() {
  const router = useRouter();
  const [checkedAuth, setCheckedAuth] = useState(false);
  const [email, setEmail] = useState<string | null>(null);

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [history, setHistory] = useState<AnalysisSummary[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/login");
      return;
    }
    setEmail(getEmail());
    setCheckedAuth(true);
  }, [router]);

  async function loadHistory() {
    setHistoryLoading(true);
    try {
      const items = await fetchHistory();
      setHistory(items);
    } catch {
      // History is a nice-to-have; a failed load here shouldn't block the form
    } finally {
      setHistoryLoading(false);
    }
  }

  useEffect(() => {
    if (checkedAuth) {
      loadHistory();
    }
  }, [checkedAuth]);

  async function handleSubmit(input: FinancialInput) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeManual(input);
      setResult(data);
      loadHistory();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong reaching the backend."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleSelectHistory(id: number) {
    setError(null);
    setLoading(true);
    try {
      const data = await fetchAnalysisById(id);
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not load that analysis."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  if (!checkedAuth) {
    return null;
  }

  return (
    <main className="min-h-screen bg-paper">
      <div className="max-w-3xl mx-auto px-6 py-16 sm:py-24">
        <div className="mb-14">
          <p className="text-xs uppercase tracking-widest text-ink/50 font-body mb-3">
            Financial Ratio Analysis
          </p>
          <h1 className="font-display text-4xl sm:text-5xl text-ink leading-tight mb-4">
            What your numbers are actually telling you.
          </h1>
        </div>

        <div className="flex items-center justify-between mb-8">
          <p className="text-sm text-ink/50 font-body">{email}</p>
          <button
            onClick={handleLogout}
            className="text-sm text-ink/60 underline underline-offset-4 hover:text-ink transition-colors font-body"
          >
            Log out
          </button>
        </div>

        <p className="font-body text-ink/70 text-base leading-relaxed max-w-xl mb-1">
          Enter your financials below. We compute the ratios and explain
          what each one means in plain language — the read a CA would
          give you, without the wait.
        </p>
        <p className="text-xs text-ink/40 font-body mb-10">
          This is an AI-generated analysis for informational purposes only,
          not professional financial or tax advice.
        </p>

        <div className="border-t border-rule pt-10">
          <UploadForm onSubmit={handleSubmit} loading={loading} />
        </div>

        {error && (
          <div className="mt-8 border-l-2 border-concern pl-6 py-1">
            <p className="text-xs uppercase tracking-widest text-concern font-body mb-1">
              Couldn't complete the analysis
            </p>
            <p className="text-sm text-ink/70 font-body">{error}</p>
          </div>
        )}

        {result && <RatioLedger result={result} />}

        <div className="mt-16 border-t border-rule pt-8">
          <p className="text-xs uppercase tracking-widest text-ink/50 font-body mb-4">
            Past analyses
          </p>
          <HistoryList
            items={history}
            onSelect={handleSelectHistory}
            loading={historyLoading}
          />
        </div>
      </div>
    </main>
  );
}
