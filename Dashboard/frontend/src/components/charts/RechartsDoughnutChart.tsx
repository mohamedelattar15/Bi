"use client"

import { Pie, PieChart, Cell } from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
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
  const chartData = labels.map((label, i) => ({
    name: label,
    value: values[i] ?? 0,
  }))

  const chartConfig: ChartConfig = {}
  labels.forEach((label, i) => {
    chartConfig[label] = {
      label,
      color: CHART_COLORS[i % CHART_COLORS.length],
    }
  })

  return (
    <ChartContainer config={chartConfig} className="w-full" style={{ height }}>
      <PieChart>
        <ChartTooltip
          content={
            <ChartTooltipContent
              indicator="dot"
              formatter={(value: number) =>
                formatValues ? formatCurrency(value) : value.toLocaleString()
              }
            />
          }
        />
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
