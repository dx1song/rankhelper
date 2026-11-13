import { useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom"
import { importManual } from "../lib/api"
import type { ManualMatch } from "../types"

const RIOT_ID_RE = /^[^#\s]+#[^#\s]+$/

const inputCls = "w-full rounded-md border px-3 py-2 text-sm"

interface MatchForm {
  date: string
  map: string
  agent: string
  result: string
  kills: string
  deaths: string
  assists: string
  hs_pct: string
  adr: string
}

const EMPTY_MATCH: MatchForm = {
  date: "",
  map: "",
  agent: "",
  result: "win",
  kills: "",
  deaths: "",
  assists: "",
  hs_pct: "",
  adr: "",
}

function Home() {
  const navigate = useNavigate()
  const [riotId, setRiotId] = useState("")
  const [currentRank, setCurrentRank] = useState("")
  const [currentRR, setCurrentRR] = useState("")
  const [peakRank, setPeakRank] = useState("")
  const [matches, setMatches] = useState<MatchForm[]>([{ ...EMPTY_MATCH }])
  const [error, setError] = useState("")
  const [submitting, setSubmitting] = useState(false)

  function updateMatch(i: number, key: keyof MatchForm, value: string) {
    setMatches((prev) => prev.map((m, idx) => (idx === i ? { ...m, [key]: value } : m)))
  }

  function addMatch() {
    setMatches((prev) => [...prev, { ...EMPTY_MATCH }])
  }

  function removeMatch(i: number) {
    setMatches((prev) => prev.filter((_, idx) => idx !== i))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const id = riotId.trim()
    if (!RIOT_ID_RE.test(id)) {
      setError("请输入 xxx#tag 格式的 Riot ID（例如 Player#1234）")
      return
    }
    const rr = Number(currentRR)
    if (!currentRank.trim() || !peakRank.trim() || Number.isNaN(rr)) {
      setError("请填写当前段位、巅峰段位和当前 RR")
      return
    }

    const parsed: ManualMatch[] = matches.map((m) => ({
      date: m.date.trim(),
      map: m.map.trim(),
      agent: m.agent.trim(),
      result: m.result,
      kills: Number(m.kills) || 0,
      deaths: Number(m.deaths) || 0,
      assists: Number(m.assists) || 0,
      hs_pct: Number(m.hs_pct) || 0,
      adr: Number(m.adr) || 0,
    }))
    if (parsed.some((m) => !m.date || !m.map || !m.agent)) {
      setError("每场对局请至少填写日期、地图、英雄")
      return
    }

    setSubmitting(true)
    setError("")
    try {
      const rank = await importManual({
        riot_id: id,
        current_rank: currentRank.trim(),
        current_rr: rr,
        peak_rank: peakRank.trim(),
        matches: parsed,
      })
      navigate(`/result?riot_id=${encodeURIComponent(id)}`, { state: { rank } })
    } catch (err) {
      setError(String(err))
      setSubmitting(false)
    }
  }

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-4">
      <div>
        <h1 className="text-2xl font-bold">无畏契约上分辅导 · 国服</h1>
        <p className="text-sm text-muted-foreground">
          手动录入排位数据，获取 AI 瞄准分析与提升方案
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <section className="space-y-3 rounded-lg border p-4">
          <h2 className="font-semibold">基础信息</h2>
          <input
            placeholder="Riot ID（如 Player#1234）"
            value={riotId}
            onChange={(e) => setRiotId(e.target.value)}
            className={inputCls}
          />
          <div className="grid grid-cols-3 gap-3">
            <input
              placeholder="当前段位（如 钻石1）"
              value={currentRank}
              onChange={(e) => setCurrentRank(e.target.value)}
              className={inputCls}
            />
            <input
              placeholder="当前 RR"
              type="number"
              value={currentRR}
              onChange={(e) => setCurrentRR(e.target.value)}
              className={inputCls}
            />
            <input
              placeholder="巅峰段位"
              value={peakRank}
              onChange={(e) => setPeakRank(e.target.value)}
              className={inputCls}
            />
          </div>
        </section>

        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold">最近对局</h2>
            <button
              type="button"
              onClick={addMatch}
              className="rounded-md border px-3 py-1 text-sm"
            >
              + 加一场
            </button>
          </div>

          {matches.map((m, i) => (
            <div key={i} className="space-y-2 rounded-lg border p-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">第 {i + 1} 场</span>
                {matches.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeMatch(i)}
                    className="text-xs text-muted-foreground hover:text-red-500"
                  >
                    删除
                  </button>
                )}
              </div>
              <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
                <input
                  placeholder="日期（如 11-12）"
                  value={m.date}
                  onChange={(e) => updateMatch(i, "date", e.target.value)}
                  className={inputCls}
                />
                <input
                  placeholder="地图"
                  value={m.map}
                  onChange={(e) => updateMatch(i, "map", e.target.value)}
                  className={inputCls}
                />
                <input
                  placeholder="英雄"
                  value={m.agent}
                  onChange={(e) => updateMatch(i, "agent", e.target.value)}
                  className={inputCls}
                />
                <select
                  value={m.result}
                  onChange={(e) => updateMatch(i, "result", e.target.value)}
                  className={inputCls}
                >
                  <option value="win">胜</option>
                  <option value="loss">负</option>
                </select>
                <input
                  placeholder="击杀"
                  type="number"
                  value={m.kills}
                  onChange={(e) => updateMatch(i, "kills", e.target.value)}
                  className={inputCls}
                />
                <input
                  placeholder="死亡"
                  type="number"
                  value={m.deaths}
                  onChange={(e) => updateMatch(i, "deaths", e.target.value)}
                  className={inputCls}
                />
                <input
                  placeholder="助攻"
                  type="number"
                  value={m.assists}
                  onChange={(e) => updateMatch(i, "assists", e.target.value)}
                  className={inputCls}
                />
                <input
                  placeholder="爆头率 %"
                  type="number"
                  value={m.hs_pct}
                  onChange={(e) => updateMatch(i, "hs_pct", e.target.value)}
                  className={inputCls}
                />
                <input
                  placeholder="ADR"
                  type="number"
                  value={m.adr}
                  onChange={(e) => updateMatch(i, "adr", e.target.value)}
                  className={inputCls}
                />
              </div>
            </div>
          ))}
        </section>

        {error && <p className="text-sm text-red-500">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-primary px-4 py-2 text-primary-foreground"
        >
          {submitting ? "提交中…" : "提交并分析"}
        </button>
      </form>
    </main>
  )
}

export default Home
