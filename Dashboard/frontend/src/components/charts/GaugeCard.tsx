"use client"

interface GaugeCardProps {
  label: string
  value: number
  target: number
  format?: "currency" | "number" | "percentage"
  suffix?: string
  inverse?: boolean // lower is better
}

export function GaugeCard({ label, value, target, format = "number", suffix = "", inverse = false }: GaugeCardProps) {
  const pct = target > 0 ? Math.min((value / target) * 100, 100) : 0
  const isGood = inverse ? value <= target : value >= target

  const fmt = (v: number) => {
    if (format === "currency") return `€${v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    if (format === "percentage") return `${v.toFixed(1)}%`
    return v.toLocaleString()
  }

  const color = isGood ? "var(--chart-2)" : "var(--chart-3)"
  const arcAngle = 180
  const rotation = -180 + (pct / 100) * arcAngle

  return (
    <div className="flex flex-col items-center rounded-lg border border-border bg-card p-4">
      <span className="text-xs font-medium text-muted-foreground mb-1">{label}</span>
      <div className="relative flex items-center justify-center" style={{ width: 100, height: 60 }}>
        {/* Background arc */}
        <svg width="100" height="60" viewBox="0 0 100 60" className="absolute">
          <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="var(--border)" strokeWidth="8" strokeLinecap="round" />
          <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke={color} strokeWidth="8" strokeLinecap="round"
            strokeDasharray={`${(pct / 100) * 125.6} 125.6`} />
        </svg>
        {/* Needle */}
        <div className="absolute bottom-1 left-1/2 origin-bottom" style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}>
          <div style={{ width: 2, height: 28, backgroundColor: color, borderRadius: 1 }} />
        </div>
      </div>
      <span className="text-lg font-bold text-foreground">{fmt(value)}{suffix}</span>
      <span className="text-[10px] text-muted-foreground">Target: {fmt(target)}{suffix}</span>
      <span className="text-xs font-medium mt-1" style={{ color }}>{pct.toFixed(0)}% {isGood ? "✓" : "⚠"}</span>
    </div>
  )
}
