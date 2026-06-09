"use client";

import { useQuery } from "@tanstack/react-query";
import { employeesApi } from "@/services/api";
import type { DashboardParams } from "@/services/api";

export function useTopEmployees(limit = 5, dateParams?: DashboardParams) {
  return useQuery({
    queryKey: ["employees", "top", limit, dateParams],
    queryFn: () => employeesApi.getTop(limit, dateParams),
    staleTime: 5 * 60 * 1000,
  });
}

export function useEmployeePerformanceByAge(dateParams?: DashboardParams) {
  return useQuery({
    queryKey: ["employees", "performance", "age", dateParams],
    queryFn: () => employeesApi.getPerformanceByAge(dateParams),
    staleTime: 10 * 60 * 1000,
  });
}

export function useEmployeePerformanceBySeniority(dateParams?: DashboardParams) {
  return useQuery({
    queryKey: ["employees", "performance", "seniority", dateParams],
    queryFn: () => employeesApi.getPerformanceBySeniority(dateParams),
    staleTime: 10 * 60 * 1000,
  });
}
