"use client";

import { useQuery } from "@tanstack/react-query";
import { salesApi, type ChartFilterParams } from "@/services/api";

export function useSalesOverTime(params?: ChartFilterParams) {
  return useQuery({
    queryKey: ["sales", "over-time", params],
    queryFn: () => salesApi.getOverTime(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useSalesByCategory(params?: ChartFilterParams) {
  return useQuery({
    queryKey: ["sales", "by-category", params],
    queryFn: () => salesApi.getByCategory(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useMonthlySales(params?: ChartFilterParams) {
  return useQuery({
    queryKey: ["sales", "monthly", params],
    queryFn: () => salesApi.getMonthly(params),
    staleTime: 5 * 60 * 1000,
  });
}
