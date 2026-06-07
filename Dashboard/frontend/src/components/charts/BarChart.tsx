"use client";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { formatCurrency } from "@/lib/utils";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface BarChartProps {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
  }>;
  title?: string;
  height?: number;
  horizontal?: boolean;
}

const CHART_COLORS = [
  "rgba(59, 130, 246, 0.8)",
  "rgba(16, 185, 129, 0.8)",
  "rgba(245, 158, 11, 0.8)",
  "rgba(239, 68, 68, 0.8)",
  "rgba(139, 92, 246, 0.8)",
  "rgba(236, 72, 153, 0.8)",
  "rgba(14, 165, 233, 0.8)",
  "rgba(168, 85, 247, 0.8)",
  "rgba(249, 115, 22, 0.8)",
  "rgba(34, 197, 94, 0.8)",
  "rgba(100, 116, 139, 0.8)",
];

export function BarChart({
  labels,
  datasets,
  title,
  height = 300,
  horizontal = false,
}: BarChartProps) {
  const data = {
    labels,
    datasets: datasets.map((ds, i) => ({
      ...ds,
      backgroundColor:
        ds.backgroundColor ||
        (Array.isArray(CHART_COLORS)
          ? CHART_COLORS.slice(0, labels.length)
          : CHART_COLORS[i % CHART_COLORS.length]),
      borderColor: ds.borderColor || "transparent",
      borderRadius: 4,
    })),
  };

  const options = {
    indexAxis: horizontal ? ("y" as const) : ("x" as const),
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
        display: datasets.length > 1,
      },
      title: title
        ? {
            display: true,
            text: title,
            font: { size: 14, weight: "600" as const },
          }
        : undefined,
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const value = context.raw as number;
            return `${context.dataset.label}: ${formatCurrency(value)}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ...(horizontal
          ? {}
          : {
              ticks: {
                callback: (value: any) => formatCurrency(value),
              },
            }),
      },
      x: {
        ...(horizontal
          ? {
              ticks: {
                callback: (value: any) => formatCurrency(value),
              },
            }
          : {}),
      },
    },
  };

  return (
    <div style={{ height }}>
      <Bar data={data} options={options} />
    </div>
  );
}
