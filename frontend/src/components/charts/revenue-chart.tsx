"use client";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts";
import { formatCurrency } from "@/lib/utils";

interface RevenueChartProps {
  data: Array<{ month: number; revenue: number }>;
}

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

export function RevenueChart({ data }: RevenueChartProps) {
  const formatted = data.map((d) => ({
    month: MONTHS[d.month - 1],
    revenue: d.revenue,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={formatted}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="month" fontSize={12} />
        <YAxis fontSize={12} tickFormatter={(v) => `$${v}`} />
        <Tooltip
          contentStyle={{ borderRadius: "8px", border: "1px solid #e5e7eb" }}
          formatter={(value: number) => [formatCurrency(value), "Revenue"]}
        />
        <Legend />
        <Bar dataKey="revenue" fill="#16a34a" radius={[4, 4, 0, 0]} name="Revenue" />
      </BarChart>
    </ResponsiveContainer>
  );
}
