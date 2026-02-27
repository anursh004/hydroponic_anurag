"use client";
import { cn } from "@/lib/utils";

export function Spinner({ className }: { className?: string }) {
  return (
    <div
      className={cn("h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-primary-600", className)}
    />
  );
}

export function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <Spinner className="h-10 w-10" />
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-1/3 mb-4" />
      <div className="h-8 bg-gray-200 rounded w-1/2 mb-2" />
      <div className="h-3 bg-gray-200 rounded w-2/3" />
    </div>
  );
}
