"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { cn, formatTimestamp, statusLabel } from "@/lib/utils";
import { getJob } from "@/lib/api";

interface Segment {
  start: number;
  end: number;
  speaker: string;
  text: string;
}

interface JobData {
  id: string;
  original_filename: string;
  status: string;
  created_at: string;
  updated_at: string;
  error?: string;
  metadata?: {
    duration_seconds?: number;
    segments?: Segment[];
  } | null;
}

export default function JobDetailPage() {
  const params = useParams();
  const jobId = params.id as string;

  const [job, setJob] = useState<JobData | null>(null);
  const [polling, setPolling] = useState(true);
  const [activeSpeaker, setActiveSpeaker] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const fetchJob = useCallback(async () => {
    try {
      const data = await getJob(jobId);
      setJob(data);

      const terminal = ["completed", "failed"];
      if (terminal.includes(data.status)) {
        setPolling(false);
      }
    } catch {
      // backend no disponible aún
    }
  }, [jobId]);

  useEffect(() => {
    fetchJob();
    if (!polling) return;
    const interval = setInterval(fetchJob, 3000);
    return () => clearInterval(interval);
  }, [fetchJob, polling]);

  const segments: Segment[] =
    job?.metadata?.segments || [];

  const speakers = Array.from(
    new Set(segments.map((s) => s.speaker))
  );

  const filteredSegments = search
    ? segments.filter((s) =>
        s.text.toLowerCase().includes(search.toLowerCase())
      )
    : segments;

  const activeSegments = activeSpeaker
    ? filteredSegments.filter((s) => s.speaker === activeSpeaker)
    : filteredSegments;

  if (!job) {
    return (
      <div className="min-h-screen bg-zinc-950 text-zinc-100 flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-2 border-zinc-600 border-t-blue-400 rounded-full" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 sticky top-0 backdrop-blur-sm z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <Link href="/" className="text-zinc-400 hover:text-zinc-200 text-sm transition-colors">
              &larr; Volver
            </Link>
            <h1 className="text-lg font-semibold mt-1">{job.original_filename}</h1>
          </div>
          <StatusBadge status={job.status} />
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {/* Error */}
        {job.status === "failed" && (
          <div className="mb-8 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
            <p className="font-medium">Error al procesar</p>
            <p className="text-sm mt-1">{job.error || "Error desconocido"}</p>
          </div>
        )}

        {/* Progreso */}
        {job.status !== "completed" && job.status !== "failed" && (
          <div className="mb-8">
            <div className="flex items-center gap揃3 mb-2">
              <div className="animate-spin h-4 w-4 border-2 border-zinc-600 border-t-blue-400 rounded-full" />
              <span className="text-sm text-zinc-400">{statusLabel(job.status)}</span>
            </div>
            <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 rounded-full animate-pulse w-2/3" />
            </div>
          </div>
        )}

        {/* Transcripción completada */}
        {job.status === "completed" && segments.length > 0 && (
          <>
            {/* Toolbar */}
            <div className="flex flex-wrap gap-4 mb-6 items-center justify-between">
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={() => setActiveSpeaker(null)}
                  className={cn(
                    "px-3 py-1.5 rounded-md text-xs font-medium transition-colors",
                    !activeSpeaker
                      ? "bg-zinc-700 text-white"
                      : "bg-zinc-800 text-zinc-400 hover:text-zinc-200"
                  )}
                >
                  Todos ({segments.length})
                </button>
                {speakers.map((spk) => {
                  const count = segments.filter((s) => s.speaker === spk).length;
                  return (
                    <button
                      key={spk}
                      onClick={() =>
                        setActiveSpeaker(activeSpeaker === spk ? null : spk)
                      }
                      className={cn(
                        "px-3 py-1.5 rounded-md text-xs font-medium transition-colors",
                        activeSpeaker === spk
                          ? "bg-blue-600 text-white"
                          : "bg-zinc-800 text-zinc-400 hover:text-zinc-200"
                      )}
                    >
                      {spk} ({count})
                    </button>
                  );
                })}
              </div>

              <input
                type="text"
                placeholder="Buscar en la transcripci&oacute;n..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="px-3 py-1.5 rounded-md text-xs bg-zinc-800 border border-zinc-700 text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-zinc-500 w-64"
              />
            </div>

            {/* Segmentos */}
            <div className="space-y-1">
              {activeSegments.map((seg, i) => (
                <div
                  key={i}
                  className={cn(
                    "group flex gap-4 px-4 py-3 rounded-lg transition-colors hover:bg-zinc-900/50",
                    activeSpeaker === seg.speaker && "bg-zinc-900/30"
                  )}
                >
                  <span className="text-xs text-zinc-500 font-mono w-14 shrink-0 pt-0.5">
                    {formatTimestamp(seg.start)}
                  </span>
                  <div className="flex-1 min-w-0">
                    <span
                      className={cn(
                        "text-xs font-semibold mr-2 px-1.5 py-0.5 rounded",
                        speakerColor(seg.speaker)
                      )}
                    >
                      {seg.speaker}
                    </span>
                    <span className="text-sm text-zinc-300 leading-relaxed">
                      {seg.text}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {activeSegments.length === 0 && (
              <p className="text-center text-zinc-500 py-12">
                No se encontraron segmentos
              </p>
            )}
          </>
        )}

        {/* Completed pero sin segmentos */}
        {job.status === "completed" && segments.length === 0 && (
          <div className="text-center text-zinc-500 py-12">
            <p className="text-lg">No se detectaron segmentos de habla</p>
            <p className="text-sm mt-2">El audio podr&iacute;a estar vac&iacute;o o ser inaudible</p>
          </div>
        )}
      </main>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    pending: "bg-zinc-800 text-zinc-400",
    extracting_audio: "bg-yellow-900/30 text-yellow-400",
    transcribing: "bg-blue-900/30 text-blue-400",
    diarizing: "bg-purple-900/30 text-purple-400",
    aligning: "bg-indigo-900/30 text-indigo-400",
    completed: "bg-green-900/30 text-green-400",
    failed: "bg-red-900/30 text-red-400",
  };

  return (
    <span
      className={cn(
        "px-2.5 py-1 rounded-md text-xs font-medium",
        colors[status] || colors.pending
      )}
    >
      {statusLabel(status)}
    </span>
  );
}

function speakerColor(speaker: string): string {
  const palettes = [
    "bg-blue-900/40 text-blue-300",
    "bg-green-900/40 text-green-300",
    "bg-amber-900/40 text-amber-300",
    "bg-purple-900/40 text-purple-300",
    "bg-pink-900/40 text-pink-300",
    "bg-cyan-900/40 text-cyan-300",
    "bg-orange-900/40 text-orange-300",
    "bg-lime-900/40 text-lime-300",
  ];
  const idx = (speaker.charCodeAt(speaker.length - 1) || 0) % palettes.length;
  return palettes[idx];
}
