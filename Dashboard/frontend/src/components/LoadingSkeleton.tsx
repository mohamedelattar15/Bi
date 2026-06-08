"use client";

import { Card, CardContent, CardHeader } from "@/components/ui/card";

export function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <div className="h-4 w-24 rounded bg-muted" />
            </CardHeader>
            <CardContent>
              <div className="mt-1 h-8 w-32 rounded bg-muted" />
              <div className="mt-2 h-3 w-20 rounded bg-muted/50" />
            </CardContent>
          </Card>
        ))}
      </div>
      {Array.from({ length: 4 }).map((_, i) => (
        <Card key={i}>
          <CardHeader>
            <div className="h-4 w-40 rounded bg-muted" />
          </CardHeader>
          <CardContent>
            <div className="h-64 rounded bg-muted/50" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
