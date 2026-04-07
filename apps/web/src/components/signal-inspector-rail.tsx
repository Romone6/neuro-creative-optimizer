"use client";

import { useMemo, useState } from "react";

export type SignalMetric = {
  id: string;
  label: string;
  value: number;
  confidence: number;
  delta?: number;
  interpretation: string;
  evidence: string[];
  revision: string[];
};

type SignalInspectorRailProps = {
  signals: SignalMetric[];
  selectedSignalId?: string | null;
  onSelectSignal: (signalId: string) => void;
  sourceExcerpt?: string;
  runSummary?: string;
};

type InspectorTab = "signal" | "evidence" | "revision";

export function SignalInspectorRail({
  signals,
  selectedSignalId,
  onSelectSignal,
  sourceExcerpt,
  runSummary,
}: SignalInspectorRailProps) {
  const [tab, setTab] = useState<InspectorTab>("signal");
  const selectedSignal = useMemo(
    () => signals.find((signal) => signal.id === selectedSignalId) ?? signals[0],
    [selectedSignalId, signals],
  );

  return (
    <aside className="glass-panel signal-scrollbar flex h-full min-h-[38rem] flex-col overflow-hidden rounded-[2rem] p-5 text-slate-100">
      <div className="mb-4 space-y-2 border-b border-white/8 pb-4">
        <p className="signal-label text-[10px] text-cyan-100/55">All Signals</p>
        <h2 className="text-lg font-medium text-slate-50">Clinical Signal Stack</h2>
        {runSummary ? <p className="text-sm leading-6 text-slate-300/70">{runSummary}</p> : null}
      </div>

      <div className="mb-5 grid gap-2">
        {signals.map((signal) => {
          const selected = selectedSignal?.id === signal.id;
          return (
            <button
              key={signal.id}
              type="button"
              onClick={() => onSelectSignal(signal.id)}
              className={`grid grid-cols-[1fr_auto] items-start gap-3 rounded-2xl border px-3 py-3 text-left transition ${
                selected
                  ? "border-cyan-200/25 bg-cyan-100/8"
                  : "border-white/6 bg-white/[0.02] hover:border-white/12 hover:bg-white/[0.04]"
              }`}
            >
              <div>
                <p className="text-sm font-medium text-slate-100">{signal.label}</p>
                <p className="mt-1 text-xs leading-5 text-slate-400">
                  Confidence {formatPercent(signal.confidence)}
                </p>
              </div>
              <div className="text-right">
                <p className="font-mono text-base text-slate-50">{formatValue(signal.value)}</p>
                <p
                  className={`mt-1 font-mono text-xs ${
                    signal.delta && signal.delta > 0 ? "text-emerald-300" : "text-slate-400"
                  }`}
                >
                  {signal.delta ? formatDelta(signal.delta) : "stable"}
                </p>
              </div>
            </button>
          );
        })}
      </div>

      <div className="mb-4 flex gap-2 border-b border-white/8 pb-4">
        {(["signal", "evidence", "revision"] as const).map((name) => (
          <button
            key={name}
            type="button"
            onClick={() => setTab(name)}
            className={`rounded-full px-3 py-1.5 text-sm transition ${
              tab === name
                ? "bg-cyan-100/12 text-cyan-50"
                : "bg-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            {name.charAt(0).toUpperCase() + name.slice(1)}
          </button>
        ))}
      </div>

      {selectedSignal ? (
        <div className="flex min-h-0 flex-1 flex-col gap-4">
          <div className="space-y-1">
            <p className="signal-label text-[10px] text-cyan-100/55">Selected Signal</p>
            <h3 className="text-xl font-medium text-slate-50">{selectedSignal.label}</h3>
            <p className="font-mono text-sm text-cyan-100/80">
              {formatValue(selectedSignal.value)} · confidence {formatPercent(selectedSignal.confidence)}
            </p>
          </div>

          {tab === "signal" ? (
            <div className="space-y-4 text-sm leading-6 text-slate-300/78">
              <p>{selectedSignal.interpretation}</p>
              {sourceExcerpt ? (
                <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                  <p className="signal-label mb-2 text-[10px] text-cyan-100/55">Selected Source</p>
                  <p className="line-clamp-6 text-sm text-slate-300/72">{sourceExcerpt}</p>
                </div>
              ) : null}
            </div>
          ) : null}

          {tab === "evidence" ? (
            <div className="space-y-3">
              {selectedSignal.evidence.map((item, index) => (
                <div key={`${selectedSignal.id}-evidence-${index}`} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                  <p className="text-sm leading-6 text-slate-300/72">{item}</p>
                </div>
              ))}
            </div>
          ) : null}

          {tab === "revision" ? (
            <div className="space-y-3">
              {selectedSignal.revision.map((item, index) => (
                <div key={`${selectedSignal.id}-revision-${index}`} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                  <p className="text-sm leading-6 text-slate-300/72">{item}</p>
                </div>
              ))}
            </div>
          ) : null}
        </div>
      ) : (
        <div className="flex flex-1 items-center justify-center rounded-2xl border border-dashed border-white/10 text-sm text-slate-500">
          No signal selected.
        </div>
      )}
    </aside>
  );
}

function formatValue(value: number) {
  return value.toFixed(2);
}

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

function formatDelta(value: number) {
  return `${value > 0 ? "+" : ""}${value.toFixed(2)}`;
}
