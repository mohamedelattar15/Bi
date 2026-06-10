"use client"

import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Cell } from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import { formatCurrency } from "@/lib/utils"

interface WaterfallItem {
  label: string
  value: number
  isTotal?: boolean
  isNegative?: boolean
}

interface WaterfallChartProps {
  data: WaterfallItem[]
  height?: number
}

export function RechartsWaterfallChart({ data, height = 320 }: WaterfallChartProps) {
  let runningTotal = 0
  const chartData = data.map((d) => {
    if (d.isTotal) {
      return { label: d.label, value: d.value, fill: "var(--chart-1)" }
    }
    if (d.isNegative) {
      runningTotal -= d.value
      return { label: d.label, value: -d.value, fill: "var(--chart-3)" }
    }
    const start = runningTotal
    runningTotal += d.value
    return { label: d.label, value: d.value, fill: "var(--chart-2)" }
  })

  const chartConfig: ChartConfig = {
    value: { label: "Value", color: "var(--chart-1)" },
  }

  return (
    <ChartContainer config={chartConfig} className="w-full" style={{ height }}>
      <BarChart data={chartData}>
        <CartesianGrid vertical={false} strokeDasharray="3 3" />
        <XAxis dataKey="label" tickLine={false} axisLine={false} tickMargin={8}
          tickFormatter={(v: string) => v?.length > 10 ? v.slice(0, 10) + "…" : v} />
        <YAxis tickLine={false} axisLine={false} tickMargin={8} width={60} />
        <ChartTooltip cursor={false} content={<ChartTooltipContent indicator="dot" formatter={(v: number) => formatCurrency(Math.abs(v))} />} />
        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
          {chartData.map((entry, i) => (
            <Cell key={i} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ChartContainer>
  )
}
