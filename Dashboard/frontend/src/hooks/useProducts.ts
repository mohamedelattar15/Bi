"use client";

import { useQuery } from "@tanstack/react-query";
import { productsApi } from "@/services/api";
import type { DashboardParams } from "@/services/api";

export function useProducts(dateParams?: DashboardParams) {
  return useQuery({
    queryKey: ["products", dateParams],
    queryFn: () => productsApi.getAll(dateParams),
    staleTime: 10 * 60 * 1000,
  });
}

export function useProductDetail(id: number) {
  return useQuery({
    queryKey: ["products", id],
    queryFn: () => productsApi.getById(id),
    enabled: !!id,
  });
}

export function usePriceDistribution(dateParams?: DashboardParams) {
  return useQuery({
    queryKey: ["products", "price-distribution", dateParams],
    queryFn: () => productsApi.getPriceDistribution(dateParams),
    staleTime: 10 * 60 * 1000,
  });
}

export function usePriceVolumeMatrix(dateParams?: DashboardParams) {
  return useQuery({
    queryKey: ["products", "price-volume-matrix", dateParams],
    queryFn: () => productsApi.getPriceVolumeMatrix(dateParams),
    staleTime: 10 * 60 * 1000,
  });
}
