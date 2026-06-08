"use client";

import { useDashboard } from "@/hooks/useDashboard";
import { KPICard } from "@/components/KPICard";
import { LineChart } from "@/components/charts/LineChart";
import { BarChart } from "@/components/charts/BarChart";
import { DoughnutChart } from "@/components/charts/DoughnutChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Wallet, ShoppingBag, Receipt, TrendingUp, Users, Package } from "lucide-react";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";

export default function SalesDashboardPage() {
  const { data: dashboard, isLoading, error } = useDashboard();

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

  return (
    <div className="space-y-6">
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
        <Card>
          <CardHeader><CardTitle>Revenue Over Time</CardTitle></CardHeader>
          <CardContent>
            <LineChart
              labels={dashboard.revenue_over_time.map((r: any) => r.period)}
              datasets={[{ label: "Revenue", data: dashboard.revenue_over_time.map((r: any) => Number(r.revenue)), borderColor: "var(--chart-1)", fill: true }]}
              height={320}
            />
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Sales by Category</CardTitle></CardHeader>
          <CardContent>
            <DoughnutChart
              labels={dashboard.sales_by_category.map((c: any) => c.category)}
              data={dashboard.sales_by_category.map((c: any) => Number(c.revenue))}
              height={320}
            />
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Monthly Seasonality</CardTitle></CardHeader>
          <CardContent>
            <BarChart
              labels={dashboard.monthly_sales.map((m: any) => `${m.month_name} ${m.year}`)}
              datasets={[{ label: "Revenue", data: dashboard.monthly_sales.map((m: any) => Number(m.revenue)) }]}
              height={320}
            />
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Top 10 Products</CardTitle></CardHeader>
          <CardContent>
            <BarChart
              labels={dashboard.top_products.map((p: any) => p.product_name)}
              datasets={[{ label: "Revenue", data: dashboard.top_products.map((p: any) => Number(p.revenue)) }]}
              height={320}
              horizontal
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
