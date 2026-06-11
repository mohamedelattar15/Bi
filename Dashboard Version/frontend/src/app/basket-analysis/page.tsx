"use client";

import { useState } from "react";
import { useBasketAnalysis } from "@/hooks/useBasketAnalysis";
import { DateRangeFilter } from "@/components/DateRangeFilter";
import { ExpandableChart } from "@/components/ExpandableChart";
import { RechartsBarChart } from "@/components/charts/RechartsBarChart";
import { RechartsScatterChart } from "@/components/charts/RechartsScatterChart";
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
import { ShoppingCart, Layers, TrendingUp, Filter, Lightbulb, Crosshair } from "lucide-react";
import type { DashboardParams } from "@/services/api";

export default function BasketAnalysisPage() {
  const [dateParams, setDateParams] = useState<DashboardParams>({});
  const [minSupport, setMinSupport] = useState(0.000001);
  const [minLift, setMinLift] = useState(0.0);

  const { data: analysis, isLoading } = useBasketAnalysis(minSupport, minLift, 50, dateParams);

  if (isLoading) return <LoadingSkeleton />;

  // Business insight helpers
  const totalRules = analysis?.rules?.length || 0;
  const strongRules = analysis?.rules?.filter((r: any) => Number(r.lift) > 2.0).length || 0;
  const highestLift = analysis?.rules?.length > 0
    ? Math.max(...analysis?.rules?.map((r: any) => Number(r.lift))) : 0;
  const topPair = analysis?.rules?.length > 0 ? analysis.rules[0] : null;

  return (
    <div className="space-y-6">
      <DateRangeFilter title="Cross-Sell Analysis — Basket Analysis" onApply={setDateParams} />

      {/* ═══ Row 1: Overview KPIs ═══ */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard label="Total Transactions Analyzed" value={analysis?.total_transactions || 0} format="number" icon={<ShoppingCart className="h-5 w-5" />} />
        <KPICard label="Products in Scope" value={analysis?.total_products || 0} format="number" icon={<Layers className="h-5 w-5" />} />
        <KPICard label="Association Rules Found" value={totalRules} format="number" icon={<Lightbulb className="h-5 w-5" />} />
        <KPICard label="Strong Rules (Lift &gt; 2)" value={strongRules} format="number" icon={<Crosshair className="h-5 w-5" />} />
      </div>

      {/* ═══ Row 2: Threshold Controls + Key Insight ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Controls */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Analysis Thresholds</CardTitle>
            <CardDescription>
              Adjust to filter which product associations are meaningful enough to act on
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-10">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground">
                  Minimum Support: <span className="text-primary font-semibold">{(minSupport * 100).toFixed(1)}%</span>
                </label>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground">0.001%</span>
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
                  Minimum Lift: <span className="text-primary font-semibold">{minLift.toFixed(1)}</span>
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
                <p className="text-xs text-muted-foreground">
                  How much more likely they&apos;re bought together vs independently
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Key Business Insight */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Cross-Sell Opportunity</CardTitle>
            <CardDescription>Top association insight based on current thresholds</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {topPair ? (
              <>
                <div className="rounded-lg border bg-gradient-to-r from-blue-50 to-indigo-50 p-4">
                  <div className="text-xs text-muted-foreground">STRONGEST ASSOCIATION</div>
                  <div className="mt-1 text-lg font-semibold">{topPair.basket_label}</div>
                  <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                    <div>
                      <div className="text-sm font-bold text-blue-600">{(Number(topPair.support) * 100).toFixed(2)}%</div>
                      <div className="text-xs text-muted-foreground">Support</div>
                    </div>
                    <div>
                      <div className="text-sm font-bold text-green-600">{(Number(topPair.confidence_p1) * 100).toFixed(1)}%</div>
                      <div className="text-xs text-muted-foreground">Confidence</div>
                    </div>
                    <div>
                      <div className="text-sm font-bold text-purple-600">{Number(topPair.lift).toFixed(2)}x</div>
                      <div className="text-xs text-muted-foreground">Lift</div>
                    </div>
                  </div>
                </div>
                <div className="rounded-lg border bg-amber-50 p-3">
                  <div className="flex items-start gap-2">
                    <Lightbulb className="mt-0.5 h-4 w-4 text-amber-600 shrink-0" />
                    <div>
                      <p className="text-sm text-amber-800">
                        <strong>Action:</strong> Customers buying these products together spend more.
                        Consider bundling, shelf placement, or targeted promotions.
                      </p>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex h-full items-center justify-center">
                <p className="text-sm text-muted-foreground">Adjust thresholds to find valid associations</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 3: Top Associations + Association Quality Matrix ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Top 10 by Lift */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Top 10 Product Pairs (by Lift)</CardTitle>
            <CardDescription>Which products are most strongly associated? Lift &gt; 1 = positive correlation</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Top 10 Product Associations" description="Highest lift values indicating strong product pairs">
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

        {/* Support vs Lift Matrix */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Association Quality Matrix</CardTitle>
            <CardDescription>
              Support (frequency) vs Lift (strength) — top-right quadrant = most actionable opportunities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Support vs Lift Matrix" description="Relationship between rule support and lift values">
              <RechartsScatterChart
                dataPoints={analysis?.matrix_data?.map((m: any) => ({ x: Number(m.support) * 100, y: Number(m.lift), label: m.label })) || []}
                xLabel="Support (%)" yLabel="Lift (strength of association)" height={320} />
            </ExpandableChart>
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 4: Full Association Rules Table ═══ */}
      <Card className="card-hover">
        <CardHeader>
          <CardTitle>Association Rules ({totalRules} found)</CardTitle>
          <CardDescription>
            Product pairs frequently purchased together — sorted by lift. Use these for cross-selling, bundling, and placement strategies.
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
                      <TableCell className="text-right">{(Number(rule.support) * 100).toFixed(2)}%</TableCell>
                      <TableCell className="text-right">{(Number(rule.confidence_p1) * 100).toFixed(1)}%</TableCell>
                      <TableCell className="text-right">{(Number(rule.confidence_p2) * 100).toFixed(1)}%</TableCell>
                      <TableCell className="text-right">
                        <Badge variant={lift >= 2 ? "default" : lift >= 1.5 ? "secondary" : "outline"}>
                          {lift.toFixed(2)}x
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        <span className={`text-xs font-medium ${
                          lift >= 2 ? "text-green-600" : lift >= 1.5 ? "text-amber-600" : "text-muted-foreground"
                        }`}>
                          {lift >= 2 ? "Strong" : lift >= 1.5 ? "Moderate" : "Weak"}
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
