"use client"

import { Area, AreaChart as RechartsArea, CartesianGrid, XAxis, YAxis } from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"

interface AreaChartProps {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    color?: string
  }>
  title?: string
  height?: number
}

export function RechartsAreaChart({
  labels,
  datasets,
  height = 300,
}: AreaChartProps) {
  const chartData = labels.map((label, i) => {
    const point: Record<string, string | number> = { label }
    datasets.forEach((ds) => {
      point[ds.label] = ds.data[i] ?? 0
    })
    return point
  })

  const chartConfig: ChartConfig = {}
  datasets.forEach((ds) => {
    chartConfig[ds.label] = {
      label: ds.label,
      color: ds.color || "var(--chart-1)",
    }
  })

  return (
    <ChartContainer config={chartConfig} className="w-full" style={{ height }}>
      <RechartsArea data={chartData}>
        <defs>
          {datasets.map((ds) => (
            <linearGradient key={ds.label} id={`fill${ds.label.replace(/\s/g, "")}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={ds.color || "var(--color-desktop, var(--chart-1))"} stopOpacity={0.3} />
              <stop offset="95%" stopColor={ds.color || "var(--color-desktop, var(--chart-1))"} stopOpacity={0.05} />
            </linearGradient>
          ))}
        </defs>
        <CartesianGrid vertical={false} strokeDasharray="3 3" />
        <XAxis
          dataKey="label"
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          tickFormatter={(value) => value?.length > 10 ? value.slice(0, 10) + "…" : value}
        />
        <YAxis tickLine={false} axisLine={false} tickMargin={8} width={60} />
        <ChartTooltip
          cursor={false}
          content={<ChartTooltipContent indicator="dot" />}
        />
        {datasets.map((ds) => (
          <Area
            key={ds.label}
            type="monotone"
            dataKey={ds.label}
            fill={`url(#fill${ds.label.replace(/\s/g, "")})`}
            stroke={ds.color || "var(--color-desktop, var(--chart-1))"}
            strokeWidth={2}
            stackId={datasets.length > 1 ? "a" : undefined}
          />
        ))}
      </RechartsArea>
    </ChartContainer>
  )
}
