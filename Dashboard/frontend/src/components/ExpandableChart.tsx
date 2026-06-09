"use client";

import { useState, cloneElement, type ReactElement } from "react";
import { Dialog as DialogPrimitive } from "@base-ui/react/dialog";
import { Maximize2, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ExpandableChartProps {
  /** The chart component to render */
  children: ReactElement;
  /** Title shown in the expanded view */
  title: string;
  /** Optional description shown in the expanded view */
  description?: string;
  /** Optional filter controls rendered inside the expand modal */
  filterControls?: React.ReactNode;
}

export function ExpandableChart({ children, title, description, filterControls }: ExpandableChartProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Inline expand button — always visible */}
      <div className="relative">
        <Button
          variant="ghost"
          size="icon-sm"
          className="absolute right-1 top-1 z-10 h-6 w-6"
          onClick={() => setOpen(true)}
          title="Expand chart"
        >
          <Maximize2 className="h-3 w-3" />
        </Button>
        {children}
      </div>

      {/* Centered modal */}
      {open && (
        <DialogPrimitive.Root open={open} onOpenChange={setOpen}>
          <DialogPrimitive.Portal>
            <DialogPrimitive.Backdrop className="fixed inset-0 z-50 bg-black/40 data-ending-style:opacity-0 data-starting-style:opacity-0" />
            <DialogPrimitive.Popup className="fixed left-1/2 top-1/2 z-50 flex w-full max-w-4xl -translate-x-1/2 -translate-y-1/2 flex-col rounded-xl border bg-popover p-6 text-popover-foreground shadow-lg data-ending-style:opacity-0 data-starting-style:opacity-0 data-ending-style:scale-95 data-starting-style:scale-95">
              {/* Header */}
              <div className="mb-4 flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <DialogPrimitive.Title className="text-base font-semibold text-foreground">
                    {title}
                  </DialogPrimitive.Title>
                  {description && (
                    <DialogPrimitive.Description className="text-sm text-muted-foreground">
                      {description}
                    </DialogPrimitive.Description>
                  )}
                  {/* Filters inside the modal */}
                  {filterControls && (
                    <div className="mt-3">
                      {filterControls}
                    </div>
                  )}
                </div>
                <DialogPrimitive.Close
                  render={
                    <Button variant="ghost" size="icon-sm" className="h-7 w-7 shrink-0">
                      <X className="h-4 w-4" />
                    </Button>
                  }
                />
              </div>

              {/* Chart body */}
              <div className="min-h-[400px]">
                {cloneElement(children, {
                  ...children.props,
                  height: Math.max(Number(children.props.height) || 300, 500),
                })}
              </div>
            </DialogPrimitive.Popup>
          </DialogPrimitive.Portal>
        </DialogPrimitive.Root>
      )}
    </>
  );
}
