import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart as RechartsRadar,
  ResponsiveContainer,
} from "recharts"
import type { RadarData } from "../types"

// 单系列：用 dataviz 参考调色板的蓝色系
const SERIES = "#2a78d6"
const GRID = "#e1e0d9"
const MUTED = "#898781"

const DIMENSIONS: { key: keyof RadarData; label: string }[] = [
  { key: "tap", label: "Tap" },
  { key: "spray", label: "Spray" },
  { key: "utility", label: "Utility" },
  { key: "positioning", label: "Positioning" },
  { key: "consistency", label: "Consistency" },
]

export default function RadarChart({ data }: { data: RadarData }) {
  const rows = DIMENSIONS.map((d) => ({ dimension: d.label, value: data[d.key] }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsRadar data={rows} cx="50%" cy="50%" outerRadius="72%">
        <PolarGrid stroke={GRID} />
        <PolarAngleAxis dataKey="dimension" tick={{ fill: MUTED, fontSize: 12 }} />
        <PolarRadiusAxis domain={[0, 100]} tick={{ fill: MUTED, fontSize: 10 }} />
        <Radar
          dataKey="value"
          stroke={SERIES}
          fill={SERIES}
          fillOpacity={0.1}
          strokeWidth={2}
        />
      </RechartsRadar>
    </ResponsiveContainer>
  )
}
