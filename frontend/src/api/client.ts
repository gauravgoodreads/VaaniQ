import type { HealthResponse, VersionResponse } from "@/types/api";

function apiBaseUrl(): string {
  const raw = import.meta.env.VITE_API_BASE_URL;
  if (typeof raw === "string" && raw.trim().length > 0) {
    return raw.replace(/\/$/, "");
  }
  return "http://127.0.0.1:8000";
}

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new ApiError(`Request failed: ${path}`, response.status);
  }
  return (await response.json()) as T;
}

/** Live liveness probe against the FastAPI backend (ROADMAP-007 / REQ-134). */
export function fetchHealth(): Promise<HealthResponse> {
  return getJson<HealthResponse>("/health");
}

export function fetchVersion(): Promise<VersionResponse> {
  return getJson<VersionResponse>("/api/v1/version");
}

export { apiBaseUrl };
