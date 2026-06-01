const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type ApiResult<T> = {
  data: T;
  error: string | null;
};

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { next: { revalidate: 30 } });
  if (!res.ok) throw new Error(`API request failed: ${res.status}`);
  return res.json();
}

export async function apiGetOrFallback<T>(path: string, fallback: T): Promise<ApiResult<T>> {
  try {
    return { data: await apiGet<T>(path), error: null };
  } catch (error) {
    const message = error instanceof Error ? error.message : "API request failed";
    console.error(`Unable to fetch ${path}: ${message}`);
    return { data: fallback, error: message };
  }
}

export async function uploadDeliveryFile(file: File) {
  const data = new FormData();
  data.append("file", file);
  const res = await fetch(`${API_BASE}/api/v1/uploads/delivery-data`, { method: "POST", body: data });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
