"use client"

import { useState } from "react"
import { formatCurrency } from "@/lib/utils"

interface HeatmapCell {
  row: string
  col: string
  value: number
}

interface HeatmapChartProps {
  rows: string[]
  cols: string[]
  data: HeatmapCell[]
  height?: number
  colorScale?: [string, string] // [minColor, maxColor]
}

export function RechartsHeatmapChart({
  rows, cols, data, height = 320,
  colorScale = ["var(--chart-5)", "var(--chart-1)"],
}: HeatmapChartProps) {
  const maxVal = Math.max(...data.map((d) => d.value), 1)
  const [tooltip, setTooltip] = useState<{ row: string; col: string; value: number } | null>(null)

  const getColor = (value: number) => {
    const ratio = value / maxVal
    return `color-mix(in srgb, ${colorScale[0]} ${(1 - ratio) * 100}%, ${colorScale[1]} ${ratio * 100}%)`
  }

  const cellSize = Math.min(
    Math.max(40, (600) / cols.length - 4),
    80
  )

  return (
    <div className="relative" style={{ height: Math.max(height, rows.length * (cellSize + 4) + 40) }}>
      <div className="flex items-end gap-0.5">
        {/* Row labels column */}
        <div style={{ width: 100, minWidth: 100 }}>
          <div style={{ height: 30 }} />
          {rows.map((row) => (
            <div key={row} style={{ height: cellSize, lineHeight: `${cellSize}px` }}
              className="truncate pr-2 text-right text-xs text-muted-foreground">
              {row}
            </div>
          ))}
        </div>
        {/* Grid */}
        <div className="overflow-x-auto">
          {/* Column headers */}
          <div className="flex gap-0.5" style={{ height: 30 }}>
            {cols.map((col) => (
              <div key={col} style={{ width: cellSize, minWidth: cellSize }}
                className="truncate text-center text-xs text-muted-foreground">
                {col.length > 8 ? col.slice(0, 6) + "…" : col}
              </div>
            ))}
          </div>
          {/* Cells */}
          {rows.map((row) => (
            <div key={row} className="flex gap-0.5">
              {cols.map((col) => {
                const cell = data.find((d) => d.row === row && d.col === col)
                const val = cell?.value ?? 0
                return (
                  <div key={`${row}-${col}`} style={{ width: cellSize, height: cellSize, minWidth: cellSize }}
                    className="flex items-center justify-center rounded-sm text-[10px] font-medium transition-opacity hover:opacity-80 cursor-default"
                    title={`${row} / ${col}: ${formatCurrency(val)}`}
                    onMouseEnter={() => setTooltip({ row, col, value: val })}
                    onMouseLeave={() => setTooltip(null)}
                    style={{ backgroundColor: getColor(val) }}>
                    <span className="drop-shadow-lg" style={{ color: val > maxVal * 0.6 ? "white" : "var(--foreground)" }}>
                      {val > 0 ? (val > 1_000_000 ? `${(val / 1_000_000).toFixed(0)}M` : val > 1_000 ? `${(val / 1_000).toFixed(0)}K` : val.toFixed(0)) : ""}
                    </span>
                  </div>
                )
              })}
            </div>
          ))}
        </div>
      </div>
      {tooltip && (
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full mt-1 border-border/50 bg-background rounded-lg border px-3 py-1.5 text-xs shadow-xl whitespace-nowrap z-50">
          <span className="font-medium">{tooltip.row}</span> / <span className="font-medium">{tooltip.col}</span>: {formatCurrency(tooltip.value)}
        </div>
      )}
      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-2 text-xs text-muted-foreground">
        <span>Low</span>
        <div className="flex h-3 w-24 rounded-sm" style={{ background: `linear-gradient(to right, ${colorScale[0]}, ${colorScale[1]})` }} />
        <span>High</span>
      </div>
    </div>
  )
}
