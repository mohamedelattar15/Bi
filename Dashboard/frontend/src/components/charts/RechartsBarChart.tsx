"use client"

import { Bar, BarChart as RechartsBar, CartesianGrid, XAxis, YAxis } from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import { formatCurrency } from "@/lib/utils"

interface BarChartProps {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    color?: string
  }>
  title?: string
  height?: number
  horizontal?: boolean
}

export function RechartsBarChart({
  labels,
  datasets,
  height = 300,
  horizontal = false,
}: BarChartProps) {
  const chartData = labels.map((label, i) => {
    const point: Record<string, string | number> = { label }
    datasets.forEach((ds) => {
      point[ds.label] = ds.data[i] ?? 0
    })
    return point
  })

  const chartConfig: ChartConfig = {}
  datasets.forEach((ds, i) => {
    const colorKey = `--chart-${(i % 5) + 1}`
    chartConfig[ds.label] = {
      label: ds.label,
      color: ds.color || `var(${colorKey})`,
    }
  })

  const barColors = datasets.map((ds, i) =>
    ds.color || `var(--chart-${(i % 5) + 1})`
  )

  return (
    <ChartContainer config={chartConfig} className="w-full" style={{ height }}>
      <RechartsBar data={chartData} layout={horizontal ? "vertical" : "horizontal"}>
        <CartesianGrid vertical={!horizontal} horizontal={horizontal} strokeDasharray="3 3" />
        {horizontal ? (
          <>
            <XAxis type="number" tickLine={false} axisLine={false} tickMargin={8} width={60} />
            <YAxis
              type="category"
              dataKey="label"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              width={100}
              tickFormatter={(value: string) => value?.length > 12 ? value.slice(0, 12) + "…" : value}
            />
          </>
        ) : (
          <>
            <XAxis dataKey="label" tickLine={false} axisLine={false} tickMargin={8} />
            <YAxis tickLine={false} axisLine={false} tickMargin={8} width={60} />
          </>
        )}
        <ChartTooltip
          cursor={false}
          content={
            <ChartTooltipContent
              indicator="dot"
              formatter={(value: number) => formatCurrency(value)}
            />
          }
        />
        {datasets.map((ds, i) => (
          <Bar
            key={ds.label}
            dataKey={ds.label}
            fill={barColors[i]}
            radius={[4, 4, 0, 0]}
            barSize={24}
          />
        ))}
      </RechartsBar>
    </ChartContainer>
  )
}
