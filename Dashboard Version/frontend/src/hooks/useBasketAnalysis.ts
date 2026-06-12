"use client";

import { useQuery } from "@tanstack/react-query";
import { basketApi } from "@/services/api";
import type { DashboardParams } from "@/services/api";

export function useBasketAnalysis(
  minSupport = 0.000001,
  minLift = 0.0,
  limit = 50,
  dateParams?: DashboardParams
) {
  return useQuery({
    queryKey: ["basket", "analysis", minSupport, minLift, limit, dateParams],
    queryFn: () => basketApi.getAnalysis(minSupport, minLift, limit, dateParams),
    staleTime: 10 * 60 * 1000,
  });
}
