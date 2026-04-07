"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { BrainCanvas3D } from "@/components/brain-canvas-3d";
import { SignalInspectorRail } from "@/components/signal-inspector-rail";
import {
  fetchBrainMesh,
  type BrainMeshData,
  type SignalMetric,
  type WorkspaceResult,
} from "@/lib/api";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export function NeuroWorkspaceShell() {
  const [projectId, setProjectId] = useState("Project 1");
  const [content, setContent] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "assistant-0",
      role: "assistant",
      content:
        "I'm ready to help you analyze and optimize your creative content. What would you like to create today?",
    },
  ]);
  const [result, setResult] = useState<WorkspaceResult | null>(null);
  const [selectedSignalId, setSelectedSignalId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [brainMeshData, setBrainMeshData] = useState<BrainMeshData | null>(null);
  const [isLoadingMesh, setIsLoadingMesh] = useState(true);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

  const handleSaveProject = useCallback(() => {
    const projectData = {
      projectId,
      messages,
      result,
      savedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(projectData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${projectId.replace(/\s+/g, "_")}_project.json`;
    a.click();
    URL.revokeObjectURL(url);
    setMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: "assistant", content: `Project "${projectId}" saved successfully.` },
    ]);
  }, [projectId, messages, result]);

  const handleLoadProject = useCallback(() => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      try {
        const text = await file.text();
        const data = JSON.parse(text);
        if (data.projectId) setProjectId(data.projectId);
        if (data.messages) setMessages(data.messages);
        if (data.result) setResult(data.result);
        setMessages((current) => [
          ...current,
          { id: crypto.randomUUID(), role: "assistant", content: `Project "${data.projectId}" loaded successfully.` },
        ]);
      } catch (err) {
        setErrorMessage("Failed to load project file");
      }
    };
    input.click();
  }, []);

  const handleRemoveFile = useCallback(() => {
    setUploadedFiles([]);
  }, []);

  const handleDeleteMessage = useCallback((messageId: string) => {
    setMessages((current) => current.filter((m) => m.id !== messageId));
  }, []);

  useEffect(() => {
    async function loadBrainMesh() {
      try {
        const mesh = await fetchBrainMesh("both", "fsaverage5");
        setBrainMeshData(mesh);
      } catch (error) {
        console.error("Failed to load brain mesh:", error);
      } finally {
        setIsLoadingMesh(false);
      }
    }
    loadBrainMesh();
  }, []);

  const signals: SignalMetric[] = result?.signals ?? [];
  const selectedSignalIdResolved = selectedSignalId ?? signals[0]?.id ?? null;
  const headerStatus = isSubmitting
    ? "Running analysis"
    : result
      ? "Analysis complete"
      : "Ready";

  async function handleSendMessage() {
    if (isSubmitting) return;
    if (!content.trim() && uploadedFiles.length === 0) return;

    let contentType = "text";
    let fileToAnalyze: File | undefined;
    
    if (uploadedFiles.length > 0) {
      const file = uploadedFiles[0];
      contentType = file.type.startsWith("audio") ? "audio" : "video";
      fileToAnalyze = file;
    }

    const userMessage = content || `Analyzing ${contentType} file: ${fileToAnalyze?.name || "uploaded file"}`;
    setMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: "user", content: userMessage },
    ]);
    setContent("");
    setUploadedFiles([]);
    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      let response;
      
      if (fileToAnalyze) {
        const formData = new FormData();
        formData.append("project_id", projectId);
        formData.append("content_type", contentType);
        formData.append("title", fileToAnalyze.name);
        formData.append("audience", JSON.stringify({ label: "General audience", platform_context: "general", target_goals: [] }));
        formData.append("file", fileToAnalyze);
        
        const endpoint = contentType === "audio" ? "/v1/analyze/audio/file" : "/v1/analyze/video";
        response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}${endpoint}`, {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/v1/analyze/text/brain-activation`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            project_id: projectId,
            content_type: "speech",
            title: "Chat analysis",
            body: userMessage,
            audience: { label: "General audience", platform_context: "general", target_goals: [] },
          }),
        });
      }

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Analysis failed: ${response.status} - ${errorText}`);
      }

      const analysis = await response.json();
      setResult(analysis);
      setSelectedSignalId(analysis.analysis?.analysis_run?.score_vector?.scores?.[0]?.dimension ?? null);
      
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: `I've processed your ${contentType} content. The neural response analysis is complete. The 3D brain model now shows activation patterns mapped to brain regions based on your target audience.`,
        },
      ]);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Analysis failed";
      setErrorMessage(message);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: `Sorry, I couldn't process that: ${message}`,
        },
      ]);
    } finally {
      setIsSubmitting(false);
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <main className="flex min-h-screen flex-col px-5 py-5 text-slate-50">
      <div className="glass-panel mx-auto flex min-h-[calc(100vh-2.5rem)] w-full max-w-[1680px] flex-1 flex-col overflow-hidden rounded-[2.5rem] border border-white/10">
        <header className="flex items-center gap-4 border-b border-white/8 px-6 py-4">
          <div className="min-w-[14rem]">
            <p className="signal-label text-[10px] text-cyan-100/55">Workspace</p>
            <h1 className="text-lg font-medium text-slate-50">Neuro Creative Optimizer</h1>
          </div>

          <label className="min-w-[12rem] flex-1">
            <span className="mb-1 block text-[11px] text-slate-400">Project</span>
            <div className="flex items-center gap-2">
              <input
                value={projectId}
                onChange={(event) => setProjectId(event.target.value)}
                className="flex-1 rounded-full border border-white/8 bg-white/[0.03] px-4 py-2.5 text-sm text-slate-100 outline-none transition focus:border-cyan-200/20"
              />
              <button
                type="button"
                onClick={handleSaveProject}
                className="rounded-full border border-white/8 bg-white/[0.03] px-3 py-2 text-xs text-slate-400 hover:text-slate-200"
                title="Save project"
              >
                💾
              </button>
              <button
                type="button"
                onClick={handleLoadProject}
                className="rounded-full border border-white/8 bg-white/[0.03] px-3 py-2 text-xs text-slate-400 hover:text-slate-200"
                title="Load project"
              >
                📂
              </button>
            </div>
          </label>

          <div className="ml-auto flex items-center gap-3">
            <div className="rounded-full border border-white/8 bg-white/[0.03] px-4 py-2 text-xs text-slate-300">
              {headerStatus}
            </div>
          </div>
        </header>

        <section className="flex flex-1 gap-5 px-5 py-5">
          <div className="flex-1">
            <BrainCanvas3D
              meshData={brainMeshData}
              signals={signals}
              selectedSignalId={selectedSignalIdResolved}
              onSelectSignal={setSelectedSignalId}
              statusLabel={headerStatus}
              summary={result?.summary}
              runtimeLabel={result?.runtimeLabel}
              isLoading={isLoadingMesh}
            />
          </div>
          <div className="w-96 shrink-0">
            <SignalInspectorRail
              signals={signals.map((signal) => ({
                id: signal.id,
                label: signal.label,
                value: signal.value,
                confidence: signal.confidence,
                delta: signal.delta,
                interpretation: signal.interpretation,
                evidence: signal.evidence,
                revision: signal.revision,
              }))}
              selectedSignalId={selectedSignalIdResolved}
              onSelectSignal={setSelectedSignalId}
              sourceExcerpt={result?.sourceExcerpt}
              runSummary={result?.detailSummary}
            />
          </div>
        </section>

        <section className="operator-composer border-t border-white/8 px-5 pb-5 pt-4">
          <div className="glass-panel flex max-h-[20rem] flex-col rounded-[2rem] border border-white/8">
            <div className="flex-1 overflow-auto p-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className="group relative mb-3 flex"
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
                      message.role === "assistant"
                        ? "bg-white/[0.03] border border-white/8 text-slate-300"
                        : "bg-cyan-100/[0.08] border border-cyan-200/10 text-slate-100 ml-auto"
                    }`}
                  >
                    <p>{message.content}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleDeleteMessage(message.id)}
                    className="absolute -top-2 -right-2 hidden rounded-full bg-slate-700 p-1 text-xs text-slate-400 opacity-0 transition hover:bg-slate-600 group-hover:opacity-100"
                  >
                    ✕
                  </button>
                </div>
              ))}
              {isSubmitting && (
                <div className="mb-3 flex">
                  <div className="rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3 text-sm text-slate-400">
                    <span className="animate-pulse">Analyzing...</span>
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center gap-3 border-t border-white/8 px-4 py-3">
              <label className="cursor-pointer rounded-full p-2 text-slate-400 hover:bg-white/10 hover:text-slate-200">
                <input
                  type="file"
                  className="hidden"
                  accept="audio/*,video/*"
                  multiple
                  onChange={(e) => {
                    if (e.target.files) {
                      setUploadedFiles(Array.from(e.target.files));
                    }
                  }}
                />
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </label>
              {uploadedFiles.length > 0 && (
                <div className="flex gap-2">
                  {uploadedFiles.map((file, i) => (
                    <span key={i} className="flex items-center gap-1 rounded-full bg-cyan-100/20 px-2 py-1 text-xs text-cyan-50">
                      {file.type.startsWith("audio") ? "🎵" : "🎬"} {file.name.slice(0, 10)}...
                      <button type="button" onClick={() => setUploadedFiles([])} className="ml-1">✕</button>
                    </span>
                  ))}
                </div>
              )}
              <input
                type="text"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Describe what you want to create and who it's for..."
                className="flex-1 rounded-full border border-white/8 bg-white/[0.03] px-4 py-2 text-sm text-slate-100 outline-none transition focus:border-cyan-200/20"
              />
              <button
                type="button"
                onClick={handleSendMessage}
                disabled={isSubmitting || (!content.trim() && uploadedFiles.length === 0)}
                className="rounded-full bg-cyan-300 px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:bg-cyan-100/60"
              >
                Send
              </button>
            </div>
          </div>

          {errorMessage ? (
            <div className="mt-4 rounded-2xl border border-rose-300/12 bg-rose-100/[0.06] px-4 py-3 text-sm text-rose-100/78">
              {errorMessage}
            </div>
          ) : null}
        </section>
      </div>
    </main>
  );
}
