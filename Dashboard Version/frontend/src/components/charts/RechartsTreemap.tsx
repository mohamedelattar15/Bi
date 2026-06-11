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

/** Custom treemap content that shows the city name + value on each rectangle */
function TreemapContent({ root, depth, x, y, width, height, index, payload, colors, name }: any) {
  if (depth > 0 && width > 30 && height > 25) {
    const fill = payload?.fill || COLORS[(index || 0) % COLORS.length];
    const shortName = name?.length > 12 ? name.slice(0, 12) + "…" : name;
    return (
      <g>
        <rect x={x} y={y} width={width} height={height} fill={fill} rx={4} ry={4} />
        <text x={x + width / 2} y={y + height / 2 - 6} textAnchor="middle" fill="white"
          fontSize={height > 50 ? 13 : 10} fontWeight={600}
          style={{ pointerEvents: "none" }}>
          {shortName}
        </text>
        <text x={x + width / 2} y={y + height / 2 + 10} textAnchor="middle" fill="rgba(255,255,255,0.8)"
          fontSize={height > 50 ? 11 : 9}
          style={{ pointerEvents: "none" }}>
          {payload?.size ? formatCurrency(payload.size) : ""}
        </text>
      </g>
    );
  }
  return <rect x={x} y={y} width={width} height={height} fill="transparent" />;
}

export function RechartsTreemapChart({ data, height = 320 }: TreemapChartProps) {
  const treeData = data.map((d, i) => ({
    name: d.name,
    size: d.value,
    fill: d.color || COLORS[i % COLORS.length],
  }))

  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer>
        <Treemap data={treeData} dataKey="size" aspectRatio={4 / 3}
          stroke="var(--background)" strokeWidth={2}
          content={<TreemapContent />}>
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
