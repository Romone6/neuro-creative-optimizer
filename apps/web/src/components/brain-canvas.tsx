"use client";

import type { SignalMetric } from "@/lib/api";

type BrainCanvasProps = {
  signals: SignalMetric[];
  selectedSignalId?: string | null;
  statusLabel: string;
  summary?: string;
  runtimeLabel?: string;
  onSelectSignal: (signalId: string) => void;
};

const BRAIN_PATH = "M 50 8 C 30 8, 15 18, 12 35 C 10 50, 15 65, 25 78 C 30 85, 40 92, 55 93 C 70 94, 82 88, 88 75 C 92 65, 92 50, 88 38 C 85 28, 75 18, 60 14 C 55 12, 52 10, 50 8 Z";

const FRONTAL_PATH = "M 25 25 C 30 18, 42 14, 52 16 C 60 18, 65 24, 66 32 C 67 40, 62 48, 55 52 C 45 58, 32 55, 28 48 C 25 42, 23 34, 25 25 Z";

const PARIETAL_PATH = "M 55 16 C 62 18, 68 22, 72 28 C 75 34, 74 42, 70 48 C 65 54, 58 56, 52 54 C 46 52, 46 44, 50 36 C 52 30, 53 24, 55 16 Z";

const TEMPORAL_PATH = "M 22 48 C 28 52, 38 56, 50 58 C 60 59, 68 62, 72 70 C 75 76, 72 84, 65 88 C 52 92, 35 90, 25 82 C 18 76, 16 62, 22 48 Z";

const OCCIPITAL_PATH = "M 70 32 C 76 38, 80 46, 80 54 C 80 62, 75 68, 68 70 C 62 72, 58 68, 60 60 C 62 52, 66 44, 70 32 Z";

const CEREBELLUM_PATH = "M 42 84 C 50 80, 60 82, 68 88 C 72 92, 70 96, 62 97 C 52 98, 42 96, 36 90 C 32 86, 34 80, 42 84 Z";

function getHeatColor(value: number): string {
  if (value >= 0.7) {
    return "rgba(239, 68, 68, 0.9)";
  } else if (value >= 0.4) {
    return "rgba(251, 191, 36, 0.85)";
  } else {
    return "rgba(96, 165, 250, 0.8)";
  }
}

function getHeatGlow(value: number): string {
  if (value >= 0.7) {
    return "0 0 15px rgba(239, 68, 68, 0.6)";
  } else if (value >= 0.4) {
    return "0 0 12px rgba(251, 191, 36, 0.5)";
  } else {
    return "0 0 10px rgba(96, 165, 250, 0.4)";
  }
}

export function BrainCanvas({
  signals,
  selectedSignalId,
  statusLabel,
  summary,
  runtimeLabel,
  onSelectSignal,
}: BrainCanvasProps) {
  const isStandby = signals.length === 0;

  return (
    <section className="glass-panel scan-grid relative min-h-[38rem] overflow-hidden rounded-[2.4rem] px-6 py-6">
      <div className="relative z-10 flex items-start justify-between gap-6">
        <div className="max-w-md space-y-3">
          <p className="signal-label text-[10px] text-cyan-100/55">{statusLabel}</p>
          <h1 className="text-[clamp(2rem,4vw,3.5rem)] font-light tracking-[-0.04em] text-slate-50">
            Brain Reaction Model
          </h1>
          <p className="max-w-xl text-sm leading-6 text-slate-300/72">
            {summary ?? "Enter text in the operator console to analyze neural response patterns."}
          </p>
        </div>
        <div className="rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-xs text-slate-300">
          {runtimeLabel ?? "Baseline analysis only"}
        </div>
      </div>

      <div className="relative z-10 mt-8 h-[30rem]">
        <div className="absolute inset-0 flex items-center justify-center">
          <svg
            viewBox="0 0 100 100"
            className="h-[22rem] w-[26rem]"
            style={{
              filter: "drop-shadow(0 0 30px rgba(121, 201, 220, 0.12))",
            }}
          >
            <defs>
              <radialGradient id="brainFill" cx="50%" cy="40%" r="55%">
                <stop offset="0%" stopColor="rgba(180, 190, 205, 0.08)" />
                <stop offset="100%" stopColor="rgba(80, 90, 105, 0.02)" />
              </radialGradient>
              <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="1.5" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            <path
              d={BRAIN_PATH}
              fill="url(#brainFill)"
              stroke="rgba(200, 210, 220, 0.25)"
              strokeWidth="0.6"
            />

            <path
              d={FRONTAL_PATH}
              fill="rgba(139, 92, 246, 0.12)"
              stroke="rgba(139, 92, 246, 0.25)"
              strokeWidth="0.3"
            />
            <text x="42" y="36" fontSize="3.5" fill="rgba(139, 92, 246, 0.5)" textAnchor="middle" fontFamily="'IBM Plex Mono', monospace">FRONTAL</text>

            <path
              d={PARIETAL_PATH}
              fill="rgba(34, 211, 238, 0.12)"
              stroke="rgba(34, 211, 238, 0.25)"
              strokeWidth="0.3"
            />
            <text x="62" y="36" fontSize="3.5" fill="rgba(34, 211, 238, 0.5)" textAnchor="middle" fontFamily="'IBM Plex Mono', monospace">PARIETAL</text>

            <path
              d={TEMPORAL_PATH}
              fill="rgba(251, 191, 36, 0.12)"
              stroke="rgba(251, 191, 36, 0.25)"
              strokeWidth="0.3"
            />
            <text x="42" y="72" fontSize="3.5" fill="rgba(251, 191, 36, 0.5)" textAnchor="middle" fontFamily="'IBM Plex Mono', monospace">TEMPORAL</text>

            <path
              d={OCCIPITAL_PATH}
              fill="rgba(236, 72, 153, 0.12)"
              stroke="rgba(236, 72, 153, 0.25)"
              strokeWidth="0.3"
            />
            <text x="72" y="52" fontSize="3.5" fill="rgba(236, 72, 153, 0.5)" textAnchor="middle" fontFamily="'IBM Plex Mono', monospace">OCCIPITAL</text>

            <path
              d={CEREBELLUM_PATH}
              fill="rgba(134, 239, 172, 0.12)"
              stroke="rgba(134, 239, 172, 0.25)"
              strokeWidth="0.3"
            />
            <text x="50" y="92" fontSize="3" fill="rgba(134, 239, 172, 0.5)" textAnchor="middle" fontFamily="'IBM Plex Mono', monospace">CEREBELLUM</text>

            <g stroke="rgba(255, 255, 255, 0.03)" strokeWidth="0.15" fill="none" opacity="0.3">
              <path d="M 30 28 C 40 25, 50 23, 62 25" />
              <path d="M 28 38 C 38 35, 50 33, 62 35" />
              <path d="M 26 48 C 36 45, 48 44, 60 46" />
              <path d="M 28 58 C 38 56, 48 55, 58 58" />
              <path d="M 32 68 C 42 66, 50 65, 56 68" />
            </g>

            {signals.map((signal) => {
              const anchor = signal.anchor;
              const isSelected = signal.id === selectedSignalId;
              const baseRadius = 5 + signal.value * 4;
              const radius = isSelected ? baseRadius + 2 : baseRadius;

              return (
                <g key={signal.id} onClick={() => onSelectSignal(signal.id)} style={{ cursor: "pointer" }}>
                  <circle
                    cx={anchor.x}
                    cy={anchor.y}
                    r={radius * 2}
                    fill={getHeatColor(signal.value)}
                    style={{
                      filter: getHeatGlow(signal.value),
                      opacity: 0.35,
                    }}
                  />
                  <circle
                    cx={anchor.x}
                    cy={anchor.y}
                    r={radius}
                    fill={getHeatColor(signal.value)}
                    style={{ filter: "url(#softGlow)" }}
                    opacity={0.9}
                  />
                  {isSelected && (
                    <circle
                      cx={anchor.x}
                      cy={anchor.y}
                      r={radius + 2.5}
                      fill="none"
                      stroke="rgba(255, 255, 255, 0.7)"
                      strokeWidth="0.8"
                      strokeDasharray="3,2"
                      style={{
                        animation: "pulseRing 1.5s ease-out infinite",
                      }}
                    />
                  )}
                  <text
                    x={anchor.x}
                    y={anchor.y + radius + 4}
                    fontSize="3.2"
                    fill="rgba(230, 240, 250, 0.75)"
                    textAnchor="middle"
                    fontFamily="'IBM Plex Mono', monospace"
                    fontWeight="500"
                    style={{ pointerEvents: "none" }}
                  >
                    {signal.label}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {!isStandby && (
          <div className="absolute inset-x-0 bottom-0 grid grid-cols-2 gap-3 px-6 pb-6 xl:grid-cols-3">
            {signals.map((signal) => (
              <button
                key={signal.id}
                type="button"
                onClick={() => onSelectSignal(signal.id)}
                className="rounded-2xl border border-white/10 bg-slate-950/58 px-3 py-3 text-left backdrop-blur-md transition hover:border-cyan-100/18"
              >
                <p className="signal-label text-[10px] text-slate-200/75">{signal.label}</p>
                <div className="mt-2 flex items-end justify-between gap-3">
                  <span className="font-mono text-lg text-slate-50">{signal.value.toFixed(2)}</span>
                  <span className="text-xs text-slate-400">{Math.round(signal.confidence * 100)}% conf</span>
                </div>
              </button>
            ))}
          </div>
        )}

        {isStandby && (
          <div className="absolute inset-x-0 bottom-0 pb-6">
            <div className="mx-auto flex max-w-md items-center justify-center gap-5 rounded-full border border-white/8 bg-white/[0.03] px-5 py-3">
              <div className="flex items-center gap-2">
                <div className="h-2.5 w-2.5 rounded-full bg-red-500" />
                <span className="text-xs text-slate-300">High (&gt;0.7)</span>
              </div>
              <div className="h-4 w-px bg-white/10" />
              <div className="flex items-center gap-2">
                <div className="h-2.5 w-2.5 rounded-full bg-amber-400" />
                <span className="text-xs text-slate-300">Med (0.4-0.7)</span>
              </div>
              <div className="h-4 w-px bg-white/10" />
              <div className="flex items-center gap-2">
                <div className="h-2.5 w-2.5 rounded-full bg-sky-400" />
                <span className="text-xs text-slate-300">Low (&lt;0.4)</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes pulseRing {
          0% {
            transform: scale(1);
            opacity: 0.7;
          }
          100% {
            transform: scale(1.6);
            opacity: 0;
          }
        }
      `}</style>
    </section>
  );
}
