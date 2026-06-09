"use client";

import { useState, useEffect } from "react";
import { useBasketAnalysis } from "@/hooks/useBasketAnalysis";
import { DateRangeFilter } from "@/components/DateRangeFilter";
import { ExpandableChart } from "@/components/ExpandableChart";
import { FilterDialog } from "@/components/FilterDialog";
import { ChartFilterBar, type FilterOption } from "@/components/ChartFilterBar";
import { RechartsBarChart } from "@/components/charts/RechartsBarChart";
import { RechartsScatterChart } from "@/components/charts/RechartsScatterChart";
import { Slider } from "@/components/ui/slider";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardAction } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import { filtersApi } from "@/services/api";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { KPICard } from "@/components/KPICard";
import { ShoppingCart, Layers, TrendingUp, Filter } from "lucide-react";
import type { DashboardParams } from "@/services/api";

type ChartFilters = Record<string, string>;

export default function BasketAnalysisPage() {
  const [dateParams, setDateParams] = useState<DashboardParams>({});
  const [minSupport, setMinSupport] = useState(0.01);
  const [minLift, setMinLift] = useState(1.5);
  const [filterOptions, setFilterOptions] = useState<Record<string, string[]>>({});
  const [rulesFilters, setRulesFilters] = useState<ChartFilters>({});
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
      param: d, label: d.charAt(0).toUpperCase() + d.slice(1),
      options: filterOptions[d], value: f[d] ?? "__all__",
      onChange: (val: string) => setF({ ...f, [d]: val }),
    }));
  }

  const { data: analysis, isLoading } = useBasketAnalysis(minSupport, minLift, 50, dateParams);

  if (isLoading) return <LoadingSkeleton />;

  const BASKET_DIMS = ["category"];

  return (
    <div className="space-y-6">
      <DateRangeFilter title="Basket Analysis" onApply={setDateParams} />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard label="Total Transactions" value={analysis?.total_transactions || 0} format="number" icon={<ShoppingCart className="h-5 w-5" />} />
        <KPICard label="Association Rules Found" value={analysis?.rules?.length || 0} format="number" icon={<Layers className="h-5 w-5" />} />
        <KPICard label="Min Support" value={minSupport * 100} suffix="%" format="percentage" icon={<Filter className="h-5 w-5" />} />
        <KPICard label="Min Lift" value={minLift} format="number" icon={<TrendingUp className="h-5 w-5" />} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Analysis Thresholds</CardTitle>
          <CardDescription>Adjust the minimum support and lift values to filter association rules</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-10">
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-foreground">
                Min Support: <span className="text-primary font-semibold">{(minSupport * 100).toFixed(1)}%</span>
              </label>
              <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground">0.1%</span>
                <Slider
                  value={[minSupport]}
                  onValueChange={([v]) => setMinSupport(v)}
                  min={0.001}
                  max={0.1}
                  step={0.001}
                  className="w-40"
                />
                <span className="text-xs text-muted-foreground">10%</span>
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-foreground">
                Min Lift: <span className="text-primary font-semibold">{minLift.toFixed(1)}</span>
              </label>
              <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground">1.0</span>
                <Slider
                  value={[minLift]}
                  onValueChange={([v]) => setMinLift(v)}
                  min={1.0}
                  max={3.0}
                  step={0.1}
                  className="w-40"
                />
                <span className="text-xs text-muted-foreground">3.0</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card><CardHeader><CardTitle>Top 10 Product Associations (by Lift)</CardTitle><CardDescription>Highest lift values indicating strong product pairs</CardDescription>
          <CardAction><FilterDialog chartName="Top Associations" filters={chartFilters(rulesFilters, setRulesFilters, BASKET_DIMS)} /></CardAction>
        </CardHeader><CardContent>
          <ExpandableChart title="Top 10 Product Associations" description="Highest lift values indicating strong product pairs"
            filterControls={<ChartFilterBar filters={chartFilters(rulesFilters, setRulesFilters, BASKET_DIMS)} />}
          >
            <RechartsBarChart
              labels={analysis?.top_rules_by_lift?.slice(0, 10).map((r: any) => r.product1.split(" ").slice(0, 2).join(" ") + " - " + r.product2.split(" ").slice(0, 2).join(" ")) || []}
              datasets={[{ label: "Lift", data: analysis?.top_rules_by_lift?.slice(0, 10).map((r: any) => Number(r.lift)) || [] }]}
              height={320} horizontal />
          </ExpandableChart>
        </CardContent></Card>
        <Card><CardHeader><CardTitle>Support vs Lift Matrix</CardTitle><CardDescription>Relationship between rule support and lift values</CardDescription>
          <CardAction><FilterDialog chartName="Support vs Lift" filters={chartFilters(matrixFilters, setMatrixFilters, BASKET_DIMS)} /></CardAction>
        </CardHeader><CardContent>
          <ExpandableChart title="Support vs Lift Matrix" description="Relationship between rule support and lift values"
            filterControls={<ChartFilterBar filters={chartFilters(matrixFilters, setMatrixFilters, BASKET_DIMS)} />}
          >
            <RechartsScatterChart
              dataPoints={analysis?.matrix_data?.map((m: any) => ({ x: Number(m.support) * 100, y: Number(m.lift), label: m.label })) || []}
              xLabel="Support (%)" yLabel="Lift" height={320} />
          </ExpandableChart>
        </CardContent></Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Association Rules ({analysis?.rules?.length || 0} found)</CardTitle>
          <CardDescription>Product pairs frequently purchased together sorted by lift</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">#</TableHead>
                <TableHead>Product Pair</TableHead>
                <TableHead className="text-right">Support (%)</TableHead>
                <TableHead className="text-right">Confidence P1→P2 (%)</TableHead>
                <TableHead className="text-right">Confidence P2→P1 (%)</TableHead>
                <TableHead className="text-right">Lift</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {analysis?.rules?.slice(0, 20).map((rule: any, i: number) => (
                <TableRow key={i}>
                  <TableCell className="text-muted-foreground">{i + 1}</TableCell>
                  <TableCell className="font-medium">{rule.basket_label}</TableCell>
                  <TableCell className="text-right">{(Number(rule.support) * 100).toFixed(2)}%</TableCell>
                  <TableCell className="text-right">{(Number(rule.confidence_p1) * 100).toFixed(1)}%</TableCell>
                  <TableCell className="text-right">{(Number(rule.confidence_p2) * 100).toFixed(1)}%</TableCell>
                  <TableCell className="text-right"><Badge variant="secondary">{Number(rule.lift).toFixed(2)}</Badge></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
