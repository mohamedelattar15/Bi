"use client"

import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import { formatCurrency } from "@/lib/utils"

interface StackedBarChartProps {
  labels: string[]
  categories: Array<{ label: string; data: number[]; color?: string }>
  height?: number
  horizontal?: boolean
}

export function RechartsStackedBarChart({
  labels, categories, height = 320, horizontal = false,
}: StackedBarChartProps) {
  const chartData = labels.map((label, i) => {
    const point: Record<string, string | number> = { label }
    categories.forEach((c) => { point[c.label] = c.data[i] ?? 0 })
    return point
  })

  const chartConfig: ChartConfig = {}
  categories.forEach((c, i) => {
    chartConfig[c.label] = { label: c.label, color: c.color || `var(--chart-${(i % 5) + 1})` }
  })

  return (
    <ChartContainer config={chartConfig} className="w-full" style={{ height }}>
      <BarChart data={chartData} layout={horizontal ? "vertical" : "horizontal"}>
        <CartesianGrid vertical={!horizontal} horizontal={horizontal} strokeDasharray="3 3" />
        {horizontal ? (
          <>
            <XAxis type="number" tickLine={false} axisLine={false} width={60} />
            <YAxis type="category" dataKey="label" tickLine={false} axisLine={false} width={100}
              tickFormatter={(v: string) => v?.length > 12 ? v.slice(0, 12) + "…" : v} />
          </>
        ) : (
          <>
            <XAxis dataKey="label" tickLine={false} axisLine={false} tickMargin={8} />
            <YAxis tickLine={false} axisLine={false} tickMargin={8} width={60} />
          </>
        )}
        <ChartTooltip cursor={false} content={<ChartTooltipContent indicator="dot" formatter={(v: number) => formatCurrency(v)} />} />
        {categories.map((c, i) => (
          <Bar key={c.label} dataKey={c.label} stackId="a" fill={c.color || `var(--chart-${(i % 5) + 1})`} radius={i === categories.length - 1 ? [4, 4, 0, 0] : undefined} />
        ))}
      </BarChart>
    </ChartContainer>
  )
}
