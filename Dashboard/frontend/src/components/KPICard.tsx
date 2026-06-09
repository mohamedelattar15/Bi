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
        {icon && (
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            {icon}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold tracking-tight text-foreground">
          {prefix}
          {formattedValue()}
          {suffix}
        </div>
        {trend !== null && trend !== undefined && (
          <div className="mt-2 flex items-center gap-1.5 text-sm">
            <span
              className={cn(
                "inline-flex items-center gap-0.5 rounded-md px-1.5 py-0.5 text-xs font-medium",
                trend_direction === "up" && "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
                trend_direction === "down" && "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
                (!trend_direction || trend_direction === "stable") &&
                  "bg-muted text-muted-foreground"
              )}
            >
              <TrendIcon />
              {Math.abs(trend).toFixed(1)}%
            </span>
            <span className="text-muted-foreground">vs previous period</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
