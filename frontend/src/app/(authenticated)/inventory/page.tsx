"use client";
import { useQuery } from "@tanstack/react-query";
import { inventoryApi } from "@/lib/api";
import { useFarmStore } from "@/stores/farm-store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader } from "@/components/ui/loading";
import { formatNumber } from "@/lib/utils";
import { Package, AlertTriangle } from "lucide-react";
import type { InventoryItem, PaginatedResponse } from "@/types";

export default function InventoryPage() {
  const { currentFarm } = useFarmStore();

  const { data, isLoading } = useQuery<PaginatedResponse<InventoryItem>>({
    queryKey: ["inventory", currentFarm?.id],
    queryFn: async () => {
      const res = await inventoryApi.list(currentFarm!.id, { limit: 100 });
      return res.data;
    },
    enabled: !!currentFarm,
  });

  const { data: lowStock } = useQuery<InventoryItem[]>({
    queryKey: ["low-stock", currentFarm?.id],
    queryFn: async () => {
      const res = await inventoryApi.lowStock(currentFarm!.id);
      return res.data;
    },
    enabled: !!currentFarm,
  });

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Inventory</h1>

      {/* Low Stock Warning */}
      {lowStock && lowStock.length > 0 && (
        <Card className="border-l-4 border-l-yellow-500">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="h-5 w-5 text-yellow-500" />
              <h3 className="font-medium text-yellow-700">Low Stock Items ({lowStock.length})</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {lowStock.map((item) => (
                <Badge key={item.id} variant="warning">
                  {item.name}: {formatNumber(item.current_stock)} {item.unit}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Inventory Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Items</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="table-header px-6 py-3">Item</th>
                  <th className="table-header px-6 py-3">Category</th>
                  <th className="table-header px-6 py-3">Stock</th>
                  <th className="table-header px-6 py-3">Unit</th>
                  <th className="table-header px-6 py-3">Reorder At</th>
                  <th className="table-header px-6 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {(data?.items || []).map((item) => {
                  const isLow = item.reorder_threshold > 0 && item.current_stock <= item.reorder_threshold;
                  return (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="table-cell font-medium">
                        <div className="flex items-center gap-2">
                          <Package className="h-4 w-4 text-gray-400" />
                          {item.name}
                        </div>
                      </td>
                      <td className="table-cell capitalize">{item.category}</td>
                      <td className="table-cell font-mono font-bold">{formatNumber(item.current_stock)}</td>
                      <td className="table-cell">{item.unit}</td>
                      <td className="table-cell font-mono">{item.reorder_threshold || "--"}</td>
                      <td className="table-cell">
                        <Badge variant={isLow ? "danger" : "success"}>
                          {isLow ? "Low" : "OK"}
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
