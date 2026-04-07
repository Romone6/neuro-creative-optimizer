import { render, screen } from "@testing-library/react";

import { SignalInspectorRail, type SignalMetric } from "@/components/signal-inspector-rail";

const signals: SignalMetric[] = [
  {
    id: "trust",
    label: "Trust",
    value: 0.78,
    confidence: 0.71,
    delta: 0.08,
    interpretation: "Credibility is elevated by concrete phrasing.",
    evidence: ["This offer is specific and credible."],
    revision: ["Add one more concrete proof point to stabilize trust."],
  },
  {
    id: "tension",
    label: "Tension",
    value: 0.61,
    confidence: 0.64,
    delta: -0.02,
    interpretation: "The current pacing creates moderate forward pull.",
    evidence: ["Why wait?"],
    revision: ["Shorten the close to make the tension resolve faster."],
  },
];

describe("SignalInspectorRail", () => {
  it("renders all signals while exposing the selected signal detail", () => {
    render(<SignalInspectorRail signals={signals} selectedSignalId="trust" onSelectSignal={() => undefined} />);

    expect(screen.getByText("All Signals")).toBeInTheDocument();
    expect(screen.getAllByText("Trust")).toHaveLength(2);
    expect(screen.getByText("Tension")).toBeInTheDocument();
    expect(screen.getByText("Credibility is elevated by concrete phrasing.")).toBeInTheDocument();
    expect(screen.getByText("Signal")).toBeInTheDocument();
    expect(screen.getByText("Evidence")).toBeInTheDocument();
    expect(screen.getByText("Revision")).toBeInTheDocument();
  });
});
