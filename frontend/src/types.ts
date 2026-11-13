// 与后端固定数据契约对齐的类型定义

export interface PlayerRank {
  riot_id: string
  current_rank: string
  current_rr: number
  peak_rank: string
  region: string
  cached: boolean
  stale: boolean
}

export interface ManualMatch {
  date: string
  map: string
  agent: string
  result: string
  kills: number
  deaths: number
  assists: number
  hs_pct: number
  adr: number
}

export interface ManualImportPayload {
  riot_id: string
  current_rank: string
  current_rr: number
  peak_rank: string
  matches: ManualMatch[]
}

export type PrimaryStyle =
  | "tap_headhunter"
  | "spray_transfer"
  | "op_holder"
  | "utility_anchor"
  | "mixed"

export interface AimStyleAnalysis {
  primary_style: PrimaryStyle
  hs_pct_benchmark: string
  strengths: string[]
  weaknesses: string[]
  confidence_note: string
}

export interface RadarData {
  tap: number
  spray: number
  utility: number
  positioning: number
  consistency: number
}

export interface AimAnalysisResponse {
  aim_style_analysis: AimStyleAnalysis
  radar: RadarData
  match_count: number
}

export interface Drill {
  name: string
  description: string
  frequency: string
  metric_to_track: string
}

export interface ImprovementPlan {
  weekly_focus: string
  drills: Drill[]
  next_5_games_goal: string
  warning: string
}

export interface PlanResponse {
  improvement_plan: ImprovementPlan
  fallback: boolean
}
