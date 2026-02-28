"use client";
import { useQuery } from "@tanstack/react-query";
import { financeApi } from "@/lib/api";
import { useFarmStore } from "@/stores/farm-store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { PageLoader } from "@/components/ui/loading";
import { formatCurrency, formatNumber } from "@/lib/utils";
import { RevenueChart } from "@/components/charts/revenue-chart";
import { DollarSign, TrendingUp, TrendingDown, Percent } from "lucide-react";
import type { RevenueSummary } from "@/types";

export default function FinancePage() {
  const { currentFarm } = useFarmStore();

  const { data: summary, isLoading } = useQuery<RevenueSummary>({
    queryKey: ["revenue-summary", currentFarm?.id],
    queryFn: async () => {
      const res = await financeApi.revenueSummary(currentFarm!.id);
      return res.data;
    },
    enabled: !!currentFarm,
  });

  const { data: monthlyRevenue } = useQuery({
    queryKey: ["monthly-revenue", currentFarm?.id],
    queryFn: async () => {
      const res = await financeApi.revenueSummary(currentFarm!.id);
      return res.data;
    },
    enabled: !!currentFarm,
  });

  const { data: profitByCrop } = useQuery({
    queryKey: ["profit-by-crop", currentFarm?.id],
    queryFn: async () => {
      const res = await financeApi.profitByCrop(currentFarm!.id);
      return res.data;
    },
    enabled: !!currentFarm,
  });

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Finance</h1>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Revenue</p>
                  <p className="text-2xl font-bold text-green-600">{formatCurrency(summary.total_revenue)}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-200" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Costs</p>
                  <p className="text-2xl font-bold text-red-600">{formatCurrency(summary.total_costs)}</p>
                </div>
                <TrendingDown className="h-8 w-8 text-red-200" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Net Profit</p>
                  <p className={`text-2xl font-bold ${summary.net_profit >= 0 ? "text-green-600" : "text-red-600"}`}>
                    {formatCurrency(summary.net_profit)}
                  </p>
                </div>
                <DollarSign className="h-8 w-8 text-gray-200" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Profit Margin</p>
                  <p className="text-2xl font-bold">{formatNumber(summary.profit_margin)}%</p>
                </div>
                <Percent className="h-8 w-8 text-gray-200" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Profit by Crop */}
      {profitByCrop && (profitByCrop as any[]).length > 0 && (
        <Card>
          <CardHeader><CardTitle>Profit by Crop</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="table-header px-6 py-3">Crop</th>
                    <th className="table-header px-6 py-3">Revenue</th>
                    <th className="table-header px-6 py-3">Costs</th>
                    <th className="table-header px-6 py-3">Profit</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {(profitByCrop as any[]).map((item: any) => (
                    <tr key={item.crop_name} className="hover:bg-gray-50">
                      <td className="table-cell font-medium">{item.crop_name}</td>
                      <td className="table-cell text-green-600">{formatCurrency(item.revenue)}</td>
                      <td className="table-cell text-red-600">{formatCurrency(item.costs)}</td>
                      <td className={`table-cell font-bold ${item.profit >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {formatCurrency(item.profit)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
