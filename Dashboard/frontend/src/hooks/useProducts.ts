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

export function useAllergenDistribution() {
  return useQuery({
    queryKey: ["products", "allergen-distribution"],
    queryFn: () => productsApi.getAllergenDistribution(),
    staleTime: 10 * 60 * 1000,
  });
}

export function useResistanceDistribution() {
  return useQuery({
    queryKey: ["products", "resistance-distribution"],
    queryFn: () => productsApi.getResistanceDistribution(),
    staleTime: 10 * 60 * 1000,
  });
}

export function useCategoryGrowth(dateParams?: DashboardParams) {
  return useQuery({
    queryKey: ["products", "category-growth", dateParams],
    queryFn: () => productsApi.getCategoryGrowth(dateParams),
    staleTime: 10 * 60 * 1000,
  });
}

export function useProductQuantitySummary(dateParams?: DashboardParams) {
  return useQuery({
    queryKey: ["products", "quantity-summary", dateParams],
    queryFn: () => productsApi.getQuantitySummary(dateParams),
    staleTime: 10 * 60 * 1000,
  });
}
