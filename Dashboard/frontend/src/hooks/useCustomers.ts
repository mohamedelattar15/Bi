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
