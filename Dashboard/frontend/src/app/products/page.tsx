"use client";

import { useProducts, usePriceDistribution, usePriceVolumeMatrix } from "@/hooks/useProducts";
import { KPICard } from "@/components/KPICard";
import { BarChart } from "@/components/charts/BarChart";
import { ScatterChart } from "@/components/charts/ScatterChart";
import { DoughnutChart } from "@/components/charts/DoughnutChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { Package, DollarSign, AlertTriangle, Layers } from "lucide-react";

export default function ProductsPage() {
  const { data: products, isLoading: loadingProducts } = useProducts();
  const { data: priceDist, isLoading: loadingPrice } = usePriceDistribution();
  const { data: priceVolume, isLoading: loadingMatrix } = usePriceVolumeMatrix();

  if (loadingProducts || loadingPrice || loadingMatrix) return <LoadingSkeleton />;

  const totalProducts = products?.length || 0;
  const avgPrice = products && products.length > 0
    ? products.reduce((sum: number, p: any) => sum + Number(p.price), 0) / products.length : 0;
  const totalRevenue = products?.reduce((sum: number, p: any) => sum + Number(p.total_revenue), 0) || 0;
  const categories = [...new Set(products?.map((p: any) => p.category) || [])];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard label="Total Products" value={totalProducts} format="number" icon={<Package className="h-5 w-5" />} />
        <KPICard label="Average Price" value={avgPrice} format="currency" icon={<DollarSign className="h-5 w-5" />} />
        <KPICard label="Total Revenue" value={totalRevenue} format="currency" icon={<Layers className="h-5 w-5" />} />
        <KPICard label="Categories" value={categories.length} format="number" icon={<AlertTriangle className="h-5 w-5" />} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card><CardHeader><CardTitle>Price Distribution</CardTitle></CardHeader><CardContent>
          <BarChart labels={priceDist?.map((d: any) => d.range_label) || []}
            datasets={[{ label: "Product Count", data: priceDist?.map((d: any) => d.product_count) || [] }]} height={320} />
        </CardContent></Card>
        <Card><CardHeader><CardTitle>Revenue by Category</CardTitle></CardHeader><CardContent>
          <DoughnutChart
            labels={products?.reduce((acc: any, p: any) => { const e = acc.find((a: any) => a.label === p.category); if (e) e.value += Number(p.total_revenue); else acc.push({ label: p.category, value: Number(p.total_revenue) }); return acc; }, []).map((c: any) => c.label) || []}
            data={products?.reduce((acc: any, p: any) => { const e = acc.find((a: any) => a.label === p.category); if (e) e.value += Number(p.total_revenue); else acc.push({ label: p.category, value: Number(p.total_revenue) }); return acc; }, []).map((c: any) => c.value) || []}
            height={320} />
        </CardContent></Card>
      </div>

      <Card><CardHeader><CardTitle>Price vs Volume Matrix</CardTitle></CardHeader><CardContent>
        <ScatterChart
          dataPoints={priceVolume?.map((p: any) => ({ x: Number(p.price), y: Number(p.total_quantity), label: p.product_name, category: p.category })) || []}
          xLabel="Unit Price (€)" yLabel="Quantity Sold" height={400} />
      </CardContent></Card>
    </div>
  );
}
