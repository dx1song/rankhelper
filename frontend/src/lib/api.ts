import type {
  AimAnalysisResponse,
  ManualImportPayload,
  PlanResponse,
  PlayerRank,
} from "../types"

const BASE_URL = import.meta.env.VITE_API_BASE_URL || ""

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })
  if (!resp.ok) {
    const body = await resp.text().catch(() => "")
    throw new Error(body || `请求失败（HTTP ${resp.status}）`)
  }
  return resp.json() as Promise<T>
}

export function importManual(payload: ManualImportPayload): Promise<PlayerRank> {
  return request<PlayerRank>("/api/player/manual", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export function getAimAnalysis(riotId: string): Promise<AimAnalysisResponse> {
  return request<AimAnalysisResponse>("/api/analysis/aim", {
    method: "POST",
    body: JSON.stringify({ riot_id: riotId }),
  })
}

export function getPlan(riotId: string): Promise<PlanResponse> {
  return request<PlanResponse>("/api/analysis/plan", {
    method: "POST",
    body: JSON.stringify({ riot_id: riotId }),
  })
}
