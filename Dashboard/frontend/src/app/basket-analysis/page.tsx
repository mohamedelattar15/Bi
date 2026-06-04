"use client";

import { useState } from "react";
import { useBasketAnalysis } from "@/hooks/useBasketAnalysis";
import { BarChart } from "@/components/charts/BarChart";
import { ScatterChart } from "@/components/charts/ScatterChart";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { KPICard } from "@/components/KPICard";
import { ShoppingCart, Layers, TrendingUp, Filter } from "lucide-react";

export default function BasketAnalysisPage() {
  const [minSupport, setMinSupport] = useState(0.01);
  const [minLift, setMinLift] = useState(1.5);

  const { data: analysis, isLoading, error } = useBasketAnalysis(
    minSupport,
    minLift,
    50
  );

  if (isLoading) return <LoadingSkeleton />;

  return (
    <div className="space-y-6">
      {/* KPI Row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          label="Total Transactions"
          value={analysis?.total_transactions || 0}
          format="number"
          icon={<ShoppingCart className="h-5 w-5" />}
        />
        <KPICard
          label="Association Rules Found"
          value={analysis?.rules?.length || 0}
          format="number"
          icon={<Layers className="h-5 w-5" />}
        />
        <KPICard
          label="Min Support"
          value={minSupport * 100}
          suffix="%"
          format="percentage"
          icon={<Filter className="h-5 w-5" />}
        />
        <KPICard
          label="Min Lift"
          value={minLift}
          format="number"
          icon={<TrendingUp className="h-5 w-5" />}
        />
      </div>

      {/* Filter Controls */}
      <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
        <h3 className="mb-4 text-sm font-semibold text-gray-700">
          Analysis Thresholds
        </h3>
        <div className="flex flex-wrap gap-6">
          <div className="flex items-center gap-3">
            <label className="text-sm text-gray-600">
              Min Support: {(minSupport * 100).toFixed(1)}%
            </label>
            <input
              type="range"
              min="0.001"
              max="0.1"
              step="0.001"
              value={minSupport}
              onChange={(e) => setMinSupport(Number(e.target.value))}
              className="w-32"
            />
          </div>
          <div className="flex items-center gap-3">
            <label className="text-sm text-gray-600">
              Min Lift: {minLift.toFixed(1)}
            </label>
            <input
              type="range"
              min="1.0"
              max="3.0"
              step="0.1"
              value={minLift}
              onChange={(e) => setMinLift(Number(e.target.value))}
              className="w-32"
            />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <BarChart
            title="Top 10 Product Associations (by Lift)"
            labels={
              analysis?.top_rules_by_lift
                ?.slice(0, 10)
                .map(
                  (r: any) =>
                    r.product1.split(" ").slice(0, 2).join(" ") +
                    " - " +
                    r.product2.split(" ").slice(0, 2).join(" ")
                ) || []
            }
            datasets={[
              {
                label: "Lift",
                data:
                  analysis?.top_rules_by_lift
                    ?.slice(0, 10)
                    .map((r: any) => Number(r.lift)) || [],
              },
            ]}
            height={320}
            horizontal
          />
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <ScatterChart
            title="Support vs Lift Matrix"
            dataPoints={
              analysis?.matrix_data?.map((m: any) => ({
                x: Number(m.support) * 100,
                y: Number(m.lift),
                label: m.label,
              })) || []
            }
            xLabel="Support (%)"
            yLabel="Lift"
            height={320}
          />
        </div>
      </div>

      {/* Rules Table */}
      <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
        <h3 className="mb-4 text-sm font-semibold text-gray-700">
          Association Rules ({analysis?.rules?.length || 0} found)
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 font-medium text-gray-600">#</th>
                <th className="px-4 py-3 font-medium text-gray-600">
                  Product Pair
                </th>
                <th className="px-4 py-3 font-medium text-gray-600">
                  Support (%)
                </th>
                <th className="px-4 py-3 font-medium text-gray-600">
                  Confidence P1→P2 (%)
                </th>
                <th className="px-4 py-3 font-medium text-gray-600">
                  Confidence P2→P1 (%)
                </th>
                <th className="px-4 py-3 font-medium text-gray-600">Lift</th>
              </tr>
            </thead>
            <tbody>
              {analysis?.rules?.slice(0, 20).map((rule: any, i: number) => (
                <tr
                  key={i}
                  className="border-b border-gray-100 transition-colors hover:bg-gray-50"
                >
                  <td className="px-4 py-3 text-gray-500">{i + 1}</td>
                  <td className="px-4 py-3 font-medium text-gray-800">
                    {rule.basket_label}
                  </td>
                  <td className="px-4 py-3">
                    {(Number(rule.support) * 100).toFixed(2)}%
                  </td>
                  <td className="px-4 py-3">
                    {(Number(rule.confidence_p1) * 100).toFixed(1)}%
                  </td>
                  <td className="px-4 py-3">
                    {(Number(rule.confidence_p2) * 100).toFixed(1)}%
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-blue-50 px-2 py-1 text-sm font-semibold text-blue-700">
                      {Number(rule.lift).toFixed(2)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
