"use client";

import { useState, useEffect } from "react";
import {
  useCustomerSegments,
  useTopCustomers,
  useCustomerActivity,
} from "@/hooks/useCustomers";
import { DateRangeFilter } from "@/components/DateRangeFilter";
import { ExpandableChart } from "@/components/ExpandableChart";
import { FilterDialog } from "@/components/FilterDialog";
import { ChartFilterBar, type FilterOption } from "@/components/ChartFilterBar";
import { KPICard } from "@/components/KPICard";
import { RechartsBarChart } from "@/components/charts/RechartsBarChart";
import { RechartsDoughnutChart } from "@/components/charts/RechartsDoughnutChart";
import { RechartsAreaChart } from "@/components/charts/RechartsAreaChart";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardAction } from "@/components/ui/card";
import { filtersApi } from "@/services/api";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { Users, UserCheck, TrendingUp, DollarSign } from "lucide-react";
import type { DashboardParams } from "@/services/api";

type ChartFilters = Record<string, string>;

export default function CustomersPage() {
  const [dateParams, setDateParams] = useState<DashboardParams>({});
  const [filterOptions, setFilterOptions] = useState<Record<string, string[]>>({});
  const [activityFilters, setActivityFilters] = useState<ChartFilters>({});

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
      param: d, label: d.charAt(0).toUpperCase() + d.slice(1),
      options: filterOptions[d], value: f[d] ?? "__all__",
      onChange: (val: string) => setF({ ...f, [d]: val }),
    }));
  }

  const { data: segments, isLoading: loadingSegments } = useCustomerSegments();
  const { data: topCustomers, isLoading: loadingTop } = useTopCustomers(10);
  const { data: activity, isLoading: loadingActivity } = useCustomerActivity(dateParams);

  if (loadingSegments || loadingTop || loadingActivity) return <LoadingSkeleton />;

  const totalCustomers = segments?.reduce((sum: number, s: any) => sum + s.customer_count, 0) || 0;
  const totalRevenue = segments?.reduce((sum: number, s: any) => sum + Number(s.total_revenue), 0) || 0;
  const vipCustomers = segments?.find((s: any) => s.segment === "VIP")?.customer_count || 0;
  const avgBasket = segments && segments.length > 0
    ? segments.reduce((sum: number, s: any) => sum + Number(s.avg_basket), 0) / segments.length : 0;

  const COMMON_DIMS = ["category", "country"];

  return (
    <div className="space-y-6">
      <DateRangeFilter title="Customer Analysis" onApply={setDateParams} />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard label="Total Customers" value={totalCustomers} format="number" icon={<Users className="h-5 w-5" />} />
        <KPICard label="VIP Customers" value={vipCustomers} format="number" icon={<UserCheck className="h-5 w-5" />} />
        <KPICard label="Total Revenue" value={totalRevenue} format="currency" icon={<DollarSign className="h-5 w-5" />} />
        <KPICard label="Avg Basket" value={avgBasket} format="currency" icon={<TrendingUp className="h-5 w-5" />} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card><CardHeader><CardTitle>Customer Segmentation</CardTitle><CardDescription>Breakdown of customers by segment type</CardDescription></CardHeader><CardContent>
          <ExpandableChart title="Customer Segmentation" description="Breakdown of customers by segment type">
            <RechartsDoughnutChart labels={segments?.map((s: any) => s.segment) || []} data={segments?.map((s: any) => Number(s.customer_count)) || []} height={320} />
          </ExpandableChart>
        </CardContent></Card>
        <Card><CardHeader><CardTitle>Top 10 Customers</CardTitle><CardDescription>Highest-spending customers this period</CardDescription></CardHeader><CardContent>
          <ExpandableChart title="Top 10 Customers" description="Highest-spending customers this period">
            <RechartsBarChart labels={topCustomers?.map((c: any) => c.full_name.split(" ")[0]) || []}
              datasets={[{ label: "Total Spent", data: topCustomers?.map((c: any) => Number(c.total_spent)) || [] }]} height={320} horizontal />
          </ExpandableChart>
        </CardContent></Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card><CardHeader><CardTitle>Active Customers Over Time</CardTitle><CardDescription>Monthly active customer count trend</CardDescription>
          <CardAction><FilterDialog chartName="Active Customers" filters={chartFilters(activityFilters, setActivityFilters, COMMON_DIMS)} /></CardAction>
        </CardHeader><CardContent>
          <ExpandableChart title="Active Customers Over Time" description="Monthly active customer count trend"
            filterControls={<ChartFilterBar filters={chartFilters(activityFilters, setActivityFilters, COMMON_DIMS)} />}
          >
            <RechartsAreaChart labels={activity?.map((a: any) => `${a.month} ${a.year}`) || []}
              datasets={[{ label: "Active Customers", data: activity?.map((a: any) => a.active_customers) || [], color: "var(--chart-2)" }]} height={320} />
          </ExpandableChart>
        </CardContent></Card>
        <Card><CardHeader><CardTitle>Avg Basket by Segment</CardTitle><CardDescription>Average purchase value per customer segment</CardDescription></CardHeader><CardContent>
          <ExpandableChart title="Avg Basket by Segment" description="Average purchase value per customer segment">
            <RechartsBarChart labels={segments?.map((s: any) => s.segment) || []}
              datasets={[{ label: "Avg Basket", data: segments?.map((s: any) => Number(s.avg_basket)) || [] }]} height={320} />
          </ExpandableChart>
        </CardContent></Card>
      </div>
    </div>
  );
}
