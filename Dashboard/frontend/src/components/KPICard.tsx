"use client";

import { cn, formatCurrency, formatCompactNumber } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

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
    if (format === "currency") return formatCurrency(value);
    if (format === "percentage") return `${value.toFixed(1)}%`;
    return formatCompactNumber(value);
  };

  const TrendIcon = () => {
    if (trend_direction === "up")
      return <TrendingUp className="h-4 w-4 text-green-500" />;
    if (trend_direction === "down")
      return <TrendingDown className="h-4 w-4 text-red-500" />;
    return <Minus className="h-4 w-4 text-muted-foreground" />;
  };

  return (
    <Card className={cn("transition-all hover:shadow-md", className)}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {label}
        </CardTitle>
        {icon && <div className="text-muted-foreground">{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold text-foreground">
          {prefix}
          {formattedValue()}
          {suffix}
        </div>
        {trend !== null && trend !== undefined && (
          <div className="mt-2 flex items-center gap-1 text-sm">
            <TrendIcon />
            <span
              className={cn(
                trend_direction === "up" && "text-green-600",
                trend_direction === "down" && "text-red-600",
                (!trend_direction || trend_direction === "stable") &&
                  "text-muted-foreground"
              )}
            >
              {Math.abs(trend).toFixed(1)}% vs previous period
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
