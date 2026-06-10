"use client";

import { useQuery } from "@tanstack/react-query";
import { customersApi, type DashboardParams } from "@/services/api";

export function useCustomerSegments() {
  return useQuery({
    queryKey: ["customers", "segments"],
    queryFn: () => customersApi.getSegments(),
    staleTime: 10 * 60 * 1000,
  });
}

export function useTopCustomers(limit = 10) {
  return useQuery({
    queryKey: ["customers", "top", limit],
    queryFn: () => customersApi.getTop(limit),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCustomerActivity(params?: DashboardParams) {
  return useQuery({
    queryKey: ["customers", "activity", params],
    queryFn: () => customersApi.getActivity(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCustomersByTransactions(limit = 10, params?: DashboardParams) {
  return useQuery({
    queryKey: ["customers", "by-transactions", limit, params],
    queryFn: () => customersApi.getByTransactions(limit, params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useAvgBasketByCity(params?: DashboardParams) {
  return useQuery({
    queryKey: ["customers", "avg-basket-by-city", params],
    queryFn: () => customersApi.getAvgBasketByCity(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCustomerGrowthByCity(params?: DashboardParams) {
  return useQuery({
    queryKey: ["customers", "growth-by-city", params],
    queryFn: () => customersApi.getGrowthByCity(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCustomerLoyaltyStats(params?: DashboardParams) {
  return useQuery({
    queryKey: ["customers", "loyalty-stats", params],
    queryFn: () => customersApi.getLoyaltyStats(params),
    staleTime: 5 * 60 * 1000,
  });
}
