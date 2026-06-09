"use client";

import { useState, useEffect } from "react";
import { useProducts, usePriceDistribution, usePriceVolumeMatrix } from "@/hooks/useProducts";
import { DateRangeFilter } from "@/components/DateRangeFilter";
import { ExpandableChart } from "@/components/ExpandableChart";
import { FilterDialog } from "@/components/FilterDialog";
import { ChartFilterBar, type FilterOption } from "@/components/ChartFilterBar";
import { KPICard } from "@/components/KPICard";
import { RechartsBarChart } from "@/components/charts/RechartsBarChart";
import { RechartsScatterChart } from "@/components/charts/RechartsScatterChart";
import { RechartsDoughnutChart } from "@/components/charts/RechartsDoughnutChart";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardAction } from "@/components/ui/card";
import { filtersApi } from "@/services/api";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { Package, DollarSign, AlertTriangle, Layers } from "lucide-react";
import type { DashboardParams } from "@/services/api";

type ChartFilters = Record<string, string>;

const DIMS = ["category"];

export default function ProductsPage() {
  const [dateParams, setDateParams] = useState<DashboardParams>({});
  const [filterOptions, setFilterOptions] = useState<Record<string, string[]>>({});
  const [priceDistFilters, setPriceDistFilters] = useState<ChartFilters>({});
  const [matrixFilters, setMatrixFilters] = useState<ChartFilters>({});

  useEffect(() => {
    filtersApi.getOptions().then((opts) => {
      const m: Record<string, string[]> = {};
      if (opts.categories?.length) m.category = opts.categories;
      if (opts.countries?.length) m.country = opts.countries;
      setFilterOptions(m);
    }).catch(() => {});
  }, []);

  function chartFilters(
    f: ChartFilters, setF: (v: ChartFilters) => void, dims: string[]
  ): FilterOption[] {
    return dims.filter((d) => (filterOptions[d]?.length ?? 0) > 0).map((d) => ({
      param: d,
      label: d.charAt(0).toUpperCase() + d.slice(1),
      options: filterOptions[d],
      value: f[d] ?? "__all__",
      onChange: (val: string) => setF({ ...f, [d]: val }),
    }));
  }

  const { data: products, isLoading: loadingProducts } = useProducts(dateParams);
  const { data: priceDist, isLoading: loadingPrice } = usePriceDistribution(dateParams);
  const { data: priceVolume, isLoading: loadingMatrix } = usePriceVolumeMatrix(dateParams);

  if (loadingProducts || loadingPrice || loadingMatrix) return <LoadingSkeleton />;

  const totalProducts = products?.length || 0;
  const avgPrice = products && products.length > 0
    ? products.reduce((sum: number, p: any) => sum + Number(p.price), 0) / products.length : 0;
  const totalRevenue = products?.reduce((sum: number, p: any) => sum + Number(p.total_revenue), 0) || 0;
  const categories = [...new Set(products?.map((p: any) => p.category) || [])];

  return (
    <div className="space-y-6">
      <DateRangeFilter title="Product Analysis" onApply={setDateParams} />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard label="Total Products" value={totalProducts} format="number" icon={<Package className="h-5 w-5" />} />
        <KPICard label="Average Price" value={avgPrice} format="currency" icon={<DollarSign className="h-5 w-5" />} />
        <KPICard label="Total Revenue" value={totalRevenue} format="currency" icon={<Layers className="h-5 w-5" />} />
        <KPICard label="Categories" value={categories.length} format="number" icon={<AlertTriangle className="h-5 w-5" />} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card><CardHeader><CardTitle>Price Distribution</CardTitle><CardDescription>Number of products by price range</CardDescription>
          <CardAction><FilterDialog chartName="Price Distribution" filters={chartFilters(priceDistFilters, setPriceDistFilters, DIMS)} /></CardAction>
        </CardHeader><CardContent>
          <ExpandableChart title="Price Distribution" description="Number of products by price range"
            filterControls={<ChartFilterBar filters={chartFilters(priceDistFilters, setPriceDistFilters, DIMS)} />}
          >
            <RechartsBarChart labels={priceDist?.map((d: any) => d.range_label) || []}
              datasets={[{ label: "Product Count", data: priceDist?.map((d: any) => d.product_count) || [] }]} height={320} />
          </ExpandableChart>
        </CardContent></Card>
        <Card><CardHeader><CardTitle>Revenue by Category</CardTitle><CardDescription>Total revenue grouped by product category</CardDescription></CardHeader><CardContent>
          <ExpandableChart title="Revenue by Category" description="Total revenue grouped by product category">
            <RechartsDoughnutChart
              labels={products?.reduce((acc: any, p: any) => { const e = acc.find((a: any) => a.label === p.category); if (e) e.value += Number(p.total_revenue); else acc.push({ label: p.category, value: Number(p.total_revenue) }); return acc; }, []).map((c: any) => c.label) || []}
              data={products?.reduce((acc: any, p: any) => { const e = acc.find((a: any) => a.label === p.category); if (e) e.value += Number(p.total_revenue); else acc.push({ label: p.category, value: Number(p.total_revenue) }); return acc; }, []).map((c: any) => c.value) || []}
              height={320} />
          </ExpandableChart>
        </CardContent></Card>
      </div>

      <Card><CardHeader><CardTitle>Price vs Volume Matrix</CardTitle><CardDescription>Unit price compared to quantity sold for each product</CardDescription>
        <CardAction><FilterDialog chartName="Price vs Volume Matrix" filters={chartFilters(matrixFilters, setMatrixFilters, DIMS)} /></CardAction>
      </CardHeader><CardContent>
        <ExpandableChart title="Price vs Volume Matrix" description="Unit price compared to quantity sold for each product"
          filterControls={<ChartFilterBar filters={chartFilters(matrixFilters, setMatrixFilters, DIMS)} />}
        >
          <RechartsScatterChart
            dataPoints={priceVolume?.map((p: any) => ({ x: Number(p.price), y: Number(p.total_quantity), label: p.product_name, category: p.category })) || []}
            xLabel="Unit Price (€)" yLabel="Quantity Sold" height={400} />
        </ExpandableChart>
      </CardContent></Card>
    </div>
  );
}
