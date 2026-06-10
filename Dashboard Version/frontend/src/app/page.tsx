"use client";

import { useState } from "react";
import { useDashboard } from "@/hooks/useDashboard";
import { useSalesOverTime, useSalesByCity, useCaGrowthByYear, useSalesByClass } from "@/hooks/useSales";
import { useTopCustomers } from "@/hooks/useCustomers";
import { useTopEmployees } from "@/hooks/useEmployees";
import { DateRangeFilter } from "@/components/DateRangeFilter";
import { KPICard } from "@/components/KPICard";
import { ExpandableChart } from "@/components/ExpandableChart";
import { RechartsBarChart } from "@/components/charts/RechartsBarChart";
import { RechartsDoughnutChart } from "@/components/charts/RechartsDoughnutChart";
import { RechartsComboChart } from "@/components/charts/RechartsComboChart";
import { RechartsTreemapChart } from "@/components/charts/RechartsTreemap";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { insightsApi, type DashboardParams } from "@/services/api";
import { Wallet, ShoppingBag, Receipt, TrendingUp, DollarSign, Activity } from "lucide-react";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { useQuery } from "@tanstack/react-query";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";

export default function SalesDashboardPage() {
  const [dateParams, setDateParams] = useState<DashboardParams>({});

  // ── Core Financial KPIs ──
  const { data: dashboard, isLoading, error } = useDashboard(dateParams);
  const { data: revenueData } = useSalesOverTime(dateParams);
  const { data: caGrowth } = useCaGrowthByYear(dateParams);
  const { data: salesByCity } = useSalesByCity(dateParams);
  const { data: salesByClass } = useSalesByClass(dateParams);

  // ── Business Insights ──
  const { data: growthMetrics } = useQuery({
    queryKey: ["insights", "growth-metrics", dateParams],
    queryFn: () => insightsApi.getGrowthMetrics(dateParams),
    staleTime: 5 * 60 * 1000,
  });
  const { data: paretoProducts } = useQuery({
    queryKey: ["insights", "pareto-products", dateParams],
    queryFn: () => insightsApi.getParetoProducts(20, dateParams),
    staleTime: 5 * 60 * 1000,
  });
  const { data: monthOverMonth } = useQuery({
    queryKey: ["insights", "month-over-month"],
    queryFn: () => insightsApi.getMonthOverMonth(),
    staleTime: 10 * 60 * 1000,
  });
  const { data: revenueByDay } = useQuery({
    queryKey: ["insights", "revenue-by-day"],
    queryFn: () => insightsApi.getRevenueByDay(),
    staleTime: 10 * 60 * 1000,
  });
  const { data: revenueConcentration } = useQuery({
    queryKey: ["insights", "revenue-concentration"],
    queryFn: () => insightsApi.getRevenueConcentration(),
    staleTime: 10 * 60 * 1000,
  });

  // ── Customer & Employee Insights ──
  const { data: topCustomers } = useTopCustomers(10);
  const { data: topEmployees } = useTopEmployees(5, dateParams);
  const { data: customerRfm } = useQuery({
    queryKey: ["insights", "customer-rfm"],
    queryFn: () => insightsApi.getCustomerRfm(),
    staleTime: 10 * 60 * 1000,
  });
  const { data: geoDistribution } = useQuery({
    queryKey: ["insights", "geographic-distribution"],
    queryFn: () => insightsApi.getGeographicDistribution(),
    staleTime: 10 * 60 * 1000,
  });

  // ── Revenue Over Time (revenue + profit combo) ──
  const revenueOverTimeData = revenueData || dashboard?.revenue_over_time || [];

  // ── Category breakdown from dashboard summary ──
  const categoryBreakdown = dashboard?.sales_by_category || [];

  // ── RFM segment colors ──
  const rfmColors: Record<string, string> = {
    Champions: "text-green-600 bg-green-50",
    Loyal: "text-blue-600 bg-blue-50",
    "At Risk": "text-amber-600 bg-amber-50",
    "Needs Attention": "text-orange-600 bg-orange-50",
    "Can't Lose": "text-red-600 bg-red-50",
    Promising: "text-purple-600 bg-purple-50",
    New: "text-cyan-600 bg-cyan-50",
    Hibernating: "text-slate-600 bg-slate-50",
    "About to Sleep": "text-yellow-600 bg-yellow-50",
    Lost: "text-gray-400 bg-gray-50",
  };

  if (isLoading) return <LoadingSkeleton />;

  if (error || !dashboard) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-foreground">Unable to load dashboard</h2>
          <p className="mt-2 text-muted-foreground">Please ensure the backend API is running.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <DateRangeFilter title="Sales Performance" onApply={setDateParams} />

      {/* ═══ Row 1: Top-Level KPIs ═══ */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <KPICard label={dashboard.total_revenue.label} value={dashboard.total_revenue.value} format="currency" icon={<Wallet className="h-5 w-5" />} />
        <KPICard label="Total Profit" value={Number(growthMetrics?.total_profit || 0)} format="currency" icon={<DollarSign className="h-5 w-5" />} />
        <KPICard label={dashboard.total_quantity.label} value={dashboard.total_quantity.value} format="number" icon={<ShoppingBag className="h-5 w-5" />} />
        <KPICard label={dashboard.total_transactions.label} value={dashboard.total_transactions.value} format="number" icon={<Receipt className="h-5 w-5" />} />
        <KPICard label="Profit Margin" value={Number(growthMetrics?.profit_margin_pct || 0)} format="percentage" icon={<Activity className="h-5 w-5" />} />
        <KPICard label={dashboard.avg_basket.label} value={dashboard.avg_basket.value} format="currency" icon={<TrendingUp className="h-5 w-5" />} />
      </div>

      {/* ═══ Row 2: Financial Performance — Revenue Trend + MoM Growth ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Revenue Over Time with Profit */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Revenue & Profit Trend</CardTitle>
            <CardDescription>Monthly revenue with profit overlay — core financial health</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Revenue & Profit" description="Monthly financial performance">
              <RechartsComboChart
                labels={revenueOverTimeData.map((r: any) => r.period)}
                bars={[{ label: "Revenue", data: revenueOverTimeData.map((r: any) => Number(r.revenue)), color: "var(--chart-1)" }]}
                lines={[{ label: "Growth %", data: caGrowth?.map((y: any) => Number(y.growth) || 0) || [], color: "var(--chart-2)" }]}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>

        {/* Month-over-Month Growth */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>⭐ Month-over-Month Growth %</CardTitle>
            <CardDescription>
              Revenue change vs previous month — green = growth, red = decline
              <span className="ml-2 text-xs text-muted-foreground">
                ⌀ run rate: €{monthOverMonth && monthOverMonth.length > 0
                  ? Number(monthOverMonth[monthOverMonth.length - 1]?.monthly_run_rate || 0).toLocaleString()
                  : "—"}
              </span>
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="MoM Growth" description="Month-over-month revenue change percentage">
              <RechartsBarChart
                labels={monthOverMonth?.map((m: any) => m.month_name?.substring(0, 3) + " " + m.year) || []}
                datasets={[
                  {
                    label: "MoM Growth %",
                    data: monthOverMonth?.map((m: any) => Number(m.mom_growth_pct)) || [],
                    color: "var(--chart-4)",
                  },
                ]}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 3: Product & Category Analysis ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Category Revenue Treemap */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Category Revenue Breakdown</CardTitle>
            <CardDescription>
              Which categories drive the business? Revenue concentration:{" "}
              <strong>{Number(revenueConcentration?.top_category_pct || 0).toFixed(1)}%</strong> from top category
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Category Revenue" description="Category contribution to total sales">
              <RechartsTreemapChart
                data={(categoryBreakdown.length > 0 ? categoryBreakdown : []).map((c: any) => ({ name: c.category || c.label, value: Number(c.revenue || c.value) }))}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>

        {/* Pareto 80/20 — Product Concentration */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Pareto: Top Products by Revenue (80/20)</CardTitle>
            <CardDescription>
              Revenue concentration index: <strong>{Number(revenueConcentration?.herfindahl_index || 0).toFixed(2)}</strong>
              {" — "}green = within the vital 80%
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-[320px] overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>#</TableHead>
                    <TableHead>Product</TableHead>
                    <TableHead className="text-right">Revenue</TableHead>
                    <TableHead className="text-right">% of Total</TableHead>
                    <TableHead className="text-right">Cumulative %</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paretoProducts?.slice(0, 15).map((p: any, i: number) => (
                    <TableRow key={i}>
                      <TableCell className="text-muted-foreground">{i + 1}</TableCell>
                      <TableCell className="font-medium max-w-[150px] truncate">{p.product_name}</TableCell>
                      <TableCell className="text-right">€{Number(p.revenue).toLocaleString()}</TableCell>
                      <TableCell className="text-right">{Number(p.pct_of_total).toFixed(1)}%</TableCell>
                      <TableCell className="text-right">
                        <span className={Number(p.cumulative_pct) <= 80 ? "text-green-600 font-medium" : "text-muted-foreground"}>
                          {Number(p.cumulative_pct).toFixed(1)}%
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 4: Customer & Geographic Insights ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Top Customers */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Top Customers by Revenue</CardTitle>
            <CardDescription>Who are your most valuable customers?</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-[320px] overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>#</TableHead>
                    <TableHead>Customer</TableHead>
                    <TableHead className="text-right">Revenue</TableHead>
                    <TableHead className="text-right">Orders</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {topCustomers?.map((c: any, i: number) => (
                    <TableRow key={i}>
                      <TableCell className="text-muted-foreground">{i + 1}</TableCell>
                      <TableCell className="font-medium">{c.full_name || `${c.first_name} ${c.last_name}`}</TableCell>
                      <TableCell className="text-right">€{Number(c.revenue || c.total_spent).toLocaleString()}</TableCell>
                      <TableCell className="text-right">{c.orders || c.transaction_count?.toLocaleString() || "-"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        {/* Sales by City */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Sales by City</CardTitle>
            <CardDescription>Geographic revenue distribution — top performing cities</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Sales by City" description="Revenue by geographic area">
              <RechartsBarChart
                labels={salesByCity?.slice(0, 10).map((c: any) => c.city || c.label) || []}
                datasets={[
                  { label: "Revenue", data: salesByCity?.slice(0, 10).map((c: any) => Number(c.revenue || c.value)) || [] },
                ]}
                height={320}
                horizontal
              />
            </ExpandableChart>
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 5: Employee Performance & Customer Segments ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Top Employees */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Top Performing Employees</CardTitle>
            <CardDescription>Sales reps driving the most revenue</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-[320px] overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>#</TableHead>
                    <TableHead>Employee</TableHead>
                    <TableHead className="text-right">Revenue</TableHead>
                    <TableHead className="text-right">Transactions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {topEmployees?.map((e: any, i: number) => (
                    <TableRow key={i}>
                      <TableCell className="text-muted-foreground">{i + 1}</TableCell>
                      <TableCell className="font-medium">{e.full_name || `${e.first_name} ${e.last_name}`}</TableCell>
                      <TableCell className="text-right">€{Number(e.revenue || e.total_revenue).toLocaleString()}</TableCell>
                      <TableCell className="text-right">{e.transactions || e.transaction_count?.toLocaleString() || "-"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        {/* Customer RFM Segments */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Customer Segments (RFM)</CardTitle>
            <CardDescription>Who are your customers? Recency, Frequency, Monetary breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-[320px] overflow-y-auto space-y-2">
              {customerRfm?.map((s: any, i: number) => (
                <div key={i} className="flex items-center justify-between rounded-lg border p-3">
                  <div className="flex items-center gap-3">
                    <div className={`rounded-full px-3 py-1 text-xs font-medium ${rfmColors[s.segment] || "bg-gray-100 text-gray-700"}`}>
                      {s.segment}
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="font-semibold">{s.customer_count?.toLocaleString() || s.count}</span>
                    <span className="ml-1 text-sm text-muted-foreground">customers</span>
                    <div className="text-xs text-muted-foreground">
                      €{Number(s.revenue || s.total_revenue || 0).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
              {(!customerRfm || customerRfm.length === 0) && (
                <p className="text-sm text-muted-foreground">No segment data available</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 6: Operational Insights ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Revenue by Day of Week */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Revenue by Day of Week</CardTitle>
            <CardDescription>Weekdays outperform weekends — typical B2B wholesale pattern</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Revenue by Day" description="Daily revenue pattern">
              <RechartsBarChart
                labels={revenueByDay?.map((d: any) => d.day_name) || []}
                datasets={[{ label: "Revenue", data: revenueByDay?.map((d: any) => Number(d.revenue)) || [] }]}
                height={300}
              />
            </ExpandableChart>
          </CardContent>
        </Card>

        {/* Product Class Distribution */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Revenue by Product Class</CardTitle>
            <CardDescription>How product tier/class contributes to total revenue</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Product Class" description="Revenue distribution by product class">
              <RechartsDoughnutChart
                labels={salesByClass?.map((c: any) => c.class_) || []}
                data={salesByClass?.map((c: any) => Number(c.revenue)) || []}
                height={300}
                formatValues
              />
            </ExpandableChart>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
