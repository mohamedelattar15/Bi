"use client";

import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Doughnut } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);

interface DoughnutChartProps {
  labels: string[];
  data: number[];
  title?: string;
  height?: number;
}

const COLORS = [
  "rgba(59, 130, 246, 0.8)",
  "rgba(16, 185, 129, 0.8)",
  "rgba(245, 158, 11, 0.8)",
  "rgba(239, 68, 68, 0.8)",
  "rgba(139, 92, 246, 0.8)",
  "rgba(236, 72, 153, 0.8)",
  "rgba(14, 165, 233, 0.8)",
  "rgba(168, 85, 247, 0.8)",
];

export function DoughnutChart({
  labels,
  data: values,
  title,
  height = 300,
}: DoughnutChartProps) {
  const chartData = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: COLORS.slice(0, labels.length),
        borderColor: COLORS.map((c) => c.replace("0.8", "1")),
        borderWidth: 1,
        hoverOffset: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "right" as const,
        labels: {
          padding: 16,
          usePointStyle: true,
        },
      },
      title: title
        ? {
            display: true,
            text: title,
            font: { size: 14, weight: "600" as const },
          }
        : undefined,
    },
  };

  return (
    <div style={{ height }}>
      <Doughnut data={chartData} options={options} />
    </div>
  );
}
