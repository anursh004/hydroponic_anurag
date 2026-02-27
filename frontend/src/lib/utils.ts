import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatNumber(n: number, decimals = 2): string {
  return n.toFixed(decimals);
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

export function getSensorUnit(sensorType: string): string {
  const units: Record<string, string> = {
    ph: "",
    ec: "mS/cm",
    temperature: "\u00B0C",
    humidity: "%",
    co2: "ppm",
    light: "lux",
    water_level: "cm",
    dissolved_oxygen: "mg/L",
    water_temperature: "\u00B0C",
  };
  return units[sensorType] || "";
}

export function getSeverityColor(severity: string): string {
  switch (severity) {
    case "critical": return "text-red-600 bg-red-50";
    case "warning": return "text-yellow-600 bg-yellow-50";
    case "info": return "text-blue-600 bg-blue-50";
    default: return "text-gray-600 bg-gray-50";
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "active": return "text-red-700 bg-red-100";
    case "acknowledged": return "text-yellow-700 bg-yellow-100";
    case "resolved": return "text-green-700 bg-green-100";
    case "pending": return "text-yellow-700 bg-yellow-100";
    case "in_progress": return "text-blue-700 bg-blue-100";
    case "completed": return "text-green-700 bg-green-100";
    case "cancelled": return "text-gray-700 bg-gray-100";
    case "blocked": return "text-red-700 bg-red-100";
    default: return "text-gray-700 bg-gray-100";
  }
}
