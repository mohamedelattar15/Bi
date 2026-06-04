"use client";

import { cn, formatCurrency, formatCompactNumber } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface KPICardProps {
  label: string;
  value: number;
  prefix?: string;
  suffix?: string;
  format?: "number" | "currency" | "percentage";
  trend?: number | null;
  trend_direction?: "up" | "down" | "stable" | null;
  icon?: React.ReactNode;
  className?: string;
}

export function KPICard({
  label,
  value,
  prefix = "",
  suffix = "",
  format = "number",
  trend,
  trend_direction,
  icon,
  className,
}: KPICardProps) {
  const formattedValue = () => {
    if (format === "currency") {
      return formatCurrency(value);
    }
    if (format === "percentage") {
      return `${value.toFixed(1)}%`;
    }
    return formatCompactNumber(value);
  };

  const trendIcon = () => {
    if (trend_direction === "up")
      return <TrendingUp className="h-4 w-4 text-green-500" />;
    if (trend_direction === "down")
      return <TrendingDown className="h-4 w-4 text-red-500" />;
    return <Minus className="h-4 w-4 text-gray-400" />;
  };

  const trendColor = () => {
    if (trend_direction === "up") return "text-green-600";
    if (trend_direction === "down") return "text-red-600";
    return "text-gray-500";
  };

  return (
    <div
      className={cn(
        "rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition-all hover:shadow-md",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-500">{label}</span>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-3xl font-bold text-gray-900">
          {prefix}
          {formattedValue()}
          {suffix}
        </span>
      </div>
      {trend !== null && trend !== undefined && (
        <div className={cn("mt-2 flex items-center gap-1 text-sm", trendColor())}>
          {trendIcon()}
          <span>
            {Math.abs(trend).toFixed(1)}% vs previous period
          </span>
        </div>
      )}
    </div>
  );
}
