"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { cn, formatBytes } from "@/lib/utils";
import { uploadFile } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const handleFile = useCallback((f: File) => {
    const allowed = [".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".mp3", ".wav", ".m4a", ".ogg", ".flac"];
    const ext = "." + f.name.split(".").pop()?.toLowerCase();
    if (!allowed.includes(ext)) {
      setError(`Formato no soportado: ${ext}. Formatos: ${allowed.join(", ")}`);
      return;
    }
    setError("");
    setFile(f);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  }, [handleFile]);

  const handleSubmit = async () => {
    if (!file) return;
    setUploading(true);
    setError("");

    try {
      const { job_id } = await uploadFile(file);
      router.push(`/job/${job_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            Transcripci&oacute;n de Audiencias
          </h1>
          <p className="text-zinc-400">
            Sube un video o audio de la audiencia. El sistema transcribir&aacute; y
            detectar&aacute; autom&aacute;ticamente qui&eacute;n habla en cada momento.
          </p>
        </div>

        <div
          className={cn(
            "relative border-2 border-dashed rounded-xl p-12 text-center transition-colors cursor-pointer",
            dragOver
              ? "border-blue-400 bg-blue-400/10"
              : "border-zinc-700 hover:border-zinc-500 bg-zinc-900/50"
          )}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => document.getElementById("file-input")?.click()}
        >
          <input
            id="file-input"
            type="file"
            className="hidden"
            accept="video/*,audio/*,.mp4,.mov,.avi,.mkv,.webm,.m4v,.mp3,.wav,.m4a,.ogg,.flac"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) handleFile(f);
            }}
          />

          {file ? (
            <div className="space-y-2">
              <div className="text-4xl">&#x1F3A6;</div>
              <p className="text-lg font-medium text-zinc-100">{file.name}</p>
              <p className="text-sm text-zinc-400">{formatBytes(file.size)}</p>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="text-5xl">&#x2B07;&#xFE0F;</div>
              <p className="text-zinc-300">
                Arrastra un archivo aqu&iacute; o haz clic para seleccionar
              </p>
              <p className="text-xs text-zinc-500">
                MP4, MOV, AVI, MKV, WebM, MP3, WAV, M4A, OGG, FLAC
              </p>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">
            {error}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={!file || uploading}
          className={cn(
            "mt-6 w-full py-3 px-4 rounded-lg font-medium text-sm transition-colors",
            file && !uploading
              ? "bg-blue-600 hover:bg-blue-500 text-white cursor-pointer"
              : "bg-zinc-800 text-zinc-500 cursor-not-allowed"
          )}
        >
          {uploading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              Subiendo...
            </span>
          ) : (
            "Iniciar Transcripci&oacute;n"
          )}
        </button>
      </div>
    </div>
  );
}
