"use client";
import { Bell, Search } from "lucide-react";
import { useFarmStore } from "@/stores/farm-store";

export function Header() {
  const { currentFarm } = useFarmStore();

  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-6">
      {/* Search */}
      <div className="flex items-center gap-2 rounded-lg bg-gray-100 px-3 py-2 w-96">
        <Search className="h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search sensors, crops, alerts..."
          className="bg-transparent text-sm outline-none w-full text-gray-700 placeholder:text-gray-400"
        />
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-500">
          {currentFarm?.location || ""}
        </span>
        <button className="relative p-2 rounded-lg hover:bg-gray-100">
          <Bell className="h-5 w-5 text-gray-600" />
          <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full" />
        </button>
      </div>
    </header>
  );
}
