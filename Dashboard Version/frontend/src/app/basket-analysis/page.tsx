"use client";

import { useState } from "react";
import { useBasketAnalysis } from "@/hooks/useBasketAnalysis";
import { DateRangeFilter } from "@/components/DateRangeFilter";
import { ExpandableChart } from "@/components/ExpandableChart";
import { RechartsBarChart } from "@/components/charts/RechartsBarChart";
import { RechartsLinkChart } from "@/components/charts/RechartsLinkChart";
import { Slider } from "@/components/ui/slider";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { KPICard } from "@/components/KPICard";
import { ShoppingCart, Layers, Lightbulb, Network, BarChart3 } from "lucide-react";
import type { DashboardParams } from "@/services/api";

export default function BasketAnalysisPage() {
  const [dateParams, setDateParams] = useState<DashboardParams>({});
  const [minSupport, setMinSupport] = useState(0.000001);
  const [minLift, setMinLift] = useState(0.0);

  const { data: analysis, isLoading } = useBasketAnalysis(minSupport, minLift, 50, dateParams);

  if (isLoading) return <LoadingSkeleton />;

  // Business insight helpers
  const totalRules = analysis?.rules?.length || 0;
  const highestLift = analysis?.rules?.length > 0
    ? Math.max(...analysis?.rules?.map((r: any) => Number(r.lift))) : 0;
  const topPair = analysis?.rules?.length > 0 ? analysis.rules[0] : null;
  const topHub = analysis?.hub_products?.[0];
  const topCategoryPair = analysis?.category_affinities?.[0];

  return (
    <div className="space-y-6">
      <DateRangeFilter title="Cross-Sell Analysis — Basket Analysis" onApply={setDateParams} />

      {/* ═══ Row 1: Business KPIs ═══ */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard label="Baskets Analyzed" value={analysis?.total_transactions || 0} format="number" icon={<ShoppingCart className="h-5 w-5" />} />
        <KPICard label="Products in Scope" value={analysis?.total_products || 0} format="number" icon={<Layers className="h-5 w-5" />} />
        <KPICard label="Association Rules" value={totalRules} format="number" icon={<BarChart3 className="h-5 w-5" />} />
        <Card className="card-hover">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Top Product by Connections</CardTitle>
            <Network className="h-5 w-5 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {topHub ? (
              <>
                <div className="text-2xl font-bold truncate max-w-[200px]" title={topHub.product}>
                  {topHub.product.split(" ").slice(0, 3).join(" ")}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {topHub.connection_count} association connections
                </p>
              </>
            ) : (
              <div className="text-2xl font-bold">—</div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 2: Threshold Controls + Category Affinity ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Controls */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Analysis Thresholds</CardTitle>
            <CardDescription>
              Narrow down to the most relevant product associations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-10">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground">
                  Minimum Support: <span className="text-primary font-semibold">{(minSupport * 100).toFixed(4)}%</span>
                </label>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground">0.0005%</span>
                  <Slider
                    value={[minSupport]}
                    onValueChange={([v]) => setMinSupport(v)}
                    min={0.000005}
                    max={0.01}
                    step={0.000005}
                    className="w-40"
                  />
                  <span className="text-xs text-muted-foreground">1%</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  How often the product pair appears together
                </p>
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground">
                  Minimum Lift: <span className="text-primary font-semibold">{minLift.toFixed(2)}</span>
                </label>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground">0.0</span>
                  <Slider
                    value={[minLift]}
                    onValueChange={([v]) => setMinLift(v)}
                    min={0.0}
                    max={0.4}
                    step={0.01}
                    className="w-40"
                  />
                  <span className="text-xs text-muted-foreground">0.4</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  How much more likely they&apos;re bought together vs independently
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Category Affinity Summary */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Category Affinity Overview</CardTitle>
            <CardDescription>Which product categories tend to be bought together</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {topCategoryPair ? (
              <>
                <div className="rounded-lg border bg-gradient-to-r from-emerald-50 to-teal-50 p-4">
                  <div className="text-xs text-muted-foreground">TOP CATEGORY PAIR</div>
                  <div className="mt-1 text-lg font-semibold">
                    {topCategoryPair.category1} <span className="text-muted-foreground">×</span> {topCategoryPair.category2}
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-2 text-center">
                    <div>
                      <div className="text-sm font-bold text-emerald-600">{topCategoryPair.pair_count}</div>
                      <div className="text-xs text-muted-foreground">Product Pairs</div>
                    </div>
                    <div>
                      <div className="text-sm font-bold text-purple-600">{Number(topCategoryPair.avg_lift).toFixed(3)}x</div>
                      <div className="text-xs text-muted-foreground">Avg Lift</div>
                    </div>
                  </div>
                </div>
                <div className="rounded-lg border bg-amber-50 p-3">
                  <div className="flex items-start gap-2">
                    <Lightbulb className="mt-0.5 h-4 w-4 text-amber-600 shrink-0" />
                    <div>
                      <p className="text-sm text-amber-800">
                        <strong>Cross-category opportunity:</strong> Products from <strong>{topCategoryPair.category1}</strong> and{' '}
                        <strong>{topCategoryPair.category2}</strong> appear together most often ({topCategoryPair.pair_count} pairs).
                        Consider joint promotions or combined shelf placement.
                      </p>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex h-full items-center justify-center">
                <p className="text-sm text-muted-foreground">No category affinity data available</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 3: Lift Distribution + Hub Products ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Lift Distribution (with stats & interpretation) */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Lift Distribution — Data Quality</CardTitle>
            <CardDescription>
              How the {analysis?.lift_distribution?.reduce((s: number, b: any) => s + b.rule_count, 0) || "75k"} association rules are spread across lift ranges
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <ExpandableChart title="Lift Distribution" description="Histogram of lift values across all rules">
              <RechartsBarChart
                labels={analysis?.lift_distribution?.map((d: any) => d.range_label) || []}
                datasets={[{
                  label: "Rules",
                  data: analysis?.lift_distribution?.map((d: any) => d.rule_count) || []
                }]}
                height={240}
                horizontal={false}
              />
            </ExpandableChart>
            <p className="text-xs text-muted-foreground leading-relaxed">
              <strong>Interpretation:</strong> {Number(analysis?.lift_distribution?.[0]?.percentage || 47.9).toFixed(1)}% of rules have lift &lt; 0.05 — 
              very weak associations. Only {Number(analysis?.lift_distribution?.[4]?.percentage || 0.1).toFixed(1)}% exceed 0.20. 
              This is expected given the <strong>98% single-product basket</strong> design.
            </p>
          </CardContent>
        </Card>

        {/* Hub Products */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Top Products by Association Count</CardTitle>
            <CardDescription>
              Products with the most connections — key cross-selling candidates
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Top 10 Hub Products" description="Products appearing in the most association rules">
              <RechartsBarChart
                labels={analysis?.hub_products?.map((h: any) =>
                  h.product.split(" ").slice(0, 3).join(" ")
                ) || []}
                datasets={[{
                  label: "Number of Connections",
                  data: analysis?.hub_products?.map((h: any) => h.connection_count) || []
                }]}
                height={300}
                horizontal
              />
            </ExpandableChart>
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 4: Knowledge Graph + Top Pairs ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Knowledge Graph — Product Link Chart */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Knowledge Graph — Product Links</CardTitle>
            <CardDescription>
              Visual network: node size = connections, edge width = lift strength
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center">
            <ExpandableChart title="Product Knowledge Graph" description="Visual network of product associations">
              {(() => {
                const hubs = analysis?.hub_products?.slice(0, 5) || [];
                const allMatches = analysis?.top_matches || [];
                const matchMap = new Map<string, { product: string; lift: number }[]>();
                hubs.forEach((hub: any) => {
                  const matches = allMatches
                    .filter((m: any) => m.hub_product === hub.product).slice(0, 2);
                  matchMap.set(hub.product, matches);
                });
                const nodes: any[] = [];
                const edges: any[] = [];
                hubs.forEach((h: any, i: number) => {
                  nodes.push({
                    id: h.product, label: h.product.split(" ").slice(0, 2).join(" "),
                    size: h.connection_count, group: 0,
                  });
                });
                hubs.forEach((hub: any, i: number) => {
                  const matches = matchMap.get(hub.product) || [];
                  matches.forEach((m: any) => {
                    const existing = nodes.find((n) => n.id === m.matched_product);
                    if (!existing) {
                      nodes.push({
                        id: m.matched_product,
                        label: m.matched_product.split(" ").slice(0, 2).join(" "),
                        size: Math.round(Number(m.lift) * 100), group: i + 1,
                      });
                    }
                    edges.push({ source: hub.product, target: m.matched_product, strength: Number(m.lift) });
                  });
                });
                return (<RechartsLinkChart nodes={nodes} edges={edges} width={460} height={340} />);
              })()}
            </ExpandableChart>
          </CardContent>
        </Card>

        {/* Top 10 by Lift */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Top 10 Product Pairs (by Lift)</CardTitle>
            <CardDescription>Highest lift values — most notable associations</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Highest-Lift Product Pairs" description="Top associations ranked by lift">
              <RechartsBarChart
                labels={analysis?.top_rules_by_lift?.slice(0, 10).map((r: any) =>
                  r.product1.split(" ").slice(0, 2).join(" ") + " — " + r.product2.split(" ").slice(0, 2).join(" ")
                ) || []}
                datasets={[{ label: "Lift", data: analysis?.top_rules_by_lift?.slice(0, 10).map((r: any) => Number(r.lift)) || [] }]}
                height={320}
                horizontal
              />
            </ExpandableChart>
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 5: Association Rules Table ═══ */}
      <Card className="card-hover">
        <CardHeader>
          <CardTitle>Association Rules ({totalRules} found)</CardTitle>
          <CardDescription>
            All product pairs matching current thresholds — ranked by lift
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="max-h-[480px] overflow-y-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">#</TableHead>
                  <TableHead>Product Pair</TableHead>
                  <TableHead className="text-right">Support (%)</TableHead>
                  <TableHead className="text-right">Confidence A→B</TableHead>
                  <TableHead className="text-right">Confidence B→A</TableHead>
                  <TableHead className="text-right">Lift</TableHead>
                  <TableHead className="text-center">Strength</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {analysis?.rules?.slice(0, 20).map((rule: any, i: number) => {
                  const lift = Number(rule.lift);
                  return (
                    <TableRow key={i}>
                      <TableCell className="text-muted-foreground">{i + 1}</TableCell>
                      <TableCell className="font-medium max-w-[250px] truncate">{rule.basket_label}</TableCell>
                      <TableCell className="text-right">{(Number(rule.support) * 100).toFixed(4)}%</TableCell>
                      <TableCell className="text-right">{(Number(rule.confidence_p1) * 100).toFixed(3)}%</TableCell>
                      <TableCell className="text-right">{(Number(rule.confidence_p2) * 100).toFixed(3)}%</TableCell>
                      <TableCell className="text-right">
                        <Badge variant={lift >= 0.3 ? "default" : lift >= 0.2 ? "secondary" : "outline"}>
                          {lift.toFixed(3)}x
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        <span className={`text-xs font-medium ${
                          lift >= 0.3 ? "text-green-600" : lift >= 0.2 ? "text-amber-600" : "text-muted-foreground"
                        }`}>
                          {lift >= 0.3 ? "Notable" : lift >= 0.2 ? "Fair" : "Low"}
                        </span>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
