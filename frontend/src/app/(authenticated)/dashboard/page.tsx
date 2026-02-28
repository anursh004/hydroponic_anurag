"use client";
import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "@/lib/api";
import { useFarmStore } from "@/stores/farm-store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader, CardSkeleton } from "@/components/ui/loading";
import { formatNumber, formatDateTime, getSensorUnit } from "@/lib/utils";
import {
  Thermometer, Droplets, Wind, Zap, Bell,
  Leaf, ClipboardList, ShoppingCart, Activity,
} from "lucide-react";
import type { DashboardData } from "@/types";

const sensorIcons: Record<string, React.ElementType> = {
  temperature: Thermometer,
  humidity: Droplets,
  co2: Wind,
  ph: Activity,
  ec: Zap,
};

export default function DashboardPage() {
  const { currentFarm } = useFarmStore();

  const { data, isLoading } = useQuery<DashboardData>({
    queryKey: ["dashboard", currentFarm?.id],
    queryFn: async () => {
      if (!currentFarm) throw new Error("No farm selected");
      const res = await dashboardApi.get(currentFarm.id);
      return res.data;
    },
    enabled: !!currentFarm,
    refetchInterval: 30_000,
  });

  if (!currentFarm) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-gray-500">
        <Leaf className="h-12 w-12 mb-4" />
        <p className="text-lg">No farm selected. Create or select a farm to get started.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <CardSkeleton key={i} />)}
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <span className="text-sm text-gray-500">
          Last updated: {formatDateTime(data.generated_at)}
        </span>
      </div>

      {/* Environment Snapshot */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {Object.entries(data.environment).map(([key, value]) => {
          const Icon = sensorIcons[key] || Activity;
          return (
            <Card key={key}>
              <CardContent className="p-4 flex items-center gap-3">
                <div className="rounded-lg bg-primary-50 p-2">
                  <Icon className="h-5 w-5 text-primary-600" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 capitalize">{key.replace("_", " ")}</p>
                  <p className="text-lg font-bold">
                    {value !== null ? `${formatNumber(value)}${getSensorUnit(key)}` : "--"}
                  </p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Active Alerts</p>
                <p className="text-3xl font-bold text-red-600">{data.alerts.active_count}</p>
              </div>
              <Bell className="h-8 w-8 text-red-200" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Active Crops</p>
                <p className="text-3xl font-bold text-green-600">{data.crops.active_count}</p>
              </div>
              <Leaf className="h-8 w-8 text-green-200" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Pending Tasks</p>
                <p className="text-3xl font-bold text-yellow-600">{data.tasks.pending_count}</p>
                {data.tasks.overdue_count > 0 && (
                  <Badge variant="danger">{data.tasks.overdue_count} overdue</Badge>
                )}
              </div>
              <ClipboardList className="h-8 w-8 text-yellow-200" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Orders Today</p>
                <p className="text-3xl font-bold text-blue-600">{data.orders.today_count}</p>
              </div>
              <ShoppingCart className="h-8 w-8 text-blue-200" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Harvests & Sensor Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Harvests</CardTitle>
          </CardHeader>
          <CardContent>
            {data.harvests.recent.length === 0 ? (
              <p className="text-gray-500 text-sm">No recent harvests</p>
            ) : (
              <div className="space-y-3">
                {data.harvests.recent.map((h) => (
                  <div key={h.id} className="flex items-center justify-between border-b pb-2">
                    <div>
                      <p className="text-sm font-medium">{formatNumber(h.weight_kg)} kg</p>
                      <p className="text-xs text-gray-500">{formatDateTime(h.harvested_at)}</p>
                    </div>
                    <Badge variant={h.grade === "A" ? "success" : h.grade === "B" ? "info" : "warning"}>
                      Grade {h.grade}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Sensor Overview</CardTitle>
          </CardHeader>
          <CardContent>
            {data.sensor_summary.length === 0 ? (
              <p className="text-gray-500 text-sm">No sensors configured</p>
            ) : (
              <div className="space-y-3">
                {data.sensor_summary.map((s) => (
                  <div key={s.sensor_type} className="flex items-center justify-between border-b pb-2">
                    <div>
                      <p className="text-sm font-medium capitalize">{s.sensor_type.replace("_", " ")}</p>
                      <p className="text-xs text-gray-500">{s.count} sensors</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-mono">
                        {s.avg_value !== null ? formatNumber(s.avg_value) : "--"}{getSensorUnit(s.sensor_type)}
                      </p>
                      <p className="text-xs text-gray-400">
                        {s.min_value !== null && s.max_value !== null
                          ? `${formatNumber(s.min_value)} - ${formatNumber(s.max_value)}`
                          : ""}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Dosing Activity */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-3">
            <Droplets className="h-5 w-5 text-blue-500" />
            <p className="text-sm text-gray-600">
              <span className="font-bold text-blue-600">{data.dosing.events_24h}</span> dosing events in the last 24 hours
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
