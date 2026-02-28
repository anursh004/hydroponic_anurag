"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { taskApi } from "@/lib/api";
import { useFarmStore } from "@/stores/farm-store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageLoader } from "@/components/ui/loading";
import { formatDate, getStatusColor } from "@/lib/utils";
import { ClipboardList, CheckCircle, PlayCircle, AlertCircle } from "lucide-react";
import toast from "react-hot-toast";
import type { Task, PaginatedResponse } from "@/types";

export default function TasksPage() {
  const { currentFarm } = useFarmStore();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery<PaginatedResponse<Task>>({
    queryKey: ["tasks", currentFarm?.id],
    queryFn: async () => {
      const res = await taskApi.list(currentFarm!.id, { limit: 50 });
      return res.data;
    },
    enabled: !!currentFarm,
  });

  const updateStatus = useMutation({
    mutationFn: ({ taskId, status }: { taskId: string; status: string }) =>
      taskApi.updateStatus(currentFarm!.id, taskId, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success("Task updated");
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Failed to update task");
    },
  });

  if (isLoading) return <PageLoader />;

  const tasks = data?.items || [];
  const grouped = {
    pending: tasks.filter((t) => t.status === "pending"),
    in_progress: tasks.filter((t) => t.status === "in_progress"),
    completed: tasks.filter((t) => t.status === "completed"),
  };

  const priorityVariant = (p: string) => {
    switch (p) {
      case "urgent": return "danger";
      case "high": return "warning";
      case "medium": return "info";
      default: return "default";
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Tasks</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pending */}
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase mb-3 flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-yellow-500" /> Pending ({grouped.pending.length})
          </h2>
          <div className="space-y-3">
            {grouped.pending.map((task) => (
              <Card key={task.id}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium text-sm">{task.title}</h3>
                    <Badge variant={priorityVariant(task.priority)}>{task.priority}</Badge>
                  </div>
                  {task.description && <p className="text-xs text-gray-500 mb-2">{task.description}</p>}
                  {task.due_date && <p className="text-xs text-gray-400">Due: {formatDate(task.due_date)}</p>}
                  <Button
                    size="sm"
                    className="mt-2 w-full"
                    variant="secondary"
                    onClick={() => updateStatus.mutate({ taskId: task.id, status: "in_progress" })}
                  >
                    <PlayCircle className="h-3 w-3 mr-1" /> Start
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* In Progress */}
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase mb-3 flex items-center gap-2">
            <PlayCircle className="h-4 w-4 text-blue-500" /> In Progress ({grouped.in_progress.length})
          </h2>
          <div className="space-y-3">
            {grouped.in_progress.map((task) => (
              <Card key={task.id} className="border-l-4 border-l-blue-500">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium text-sm">{task.title}</h3>
                    <Badge variant={priorityVariant(task.priority)}>{task.priority}</Badge>
                  </div>
                  {task.due_date && <p className="text-xs text-gray-400">Due: {formatDate(task.due_date)}</p>}
                  <Button
                    size="sm"
                    className="mt-2 w-full"
                    onClick={() => updateStatus.mutate({ taskId: task.id, status: "completed" })}
                  >
                    <CheckCircle className="h-3 w-3 mr-1" /> Complete
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Completed */}
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase mb-3 flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-500" /> Completed ({grouped.completed.length})
          </h2>
          <div className="space-y-3">
            {grouped.completed.slice(0, 10).map((task) => (
              <Card key={task.id} className="opacity-75">
                <CardContent className="p-4">
                  <h3 className="font-medium text-sm line-through text-gray-400">{task.title}</h3>
                  {task.completed_at && <p className="text-xs text-gray-400 mt-1">Done: {formatDate(task.completed_at)}</p>}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
