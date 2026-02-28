"use client";
import { useState } from "react";
import { useAuthStore } from "@/stores/auth-store";
import { useFarmStore } from "@/stores/farm-store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Settings, User, Building2 } from "lucide-react";

export default function SettingsPage() {
  const { user } = useAuthStore();
  const { farms, currentFarm, setCurrentFarm } = useFarmStore();

  return (
    <div className="space-y-6 max-w-4xl">
      <h1 className="text-2xl font-bold">Settings</h1>

      {/* User Profile */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" /> User Profile
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Full Name</label>
              <p className="text-gray-900">{user?.full_name || "--"}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Email</label>
              <p className="text-gray-900">{user?.email || "--"}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Role</label>
              <p><Badge>{user?.role?.name || "user"}</Badge></p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Status</label>
              <p><Badge variant={user?.is_active ? "success" : "danger"}>{user?.is_active ? "Active" : "Inactive"}</Badge></p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Farm Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" /> Farm Selection
          </CardTitle>
        </CardHeader>
        <CardContent>
          {farms.length === 0 ? (
            <p className="text-gray-500">No farms available.</p>
          ) : (
            <div className="space-y-2">
              {farms.map((farm) => (
                <div
                  key={farm.id}
                  className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-colors ${
                    currentFarm?.id === farm.id ? "border-primary-500 bg-primary-50" : "hover:bg-gray-50"
                  }`}
                  onClick={() => setCurrentFarm(farm)}
                >
                  <div>
                    <p className="font-medium">{farm.name}</p>
                    <p className="text-sm text-gray-500">{farm.location}</p>
                  </div>
                  {currentFarm?.id === farm.id && <Badge variant="success">Active</Badge>}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* System Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" /> System Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <label className="text-gray-500">Platform</label>
              <p className="font-medium">GreenOS v1.0.0</p>
            </div>
            <div>
              <label className="text-gray-500">API Version</label>
              <p className="font-medium">v1</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
