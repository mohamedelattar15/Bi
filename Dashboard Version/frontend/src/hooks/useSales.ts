"use client";

import { useQuery } from "@tanstack/react-query";
import { salesApi, type ChartFilterParams, type DashboardParams } from "@/services/api";

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

export function useSalesByCity(params?: DashboardParams) {
  return useQuery({
    queryKey: ["sales", "by-city", params],
    queryFn: () => salesApi.getByCity(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useSalesFunnelByCity(params?: DashboardParams) {
  return useQuery({
    queryKey: ["sales", "funnel", params],
    queryFn: () => salesApi.getFunnelByCity(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCaGrowthByYear(params?: DashboardParams) {
  return useQuery({
    queryKey: ["sales", "ca-growth", params],
    queryFn: () => salesApi.getCaGrowthByYear(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useSalesByClass(params?: DashboardParams) {
  return useQuery({
    queryKey: ["sales", "by-class", params],
    queryFn: () => salesApi.getByClass(params),
    staleTime: 5 * 60 * 1000,
  });
}
