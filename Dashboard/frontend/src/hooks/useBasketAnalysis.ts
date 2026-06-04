"use client";

import { useQuery } from "@tanstack/react-query";
import { basketApi } from "@/services/api";

export function useBasketAnalysis(
  minSupport = 0.01,
  minLift = 1.5,
  limit = 50
) {
  return useQuery({
    queryKey: ["basket", "analysis", minSupport, minLift, limit],
    queryFn: () => basketApi.getAnalysis(minSupport, minLift, limit),
    staleTime: 10 * 60 * 1000,
  });
}
