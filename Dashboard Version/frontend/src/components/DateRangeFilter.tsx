"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { filtersApi, type DashboardParams } from "@/services/api";
import { Calendar } from "lucide-react";

interface DateRangeFilterProps {
  /** Called whenever the user applies a new date range */
  onApply: (params: DashboardParams) => void;
  /** Page title shown next to the filter */
  title: string;
}

export function DateRangeFilter({ onApply, title }: DateRangeFilterProps) {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [dateBounds, setDateBounds] = useState<{ min: string; max: string } | null>(null);

  // Fetch dataset date boundaries once on mount
  useEffect(() => {
    filtersApi.getOptions().then((opts) => {
      const dr = opts.date_range;
      if (dr?.[0] && dr?.[1]) {
        const min = dr[0].slice(0, 10);
        const max = dr[1].slice(0, 10);
        setDateBounds({ min, max });
        setStartDate(min);
        setEndDate(max);
        onApply({ start_date: min, end_date: max });
      }
    }).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleApply() {
    if (startDate && endDate && startDate > endDate) return;
    onApply({
      ...(startDate && { start_date: startDate }),
      ...(endDate && { end_date: endDate }),
    });
  }

  function handleReset() {
    if (dateBounds) {
      setStartDate(dateBounds.min);
      setEndDate(dateBounds.max);
      onApply({ start_date: dateBounds.min, end_date: dateBounds.max });
    }
  }

  return (
    <div className="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">{title}</h2>
        <p className="text-sm text-muted-foreground">
          {startDate && endDate ? `${startDate} → ${endDate}` : "Loading date range..."}
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-muted-foreground" />
          <Input
            type="date"
            value={startDate}
            min={dateBounds?.min}
            max={endDate || dateBounds?.max}
            onChange={(e) => setStartDate(e.target.value)}
            className="h-8 w-40"
          />
          <span className="text-muted-foreground">→</span>
          <Input
            type="date"
            value={endDate}
            min={startDate || dateBounds?.min}
            max={dateBounds?.max}
            onChange={(e) => setEndDate(e.target.value)}
            className="h-8 w-40"
          />
        </div>
        <Button size="sm" onClick={handleApply} disabled={!startDate || !endDate}>
          Apply
        </Button>
        <Button size="sm" variant="ghost" onClick={handleReset}>
          All time
        </Button>
      </div>
    </div>
  );
}
