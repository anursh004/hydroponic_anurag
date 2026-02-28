"use client";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts";
import { getSensorUnit } from "@/lib/utils";

interface SensorChartProps {
  data: Array<{ recorded_at: string; value: number }>;
  sensorType: string;
  color?: string;
}

export function SensorChart({ data, sensorType, color = "#16a34a" }: SensorChartProps) {
  const unit = getSensorUnit(sensorType);
  const formatted = data.map((d) => ({
    time: new Date(d.recorded_at).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    }),
    value: Number(d.value),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={formatted}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="time" fontSize={12} tickLine={false} />
        <YAxis fontSize={12} tickLine={false} unit={unit ? ` ${unit}` : ""} />
        <Tooltip
          contentStyle={{ borderRadius: "8px", border: "1px solid #e5e7eb" }}
          formatter={(value: number) => [`${value.toFixed(2)}${unit ? ` ${unit}` : ""}`, sensorType]}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={2}
          dot={false}
          name={sensorType}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
