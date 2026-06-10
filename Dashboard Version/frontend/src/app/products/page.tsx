"use client";

import { useState } from "react";
import { useProducts, usePriceDistribution, useCategoryGrowth, useProductQuantitySummary } from "@/hooks/useProducts";
import { useSalesByClass } from "@/hooks/useSales";
import { DateRangeFilter } from "@/components/DateRangeFilter";
import { ExpandableChart } from "@/components/ExpandableChart";
import { KPICard } from "@/components/KPICard";
import { RechartsBarChart } from "@/components/charts/RechartsBarChart";
import { RechartsDoughnutChart } from "@/components/charts/RechartsDoughnutChart";
import { RechartsTreemapChart } from "@/components/charts/RechartsTreemap";
import { RechartsComboChart } from "@/components/charts/RechartsComboChart";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { insightsApi, type DashboardParams } from "@/services/api";
import { Package, DollarSign, Layers, TrendingUp, Tags, BarChart3 } from "lucide-react";
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

export default function ProductsPage() {
  const [dateParams, setDateParams] = useState<DashboardParams>({});

  const { data: products, isLoading: loadingProducts } = useProducts(dateParams);
  const { data: priceDist } = usePriceDistribution(dateParams);
  const { data: categoryGrowth } = useCategoryGrowth(dateParams);
  const { data: quantitySummary } = useProductQuantitySummary(dateParams);
  const { data: salesByClass } = useSalesByClass(dateParams);

  // Business insights from API
  const { data: paretoProducts } = useQuery({
    queryKey: ["insights", "pareto-products", dateParams],
    queryFn: () => insightsApi.getParetoProducts(20, dateParams),
    staleTime: 5 * 60 * 1000,
  });
  const { data: revenueConcentration } = useQuery({
    queryKey: ["insights", "revenue-concentration"],
    queryFn: () => insightsApi.getRevenueConcentration(),
    staleTime: 10 * 60 * 1000,
  });

  if (loadingProducts) return <LoadingSkeleton />;

  const totalProducts = products?.length || 0;
  const avgPrice = products && products.length > 0
    ? products.reduce((sum: number, p: any) => sum + Number(p.price), 0) / products.length : 0;
  const totalRevenue = products?.reduce((sum: number, p: any) => sum + Number(p.total_revenue), 0) || 0;
  const categoryCount = revenueConcentration?.category_count || 0;

  // Build treemap data: category revenue
  const treemapData: Array<{ name: string; value: number }> = [];
  if (products) {
    const catMap: Record<string, number> = {};
    for (const p of products) {
      catMap[p.category] = (catMap[p.category] || 0) + Number(p.total_revenue);
    }
    for (const [name, value] of Object.entries(catMap)) {
      treemapData.push({ name, value });
    }
  }

  return (
    <div className="space-y-6">
      <DateRangeFilter title="Product Portfolio" onApply={setDateParams} />

      {/* ═══ Row 1: Product Portfolio KPIs ═══ */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        <KPICard label="Total Products" value={totalProducts} format="number" icon={<Package className="h-5 w-5" />} />
        <KPICard label="Categories" value={categoryCount} format="number" icon={<Tags className="h-5 w-5" />} />
        <KPICard label="Average Price" value={avgPrice} format="currency" icon={<DollarSign className="h-5 w-5" />} />
        <KPICard label="Total Revenue" value={totalRevenue} format="currency" icon={<Layers className="h-5 w-5" />} />
        <KPICard
          label="Top Category"
          value={Number(revenueConcentration?.top_category_pct || 0)}
          format="percentage"
          icon={<BarChart3 className="h-5 w-5" />}
        />
      </div>

      {/* ═══ Row 2: Category & Product Revenue Concentration ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Category Revenue Treemap */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Category Revenue Breakdown</CardTitle>
            <CardDescription>
              Revenue distribution across {categoryCount} categories —
              top category: <strong>{revenueConcentration?.top_category || "—"}</strong> at{" "}
              <strong>{Number(revenueConcentration?.top_category_pct || 0).toFixed(1)}%</strong>
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Category Revenue" description="Category contribution to total product revenue">
              <RechartsTreemapChart data={treemapData} height={320} />
            </ExpandableChart>
          </CardContent>
        </Card>

        {/* Top Products by Revenue (Pareto 80/20) */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Top Products by Revenue (80/20)</CardTitle>
            <CardDescription>
              Revenue concentration: <strong>{Number(revenueConcentration?.herfindahl_index || 0).toFixed(2)}</strong>
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
                    <TableHead className="text-right">%</TableHead>
                    <TableHead className="text-right">Cumulative</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paretoProducts?.slice(0, 15).map((p: any, i: number) => (
                    <TableRow key={i}>
                      <TableCell className="text-muted-foreground">{i + 1}</TableCell>
                      <TableCell className="max-w-[150px] truncate font-medium">{p.product_name}</TableCell>
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

      {/* ═══ Row 3: Category Growth & Product Class Mix ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Category Growth Rates */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Category Growth Rates</CardTitle>
            <CardDescription>Which categories are growing? Revenue and volume trends by category</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-[320px] overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">Revenue</TableHead>
                    <TableHead className="text-right">CA Growth</TableHead>
                    <TableHead className="text-right">Volume Growth</TableHead>
                    <TableHead className="text-right">Transaction Growth</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {categoryGrowth?.map((c: any, i: number) => (
                    <TableRow key={i}>
                      <TableCell className="font-medium">{c.category}</TableCell>
                      <TableCell className="text-right">€{Number(c.revenue).toLocaleString()}</TableCell>
                      <TableCell className={`text-right ${Number(c.ca_growth_pct) >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {Number(c.ca_growth_pct).toFixed(1)}%
                      </TableCell>
                      <TableCell className={`text-right ${Number(c.quant_growth_pct) >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {Number(c.quant_growth_pct).toFixed(1)}%
                      </TableCell>
                      <TableCell className={`text-right ${Number(c.transa_growth_pct) >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {Number(c.transa_growth_pct).toFixed(1)}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        {/* Revenue by Product Class */}
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

      {/* ═══ Row 4: Pricing & Volume Analysis ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Price Distribution */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Price Distribution</CardTitle>
            <CardDescription>Product count by price tier — where is your portfolio positioned?</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Price Distribution" description="Number of products by price range">
              <RechartsBarChart
                labels={priceDist?.map((d: any) => d.range_label) || []}
                datasets={[{ label: "Product Count", data: priceDist?.map((d: any) => d.product_count) || [] }]}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>

        {/* Top Products: Quantity vs Revenue */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Top Products: Volume vs Revenue</CardTitle>
            <CardDescription>Which products drive volume (bars) vs value (line)?</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Quantity vs Revenue" description="Top products by quantity and revenue">
              <RechartsComboChart
                labels={quantitySummary?.slice(0, 15).map((p: any) => p.product_name.substring(0, 15)) || []}
                bars={[{ label: "Quantity", data: quantitySummary?.slice(0, 15).map((p: any) => Number(p.total_quantity)) || [] }]}
                lines={[{ label: "Revenue (€M)", data: quantitySummary?.slice(0, 15).map((p: any) => Number(p.total_revenue) / 1_000_000) || [] }]}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
