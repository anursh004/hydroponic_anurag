"use client";
import { useQuery } from "@tanstack/react-query";
import { useFarmStore } from "@/stores/farm-store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageLoader } from "@/components/ui/loading";
import { Sun, Power } from "lucide-react";
import api from "@/lib/api";

export default function LightingPage() {
  const { currentFarm } = useFarmStore();

  const { data: zones, isLoading } = useQuery({
    queryKey: ["light-zones", currentFarm?.id],
    queryFn: async () => {
      const res = await api.get(`/farms/${currentFarm!.id}/lighting/zones`);
      return res.data;
    },
    enabled: !!currentFarm,
  });

  const { data: schedules } = useQuery({
    queryKey: ["light-schedules", currentFarm?.id],
    queryFn: async () => {
      const res = await api.get(`/farms/${currentFarm!.id}/lighting/schedules`);
      return res.data;
    },
    enabled: !!currentFarm,
  });

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Lighting Control</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {(zones || []).length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="p-8 text-center text-gray-500">No lighting zones configured.</CardContent>
          </Card>
        ) : (
          (zones || []).map((zone: any) => (
            <Card key={zone.id}>
              <CardContent className="p-5">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Sun className="h-5 w-5 text-yellow-500" />
                    <h3 className="font-medium">{zone.name}</h3>
                  </div>
                  <Badge variant={zone.current_state?.on ? "success" : "default"}>
                    {zone.current_state?.on ? "ON" : "OFF"}
                  </Badge>
                </div>
                <p className="text-sm text-gray-500">
                  Fixture: {zone.fixture_type || "LED"}
                </p>
                {zone.current_state?.intensity !== undefined && (
                  <div className="mt-2">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>Intensity</span>
                      <span>{zone.current_state.intensity}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-yellow-400 h-2 rounded-full"
                        style={{ width: `${zone.current_state.intensity}%` }}
                      />
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Schedules */}
      {schedules && (schedules as any[]).length > 0 && (
        <Card>
          <CardHeader><CardTitle>Light Schedules</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {(schedules as any[]).map((s: any) => (
                <div key={s.id} className="flex items-center justify-between border-b pb-2">
                  <div>
                    <p className="font-medium text-sm">{s.name}</p>
                    <p className="text-xs text-gray-500">
                      {s.is_active ? "Active" : "Inactive"}
                    </p>
                  </div>
                  <Badge variant={s.is_active ? "success" : "default"}>
                    {s.is_active ? "Running" : "Paused"}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
