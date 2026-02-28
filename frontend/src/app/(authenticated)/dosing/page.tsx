"use client";
import { useQuery } from "@tanstack/react-query";
import { useFarmStore } from "@/stores/farm-store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader } from "@/components/ui/loading";
import { Droplets, Beaker } from "lucide-react";
import api from "@/lib/api";

export default function DosingPage() {
  const { currentFarm } = useFarmStore();

  const { data: pumps, isLoading: loadingPumps } = useQuery({
    queryKey: ["dosing-pumps", currentFarm?.id],
    queryFn: async () => {
      const res = await api.get(`/farms/${currentFarm!.id}/dosing/pumps`);
      return res.data;
    },
    enabled: !!currentFarm,
  });

  const { data: recipes, isLoading: loadingRecipes } = useQuery({
    queryKey: ["dosing-recipes", currentFarm?.id],
    queryFn: async () => {
      const res = await api.get(`/farms/${currentFarm!.id}/dosing/recipes`);
      return res.data;
    },
    enabled: !!currentFarm,
  });

  if (loadingPumps) return <PageLoader />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Nutrient Dosing</h1>

      {/* Pumps */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Dosing Pumps</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(pumps || []).length === 0 ? (
            <Card className="col-span-full"><CardContent className="p-8 text-center text-gray-500">No dosing pumps configured.</CardContent></Card>
          ) : (
            (pumps || []).map((pump: any) => (
              <Card key={pump.id}>
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Droplets className="h-5 w-5 text-blue-500" />
                      <h3 className="font-medium">{pump.name}</h3>
                    </div>
                    <Badge variant={pump.is_active ? "success" : "default"}>
                      {pump.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-500">Type: {pump.pump_type}</p>
                  <p className="text-sm text-gray-500">Rate: {pump.ml_per_second} mL/s</p>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>

      {/* Recipes */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Dosing Recipes</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(recipes || []).length === 0 ? (
            <Card className="col-span-full"><CardContent className="p-8 text-center text-gray-500">No dosing recipes configured.</CardContent></Card>
          ) : (
            (recipes || []).map((recipe: any) => (
              <Card key={recipe.id}>
                <CardContent className="p-5">
                  <div className="flex items-center gap-2 mb-2">
                    <Beaker className="h-5 w-5 text-purple-500" />
                    <h3 className="font-medium">{recipe.name}</h3>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                    <div>Target pH: {recipe.target_ph_min} - {recipe.target_ph_max}</div>
                    <div>Target EC: {recipe.target_ec_min} - {recipe.target_ec_max}</div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
