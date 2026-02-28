"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { sensorApi } from "@/lib/api";
import { useFarmStore } from "@/stores/farm-store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { PageLoader } from "@/components/ui/loading";
import { SensorChart } from "@/components/charts/sensor-chart";
import { formatNumber, formatDateTime, getSensorUnit } from "@/lib/utils";
import { Plus, Activity } from "lucide-react";
import toast from "react-hot-toast";
import type { Sensor, SensorReading } from "@/types";

export default function SensorsPage() {
  const { currentFarm } = useFarmStore();
  const queryClient = useQueryClient();
  const [selectedSensor, setSelectedSensor] = useState<Sensor | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newSensor, setNewSensor] = useState({ name: "", sensor_type: "ph", mqtt_topic: "" });

  const { data: sensors, isLoading } = useQuery<Sensor[]>({
    queryKey: ["sensors", currentFarm?.id],
    queryFn: async () => {
      const res = await sensorApi.list(currentFarm!.id);
      return res.data;
    },
    enabled: !!currentFarm,
  });

  const { data: readings } = useQuery<SensorReading[]>({
    queryKey: ["readings", selectedSensor?.id],
    queryFn: async () => {
      const res = await sensorApi.readings(currentFarm!.id, selectedSensor!.id, { limit: 100 });
      return res.data;
    },
    enabled: !!selectedSensor && !!currentFarm,
    refetchInterval: 15_000,
  });

  const createMutation = useMutation({
    mutationFn: () => sensorApi.create(currentFarm!.id, newSensor),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sensors"] });
      setShowCreate(false);
      setNewSensor({ name: "", sensor_type: "ph", mqtt_topic: "" });
      toast.success("Sensor created");
    },
    onError: () => toast.error("Failed to create sensor"),
  });

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Sensors</h1>
        <Button onClick={() => setShowCreate(!showCreate)}>
          <Plus className="h-4 w-4 mr-2" /> Add Sensor
        </Button>
      </div>

      {showCreate && (
        <Card>
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input label="Name" value={newSensor.name} onChange={(e) => setNewSensor({ ...newSensor, name: e.target.value })} />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                  value={newSensor.sensor_type}
                  onChange={(e) => setNewSensor({ ...newSensor, sensor_type: e.target.value })}
                >
                  {["ph","ec","temperature","humidity","co2","light","water_level","dissolved_oxygen","water_temperature"].map((t) => (
                    <option key={t} value={t}>{t.replace("_", " ")}</option>
                  ))}
                </select>
              </div>
              <Input label="MQTT Topic" value={newSensor.mqtt_topic} onChange={(e) => setNewSensor({ ...newSensor, mqtt_topic: e.target.value })} />
            </div>
            <Button className="mt-4" onClick={() => createMutation.mutate()} disabled={createMutation.isPending}>
              Create Sensor
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Sensor Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sensors?.map((sensor) => (
          <Card
            key={sensor.id}
            className={`cursor-pointer transition-all ${selectedSensor?.id === sensor.id ? "ring-2 ring-primary-500" : "hover:shadow-md"}`}
            onClick={() => setSelectedSensor(sensor)}
          >
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-primary-600" />
                  <h3 className="font-medium text-sm">{sensor.name}</h3>
                </div>
                <Badge variant={sensor.is_active ? "success" : "default"}>
                  {sensor.is_active ? "Active" : "Inactive"}
                </Badge>
              </div>
              <div className="flex items-end justify-between">
                <div>
                  <p className="text-2xl font-bold">
                    {sensor.last_value !== null && sensor.last_value !== undefined
                      ? `${formatNumber(sensor.last_value)}${getSensorUnit(sensor.sensor_type)}`
                      : "--"}
                  </p>
                  <p className="text-xs text-gray-500 capitalize">{sensor.sensor_type.replace("_", " ")}</p>
                </div>
                {sensor.last_reading_at && (
                  <p className="text-xs text-gray-400">{formatDateTime(sensor.last_reading_at)}</p>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Chart */}
      {selectedSensor && readings && readings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>{selectedSensor.name} - History</CardTitle>
          </CardHeader>
          <CardContent>
            <SensorChart data={readings} sensorType={selectedSensor.sensor_type} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
