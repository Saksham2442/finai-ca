"use client";

import type { AnalysisResult } from "@/lib/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const CONCERN_STYLES: Record<string, { dot: string; label: string }> = {
  healthy: { dot: "bg-accent", label: "text-accent" },
  watch: { dot: "bg-watch", label: "text-watch" },
  concerning: { dot: "bg-concern", label: "text-concern" },
};

function formatRatioName(key: string) {
  return key
    .split("_")
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(" ");
}

export default function RatioLedger({ result }: { result: AnalysisResult }) {
  const chartData = Object.entries(result.ratios)
    .filter(([, v]) => v !== null)
    .map(([key, value]) => ({
      name: formatRatioName(key)
        .replace("Return On Assets", "ROA")
        .replace("Debt To Equity", "D/E"),
      value: value as number,
    }));

  return (
    <div className="mt-14 space-y-10">
      {/* Data warnings - shown before the summary since they affect how much to trust it */}
      {result.warnings && result.warnings.length > 0 && (
        <div className="border-l-2 border-watch pl-6 py-1 bg-watch-soft/40">
          <p className="text-xs uppercase tracking-widest text-watch font-body mb-2">
            Worth double-checking
          </p>
          <ul className="space-y-1.5">
            {result.warnings.map((w, i) => (
              <li key={i} className="text-sm text-ink/80 font-body leading-relaxed">
                {w}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Overall summary */}
      <div className="border-l-2 border-ink pl-6 py-1">
        <p className="text-xs uppercase tracking-widest text-ink/50 font-body mb-2">
          Summary
        </p>
        <p className="font-display text-xl leading-relaxed text-ink">
          {result.analysis.overall_summary}
        </p>
      </div>

      {/* Chart */}
      <div className="border-t border-rule pt-8">
        <p className="text-xs uppercase tracking-widest text-ink/50 font-body mb-4">
          Ratios at a glance
        </p>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#D8D4C8" vertical={false} />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 11, fill: "#14231F99" }}
                axisLine={{ stroke: "#D8D4C8" }}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 11, fill: "#14231F99" }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  background: "#F4F5F3",
                  border: "1px solid #D8D4C8",
                  borderRadius: 0,
                  fontFamily: "monospace",
                  fontSize: 12,
                }}
              />
              <Bar dataKey="value" fill="#3D6B52" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Ledger rows */}
      <div className="border-t border-rule">
        <p className="text-xs uppercase tracking-widest text-ink/50 font-body pt-8 mb-4">
          Ratio by ratio
        </p>
        <div className="divide-y divide-rule">
          {result.analysis.explanations.map((exp) => {
            const style =
              CONCERN_STYLES[exp.concern_level] ?? CONCERN_STYLES.watch;
            const rawValue = result.ratios[
              exp.ratio_name
                .toLowerCase()
                .replace(/ /g, "_")
                .replace("roa", "return_on_assets")
            ];
            return (
              <div
                key={exp.ratio_name}
                className="py-6 grid grid-cols-1 sm:grid-cols-[1fr_2fr] gap-x-8 gap-y-2"
              >
                <div className="flex items-baseline gap-2">
                  <span className={`inline-block w-2 h-2 rounded-full ${style.dot}`} />
                  <span className="font-display text-lg text-ink">
                    {exp.ratio_name}
                  </span>
                  {rawValue !== undefined && rawValue !== null && (
                    <span className="font-mono text-sm text-ink/50 tabular-nums ml-1">
                      {rawValue}
                    </span>
                  )}
                </div>
                <div>
                  <p className="text-sm leading-relaxed text-ink/80 font-body">
                    {exp.explanation}
                  </p>
                  <span
                    className={`inline-block mt-2 text-xs uppercase tracking-wide font-body ${style.label}`}
                  >
                    {exp.concern_level}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
