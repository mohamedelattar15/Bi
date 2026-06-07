"use client";

import { useDashboard } from "@/hooks/useDashboard";
import { KPICard } from "@/components/KPICard";
import { LineChart } from "@/components/charts/LineChart";
import { BarChart } from "@/components/charts/BarChart";
import { DoughnutChart } from "@/components/charts/DoughnutChart";
import { Wallet, ShoppingBag, Receipt, TrendingUp, Users, Package } from "lucide-react";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";

export default function SalesDashboardPage() {
  const { data: dashboard, isLoading, error } = useDashboard();

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (error || !dashboard) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-700">
            Unable to load dashboard
          </h2>
          <p className="mt-2 text-gray-500">
            Please ensure the backend API is running.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <KPICard
          label={dashboard.total_revenue.label}
          value={dashboard.total_revenue.value}
          format="currency"
          icon={<Wallet className="h-5 w-5" />}
        />
        <KPICard
          label={dashboard.total_quantity.label}
          value={dashboard.total_quantity.value}
          format="number"
          icon={<ShoppingBag className="h-5 w-5" />}
        />
        <KPICard
          label={dashboard.total_transactions.label}
          value={dashboard.total_transactions.value}
          format="number"
          icon={<Receipt className="h-5 w-5" />}
        />
        <KPICard
          label={dashboard.avg_basket.label}
          value={dashboard.avg_basket.value}
          format="currency"
          icon={<TrendingUp className="h-5 w-5" />}
        />
        {dashboard.unique_customers && (
          <KPICard
            label={dashboard.unique_customers.label}
            value={dashboard.unique_customers.value}
            format="number"
            icon={<Users className="h-5 w-5" />}
          />
        )}
        {dashboard.total_products && (
          <KPICard
            label={dashboard.total_products.label}
            value={dashboard.total_products.value}
            format="number"
            icon={<Package className="h-5 w-5" />}
          />
        )}
      </div>

      {/* Charts Row 1 - Revenue Over Time & Sales by Category */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <LineChart
            title="Revenue Over Time"
            labels={dashboard.revenue_over_time.map(
              (r: any) => r.period
            )}
            datasets={[
              {
                label: "Revenue",
                data: dashboard.revenue_over_time.map((r: any) =>
                  Number(r.revenue)
                ),
                borderColor: "#3b82f6",
                fill: true,
              },
            ]}
            height={320}
          />
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <DoughnutChart
            title="Sales by Category"
            labels={dashboard.sales_by_category.map((c: any) => c.category)}
            data={dashboard.sales_by_category.map((c: any) =>
              Number(c.revenue)
            )}
            height={320}
          />
        </div>
      </div>

      {/* Charts Row 2 - Monthly Seasonality & Top Products */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <BarChart
            title="Monthly Seasonality"
            labels={dashboard.monthly_sales.map(
              (m: any) => `${m.month_name} ${m.year}`
            )}
            datasets={[
              {
                label: "Revenue",
                data: dashboard.monthly_sales.map((m: any) =>
                  Number(m.revenue)
                ),
              },
            ]}
            height={320}
          />
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <BarChart
            title="Top 10 Products"
            labels={dashboard.top_products.map(
              (p: any) => p.product_name
            )}
            datasets={[
              {
                label: "Revenue",
                data: dashboard.top_products.map((p: any) =>
                  Number(p.revenue)
                ),
              },
            ]}
            height={320}
            horizontal
          />
        </div>
      </div>
    </div>
  );
}
