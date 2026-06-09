"use client";

import { useState, useEffect } from "react";
import {
  useTopEmployees,
  useEmployeePerformanceByAge,
  useEmployeePerformanceBySeniority,
} from "@/hooks/useEmployees";
import { DateRangeFilter } from "@/components/DateRangeFilter";
import { ExpandableChart } from "@/components/ExpandableChart";
import { FilterDialog } from "@/components/FilterDialog";
import { ChartFilterBar, type FilterOption } from "@/components/ChartFilterBar";
import { KPICard } from "@/components/KPICard";
import { RechartsBarChart } from "@/components/charts/RechartsBarChart";
import { RechartsDoughnutChart } from "@/components/charts/RechartsDoughnutChart";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardAction } from "@/components/ui/card";
import { filtersApi } from "@/services/api";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { Briefcase, TrendingUp, Users, DollarSign } from "lucide-react";
import type { DashboardParams } from "@/services/api";

type ChartFilters = Record<string, string>;

const GENDER_DIMS = ["category"];

export default function EmployeesPage() {
  const [dateParams, setDateParams] = useState<DashboardParams>({});
  const [filterOptions, setFilterOptions] = useState<Record<string, string[]>>({});
  const [topEmpFilters, setTopEmpFilters] = useState<ChartFilters>({});
  const [ageFilters, setAgeFilters] = useState<ChartFilters>({});
  const [seniorityFilters, setSeniorityFilters] = useState<ChartFilters>({});

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

  const { data: topEmployees, isLoading: loadingTop } = useTopEmployees(5, dateParams);
  const { data: byAge, isLoading: loadingAge } = useEmployeePerformanceByAge(dateParams);
  const { data: bySeniority, isLoading: loadingSeniority } = useEmployeePerformanceBySeniority(dateParams);

  if (loadingTop || loadingAge || loadingSeniority) return <LoadingSkeleton />;

  const totalEmployees = byAge?.reduce((sum: number, a: any) => sum + a.employee_count, 0) || 0;
  const totalRevenue = topEmployees?.reduce((sum: number, e: any) => sum + Number(e.total_revenue), 0) || 0;
  const avgRevenue = totalEmployees > 0 && byAge && byAge.length > 0
    ? byAge.reduce((sum: number, a: any) => sum + Number(a.avg_revenue_per_employee), 0) / byAge.length : 0;

  return (
    <div className="space-y-6">
      <DateRangeFilter title="Employee Analysis" onApply={setDateParams} />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard label="Total Employees" value={totalEmployees} format="number" icon={<Briefcase className="h-5 w-5" />} />
        <KPICard label="Total Revenue" value={totalRevenue} format="currency" icon={<DollarSign className="h-5 w-5" />} />
        <KPICard label="Avg Revenue/Employee" value={avgRevenue} format="currency" icon={<TrendingUp className="h-5 w-5" />} />
        <KPICard label="Active Employees" value={topEmployees?.length || 0} format="number" icon={<Users className="h-5 w-5" />} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card><CardHeader><CardTitle>Top 5 Employees</CardTitle><CardDescription>Highest revenue-generating employees</CardDescription>
          <CardAction><FilterDialog chartName="Top 5 Employees" filters={chartFilters(topEmpFilters, setTopEmpFilters, GENDER_DIMS)} /></CardAction>
        </CardHeader><CardContent>
          <ExpandableChart title="Top 5 Employees" description="Highest revenue-generating employees"
            filterControls={<ChartFilterBar filters={chartFilters(topEmpFilters, setTopEmpFilters, GENDER_DIMS)} />}
          >
            <RechartsBarChart labels={topEmployees?.map((e: any) => e.full_name.split(" ")[0]) || []}
              datasets={[{ label: "Revenue Generated", data: topEmployees?.map((e: any) => Number(e.total_revenue)) || [] }]} height={320} horizontal />
          </ExpandableChart>
        </CardContent></Card>
        <Card><CardHeader><CardTitle>Revenue Distribution</CardTitle><CardDescription>Revenue share among top performers</CardDescription></CardHeader><CardContent>
          <ExpandableChart title="Revenue Distribution" description="Revenue share among top performers">
            <RechartsDoughnutChart labels={topEmployees?.map((e: any) => e.full_name.split(" ")[0]) || []}
              data={topEmployees?.map((e: any) => Number(e.total_revenue)) || []} height={320} formatValues />
          </ExpandableChart>
        </CardContent></Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card><CardHeader><CardTitle>Performance by Age Group</CardTitle><CardDescription>Average revenue per employee by age bracket</CardDescription>
          <CardAction><FilterDialog chartName="Performance by Age" filters={chartFilters(ageFilters, setAgeFilters, GENDER_DIMS)} /></CardAction>
        </CardHeader><CardContent>
          <ExpandableChart title="Performance by Age Group" description="Average revenue per employee by age bracket"
            filterControls={<ChartFilterBar filters={chartFilters(ageFilters, setAgeFilters, GENDER_DIMS)} />}
          >
            <RechartsBarChart labels={byAge?.map((a: any) => a.group_name) || []}
              datasets={[{ label: "Avg Revenue/Employee", data: byAge?.map((a: any) => Number(a.avg_revenue_per_employee)) || [] }]} height={320} />
          </ExpandableChart>
        </CardContent></Card>
        <Card><CardHeader><CardTitle>Performance by Seniority</CardTitle><CardDescription>Average revenue per employee by seniority level</CardDescription>
          <CardAction><FilterDialog chartName="Performance by Seniority" filters={chartFilters(seniorityFilters, setSeniorityFilters, GENDER_DIMS)} /></CardAction>
        </CardHeader><CardContent>
          <ExpandableChart title="Performance by Seniority" description="Average revenue per employee by seniority level"
            filterControls={<ChartFilterBar filters={chartFilters(seniorityFilters, setSeniorityFilters, GENDER_DIMS)} />}
          >
            <RechartsBarChart labels={bySeniority?.map((s: any) => s.group_name) || []}
              datasets={[{ label: "Avg Revenue/Employee", data: bySeniority?.map((s: any) => Number(s.avg_revenue_per_employee)) || [] }]} height={320} />
          </ExpandableChart>
        </CardContent></Card>
      </div>
    </div>
  );
}
