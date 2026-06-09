"use client"

import { Scatter, ScatterChart as RechartsScatter, CartesianGrid, XAxis, YAxis, Tooltip } from "recharts"
import {
  ChartContainer,
  type ChartConfig,
} from "@/components/ui/chart"
import { formatCurrency } from "@/lib/utils"

interface ScatterDataPoint {
  x: number
  y: number
  label: string
  category?: string
}

interface ScatterChartProps {
  dataPoints: ScatterDataPoint[]
  xLabel?: string
  yLabel?: string
  title?: string
  height?: number
}

const COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
]

export function RechartsScatterChart({
  dataPoints,
  xLabel = "X",
  yLabel = "Y",
  height = 300,
}: ScatterChartProps) {
  const chartConfig: ChartConfig = {
    products: { label: "Products", color: "var(--chart-1)" },
  }

  const chartData = dataPoints.map((p) => ({
    x: p.x,
    y: p.y,
    label: p.label,
    category: p.category,
  }))

  return (
    <ChartContainer config={chartConfig} className="w-full" style={{ height }}>
      <RechartsScatter data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          type="number"
          dataKey="x"
          name={xLabel}
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          tickFormatter={(v: number) => formatCurrency(v)}
        />
        <YAxis
          type="number"
          dataKey="y"
          name={yLabel}
          tickLine={false}
          axisLine={false}
          tickMargin={8}
        />
        <Tooltip
          cursor={{ strokeDasharray: "3 3" }}
          content={({ active, payload }) => {
            if (!active || !payload?.length) return null
            const data = payload[0].payload
            return (
              <div className="border-border/50 bg-background grid min-w-[8rem] items-start gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs shadow-xl">
                <p className="font-medium text-foreground">{data.label}</p>
                <p className="text-muted-foreground">
                  {xLabel}: {formatCurrency(data.x)}
                </p>
                <p className="text-muted-foreground">
                  {yLabel}: {data.y.toLocaleString()}
                </p>
              </div>
            )
          }}
        />
        <Scatter
          data={chartData}
          fill={COLORS[0]}
          stroke={COLORS[0]}
          strokeWidth={0.5}
        />
      </RechartsScatter>
    </ChartContainer>
  )
}
