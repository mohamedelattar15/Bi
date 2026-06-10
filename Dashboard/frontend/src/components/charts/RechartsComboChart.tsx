"use client"

import { Bar, BarChart, Line, ComposedChart, CartesianGrid, XAxis, YAxis } from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import { formatCurrency } from "@/lib/utils"

interface ComboChartProps {
  labels: string[]
  bars: Array<{ label: string; data: number[]; color?: string }>
  lines: Array<{ label: string; data: number[]; color?: string }>
  height?: number
  xLabel?: string
}

export function RechartsComboChart({
  labels,
  bars,
  lines,
  height = 320,
}: ComboChartProps) {
  const chartData = labels.map((label, i) => {
    const point: Record<string, string | number> = { label }
    bars.forEach((b) => { point[b.label] = b.data[i] ?? 0 })
    lines.forEach((l) => { point[l.label] = l.data[i] ?? 0 })
    return point
  })

  const chartConfig: ChartConfig = {}
  bars.forEach((b, i) => {
    chartConfig[b.label] = { label: b.label, color: b.color || `var(--chart-${(i % 5) + 1})` }
  })
  lines.forEach((l, i) => {
    chartConfig[l.label] = { label: l.label, color: l.color || `var(--chart-${((i + bars.length) % 5) + 1})` }
  })

  return (
    <ChartContainer config={chartConfig} className="w-full" style={{ height }}>
      <ComposedChart data={chartData}>
        <CartesianGrid vertical={false} strokeDasharray="3 3" />
        <XAxis dataKey="label" tickLine={false} axisLine={false} tickMargin={8}
          tickFormatter={(v: string) => v?.length > 10 ? v.slice(0, 10) + "…" : v} />
        <YAxis yAxisId="left" tickLine={false} axisLine={false} tickMargin={8} width={60} />
        <YAxis yAxisId="right" orientation="right" tickLine={false} axisLine={false} tickMargin={8} width={60} />
        <ChartTooltip cursor={false} content={<ChartTooltipContent indicator="dot" formatter={(v: number) => formatCurrency(v)} />} />
        {bars.map((b, i) => (
          <Bar key={b.label} yAxisId="left" dataKey={b.label} fill={b.color || `var(--chart-${(i % 5) + 1})`} radius={[4, 4, 0, 0]} barSize={24} />
        ))}
        {lines.map((l, i) => (
          <Line key={l.label} yAxisId="right" type="monotone" dataKey={l.label}
            stroke={l.color || `var(--chart-${((i + bars.length) % 5) + 1})`}
            strokeWidth={2} dot={{ r: 3 }} />
        ))}
      </ComposedChart>
    </ChartContainer>
  )
}
