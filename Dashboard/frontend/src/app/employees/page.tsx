"use client";

import { useState } from "react";
import {
  useTopEmployees,
  useEmployeePerformanceByAge,
  useEmployeePerformanceBySeniority,
  useEmployeeAgeCategory,
  useEmployeeGender,
  useEmployeeCaByAgeTranche,
  useEmployeePerformanceTable,
} from "@/hooks/useEmployees";
import { DateRangeFilter } from "@/components/DateRangeFilter";
import { ExpandableChart } from "@/components/ExpandableChart";
import { KPICard } from "@/components/KPICard";
import { RechartsBarChart } from "@/components/charts/RechartsBarChart";
import { RechartsDoughnutChart } from "@/components/charts/RechartsDoughnutChart";
import { RechartsComboChart } from "@/components/charts/RechartsComboChart";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { insightsApi, type DashboardParams } from "@/services/api";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { Briefcase, TrendingUp, DollarSign, Users, Award, BarChart3 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";

export default function EmployeesPage() {
  const [dateParams, setDateParams] = useState<DashboardParams>({});

  const { data: topEmployees, isLoading: loadingTop } = useTopEmployees(5, dateParams);
  const { data: byAge, isLoading: loadingAge } = useEmployeePerformanceByAge(dateParams);
  const { data: bySeniority, isLoading: loadingSeniority } = useEmployeePerformanceBySeniority(dateParams);
  const { data: ageCategoryDist } = useEmployeeAgeCategory();
  const { data: genderDist } = useEmployeeGender();
  const { data: caByAgeTranche } = useEmployeeCaByAgeTranche(dateParams);
  const { data: perfTable } = useEmployeePerformanceTable(dateParams);

  const { data: growthMetrics } = useQuery({
    queryKey: ["insights", "growth-metrics", dateParams],
    queryFn: () => insightsApi.getGrowthMetrics(dateParams),
    staleTime: 5 * 60 * 1000,
  });

  if (loadingTop || loadingAge || loadingSeniority) return <LoadingSkeleton />;

  const totalEmployees = byAge?.reduce((sum: number, a: any) => sum + a.employee_count, 0) || 0;
  const totalRevenue = topEmployees?.reduce((sum: number, e: any) => sum + Number(e.total_revenue), 0) || 0;
  const avgRevenue = totalEmployees > 0 && byAge && byAge.length > 0
    ? byAge.reduce((sum: number, a: any) => sum + Number(a.avg_revenue_per_employee), 0) / byAge.length : 0;
  const maleCount = genderDist?.find((g: any) => g.gender === "M")?.employee_count || 0;
  const femaleCount = genderDist?.find((g: any) => g.gender === "F")?.employee_count || 0;

  return (
    <div className="space-y-6">
      <DateRangeFilter title="Sales Team Performance" onApply={setDateParams} />

      {/* ═══ Row 1: Team KPIs ═══ */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard label="Total Employees" value={totalEmployees} format="number" icon={<Briefcase className="h-5 w-5" />} />
        <KPICard label="Total Revenue" value={totalRevenue} format="currency" icon={<DollarSign className="h-5 w-5" />} />
        <KPICard label="Avg Revenue / Employee" value={avgRevenue} format="currency" icon={<TrendingUp className="h-5 w-5" />} />
        <KPICard label="Revenue per Employee" value={totalEmployees > 0 ? totalRevenue / totalEmployees : 0} format="currency" icon={<Award className="h-5 w-5" />} />
      </div>

      {/* ═══ Row 2: Top Performers & Performance Table ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Top 5 Employees */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Top 5 Performing Employees</CardTitle>
            <CardDescription>Who generates the most revenue?</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Top 5 Employees" description="Highest revenue-generating employees">
              <RechartsBarChart
                labels={topEmployees?.map((e: any) => e.full_name?.split(" ")[0] || e.first_name) || []}
                datasets={[{ label: "Revenue Generated", data: topEmployees?.map((e: any) => Number(e.total_revenue)) || [] }]}
                height={320}
                horizontal
              />
            </ExpandableChart>
          </CardContent>
        </Card>

        {/* Employee Performance Table */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Employee Performance Overview</CardTitle>
            <CardDescription>All employees ranked by revenue with growth trend</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-[320px] overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Employee</TableHead>
                    <TableHead className="text-right">Revenue</TableHead>
                    <TableHead className="text-right">Growth</TableHead>
                    <TableHead className="text-right">Performance</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {perfTable?.map((e: any, i: number) => {
                    const growth = Number(e.ca_growth);
                    return (
                      <TableRow key={i}>
                        <TableCell className="font-medium">{e.full_name_emp}</TableCell>
                        <TableCell className="text-right">€{Number(e.total_revenue).toLocaleString()}</TableCell>
                        <TableCell className={`text-right ${growth >= 0 ? "text-green-600" : "text-red-600"}`}>
                          {growth >= 0 ? "↑" : "↓"} {Math.abs(growth).toFixed(1)}%
                        </TableCell>
                        <TableCell className="text-right">
                          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                            growth >= 10 ? "bg-green-100 text-green-700" :
                            growth >= 0 ? "bg-blue-100 text-blue-700" :
                            growth >= -10 ? "bg-amber-100 text-amber-700" :
                            "bg-red-100 text-red-700"
                          }`}>
                            {growth >= 10 ? "Star" : growth >= 0 ? "Stable" : growth >= -10 ? "Slowing" : "At Risk"}
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

      {/* ═══ Row 3: Team Demographics ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Employees by Age Category */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Team by Age Group</CardTitle>
            <CardDescription>Age distribution — understanding team experience levels</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Employees by Age Category" description="Employee count by age category">
              <RechartsDoughnutChart
                labels={ageCategoryDist?.map((a: any) => a.age_category) || []}
                data={ageCategoryDist?.map((a: any) => a.employee_count) || []}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>

        {/* Employees by Gender */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Team by Gender</CardTitle>
            <CardDescription>
              Workforce composition — {maleCount} male, {femaleCount} female
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Employees by Gender" description="Employee count by gender">
              <RechartsDoughnutChart
                labels={genderDist?.map((g: any) => g.gender === "M" ? "Male" : g.gender === "F" ? "Female" : g.gender) || []}
                data={genderDist?.map((g: any) => g.employee_count) || []}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 4: Performance by Demographics ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Revenue & Headcount by Age */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Revenue Contribution by Age Group</CardTitle>
            <CardDescription>Which age groups drive the business? Revenue (bars) vs headcount (line)</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="CA by Age Tranche" description="Revenue and employee count by age">
              <RechartsComboChart
                labels={caByAgeTranche?.map((a: any) => a.age_tranche) || []}
                bars={[{ label: "Total Revenue", data: caByAgeTranche?.map((a: any) => Number(a.total_revenue)) || [] }]}
                lines={[{ label: "Employee Count", data: caByAgeTranche?.map((a: any) => a.employee_count) || [] }]}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>

        {/* Average Revenue by Age Group */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Avg Revenue by Age Group</CardTitle>
            <CardDescription>Productivity per employee across age brackets</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Avg Revenue by Age Group" description="Average revenue per employee by age bracket">
              <RechartsBarChart
                labels={byAge?.map((a: any) => a.group_name) || []}
                datasets={[{ label: "Avg Revenue/Employee", data: byAge?.map((a: any) => Number(a.avg_revenue_per_employee)) || [] }]}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>
      </div>

      {/* ═══ Row 5: Seniority & Performance Insight ═══ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Avg Revenue by Seniority */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Performance by Seniority</CardTitle>
            <CardDescription>Does experience drive results? Avg revenue by tenure level</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpandableChart title="Avg Revenue by Seniority" description="Average revenue per employee by seniority level">
              <RechartsBarChart
                labels={bySeniority?.map((s: any) => s.group_name) || []}
                datasets={[{ label: "Avg Revenue/Employee", data: bySeniority?.map((s: any) => Number(s.avg_revenue_per_employee)) || [] }]}
                height={320}
              />
            </ExpandableChart>
          </CardContent>
        </Card>

        {/* Profit Margin Card */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle>Team Financial Impact</CardTitle>
            <CardDescription>How the sales team contributes to overall profitability</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border p-4">
              <div className="text-sm text-muted-foreground">Profit Margin</div>
              <div className="text-3xl font-bold text-green-600">
                {Number(growthMetrics?.profit_margin_pct || 0).toFixed(1)}%
              </div>
              <div className="mt-1 text-xs text-muted-foreground">
                of total revenue translates to profit
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border p-3">
                <div className="text-xs text-muted-foreground">Avg per Employee</div>
                <div className="text-lg font-semibold">€{avgRevenue.toLocaleString()}</div>
              </div>
              <div className="rounded-lg border p-3">
                <div className="text-xs text-muted-foreground">Total Profit</div>
                <div className="text-lg font-semibold">€{Number(growthMetrics?.total_profit || 0).toLocaleString()}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
