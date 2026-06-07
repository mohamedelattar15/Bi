"use client";

export function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* KPI Skeleton */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
          >
            <div className="h-4 w-24 rounded bg-gray-200" />
            <div className="mt-3 h-8 w-32 rounded bg-gray-200" />
            <div className="mt-2 h-3 w-20 rounded bg-gray-100" />
          </div>
        ))}
      </div>

      {/* Charts Skeleton */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {Array.from({ length: 2 }).map((_, i) => (
          <div
            key={i}
            className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
          >
            <div className="h-4 w-40 rounded bg-gray-200" />
            <div className="mt-4 h-64 rounded bg-gray-100" />
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {Array.from({ length: 2 }).map((_, i) => (
          <div
            key={i}
            className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
          >
            <div className="h-4 w-40 rounded bg-gray-200" />
            <div className="mt-4 h-64 rounded bg-gray-100" />
          </div>
        ))}
      </div>
    </div>
  );
}
