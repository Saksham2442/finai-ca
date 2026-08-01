"use client";

import type { AnalysisSummary } from "@/lib/api";

function formatDate(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function HistoryList({
  items,
  onSelect,
  loading,
}: {
  items: AnalysisSummary[];
  onSelect: (id: number) => void;
  loading: boolean;
}) {
  if (loading) {
    return (
      <p className="text-sm text-ink/50 font-body">Loading history…</p>
    );
  }

  if (items.length === 0) {
    return (
      <p className="text-sm text-ink/50 font-body">
        No past analyses yet — run one above and it'll show up here.
      </p>
    );
  }

  return (
    <div className="divide-y divide-rule">
      {items.map((item) => (
        <button
          key={item.id}
          onClick={() => onSelect(item.id)}
          className="w-full text-left py-3 flex items-center justify-between group"
        >
          <span className="font-body text-ink group-hover:text-accent transition-colors">
            {item.company_name}
          </span>
          <span className="text-xs text-ink/40 font-mono tabular-nums">
            {formatDate(item.created_at)}
          </span>
        </button>
      ))}
    </div>
  );
}
