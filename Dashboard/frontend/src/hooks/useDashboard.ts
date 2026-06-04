"use client";

import { useQuery } from "@tanstack/react-query";
import { dashboardApi, type DashboardParams } from "@/services/api";

/**
 * Hook to fetch the complete dashboard summary.
 */
export function useDashboard(params?: DashboardParams) {
  return useQuery({
    queryKey: ["dashboard", "summary", params],
    queryFn: () => dashboardApi.getSummary(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  });
}
