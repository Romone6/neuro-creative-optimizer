"use client";

import { useCallback, useMemo, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import {
  OrbitControls,
  Html,
  useCursor,
} from "@react-three/drei";
import * as THREE from "three";

import type { BrainMeshData, SignalMetric } from "@/lib/api";

type BrainCanvas3DProps = {
  meshData: BrainMeshData | null;
  signals: SignalMetric[];
  selectedSignalId: string | null;
  onSelectSignal: (signalId: string) => void;
  statusLabel: string;
  summary?: string;
  runtimeLabel?: string;
  isLoading?: boolean;
};

const ROI_TO_SIGNAL_MAP: Record<string, string> = {
  frontal: "trust",
  parietal: "attention_focus",
  temporal: "clarity",
  occipital: "visual_imagery",
  cingulate: "tension",
  insula: "emotional_engagement",
  amygdala: "urgency",
  hippocampus: "memorability",
  putamen: "reward_response",
  caudate: "decision_confidence",
};

function getHeatColor(value: number): THREE.Color {
  if (value >= 0.7) {
    return new THREE.Color(0.93, 0.27, 0.27);
  } else if (value >= 0.4) {
    return new THREE.Color(0.98, 0.75, 0.14);
  } else if (value >= 0.2) {
    return new THREE.Color(0.38, 0.65, 0.98);
  }
  return new THREE.Color(0.3, 0.3, 0.35);
}

function BrainMesh({
  meshData,
  signals,
  selectedSignalId,
  onSelectSignal,
}: {
  meshData: BrainMeshData;
  signals: SignalMetric[];
  selectedSignalId: string | null;
  onSelectSignal: (signalId: string) => void;
}) {
  const [hoveredRoi, setHoveredRoi] = useState<string | null>(null);
  useCursor(hoveredRoi !== null, "pointer", "auto");

  const geometry = useMemo(() => {
    const vertices = meshData.vertices.map((v) => new THREE.Vector3(v.x, v.y, v.z));
    const indices = meshData.faces.flatMap((f) => [f.a, f.b, f.c]);

    const positionArray = new Float32Array(vertices.length * 3);
    vertices.forEach((v, i) => {
      positionArray[i * 3] = v.x;
      positionArray[i * 3 + 1] = v.y;
      positionArray[i * 3 + 2] = v.z;
    });

    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(positionArray, 3));
    geo.setIndex(indices);
    geo.computeVertexNormals();

    return geo;
  }, [meshData]);

  const colors = useMemo(() => {
    const colorArray = new Float32Array(meshData.vertices.length * 3);
    const baseColor = new THREE.Color(0.35, 0.38, 0.42);
    const activationMap: Record<string, number> = {};

    signals.forEach((signal) => {
      for (const [roi, signalId] of Object.entries(ROI_TO_SIGNAL_MAP)) {
        if (signalId === signal.id) {
          activationMap[roi] = signal.value;
          break;
        }
      }
    });

    meshData.vertices.forEach((_, i) => {
      let activation = 0;
      for (const roi of meshData.rois) {
        if (roi.vertex_indices.includes(i) && activationMap[roi.name] !== undefined) {
          activation = Math.max(activation, activationMap[roi.name]);
          break;
        }
      }

      const color = activation > 0 ? getHeatColor(activation) : baseColor;
      colorArray[i * 3] = color.r;
      colorArray[i * 3 + 1] = color.g;
      colorArray[i * 3 + 2] = color.b;
    });

    return colorArray;
  }, [meshData, signals]);

  const [hoveredVertex, setHoveredVertex] = useState<number | null>(null);

  const handleClick = useCallback(
    (event: THREE.Event) => {
      if (hoveredRoi) {
        const signalId = ROI_TO_SIGNAL_MAP[hoveredRoi];
        if (signalId) {
          onSelectSignal(signalId);
        }
      }
    },
    [hoveredRoi, onSelectSignal]
  );

  return (
    <group>
      <mesh geometry={geometry} onClick={handleClick}>
        <bufferAttribute
          attach="attributes-color"
          args={[colors, 3]}
        />
        <meshStandardMaterial
          vertexColors
          roughness={0.6}
          metalness={0.1}
          side={THREE.DoubleSide}
        />
      </mesh>

      {meshData.rois.map((roi, idx) => {
        const signalId = ROI_TO_SIGNAL_MAP[roi.name];
        const signal = signals.find((s) => s.id === signalId);
        const isSelected = signalId === selectedSignalId;
        const isHovered = hoveredRoi === roi.name;

        return (
          <group key={`${roi.name}-${idx}`} position={[roi.center.x, roi.center.y, roi.center.z]}>
            <mesh
              onPointerOver={(e) => {
                e.stopPropagation();
                setHoveredRoi(roi.name);
              }}
              onPointerOut={() => setHoveredRoi(null)}
            >
              <sphereGeometry args={[isHovered || isSelected ? 3 : 2, 16, 16]} />
              <meshStandardMaterial
                color={isSelected ? "#ffffff" : isHovered ? "#aaffaa" : "#444444"}
                emissive={isSelected ? "#44ff88" : isHovered ? "#22ff22" : "#000000"}
                emissiveIntensity={isSelected || isHovered ? 0.5 : 0}
                transparent
                opacity={isHovered || isSelected ? 0.9 : 0}
              />
            </mesh>
            {(isHovered || isSelected) && (
              <Html position={[0, 5, 0]} center>
                <div
                  className={`px-3 py-2 rounded-lg text-xs font-mono whitespace-nowrap ${
                    isSelected
                      ? "bg-cyan-500/90 text-white"
                      : "bg-slate-800/90 text-slate-200"
                  }`}
                >
                  <div className="font-semibold">{roi.label}</div>
                  {signal && (
                    <div className="text-[10px] opacity-80">
                      {signal.label}: {signal.value.toFixed(2)}
                    </div>
                  )}
                </div>
              </Html>
            )}
          </group>
        );
      })}
    </group>
  );
}

function RotatingBrain({
  meshData,
  signals,
  selectedSignalId,
  onSelectSignal,
}: {
  meshData: BrainMeshData;
  signals: SignalMetric[];
  selectedSignalId: string | null;
  onSelectSignal: (signalId: string) => void;
}) {
  const groupRef = useRef<THREE.Group>(null);

  const centroid = useMemo(() => {
    if (!meshData.vertices.length) return { x: 0, y: 0, z: 0 };
    let sumX = 0, sumY = 0, sumZ = 0;
    for (const v of meshData.vertices) {
      sumX += v.x;
      sumY += v.y;
      sumZ += v.z;
    }
    const count = meshData.vertices.length;
    return { x: sumX / count, y: sumY / count, z: sumZ / count };
  }, [meshData.vertices]);

  useFrame((state) => {
    if (groupRef.current && signals.length === 0) {
      groupRef.current.rotation.y += 0.002;
    }
  });

  return (
    <group ref={groupRef} position={[-centroid.x, -centroid.y, -centroid.z]}>
      <BrainMesh
        meshData={meshData}
        signals={signals}
        selectedSignalId={selectedSignalId}
        onSelectSignal={onSelectSignal}
      />
    </group>
  );
}

function importRef<T>(...refs: (React.RefObject<T> | undefined)[]) {
  return refs[0];
}

export function BrainCanvas3D({
  meshData,
  signals,
  selectedSignalId,
  onSelectSignal,
  statusLabel,
  summary,
  runtimeLabel,
  isLoading,
}: BrainCanvas3DProps) {
  const isStandby = signals.length === 0 && !isLoading;

  return (
    <section className="glass-panel scan-grid relative min-h-[38rem] overflow-hidden rounded-[2.4rem] px-6 py-6">
      <div className="relative z-10 flex items-start justify-between gap-6 mb-4">
        <div className="max-w-md space-y-3">
          <p className="signal-label text-[10px] text-cyan-100/55">{statusLabel}</p>
          <h1 className="text-[clamp(2rem,4vw,3.5rem)] font-light tracking-[-0.04em] text-slate-50">
            Neural Response Model
          </h1>
          <p className="max-w-xl text-sm leading-6 text-slate-300/72">
            {summary ?? "Loading brain mesh data..."}
          </p>
        </div>
        <div className="rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-xs text-slate-300">
          {runtimeLabel ?? "Awaiting analysis"}
        </div>
      </div>

      <div className="relative z-10 h-[28rem] w-full">
        {isLoading && !meshData ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
              <div className="h-12 w-12 animate-spin rounded-full border-2 border-cyan-500/30 border-t-cyan-400" />
              <p className="text-sm text-slate-400">Loading brain mesh...</p>
            </div>
          </div>
        ) : meshData ? (
          <Canvas camera={{ position: [0, 0, 120], fov: 45 }}>
            <ambientLight intensity={0.4} />
            <pointLight position={[50, 50, 50]} intensity={1} color="#ffffff" />
            <pointLight position={[-50, -50, -50]} intensity={0.5} color="#88ccff" />
            <RotatingBrain
              meshData={meshData}
              signals={signals}
              selectedSignalId={selectedSignalId}
              onSelectSignal={onSelectSignal}
            />
            <OrbitControls
              enablePan={true}
              enableZoom={true}
              enableRotate={true}
              minDistance={50}
              maxDistance={250}
              autoRotate={signals.length === 0}
              autoRotateSpeed={0.5}
            />
          </Canvas>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-sm text-slate-400">No mesh data available</p>
          </div>
        )}
      </div>

      {!isStandby && !isLoading && (
        <div className="absolute inset-x-0 bottom-0 grid grid-cols-2 gap-3 px-6 pb-6 xl:grid-cols-3">
          {signals.map((signal) => (
            <button
              key={signal.id}
              type="button"
              onClick={() => onSelectSignal(signal.id)}
              className={`rounded-2xl border px-3 py-3 text-left backdrop-blur-md transition ${
                signal.id === selectedSignalId
                  ? "border-cyan-400/50 bg-cyan-950/58"
                  : "border-white/10 bg-slate-950/58 hover:border-cyan-100/18"
              }`}
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

      {isStandby && !isLoading && (
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
    </section>
  );
}