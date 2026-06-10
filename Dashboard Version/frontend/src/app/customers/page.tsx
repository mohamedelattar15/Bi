"use client";

import { useState } from "react";
import {
  useCustomerSegments,
  useTopCustomers,
  useCustomerActivity,
  useAvgBasketByCity,
  useCustomerGrowthByCity,
  useCustomerLoyaltyStats,
} from "@/hooks/useCustomers";
import { DateRangeFilter } from "@/components/DateRangeFilter";
import { ExpandableChart } from "@/components/ExpandableChart";
import { KPICard } from "@/components/KPICard";
import { RechartsBarChart } from "@/components/charts/RechartsBarChart";
import { RechartsDoughnutChart } from "@/components/charts/RechartsDoughnutChart";
import { RechartsComboChart } from "@/components/charts/RechartsComboChart";
import { RechartsTreemapChart } from "@/components/charts/RechartsTreemap";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { insightsApi, type DashboardParams } from "@/services/api";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { Users, UserCheck, TrendingUp, DollarSign, Heart, RefreshCw, MapPin, Award } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";

export default function CustomersPage() {
  const [dateParams, setDateParams] = useState<DashboardParams>({});

  const { data: segments, isLoading: loadingSegments } = useCustomerSegments();
  const { data: topCustomers, isLoading: loadingTop } = useTopCustomers(10);
  const { data: activity, isLoading: loadingActivity } = useCustomerActivity(dateParams);
  const { data: avgBasketByCity } = useAvgBasketByCity(dateParams);
  const { data: growthByCity } = useCustomerGrowthByCity(dateParams);
  const { data: loyaltyStats } = useCustomerLoyaltyStats(dateParams);

  const { data: growthMetrics } = useQuery({
    queryKey: ["insights", "growth-metrics", dateParams],
    queryFn: () => insightsApi.getGrowthMetrics(dateParams),
    staleTime: 5 * 60 * 1000,
  });

  if (loadingSegments || loadingTop || loadingActivity) return <LoadingSkeleton />;

  const totalCustomers = segments?.reduce((sum: number, s: any) => sum + s.customer_count, 0) || 0;
  const totalRevenue = segments?.reduce((sum: number, s: any) => sum + Number(s.total_revenue), 0) || 0;
  const avgBasket = segments && segments.length > 0
    ? segments.reduce((sum: number, s: any) => sum + Number(s.avg_basket), 0) / segments.length : 0;
  const repurchaseRate = Number(loyaltyStats?.repurchase_rate || 0);
  const activeCustomers = loyaltyStats?.active_customers || 0;
  const loyaltyRate = totalCustomers > 0 ? (activeCustomers / totalCustomers * 100) : 0;

  return (
    <div className="space-y-6">
      <DateRangeFilter title="Customer Performance" onApply={setDateParams} />

      {/* ═══ Row 1: Customer KPIs ═══ */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <KPICard label="Total Customers" value={totalCustomers} format="number" icon={<Users className="h-5 w-5" />} />
        <KPICard label="Active Customers" value={activeCustomers} format="number" icon={<UserCheck className="h-5 w-5" />} />
        <KPICard label="Loyalty Rate" value={loyaltyRate} format="percentage" icon={<Heart className="h-5 w-5" />} />
        <KPICard label="Avg Basket" value={avgBasket} format="currency" icon={<TrendingUp className="h-5 w-5" />} />
        <KPICard label="Total Revenue" value={totalRevenue} format="currency" icon={<DollarSign className="h-5 w-5" />} />
        <KPICard label="Repurchase Rate" value={repurchaseRate} format="percentage" icon={<RefreshCw className="h-5 w-5" />} />
      </div>

      {/* ═══ Row 2: Customer Segmentation & Top Customers ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Customer Segmentation */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Customer Segmentation</CardTitle>
            <CardDescription>Breakdown of {totalCustomers.toLocaleString()} customers by segment</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Customer Segmentation" description="Customer count by segment">
              <RechartsDoughnutChart
                labels={segments?.map((s: any) => s.segment) || []}
                data={segments?.map((s: any) => Number(s.customer_count)) || []}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>

        {/* Top Customers by Revenue */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Top Customers by Revenue</CardTitle>
            <CardDescription>Your most valuable customers — who to nurture</CardDescription>
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
      </div>

      {/* ═══ Row 3: Customer Activity & Geographic Revenue ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Active Customers × Revenue Combo */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Active Customers & Revenue Trend</CardTitle>
            <CardDescription>Active customer base (bars) vs revenue (line) over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Customers & Revenue" description="Active customers vs revenue trend">
              <RechartsComboChart
                labels={activity?.map((a: any) => `${a.month_name || a.month} ${a.year}`) || []}
                bars={[{ label: "Active Customers", data: activity?.map((a: any) => a.active_customers) || [], color: "var(--chart-2)" }]}
                lines={[{ label: "Revenue (€M)", data: activity?.map((a: any) => Number(a.total_revenue) / 1_000_000) || [], color: "var(--chart-1)" }]}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>

        {/* Revenue by City Treemap */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Revenue by City</CardTitle>
            <CardDescription>Geographic contribution — which cities drive the business</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Revenue by City" description="City contribution to total revenue">
              <RechartsTreemapChart
                data={(avgBasketByCity || []).slice(0, 15).map((c: any) => ({ name: c.city, value: Number(c.total_revenue) }))}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 4: Geographic Performance Details ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Avg Basket by City */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Avg Basket by City</CardTitle>
            <CardDescription>Which cities have the highest spend per visit?</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Avg Basket by City" description="Average basket value by city">
              <RechartsBarChart
                labels={avgBasketByCity?.slice(0, 10).map((c: any) => c.city) || []}
                datasets={[{ label: "Avg Basket (€)", data: avgBasketByCity?.slice(0, 10).map((c: any) => Number(c.avg_basket)) || [] }]}
                height={320}
                horizontal
              />
            </ExpandableChart>
          </CardContent>
        </Card>

        {/* Growth by City Table */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>City Growth Overview</CardTitle>
            <CardDescription>Which cities are growing or declining? Revenue, transaction & volume trends</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-[320px] overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>City</TableHead>
                    <TableHead className="text-right">Revenue</TableHead>
                    <TableHead className="text-right">CA Growth</TableHead>
                    <TableHead className="text-right">Transactions</TableHead>
                    <TableHead className="text-right">Volume</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {growthByCity?.slice(0, 10).map((c: any, i: number) => (
                    <TableRow key={i}>
                      <TableCell className="font-medium">{c.city}</TableCell>
                      <TableCell className="text-right">€{Number(c.revenue).toLocaleString()}</TableCell>
                      <TableCell className={`text-right ${Number(c.ca_growth_pct) >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {Number(c.ca_growth_pct).toFixed(1)}%
                      </TableCell>
                      <TableCell className={`text-right ${Number(c.transa_growth_pct) >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {Number(c.transa_growth_pct).toFixed(1)}%
                      </TableCell>
                      <TableCell className={`text-right ${Number(c.quant_growth_pct) >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {Number(c.quant_growth_pct).toFixed(1)}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 5: Customer Health Summary ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Segment Value Breakdown */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Segment Value Breakdown</CardTitle>
            <CardDescription>Average basket and total revenue by customer segment</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-[320px] overflow-y-auto space-y-2">
              {segments?.map((s: any, i: number) => (
                <div key={i} className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <span className="font-medium">{s.segment}</span>
                    <span className="ml-2 text-sm text-muted-foreground">
                      {s.customer_count?.toLocaleString()} customers
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold">€{Number(s.avg_basket).toFixed(2)} avg</div>
                    <div className="text-xs text-muted-foreground">
                      €{Number(s.total_revenue || 0).toLocaleString()} total
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Customer Health Dashboard */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Customer Health Dashboard</CardTitle>
            <CardDescription>Key loyalty and retention metrics at a glance</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border p-4 text-center">
                <div className="text-xs text-muted-foreground">Loyalty Rate</div>
                <div className="text-2xl font-bold text-green-600">{loyaltyRate.toFixed(1)}%</div>
                <div className="text-xs text-muted-foreground">{activeCustomers.toLocaleString()} active</div>
              </div>
              <div className="rounded-lg border p-4 text-center">
                <div className="text-xs text-muted-foreground">Repurchase Rate</div>
                <div className="text-2xl font-bold text-blue-600">{repurchaseRate.toFixed(1)}%</div>
                <div className="text-xs text-muted-foreground">repeat buyers</div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border p-4 text-center">
                <div className="text-xs text-muted-foreground">Avg Frequency</div>
                <div className="text-2xl font-bold text-amber-600">{Number(loyaltyStats?.avg_frequency || 0).toFixed(1)}</div>
                <div className="text-xs text-muted-foreground">purchases/customer</div>
              </div>
              <div className="rounded-lg border p-4 text-center">
                <div className="text-xs text-muted-foreground">Avg Basket</div>
                <div className="text-2xl font-bold text-purple-600">€{avgBasket.toFixed(2)}</div>
                <div className="text-xs text-muted-foreground">per transaction</div>
              </div>
            </div>
            <div className="rounded-lg border bg-gradient-to-r from-green-50 to-blue-50 p-4 text-center">
              <div className="text-xs text-muted-foreground">Customer Profitability</div>
              <div className="text-lg font-semibold">
                €{totalCustomers > 0 ? (Number(growthMetrics?.total_profit || 0) / totalCustomers).toFixed(2) : "0.00"}
                <span className="text-sm font-normal text-muted-foreground"> profit per customer</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
