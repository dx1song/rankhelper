import { useEffect, useState, type ReactNode } from "react"
import { useLocation, useSearchParams } from "react-router-dom"
import { getAimAnalysis, getPlan } from "../lib/api"
import type { AimAnalysisResponse, PlanResponse, PlayerRank } from "../types"
import RadarChart from "../components/RadarChart"

type LoadState<T> =
  | { status: "loading" }
  | { status: "ok"; data: T }
  | { status: "error"; message: string }

function Loading() {
  return (
    <div className="flex h-64 items-center justify-center text-sm text-muted-foreground">
      加载中…
    </div>
  )
}

function Banner({ children, tone = "warning" }: { children: ReactNode; tone?: "warning" | "muted" }) {
  const cls =
    tone === "warning"
      ? "border-amber-300 bg-amber-50 text-amber-800"
      : "border-border bg-muted/50 text-muted-foreground"
  return <div className={`rounded-md border px-3 py-2 text-sm ${cls}`}>{children}</div>
}

function Result() {
  const [params] = useSearchParams()
  const riotId = params.get("riot_id") || ""
  const location = useLocation()
  const rank = (location.state as { rank?: PlayerRank } | null)?.rank

  const [aim, setAim] = useState<LoadState<AimAnalysisResponse>>({ status: "loading" })
  const [plan, setPlan] = useState<LoadState<PlanResponse>>({ status: "loading" })

  useEffect(() => {
    if (!riotId) return
    getAimAnalysis(riotId)
      .then((d) => setAim({ status: "ok", data: d }))
      .catch((e) => setAim({ status: "error", message: String(e) }))
    getPlan(riotId)
      .then((d) => setPlan({ status: "ok", data: d }))
      .catch((e) => setPlan({ status: "error", message: String(e) }))
  }, [riotId])

  const matchCount = aim.status === "ok" ? aim.data.match_count : null
  const aiFootnote =
    matchCount != null
      ? `AI 教练建议，基于最近 ${matchCount} 场竞技对局`
      : "AI 教练建议，基于最近竞技对局"
  const aimUnavailable =
    aim.status === "ok" && aim.data.aim_style_analysis.confidence_note === "AI 分析不可用"

  return (
    <main className="mx-auto max-w-4xl space-y-6 p-4">
      {/* 顶部：段位 + RR */}
      <section className="flex items-center justify-between rounded-lg border p-4">
        <div>
          <p className="text-sm text-muted-foreground">当前段位</p>
          <h1 className="text-3xl font-bold">{rank?.current_rank || "—"}</h1>
          {rank && <p className="text-xs text-muted-foreground">巅峰 {rank.peak_rank}</p>}
        </div>
        <div className="text-right">
          <p className="text-sm text-muted-foreground">当前 RR</p>
          <p className="text-4xl font-bold tabular-nums">{rank?.current_rr ?? "—"}</p>
        </div>
      </section>

      {/* 降级提示条 */}
      {plan.status === "ok" && plan.data.fallback && (
        <Banner>AI 提升方案不可用，已显示规则兜底方案</Banner>
      )}
      {aimUnavailable && <Banner>AI 瞄准分析不可用，雷达图为默认值</Banner>}

      {/* 瞄准风格雷达 */}
      <section className="rounded-lg border p-4">
        <h2 className="mb-2 font-semibold">瞄准风格</h2>
        {aim.status === "ok" ? (
          <>
            <RadarChart data={aim.data.radar} />
            <p className="mt-2 text-xs text-muted-foreground">{aiFootnote}</p>
          </>
        ) : aim.status === "error" ? (
          <p className="text-sm text-muted-foreground">分析失败：{aim.message}</p>
        ) : (
          <Loading />
        )}
      </section>

      {/* 本周提升方案 */}
      <section>
        <h2 className="mb-3 font-semibold">本周提升方案</h2>
        {plan.status === "ok" ? (
          <>
            <p className="mb-3 text-sm">{plan.data.improvement_plan.weekly_focus}</p>
            <div className="grid gap-4 md:grid-cols-2">
              {plan.data.improvement_plan.drills.map((d) => (
                <div key={d.name} className="rounded-lg border p-4">
                  <h3 className="font-semibold">{d.name}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{d.description}</p>
                  <div className="mt-2 text-xs text-muted-foreground">
                    <span>{d.frequency}</span>
                    <span className="mx-1">·</span>
                    <span>{d.metric_to_track}</span>
                  </div>
                </div>
              ))}
            </div>
            <p className="mt-4 text-xs text-muted-foreground">{aiFootnote}</p>
          </>
        ) : plan.status === "error" ? (
          <p className="text-sm text-muted-foreground">方案加载失败：{plan.message}</p>
        ) : (
          <Loading />
        )}
      </section>
    </main>
  )
}

export default Result
