const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function uploadFile(file: File): Promise<{ job_id: string; status: string; original_filename: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.detail || "Error al subir el archivo");
  }

  return res.json();
}

export async function getJob(jobId: string) {
  const res = await fetch(`${API_URL}/api/jobs/${jobId}`);
  if (!res.ok) throw new Error("Job no encontrado");
  return res.json();
}

export async function listJobs() {
  const res = await fetch(`${API_URL}/api/jobs`);
  if (!res.ok) throw new Error("Error al listar jobs");
  return res.json();
}
