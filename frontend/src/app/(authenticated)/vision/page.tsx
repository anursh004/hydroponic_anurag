"use client";
import { useQuery } from "@tanstack/react-query";
import { visionApi } from "@/lib/api";
import { useFarmStore } from "@/stores/farm-store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader } from "@/components/ui/loading";
import { formatDateTime, formatNumber } from "@/lib/utils";
import { Eye, Brain, AlertTriangle, TrendingUp } from "lucide-react";

export default function VisionPage() {
  const { currentFarm } = useFarmStore();

  const { data: advisory, isLoading } = useQuery({
    queryKey: ["ai-advisory", currentFarm?.id],
    queryFn: async () => {
      const res = await visionApi.advisory(currentFarm!.id);
      return res.data;
    },
    enabled: !!currentFarm,
  });

  const { data: anomalyStats } = useQuery({
    queryKey: ["anomaly-stats", currentFarm?.id],
    queryFn: async () => {
      const res = await visionApi.anomalyStats(currentFarm!.id);
      return res.data;
    },
    enabled: !!currentFarm,
  });

  const { data: scans } = useQuery({
    queryKey: ["scans", currentFarm?.id],
    queryFn: async () => {
      const res = await visionApi.scans(currentFarm!.id, { limit: 20 });
      return res.data;
    },
    enabled: !!currentFarm,
  });

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Vision AI</h1>

      {/* AI Advisory */}
      {advisory && (
        <Card className="border-l-4 border-l-purple-500">
          <CardContent className="p-6">
            <div className="flex items-center gap-2 mb-3">
              <Brain className="h-6 w-6 text-purple-600" />
              <h2 className="text-lg font-semibold">AI Advisory</h2>
              {(advisory as any).health_trend && (
                <Badge variant={(advisory as any).health_trend === "improving" ? "success" : (advisory as any).health_trend === "declining" ? "danger" : "default"}>
                  {(advisory as any).health_trend}
                </Badge>
              )}
            </div>
            <p className="text-gray-700 mb-4">{(advisory as any).summary}</p>
            {(advisory as any).recommendations?.length > 0 && (
              <div>
                <h3 className="font-medium text-sm mb-2">Recommendations:</h3>
                <ul className="space-y-1">
                  {(advisory as any).recommendations.map((r: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                      <AlertTriangle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Anomaly Stats */}
      {anomalyStats && (anomalyStats as any[]).length > 0 && (
        <Card>
          <CardHeader><CardTitle>Anomaly Detection Stats</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {(anomalyStats as any[]).map((stat: any) => (
                <div key={stat.anomaly_type} className="text-center p-3 rounded-lg bg-gray-50">
                  <p className="text-2xl font-bold text-purple-600">{stat.count}</p>
                  <p className="text-xs text-gray-500 capitalize">{stat.anomaly_type.replace("_", " ")}</p>
                  <p className="text-xs text-gray-400">Avg conf: {formatNumber(stat.avg_confidence * 100)}%</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Scans */}
      <Card>
        <CardHeader><CardTitle>Recent Scans</CardTitle></CardHeader>
        <CardContent>
          {(!scans || (scans as any).items?.length === 0) ? (
            <p className="text-gray-500 text-center py-8">No scans recorded yet. Upload plant images to begin AI analysis.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {((scans as any).items || []).map((scan: any) => (
                <div key={scan.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <Eye className="h-4 w-4 text-purple-500" />
                    <Badge variant={scan.analysis_status === "completed" ? "success" : scan.analysis_status === "failed" ? "danger" : "warning"}>
                      {scan.analysis_status}
                    </Badge>
                  </div>
                  {scan.health_score !== null && (
                    <p className="text-lg font-bold">Health: {formatNumber(scan.health_score)}%</p>
                  )}
                  <p className="text-xs text-gray-400">{formatDateTime(scan.created_at)}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
