"use client";
import { useQuery } from "@tanstack/react-query";
import { orderApi } from "@/lib/api";
import { useFarmStore } from "@/stores/farm-store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader } from "@/components/ui/loading";
import { formatDate, formatCurrency, getStatusColor } from "@/lib/utils";
import { ShoppingCart } from "lucide-react";
import type { Order, PaginatedResponse } from "@/types";

export default function OrdersPage() {
  const { currentFarm } = useFarmStore();

  const { data, isLoading } = useQuery<PaginatedResponse<Order>>({
    queryKey: ["orders", currentFarm?.id],
    queryFn: async () => {
      const res = await orderApi.list(currentFarm!.id, { limit: 50 });
      return res.data;
    },
    enabled: !!currentFarm,
  });

  const statusVariant = (status: string) => {
    switch (status) {
      case "pending": return "warning";
      case "confirmed": case "processing": return "info";
      case "shipped": return "info";
      case "delivered": return "success";
      case "cancelled": return "danger";
      default: return "default";
    }
  };

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Orders</h1>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="table-header px-6 py-3">Order #</th>
                  <th className="table-header px-6 py-3">Status</th>
                  <th className="table-header px-6 py-3">Total</th>
                  <th className="table-header px-6 py-3">Delivery Date</th>
                  <th className="table-header px-6 py-3">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {(data?.items || []).length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                      No orders yet.
                    </td>
                  </tr>
                ) : (
                  data?.items.map((order) => (
                    <tr key={order.id} className="hover:bg-gray-50">
                      <td className="table-cell font-mono font-medium">{order.order_number}</td>
                      <td className="table-cell">
                        <Badge variant={statusVariant(order.status)}>{order.status}</Badge>
                      </td>
                      <td className="table-cell font-bold">{formatCurrency(order.total_amount)}</td>
                      <td className="table-cell">{order.delivery_date ? formatDate(order.delivery_date) : "--"}</td>
                      <td className="table-cell">{formatDate(order.created_at)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
