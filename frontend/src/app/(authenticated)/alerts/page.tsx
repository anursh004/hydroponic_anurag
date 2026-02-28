"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { alertApi } from "@/lib/api";
import { useFarmStore } from "@/stores/farm-store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageLoader } from "@/components/ui/loading";
import { formatDateTime, getSeverityColor } from "@/lib/utils";
import { Bell, CheckCircle, XCircle } from "lucide-react";
import toast from "react-hot-toast";
import type { Alert, PaginatedResponse } from "@/types";

export default function AlertsPage() {
  const { currentFarm } = useFarmStore();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery<PaginatedResponse<Alert>>({
    queryKey: ["alerts", currentFarm?.id],
    queryFn: async () => {
      const res = await alertApi.list(currentFarm!.id, { limit: 50 });
      return res.data;
    },
    enabled: !!currentFarm,
    refetchInterval: 15_000,
  });

  const ackMutation = useMutation({
    mutationFn: (alertId: string) => alertApi.acknowledge(currentFarm!.id, alertId, "Acknowledged from dashboard"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
      toast.success("Alert acknowledged");
    },
  });

  const resolveMutation = useMutation({
    mutationFn: (alertId: string) => alertApi.resolve(currentFarm!.id, alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
      toast.success("Alert resolved");
    },
  });

  if (isLoading) return <PageLoader />;

  const alerts = data?.items || [];
  const activeAlerts = alerts.filter((a) => a.status === "active");
  const otherAlerts = alerts.filter((a) => a.status !== "active");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Alerts</h1>
        <Badge variant={activeAlerts.length > 0 ? "danger" : "success"}>
          {activeAlerts.length} active
        </Badge>
      </div>

      {activeAlerts.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-3" />
            <p className="text-gray-500">No active alerts. All systems normal.</p>
          </CardContent>
        </Card>
      )}

      {activeAlerts.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-red-600">Active Alerts</h2>
          {activeAlerts.map((alert) => (
            <Card key={alert.id} className="border-l-4 border-l-red-500">
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Bell className="h-5 w-5 text-red-500" />
                  <div>
                    <p className="font-medium">{alert.message}</p>
                    <p className="text-xs text-gray-500">
                      Triggered value: {alert.triggered_value} | {formatDateTime(alert.created_at)}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="secondary" onClick={() => ackMutation.mutate(alert.id)}>
                    Acknowledge
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {otherAlerts.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-600">History</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 bg-white rounded-lg">
              <thead>
                <tr>
                  <th className="table-header px-6 py-3">Message</th>
                  <th className="table-header px-6 py-3">Status</th>
                  <th className="table-header px-6 py-3">Value</th>
                  <th className="table-header px-6 py-3">Date</th>
                  <th className="table-header px-6 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {otherAlerts.map((alert) => (
                  <tr key={alert.id}>
                    <td className="table-cell">{alert.message}</td>
                    <td className="table-cell">
                      <Badge variant={alert.status === "resolved" ? "success" : "warning"}>
                        {alert.status}
                      </Badge>
                    </td>
                    <td className="table-cell font-mono">{alert.triggered_value}</td>
                    <td className="table-cell">{formatDateTime(alert.created_at)}</td>
                    <td className="table-cell">
                      {alert.status === "acknowledged" && (
                        <Button size="sm" variant="ghost" onClick={() => resolveMutation.mutate(alert.id)}>
                          Resolve
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
