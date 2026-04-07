import { render, screen } from "@testing-library/react";

import { NeuroWorkspaceShell } from "@/components/neuro-workspace-shell";

describe("NeuroWorkspaceShell", () => {
  it("renders the operator-first standby layout", () => {
    render(<NeuroWorkspaceShell />);

    expect(screen.getByText("Neuro Creative Optimizer")).toBeInTheDocument();
    expect(screen.getByText("Operator Console")).toBeInTheDocument();
    expect(screen.getAllByText("Baseline text analysis ready")).toHaveLength(2);
    expect(screen.getByText("No verified TRIBE run loaded.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyze" })).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Operator prompt" })).toBeInTheDocument();
  });
});
