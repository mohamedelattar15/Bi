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

export function useEmployeeAgeCategory() {
  return useQuery({
    queryKey: ["employees", "demographics", "age-category"],
    queryFn: () => employeesApi.getAgeCategoryDistribution(),
    staleTime: 10 * 60 * 1000,
  });
}

export function useEmployeeAgeTranche() {
  return useQuery({
    queryKey: ["employees", "demographics", "age-tranche"],
    queryFn: () => employeesApi.getAgeTrancheDistribution(),
    staleTime: 10 * 60 * 1000,
  });
}

export function useEmployeeGender() {
  return useQuery({
    queryKey: ["employees", "demographics", "gender"],
    queryFn: () => employeesApi.getGenderDistribution(),
    staleTime: 10 * 60 * 1000,
  });
}

export function useEmployeeCaByAgeTranche(dateParams?: DashboardParams) {
  return useQuery({
    queryKey: ["employees", "ca-by-age-tranche", dateParams],
    queryFn: () => employeesApi.getCaByAgeTranche(dateParams),
    staleTime: 5 * 60 * 1000,
  });
}

export function useEmployeePerformanceTable(dateParams?: DashboardParams) {
  return useQuery({
    queryKey: ["employees", "performance-table", dateParams],
    queryFn: () => employeesApi.getPerformanceTable(dateParams),
    staleTime: 5 * 60 * 1000,
  });
}
