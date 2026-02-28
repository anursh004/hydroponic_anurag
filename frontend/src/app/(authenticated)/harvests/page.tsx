"use client";
import { useQuery } from "@tanstack/react-query";
import { harvestApi } from "@/lib/api";
import { useFarmStore } from "@/stores/farm-store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader } from "@/components/ui/loading";
import { formatDate, formatNumber } from "@/lib/utils";
import { Sprout, TrendingUp } from "lucide-react";
import type { PaginatedResponse, Harvest } from "@/types";

export default function HarvestsPage() {
  const { currentFarm } = useFarmStore();

  const { data, isLoading } = useQuery<PaginatedResponse<Harvest>>({
    queryKey: ["harvests", currentFarm?.id],
    queryFn: async () => {
      const res = await harvestApi.list(currentFarm!.id, { limit: 50 });
      return res.data;
    },
    enabled: !!currentFarm,
  });

  const { data: yieldReport } = useQuery({
    queryKey: ["yield-report", currentFarm?.id],
    queryFn: async () => {
      const res = await harvestApi.yieldReport(currentFarm!.id);
      return res.data;
    },
    enabled: !!currentFarm,
  });

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Harvests</h1>

      {/* Yield Summary */}
      {yieldReport && (yieldReport as any[]).length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(yieldReport as any[]).slice(0, 6).map((r: any) => (
            <Card key={r.crop_name}>
              <CardContent className="p-4 flex items-center gap-3">
                <TrendingUp className="h-5 w-5 text-green-500" />
                <div>
                  <p className="text-sm font-medium">{r.crop_name}</p>
                  <p className="text-lg font-bold">{formatNumber(r.total_weight_kg)} kg</p>
                  <p className="text-xs text-gray-500">{r.harvest_count} harvests</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Harvest Table */}
      <Card>
        <CardHeader>
          <CardTitle>Harvest Log</CardTitle>
        </CardHeader>
        <CardContent>
          {(data?.items || []).length === 0 ? (
            <p className="text-gray-500 text-center py-8">No harvests recorded yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="table-header px-6 py-3">Date</th>
                    <th className="table-header px-6 py-3">Weight (kg)</th>
                    <th className="table-header px-6 py-3">Grade</th>
                    <th className="table-header px-6 py-3">Waste (kg)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {data?.items.map((h) => (
                    <tr key={h.id} className="hover:bg-gray-50">
                      <td className="table-cell">{formatDate(h.harvested_at)}</td>
                      <td className="table-cell font-mono font-bold">{formatNumber(h.weight_kg)}</td>
                      <td className="table-cell">
                        <Badge variant={h.grade === "A" ? "success" : h.grade === "B" ? "info" : "warning"}>
                          Grade {h.grade}
                        </Badge>
                      </td>
                      <td className="table-cell font-mono">{h.waste_kg ? formatNumber(h.waste_kg) : "--"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
