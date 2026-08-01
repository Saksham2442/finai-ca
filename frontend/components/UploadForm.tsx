"use client";

import { useState } from "react";
import type { FinancialInput } from "@/lib/api";

const FIELDS: { key: keyof Omit<FinancialInput, "company_name">; label: string }[] = [
  { key: "revenue", label: "Revenue" },
  { key: "cost_of_goods_sold", label: "Cost of goods sold" },
  { key: "net_income", label: "Net income" },
  { key: "current_assets", label: "Current assets" },
  { key: "current_liabilities", label: "Current liabilities" },
  { key: "inventory", label: "Inventory" },
  { key: "total_assets", label: "Total assets" },
  { key: "total_liabilities", label: "Total liabilities" },
  { key: "total_equity", label: "Total equity" },
];

const SAMPLE: FinancialInput = {
  company_name: "Sample Co",
  revenue: 1000000,
  cost_of_goods_sold: 600000,
  net_income: 120000,
  current_assets: 300000,
  current_liabilities: 150000,
  inventory: 80000,
  total_assets: 900000,
  total_liabilities: 400000,
  total_equity: 500000,
};

export default function UploadForm({
  onSubmit,
  loading,
}: {
  onSubmit: (input: FinancialInput) => void;
  loading: boolean;
}) {
  const [companyName, setCompanyName] = useState("");
  const [values, setValues] = useState<Record<string, string>>({});

  function handleChange(key: string, val: string) {
    setValues((prev) => ({ ...prev, [key]: val }));
  }

  function fillSample() {
    setCompanyName(SAMPLE.company_name);
    const asStrings: Record<string, string> = {};
    FIELDS.forEach(({ key }) => (asStrings[key] = String(SAMPLE[key])));
    setValues(asStrings);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const parsed: Partial<FinancialInput> = {
      company_name: companyName.trim() || "Untitled",
    };
    for (const { key } of FIELDS) {
      const num = parseFloat(values[key]);
      parsed[key] = isNaN(num) ? 0 : num;
    }
    onSubmit(parsed as FinancialInput);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <label className="block">
        <span className="text-sm text-ink/70 font-body">Company name</span>
        <div className="mt-1 flex items-baseline border-b border-rule focus-within:border-ink transition-colors">
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className="w-full bg-transparent py-2 font-body text-ink outline-none placeholder:text-ink/30"
            placeholder="e.g. Acme Traders"
          />
        </div>
      </label>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5">
        {FIELDS.map(({ key, label }) => (
          <label key={key} className="block">
            <span className="text-sm text-ink/70 font-body">{label}</span>
            <div className="mt-1 flex items-baseline border-b border-rule focus-within:border-ink transition-colors">
              <span className="text-ink/40 font-mono text-sm pr-1">₹</span>
              <input
                type="number"
                step="any"
                required
                value={values[key] ?? ""}
                onChange={(e) => handleChange(key, e.target.value)}
                className="w-full bg-transparent py-2 font-mono text-ink tabular-nums outline-none placeholder:text-ink/30"
                placeholder="0"
              />
            </div>
          </label>
        ))}
      </div>

      <div className="flex items-center gap-4 pt-2">
        <button
          type="submit"
          disabled={loading}
          className="bg-ink text-paper px-6 py-3 font-body text-sm tracking-wide hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Analyzing…" : "Analyze financials"}
        </button>
        <button
          type="button"
          onClick={fillSample}
          className="text-sm text-ink/60 underline underline-offset-4 hover:text-ink transition-colors"
        >
          Fill sample numbers
        </button>
      </div>
    </form>
  );
}
