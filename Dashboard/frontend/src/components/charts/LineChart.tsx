"use client";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Line } from "react-chartjs-2";
import { formatCurrency } from "@/lib/utils";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface LineChartProps {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    borderColor?: string;
    backgroundColor?: string;
    fill?: boolean;
  }>;
  title?: string;
  height?: number;
}

export function LineChart({
  labels,
  datasets,
  title,
  height = 300,
}: LineChartProps) {
  const data = {
    labels,
    datasets: datasets.map((ds) => ({
      ...ds,
      borderColor: ds.borderColor || "#3b82f6",
      backgroundColor: ds.backgroundColor || "rgba(59, 130, 246, 0.1)",
      tension: 0.3,
      pointRadius: 3,
      pointHoverRadius: 6,
      fill: ds.fill ?? false,
    })),
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
      },
      title: title
        ? {
            display: true,
            text: title,
            font: { size: 14, weight: 600 },
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
        ticks: {
          callback: (value: any) => formatCurrency(value),
        },
      },
    },
  };

  return (
    <div style={{ height }}>
      <Line data={data} options={options} />
    </div>
  );
}
