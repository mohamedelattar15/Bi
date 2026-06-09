"use client";

import { Dialog as DialogPrimitive } from "@base-ui/react/dialog";
import { Filter, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChartFilterBar, type FilterOption } from "@/components/ChartFilterBar";
import { cn } from "@/lib/utils";

interface FilterDialogProps {
  /** Human-readable chart name (for the dialog title) */
  chartName: string;
  /** Filter definitions for this chart */
  filters: FilterOption[];
}

export function FilterDialog({ chartName, filters }: FilterDialogProps) {
  const hasActiveFilters = filters.some(
    (f) => f.value && f.value !== "__all__"
  );

  return (
    <DialogPrimitive.Root>
      {/* Trigger button in CardAction slot */}
      <DialogPrimitive.Trigger
        render={
          <Button
            variant="ghost"
            size="icon-sm"
            className={cn(
              "h-7 w-7",
              hasActiveFilters && "text-primary"
            )}
            title="Chart filters"
          >
            <Filter className="h-4 w-4" />
          </Button>
        }
      />

      {/* Centered modal */}
      <DialogPrimitive.Portal>
        <DialogPrimitive.Backdrop className="fixed inset-0 z-50 bg-black/40 data-ending-style:opacity-0 data-starting-style:opacity-0" />
        <DialogPrimitive.Popup className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-xl border bg-popover p-6 text-popover-foreground shadow-lg data-ending-style:opacity-0 data-starting-style:opacity-0 data-ending-style:scale-95 data-starting-style:scale-95">
          {/* Header */}
          <div className="mb-4 flex items-center justify-between">
            <div>
              <DialogPrimitive.Title className="text-base font-semibold text-foreground">
                {chartName} Filters
              </DialogPrimitive.Title>
              <DialogPrimitive.Description className="text-sm text-muted-foreground">
                Refine the data shown in this chart
              </DialogPrimitive.Description>
            </div>
            <DialogPrimitive.Close
              render={
                <Button variant="ghost" size="icon-sm" className="h-7 w-7">
                  <X className="h-4 w-4" />
                </Button>
              }
            />
          </div>

          {/* Filter controls */}
          <div className="space-y-4">
            <ChartFilterBar filters={filters} />
          </div>

          {/* Footer actions */}
          <div className="mt-6 flex items-center justify-end gap-2">
            <DialogPrimitive.Close
              render={
                <Button variant="outline" size="sm">
                  Close
                </Button>
              }
            />
          </div>
        </DialogPrimitive.Popup>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}
