"use client";

import { X } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";

export interface FilterOption {
  /** The field key sent to the API (e.g. "category") */
  param: string;
  /** Human-readable label (e.g. "Category") */
  label: string;
  /** Available choices */
  options: string[];
  /** Currently selected value */
  value: string;
  /** Called when the selection changes */
  onChange: (value: string) => void;
}

interface ChartFilterBarProps {
  filters: FilterOption[];
}

export function ChartFilterBar({ filters }: ChartFilterBarProps) {
  const activeFilters = filters.filter((f) => f.options.length > 0);

  if (activeFilters.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2">
      {activeFilters.map((f) => (
        <div key={f.param} className="flex items-center gap-1.5">
          <span className="text-xs text-muted-foreground">{f.label}:</span>
          <Select value={f.value} onValueChange={f.onChange}>
            <SelectTrigger className="h-7 w-auto min-w-[100px] text-xs">
              <SelectValue placeholder={`All ${f.label}s`} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">All {f.label}s</SelectItem>
              {f.options.map((opt) => (
                <SelectItem key={opt} value={opt}>
                  {opt}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {f.value && f.value !== "__all__" && (
            <Button
              variant="ghost"
              size="icon-xs"
              className="h-5 w-5"
              onClick={() => f.onChange("__all__")}
            >
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>
      ))}
    </div>
  );
}
