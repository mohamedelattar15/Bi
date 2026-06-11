"use client"

import { Bar, Line, ComposedChart, CartesianGrid, XAxis, YAxis, Legend } from "recharts"
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
  /** Optional label for the left Y-axis (bar values) */
  leftLabel?: string
  /** Optional label for the right Y-axis (line values) */
  rightLabel?: string
}

/** Abbreviate large numbers for axis ticks: 1_000_000_000 → "1B" */
function compactAxisValue(value: number): string {
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(1)}B`;
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toLocaleString();
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

  /** Custom tooltip formatter — shows percentage for Growth % line, currency for bars */
  const tooltipFormatter = (value: number, name: string) => {
    if (name === "Growth %") {
      const sign = value >= 0 ? "+" : "";
      const label = `${sign}${value.toFixed(1)}%`;
      return label;
    }
    return formatCurrency(value);
  };

  return (
    <ChartContainer config={chartConfig} className="w-full" style={{ height }}>
      <ComposedChart data={chartData} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
        <CartesianGrid vertical={false} strokeDasharray="3 3" />
        <XAxis dataKey="label" tickLine={false} axisLine={false} tickMargin={8}
          tickFormatter={(v: string) => v?.length > 8 ? v.slice(0, 8) + "…" : v} />
        {/* Left axis — bar values (currency, compact) */}
        <YAxis yAxisId="left" tickLine={false} axisLine={false} tickMargin={8}
          width={70} tickFormatter={compactAxisValue}
          domain={['auto', 'auto']} />
        {/* Right axis — line values (percentage) */}
        <YAxis yAxisId="right" orientation="right" tickLine={false} axisLine={false}
          tickMargin={8} width={50}
          tickFormatter={(v: number) => `${v.toFixed(0)}%`}
          domain={['auto', 'auto']} />
        <ChartTooltip cursor={false}
          content={<ChartTooltipContent indicator="dot" formatter={tooltipFormatter} />} />
        <Legend
          verticalAlign="bottom"
          align="center"
          iconType="rect"
          formatter={(value: string) => (
            <span className="text-sm font-medium text-muted-foreground">{value}</span>
          )}
        />
        {bars.map((b, i) => (
          <Bar key={b.label} yAxisId="left" dataKey={b.label}
            fill={b.color || `var(--chart-${(i % 5) + 1})`}
            radius={[4, 4, 0, 0]} barSize={24} />
        ))}
        {lines.map((l, i) => (
          <Line key={l.label} yAxisId="right" type="monotone" dataKey={l.label}
            stroke={l.color || `var(--chart-${((i + bars.length) % 5) + 1})`}
            strokeWidth={2.5} dot={{ r: 3 }}
            // Color each dot green/red based on positive/negative value
            dot={(props: any) => {
              const { cx, cy, payload, dataKey } = props;
              const val = payload?.[dataKey as string] as number ?? 0;
              const fill = val >= 0 ? "#22c55e" : "#ef4444";
              return <circle cx={cx} cy={cy} r={4} fill={fill} stroke="none" />;
            }}
          />
        ))}
      </ComposedChart>
    </ChartContainer>
  )
}
