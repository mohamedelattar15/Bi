"use client"

import { Bar, BarChart as RechartsBar, Cell, CartesianGrid, XAxis, YAxis } from "recharts"
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
  /** When true, colors each bar green (≥0) or red (<0) based on its value */
  colorByValue?: boolean
}

export function RechartsBarChart({
  labels,
  datasets,
  height = 300,
  horizontal = false,
  colorByValue = false,
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

  /** Tooltip formatter: show % for MoM Growth, currency otherwise */
  const tooltipFormatter = (value: number, name: string) => {
    if (name === "MoM Growth %") {
      const color = value >= 0 ? "#22c55e" : "#ef4444";
      const sign = value >= 0 ? "+" : "";
      return <span style={{ color }}>{sign}{value.toFixed(1)}%</span>;
    }
    return formatCurrency(value);
  };

  return (
    <ChartContainer config={chartConfig} className="w-full" style={{ height }}>
      <RechartsBar data={chartData} layout={horizontal ? "vertical" : "horizontal"}>
        <CartesianGrid vertical={!horizontal} horizontal={horizontal} strokeDasharray="3 3" />
        {horizontal ? (
          <>
            <XAxis type="number" tickLine={false} axisLine={false} tickMargin={8} width={60}
              tickFormatter={(v: number) => {
                if (v >= 1_000_000_000) return `${(v / 1_000_000_000).toFixed(1)}B`;
                if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
                if (v >= 1_000) return `${(v / 1_000).toFixed(1)}K`;
                return v.toLocaleString();
              }} />
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
            <YAxis tickLine={false} axisLine={false} tickMargin={8} width={65}
              tickFormatter={(v: number) => {
                if (colorByValue) return `${v.toFixed(0)}%`;
                if (v >= 1_000_000_000) return `${(v / 1_000_000_000).toFixed(1)}B`;
                if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
                if (v >= 1_000) return `${(v / 1_000).toFixed(1)}K`;
                return v.toLocaleString();
              }} />
          </>
        )}
        <ChartTooltip
          cursor={false}
          content={
            <ChartTooltipContent
              indicator="dot"
              formatter={tooltipFormatter}
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
          >
            {colorByValue && chartData.map((entry: any, idx: number) => (
              <Cell key={`cell-${idx}`}
                fill={entry[ds.label] >= 0 ? "#22c55e" : "#ef4444"} />
            ))}
          </Bar>
        ))}
      </RechartsBar>
    </ChartContainer>
  )
}
