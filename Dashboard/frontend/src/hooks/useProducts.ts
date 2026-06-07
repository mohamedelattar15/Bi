"use client";

import { useQuery } from "@tanstack/react-query";
import { productsApi } from "@/services/api";

export function useProducts() {
  return useQuery({
    queryKey: ["products"],
    queryFn: () => productsApi.getAll(),
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

export function usePriceDistribution() {
  return useQuery({
    queryKey: ["products", "price-distribution"],
    queryFn: () => productsApi.getPriceDistribution(),
    staleTime: 10 * 60 * 1000,
  });
}

export function usePriceVolumeMatrix() {
  return useQuery({
    queryKey: ["products", "price-volume-matrix"],
    queryFn: () => productsApi.getPriceVolumeMatrix(),
    staleTime: 10 * 60 * 1000,
  });
}
