"use client"

import { useMemo } from "react"

interface LinkNode {
  id: string
  label: string
  size: number       // connection count
  group: number      // hub group (0 = hub, 1+ = match)
}

interface LinkEdge {
  source: string
  target: string
  strength: number   // lift value for thickness
}

interface LinkChartProps {
  nodes: LinkNode[]
  edges: LinkEdge[]
  width?: number
  height?: number
}

const COLORS = [
  "#6366f1", // indigo
  "#f59e0b", // amber
  "#10b981", // emerald
  "#ef4444", // red
  "#3b82f6", // blue
  "#8b5cf6", // violet
  "#ec4899", // pink
  "#14b8a6", // teal
  "#f97316", // orange
  "#06b6d4", // cyan
]

/**
 * Simple circular-link chart that renders a knowledge-graph style
 * visualization of product connections.
 *
 * Hub products are placed evenly on a circle. Their matches orbit
 * close to their hub. Edges connect hubs to their matches with
 * thickness proportional to lift.
 */
export function RechartsLinkChart({
  nodes,
  edges,
  width = 500,
  height = 400,
}: LinkChartProps) {
  const cx = width / 2
  const cy = height / 2
  const radius = Math.min(cx, cy) - 60

  // Assign positions: hubs on a circle, matches near their hub
  const positions = useMemo(() => {
    const pos: Record<string, { x: number; y: number }> = {}
    const hubIds = nodes.filter((n) => n.group === 0).map((n) => n.id)
    const hubCount = hubIds.length
    const matchR = radius * 0.35 // match orbit radius

    hubIds.forEach((id, i) => {
      const angle = (2 * Math.PI * i) / hubCount - Math.PI / 2
      pos[id] = { x: cx + radius * Math.cos(angle), y: cy + radius * Math.sin(angle) }

      // Place matches near this hub
      const matchNodes = nodes.filter((n) => n.group === i + 1)
      matchNodes.forEach((m, mi) => {
        const spread = matchNodes.length > 1 ? (2 * Math.PI * mi) / matchNodes.length : 0
        pos[m.id] = {
          x: pos[id].x + matchR * Math.cos(spread + angle * 0.5),
          y: pos[id].y + matchR * Math.sin(spread + angle * 0.5),
        }
      })
    })

    return pos
  }, [nodes, cx, cy, radius])

  // Scale node sizes
  const maxSize = Math.max(...nodes.map((n) => n.size), 1)
  const minSize = Math.min(...nodes.map((n) => n.size), 1)

  return (
    <svg width={width} height={height} className="overflow-visible">
      {/* Background */}
      <rect width={width} height={height} fill="transparent" rx={8} />

      {/* Edges */}
      {edges.map((e, i) => {
        const from = positions[e.source]
        const to = positions[e.target]
        if (!from || !to) return null
        const strokeW = Math.max(1, (e.strength / 0.4) * 4)
        return (
          <line
            key={`edge-${i}`}
            x1={from.x}
            y1={from.y}
            x2={to.x}
            y2={to.y}
            stroke="#94a3b8"
            strokeWidth={strokeW}
            strokeOpacity={0.5}
            className="transition-all duration-300"
          />
        )
      })}

      {/* Nodes */}
      {nodes.map((node, i) => {
        const p = positions[node.id]
        if (!p) return null
        const r = node.group === 0
          ? 8 + (node.size / maxSize) * 18   // hubs: 8–26px
          : 4 + (node.size / maxSize) * 10   // matches: 4–14px
        const color = COLORS[node.group % COLORS.length]
        return (
          <g key={`node-${i}`}>
            {/* Glow for hubs */}
            {node.group === 0 && (
              <circle cx={p.x} cy={p.y} r={r + 4} fill={color} opacity={0.15} />
            )}
            <circle
              cx={p.x}
              cy={p.y}
              r={r}
              fill={color}
              stroke="#fff"
              strokeWidth={2}
              className="transition-all duration-300"
            />
            <title>{`${node.label} (${node.size} connections)`}</title>
            {/* Label */}
            <text
              x={p.x}
              y={p.y + r + 12}
              textAnchor="middle"
              className="fill-foreground text-[10px] font-medium"
              style={{ pointerEvents: "none" }}
            >
              {node.label.length > 14 ? node.label.slice(0, 12) + "…" : node.label}
            </text>
          </g>
        )
      })}
    </svg>
  )
}
