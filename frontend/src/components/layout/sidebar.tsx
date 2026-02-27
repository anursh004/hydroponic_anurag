"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, Thermometer, Bell, Leaf, Droplets,
  Package, ShoppingCart, ClipboardList, DollarSign, Eye,
  Settings, Sprout, Sun, LogOut,
} from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";
import { useFarmStore } from "@/stores/farm-store";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Sensors", href: "/sensors", icon: Thermometer },
  { name: "Alerts", href: "/alerts", icon: Bell },
  { name: "Crops", href: "/crops", icon: Leaf },
  { name: "Dosing", href: "/dosing", icon: Droplets },
  { name: "Harvests", href: "/harvests", icon: Sprout },
  { name: "Inventory", href: "/inventory", icon: Package },
  { name: "Lighting", href: "/lighting", icon: Sun },
  { name: "Orders", href: "/orders", icon: ShoppingCart },
  { name: "Tasks", href: "/tasks", icon: ClipboardList },
  { name: "Finance", href: "/finance", icon: DollarSign },
  { name: "Vision AI", href: "/vision", icon: Eye },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { logout, user } = useAuthStore();
  const { currentFarm } = useFarmStore();

  return (
    <aside className="flex h-screen w-64 flex-col bg-gray-900 text-white">
      {/* Logo */}
      <div className="flex items-center gap-2 px-6 py-5 border-b border-gray-800">
        <Leaf className="h-8 w-8 text-primary-400" />
        <div>
          <h1 className="text-lg font-bold text-white">GreenOS</h1>
          <p className="text-xs text-gray-400 truncate">
            {currentFarm?.name || "Select a farm"}
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary-600 text-white"
                  : "text-gray-300 hover:bg-gray-800 hover:text-white"
              )}
            >
              <item.icon className="h-5 w-5 flex-shrink-0" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* User section */}
      <div className="border-t border-gray-800 px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-sm font-bold">
            {user?.full_name?.[0] || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.full_name || "User"}</p>
            <p className="text-xs text-gray-400 truncate">{user?.role?.name || "user"}</p>
          </div>
          <button onClick={logout} className="text-gray-400 hover:text-white" title="Logout">
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
