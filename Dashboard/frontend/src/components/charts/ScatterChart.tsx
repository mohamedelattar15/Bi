"use client";

import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Scatter } from "react-chartjs-2";
import { formatCurrency } from "@/lib/utils";

ChartJS.register(LinearScale, PointElement, Tooltip, Legend);

interface ScatterDataPoint {
  x: number;
  y: number;
  r?: number;
}

interface ScatterChartProps {
  dataPoints: Array<{
    x: number;
    y: number;
    label: string;
    category?: string;
  }>;
  xLabel?: string;
  yLabel?: string;
  title?: string;
  height?: number;
}

const COLORS = [
  "rgba(59, 130, 246, 0.7)",
  "rgba(16, 185, 129, 0.7)",
  "rgba(245, 158, 11, 0.7)",
  "rgba(239, 68, 68, 0.7)",
  "rgba(139, 92, 246, 0.7)",
];

export function ScatterChart({
  dataPoints,
  xLabel = "X",
  yLabel = "Y",
  title,
  height = 300,
}: ScatterChartProps) {
  const data = {
    datasets: [
      {
        label: "Products",
        data: dataPoints.map((p) => ({ x: p.x, y: p.y } as ScatterDataPoint)),
        backgroundColor: COLORS[0],
        pointRadius: 6,
        pointHoverRadius: 10,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
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
            const point = dataPoints[context.dataIndex];
            return `${point.label}: ${formatCurrency(context.parsed.x)} (Price), ${context.parsed.y} (Qty)`;
          },
        },
      },
    },
    scales: {
      x: {
        title: { display: true, text: xLabel },
        ticks: {
          callback: (value: any) => formatCurrency(value),
        },
      },
      y: {
        title: { display: true, text: yLabel },
        beginAtZero: true,
      },
    },
  };

  return (
    <div style={{ height }}>
      <Scatter data={data} options={options} />
    </div>
  );
}
