"use client";

import { useState, useEffect } from "react";
import { useDashboard } from "@/hooks/useDashboard";
import { useSalesOverTime, useMonthlySales } from "@/hooks/useSales";
import { DateRangeFilter } from "@/components/DateRangeFilter";
import { FilterDialog } from "@/components/FilterDialog";
import { ChartFilterBar, type FilterOption } from "@/components/ChartFilterBar";
import { KPICard } from "@/components/KPICard";
import { ExpandableChart } from "@/components/ExpandableChart";
import { RechartsAreaChart } from "@/components/charts/RechartsAreaChart";
import { RechartsBarChart } from "@/components/charts/RechartsBarChart";
import { RechartsDoughnutChart } from "@/components/charts/RechartsDoughnutChart";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardAction } from "@/components/ui/card";
import { filtersApi } from "@/services/api";
import { Wallet, ShoppingBag, Receipt, TrendingUp, Users, Package } from "lucide-react";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import type { DashboardParams, ChartFilterParams } from "@/services/api";

/** Per-chart filter state: maps dimension param → selected value ("__all__" = no filter) */
type ChartFilters = Record<string, string>;

/** Default: all filters cleared */
const NO_FILTERS: ChartFilters = {};

export default function SalesDashboardPage() {
  const [dateParams, setDateParams] = useState<DashboardParams>({});
  const [filterOptions, setFilterOptions] = useState<Record<string, string[]>>({});

  // Per-chart independent filter state
  const [revenueFilters, setRevenueFilters] = useState<ChartFilters>({});
  const [seasonalityFilters, setSeasonalityFilters] = useState<ChartFilters>({});
  const [topProductFilters, setTopProductFilters] = useState<ChartFilters>({});

  // Fetch available filter dimensions once
  useEffect(() => {
    filtersApi.getOptions().then((opts) => {
      const optsMap: Record<string, string[]> = {};
      if (opts.categories?.length) optsMap.category = opts.categories;
      if (opts.countries?.length) optsMap.country = opts.countries;
      if (opts.employees?.length) optsMap.employee = opts.employees;
      setFilterOptions(optsMap);
    }).catch(() => {});
  }, []);

  /** Convert ChartFilters to ChartFilterParams (strip "__all__" entries) */
  function toParams(filters: ChartFilters): ChartFilterParams {
    const p: ChartFilterParams = {};
    for (const [key, val] of Object.entries(filters)) {
      if (val && val !== "__all__") p[key as keyof ChartFilterParams] = val;
    }
    return { ...dateParams, ...p };
  }

  /** Build FilterOption[] for a chart, given its current state + setter */
  function chartFilters(
    filters: ChartFilters,
    setFilters: (f: ChartFilters) => void,
    dimensions: string[],
  ): FilterOption[] {
    return dimensions
      .filter((dim) => (filterOptions[dim]?.length ?? 0) > 0)
      .map((dim) => ({
        param: dim,
        label: dim.charAt(0).toUpperCase() + dim.slice(1),
        options: filterOptions[dim],
        value: filters[dim] ?? "__all__",
        onChange: (val: string) => setFilters({ ...filters, [dim]: val }),
      }));
  }

  // ---- Global KPIs ----
  const { data: dashboard, isLoading, error } = useDashboard(dateParams);

  // ---- Chart-specific data ----
  const { data: revenueData } = useSalesOverTime(toParams(revenueFilters));
  const { data: seasonalityData } = useMonthlySales(toParams(seasonalityFilters));

  // Dimensions each chart exposes
  const COMMON_DIMS = ["category", "country"];

  if (isLoading) return <LoadingSkeleton />;

  if (error || !dashboard) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-foreground">
            Unable to load dashboard
          </h2>
          <p className="mt-2 text-muted-foreground">
            Please ensure the backend API is running.
          </p>
        </div>
      </div>
    );
  }

  const clearFilters = (setter: (f: ChartFilters) => void) => () => setter({});

  return (
    <div className="space-y-6">
      <DateRangeFilter title="Sales Dashboard" onApply={setDateParams} />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <KPICard label={dashboard.total_revenue.label} value={dashboard.total_revenue.value} format="currency" icon={<Wallet className="h-5 w-5" />} />
        <KPICard label={dashboard.total_quantity.label} value={dashboard.total_quantity.value} format="number" icon={<ShoppingBag className="h-5 w-5" />} />
        <KPICard label={dashboard.total_transactions.label} value={dashboard.total_transactions.value} format="number" icon={<Receipt className="h-5 w-5" />} />
        <KPICard label={dashboard.avg_basket.label} value={dashboard.avg_basket.value} format="currency" icon={<TrendingUp className="h-5 w-5" />} />
        {dashboard.unique_customers && (
          <KPICard label={dashboard.unique_customers.label} value={dashboard.unique_customers.value} format="number" icon={<Users className="h-5 w-5" />} />
        )}
        {dashboard.total_products && (
          <KPICard label={dashboard.total_products.label} value={dashboard.total_products.value} format="number" icon={<Package className="h-5 w-5" />} />
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Revenue Over Time</CardTitle>
            <CardDescription>Daily revenue trend over the selected period</CardDescription>
            <CardAction>
              <FilterDialog chartName="Revenue Over Time" filters={chartFilters(revenueFilters, setRevenueFilters, COMMON_DIMS)} />
            </CardAction>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Revenue Over Time" description="Daily revenue trend over the selected period"
              filterControls={<ChartFilterBar filters={chartFilters(revenueFilters, setRevenueFilters, COMMON_DIMS)} />}
            >
              <RechartsAreaChart
                labels={(revenueData || dashboard.revenue_over_time).map((r: any) => r.period)}
                datasets={[{ label: "Revenue", data: (revenueData || dashboard.revenue_over_time).map((r: any) => Number(r.revenue)), color: "var(--chart-1)" }]}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Sales by Category</CardTitle>
            <CardDescription>Revenue breakdown across product categories</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Sales by Category" description="Revenue breakdown across product categories">
              <RechartsDoughnutChart
              labels={dashboard.sales_by_category.map((c: any) => c.category)}
              data={dashboard.sales_by_category.map((c: any) => Number(c.revenue))}
              height={320}
              formatValues
            />
            </ExpandableChart>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Monthly Seasonality</CardTitle>
            <CardDescription>Revenue pattern across months and years</CardDescription>
            <CardAction>
              <FilterDialog chartName="Monthly Seasonality" filters={chartFilters(seasonalityFilters, setSeasonalityFilters, COMMON_DIMS)} />
            </CardAction>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Monthly Seasonality" description="Revenue pattern across months and years"
              filterControls={<ChartFilterBar filters={chartFilters(seasonalityFilters, setSeasonalityFilters, COMMON_DIMS)} />}
            >
              <RechartsBarChart
                labels={(seasonalityData || dashboard.monthly_sales).map((m: any) => `${m.month_name} ${m.year}`)}
                datasets={[{ label: "Revenue", data: (seasonalityData || dashboard.monthly_sales).map((m: any) => Number(m.revenue)) }]}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Top 10 Products</CardTitle>
            <CardDescription>Highest revenue-generating products</CardDescription>
            <CardAction>
              <FilterDialog chartName="Top 10 Products" filters={chartFilters(topProductFilters, setTopProductFilters, COMMON_DIMS)} />
            </CardAction>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Top 10 Products" description="Highest revenue-generating products"
              filterControls={<ChartFilterBar filters={chartFilters(topProductFilters, setTopProductFilters, COMMON_DIMS)} />}
            >
              <RechartsBarChart
                labels={dashboard.top_products.map((p: any) => p.product_name)}
                datasets={[{ label: "Revenue", data: dashboard.top_products.map((p: any) => Number(p.revenue)) }]}
                height={320}
                horizontal
              />
            </ExpandableChart>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
