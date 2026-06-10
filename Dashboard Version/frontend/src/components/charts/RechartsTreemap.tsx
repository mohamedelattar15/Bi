"use client"

import { Treemap, ResponsiveContainer, Tooltip } from "recharts"
import { formatCurrency } from "@/lib/utils"

interface TreemapItem {
  name: string
  value: number
  color?: string
}

interface TreemapChartProps {
  data: TreemapItem[]
  height?: number
}

const COLORS = [
  "var(--chart-1)", "var(--chart-2)", "var(--chart-3)",
  "var(--chart-4)", "var(--chart-5)", "var(--chart-1)",
  "var(--chart-2)", "var(--chart-3)", "var(--chart-4)",
  "var(--chart-5)", "var(--chart-1)",
]

export function RechartsTreemapChart({ data, height = 320 }: TreemapChartProps) {
  const treeData = data.map((d, i) => ({
    name: d.name,
    size: d.value,
    fill: d.color || COLORS[i % COLORS.length],
  }))

  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer>
        <Treemap data={treeData} dataKey="size" aspectRatio={4 / 3} stroke="var(--background)" strokeWidth={2}>
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null
              const d = payload[0].payload
              return (
                <div className="border-border/50 bg-background grid min-w-[8rem] items-start gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs shadow-xl">
                  <p className="font-medium text-foreground">{d.name}</p>
                  <p className="text-muted-foreground">{formatCurrency(d.value)}</p>
                </div>
              )
            }}
          />
        </Treemap>
      </ResponsiveContainer>
    </div>
  )
}
