"use client";

import {
  useCustomerSegments,
  useTopCustomers,
  useCustomerActivity,
} from "@/hooks/useCustomers";
import { KPICard } from "@/components/KPICard";
import { BarChart } from "@/components/charts/BarChart";
import { DoughnutChart } from "@/components/charts/DoughnutChart";
import { LineChart } from "@/components/charts/LineChart";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { Users, UserCheck, TrendingUp, DollarSign } from "lucide-react";

export default function CustomersPage() {
  const { data: segments, isLoading: loadingSegments } = useCustomerSegments();
  const { data: topCustomers, isLoading: loadingTop } = useTopCustomers(10);
  const { data: activity, isLoading: loadingActivity } = useCustomerActivity();

  if (loadingSegments || loadingTop || loadingActivity) {
    return <LoadingSkeleton />;
  }

  const totalCustomers =
    segments?.reduce(
      (sum: number, s: any) => sum + s.customer_count,
      0
    ) || 0;
  const totalRevenue =
    segments?.reduce(
      (sum: number, s: any) => sum + Number(s.total_revenue),
      0
    ) || 0;
  const vipCustomers =
    segments?.find((s: any) => s.segment === "VIP")?.customer_count || 0;
  const avgBasket =
    segments && segments.length > 0
      ? segments.reduce(
          (sum: number, s: any) => sum + Number(s.avg_basket),
          0
        ) / segments.length
      : 0;

  return (
    <div className="space-y-6">
      {/* KPI Row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          label="Total Customers"
          value={totalCustomers}
          format="number"
          icon={<Users className="h-5 w-5" />}
        />
        <KPICard
          label="VIP Customers"
          value={vipCustomers}
          format="number"
          icon={<UserCheck className="h-5 w-5" />}
        />
        <KPICard
          label="Total Revenue"
          value={totalRevenue}
          format="currency"
          icon={<DollarSign className="h-5 w-5" />}
        />
        <KPICard
          label="Avg Basket"
          value={avgBasket}
          format="currency"
          icon={<TrendingUp className="h-5 w-5" />}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <DoughnutChart
            title="Customer Segmentation"
            labels={segments?.map((s: any) => s.segment) || []}
            data={
              segments?.map((s: any) => Number(s.customer_count)) || []
            }
            height={320}
          />
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <BarChart
            title="Top 10 Customers"
            labels={
              topCustomers?.map((c: any) => c.full_name.split(" ")[0]) ||
              []
            }
            datasets={[
              {
                label: "Total Spent",
                data:
                  topCustomers?.map((c: any) =>
                    Number(c.total_spent)
                  ) || [],
              },
            ]}
            height={320}
            horizontal
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <LineChart
            title="Active Customers Over Time"
            labels={
              activity?.map(
                (a: any) => `${a.month} ${a.year}`
              ) || []
            }
            datasets={[
              {
                label: "Active Customers",
                data:
                  activity?.map((a: any) => a.active_customers) || [],
                borderColor: "#10b981",
                fill: true,
              },
            ]}
            height={320}
          />
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <BarChart
            title="Avg Basket by Segment"
            labels={segments?.map((s: any) => s.segment) || []}
            datasets={[
              {
                label: "Avg Basket",
                data:
                  segments?.map((s: any) =>
                    Number(s.avg_basket)
                  ) || [],
              },
            ]}
            height={320}
          />
        </div>
      </div>
    </div>
  );
}
