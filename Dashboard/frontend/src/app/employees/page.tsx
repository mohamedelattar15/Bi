"use client";

import {
  useTopEmployees,
  useEmployeePerformanceByAge,
  useEmployeePerformanceBySeniority,
} from "@/hooks/useEmployees";
import { KPICard } from "@/components/KPICard";
import { BarChart } from "@/components/charts/BarChart";
import { DoughnutChart } from "@/components/charts/DoughnutChart";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { Briefcase, TrendingUp, Users, DollarSign } from "lucide-react";

export default function EmployeesPage() {
  const { data: topEmployees, isLoading: loadingTop } = useTopEmployees(5);
  const { data: byAge, isLoading: loadingAge } = useEmployeePerformanceByAge();
  const { data: bySeniority, isLoading: loadingSeniority } =
    useEmployeePerformanceBySeniority();

  if (loadingTop || loadingAge || loadingSeniority) {
    return <LoadingSkeleton />;
  }

  const totalEmployees =
    byAge?.reduce(
      (sum: number, a: any) => sum + a.employee_count,
      0
    ) || 0;
  const totalRevenue =
    topEmployees?.reduce(
      (sum: number, e: any) => sum + Number(e.total_revenue),
      0
    ) || 0;
  const avgRevenue =
    totalEmployees > 0
      ? byAge?.reduce(
          (sum: number, a: any) => sum + Number(a.avg_revenue_per_employee),
          0
        ) / byAge?.length || 0
      : 0;

  return (
    <div className="space-y-6">
      {/* KPI Row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          label="Total Employees"
          value={totalEmployees}
          format="number"
          icon={<Briefcase className="h-5 w-5" />}
        />
        <KPICard
          label="Total Revenue"
          value={totalRevenue}
          format="currency"
          icon={<DollarSign className="h-5 w-5" />}
        />
        <KPICard
          label="Avg Revenue/Employee"
          value={avgRevenue}
          format="currency"
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <KPICard
          label="Active Employees"
          value={topEmployees?.length || 0}
          format="number"
          icon={<Users className="h-5 w-5" />}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <BarChart
            title="Top 5 Employees"
            labels={
              topEmployees?.map((e: any) => e.full_name.split(" ")[0]) ||
              []
            }
            datasets={[
              {
                label: "Revenue Generated",
                data:
                  topEmployees?.map((e: any) =>
                    Number(e.total_revenue)
                  ) || [],
              },
            ]}
            height={320}
            horizontal
          />
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <DoughnutChart
            title="Revenue Distribution"
            labels={
              topEmployees?.map((e: any) => e.full_name.split(" ")[0]) ||
              []
            }
            data={
              topEmployees?.map((e: any) =>
                Number(e.total_revenue)
              ) || []
            }
            height={320}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <BarChart
            title="Performance by Age Group"
            labels={byAge?.map((a: any) => a.group_name) || []}
            datasets={[
              {
                label: "Avg Revenue/Employee",
                data:
                  byAge?.map((a: any) =>
                    Number(a.avg_revenue_per_employee)
                  ) || [],
              },
            ]}
            height={320}
          />
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <BarChart
            title="Performance by Seniority"
            labels={
              bySeniority?.map((s: any) => s.group_name) || []
            }
            datasets={[
              {
                label: "Avg Revenue/Employee",
                data:
                  bySeniority?.map((s: any) =>
                    Number(s.avg_revenue_per_employee)
                  ) || [],
              },
            ]}
            height={320}
          />
        </div>
      </div>
    </div>
  );
}
