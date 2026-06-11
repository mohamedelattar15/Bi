"use client"

import { Pie, PieChart, Cell } from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  type ChartConfig,
} from "@/components/ui/chart"
import { formatCurrency } from "@/lib/utils"

interface DoughnutChartProps {
  labels: string[]
  data: number[]
  title?: string
  height?: number
  formatValues?: boolean
}

const CHART_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
]

export function RechartsDoughnutChart({
  labels,
  data: values,
  height = 300,
  formatValues = false,
}: DoughnutChartProps) {
  const total = values.reduce((s, v) => s + v, 0);

  const chartData = labels.map((label, i) => ({
    name: label,
    value: values[i] ?? 0,
    pct: total > 0 ? ((values[i] ?? 0) / total * 100) : 0,
  }))

  const chartConfig: ChartConfig = {}
  labels.forEach((label, i) => {
    chartConfig[label] = {
      label,
      color: CHART_COLORS[i % CHART_COLORS.length],
    }
  })

  /** Custom tooltip that always shows the segment name */
  function CustomTooltip({ active, payload }: any) {
    if (!active || !payload?.length) return null;
    const entry = payload[0];
    const name = entry.name;
    const value = entry.value as number;
    const pct = entry.payload.pct as number;
    const formatted = formatValues ? formatCurrency(value) : value.toLocaleString();
    const color = entry.payload.fill || CHART_COLORS[0];
    return (
      <div className="border-border/50 bg-background grid min-w-[8rem] items-start gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs shadow-xl">
        <div className="font-medium text-foreground">{name}</div>
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full" style={{ background: color }} />
          <span className="text-muted-foreground">{formatted}</span>
          <span className="text-muted-foreground">({pct.toFixed(1)}%)</span>
        </div>
      </div>
    );
  }

  return (
    <ChartContainer config={chartConfig} className="w-full" style={{ height }}>
      <PieChart>
        <ChartTooltip content={<CustomTooltip />} />
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          innerRadius={50}
          outerRadius={110}
          strokeWidth={2}
          stroke="var(--background)"
          paddingAngle={2}
        >
          {chartData.map((entry, i) => (
            <Cell key={entry.name} fill={CHART_COLORS[i % CHART_COLORS.length]} />
          ))}
        </Pie>
      </PieChart>
    </ChartContainer>
  )
}
