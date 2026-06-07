"use client";

import { useQuery } from "@tanstack/react-query";
import { employeesApi } from "@/services/api";

export function useTopEmployees(limit = 5) {
  return useQuery({
    queryKey: ["employees", "top", limit],
    queryFn: () => employeesApi.getTop(limit),
    staleTime: 5 * 60 * 1000,
  });
}

export function useEmployeePerformanceByAge() {
  return useQuery({
    queryKey: ["employees", "performance", "age"],
    queryFn: () => employeesApi.getPerformanceByAge(),
    staleTime: 10 * 60 * 1000,
  });
}

export function useEmployeePerformanceBySeniority() {
  return useQuery({
    queryKey: ["employees", "performance", "seniority"],
    queryFn: () => employeesApi.getPerformanceBySeniority(),
    staleTime: 10 * 60 * 1000,
  });
}
