"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { cropApi } from "@/lib/api";
import { useFarmStore } from "@/stores/farm-store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageLoader } from "@/components/ui/loading";
import { formatDate, getStatusColor } from "@/lib/utils";
import { Leaf, Plus } from "lucide-react";
import toast from "react-hot-toast";
import type { CropCycle, CropProfile, PaginatedResponse } from "@/types";

export default function CropsPage() {
  const { currentFarm } = useFarmStore();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<"cycles" | "profiles">("cycles");

  const { data: cycles, isLoading: loadingCycles } = useQuery<PaginatedResponse<CropCycle>>({
    queryKey: ["crop-cycles", currentFarm?.id],
    queryFn: async () => {
      const res = await cropApi.cycles(currentFarm!.id, { limit: 50 });
      return res.data;
    },
    enabled: !!currentFarm && tab === "cycles",
  });

  const { data: profiles, isLoading: loadingProfiles } = useQuery<CropProfile[]>({
    queryKey: ["crop-profiles"],
    queryFn: async () => {
      const res = await cropApi.profiles();
      return res.data;
    },
    enabled: tab === "profiles",
  });

  const statusVariant = (status: string) => {
    switch (status) {
      case "seeded": return "info";
      case "germinating": return "info";
      case "vegetative": return "success";
      case "flowering": return "warning";
      case "harvested": return "success";
      case "failed": return "danger";
      default: return "default";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Crops</h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        <button
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${tab === "cycles" ? "border-primary-600 text-primary-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}
          onClick={() => setTab("cycles")}
        >
          Active Cycles
        </button>
        <button
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${tab === "profiles" ? "border-primary-600 text-primary-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}
          onClick={() => setTab("profiles")}
        >
          Crop Profiles
        </button>
      </div>

      {tab === "cycles" && (
        <>
          {loadingCycles ? <PageLoader /> : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {(cycles?.items || []).map((cycle) => (
                <Card key={cycle.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-5">
                    <div className="flex items-center justify-between mb-3">
                      <Leaf className="h-5 w-5 text-green-600" />
                      <Badge variant={statusVariant(cycle.status)}>{cycle.status}</Badge>
                    </div>
                    <h3 className="font-semibold">{cycle.crop_profile?.name || "Crop"}</h3>
                    <p className="text-sm text-gray-500 font-mono">{cycle.batch_code}</p>
                    <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-gray-500">
                      <div>Seeded: {formatDate(cycle.seeded_at)}</div>
                      <div>Trays: {cycle.tray_count}</div>
                      {cycle.seed_batch && <div>Seed: {cycle.seed_batch}</div>}
                    </div>
                  </CardContent>
                </Card>
              ))}
              {(cycles?.items || []).length === 0 && (
                <Card className="col-span-full">
                  <CardContent className="p-8 text-center text-gray-500">
                    No active crop cycles. Start by creating a new cycle.
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </>
      )}

      {tab === "profiles" && (
        <>
          {loadingProfiles ? <PageLoader /> : (
            <div className="overflow-x-auto bg-white rounded-lg border">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="table-header px-6 py-3">Name</th>
                    <th className="table-header px-6 py-3">Species</th>
                    <th className="table-header px-6 py-3">Growth Days</th>
                    <th className="table-header px-6 py-3">pH Range</th>
                    <th className="table-header px-6 py-3">EC Range</th>
                    <th className="table-header px-6 py-3">Temp Range</th>
                    <th className="table-header px-6 py-3">Light</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {(profiles || []).map((p) => (
                    <tr key={p.id} className="hover:bg-gray-50">
                      <td className="table-cell font-medium">{p.name}</td>
                      <td className="table-cell italic text-gray-500">{p.species}</td>
                      <td className="table-cell">{p.growth_days} days</td>
                      <td className="table-cell font-mono">{p.ideal_ph_min} - {p.ideal_ph_max}</td>
                      <td className="table-cell font-mono">{p.ideal_ec_min} - {p.ideal_ec_max}</td>
                      <td className="table-cell font-mono">{p.ideal_temp_min} - {p.ideal_temp_max}&deg;C</td>
                      <td className="table-cell">{p.ideal_light_hours}h</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
