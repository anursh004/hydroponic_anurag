/**
 * API client for GreenOS backend.
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

// Request interceptor: attach JWT token
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor: handle 401 with token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (refreshToken) {
          const { data } = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem("access_token", data.access_token);
          localStorage.setItem("refresh_token", data.refresh_token);
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          }
          return api(originalRequest);
        }
      } catch {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// --- Auth API ---
export const authApi = {
  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post("/auth/register", data),
  me: () => api.get("/auth/me"),
  refresh: (refreshToken: string) =>
    api.post("/auth/refresh", { refresh_token: refreshToken }),
};

// --- Farm API ---
export const farmApi = {
  list: (skip = 0, limit = 20) =>
    api.get("/farms/", { params: { skip, limit } }),
  get: (id: string) => api.get(`/farms/${id}`),
  create: (data: Record<string, unknown>) => api.post("/farms/", data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/farms/${id}`, data),
  delete: (id: string) => api.delete(`/farms/${id}`),
  getZones: (farmId: string) => api.get(`/farms/${farmId}/zones`),
  createZone: (farmId: string, data: Record<string, unknown>) =>
    api.post(`/farms/${farmId}/zones`, data),
};

// --- Sensor API ---
export const sensorApi = {
  list: (farmId: string) => api.get(`/farms/${farmId}/sensors/`),
  get: (farmId: string, sensorId: string) =>
    api.get(`/farms/${farmId}/sensors/${sensorId}`),
  create: (farmId: string, data: Record<string, unknown>) =>
    api.post(`/farms/${farmId}/sensors/`, data),
  summary: (farmId: string) => api.get(`/farms/${farmId}/sensors/summary`),
  readings: (farmId: string, sensorId: string, params?: Record<string, unknown>) =>
    api.get(`/farms/${farmId}/sensors/${sensorId}/readings`, { params }),
  recordReading: (farmId: string, sensorId: string, data: { value: number }) =>
    api.post(`/farms/${farmId}/sensors/${sensorId}/readings`, data),
};

// --- Alert API ---
export const alertApi = {
  list: (farmId: string, params?: Record<string, unknown>) =>
    api.get(`/farms/${farmId}/alerts/`, { params }),
  acknowledge: (farmId: string, alertId: string, notes?: string) =>
    api.post(`/farms/${farmId}/alerts/${alertId}/acknowledge`, { notes }),
  resolve: (farmId: string, alertId: string) =>
    api.post(`/farms/${farmId}/alerts/${alertId}/resolve`),
  rules: (farmId: string) => api.get(`/farms/${farmId}/alerts/rules`),
  createRule: (farmId: string, data: Record<string, unknown>) =>
    api.post(`/farms/${farmId}/alerts/rules`, data),
  countActive: (farmId: string) =>
    api.get(`/farms/${farmId}/alerts/count/active`),
};

// --- Crop API ---
export const cropApi = {
  profiles: () => api.get("/crops/profiles"),
  createProfile: (data: Record<string, unknown>) =>
    api.post("/crops/profiles", data),
  cycles: (farmId: string, params?: Record<string, unknown>) =>
    api.get("/crops/cycles", { params: { farm_id: farmId, ...params } }),
  createCycle: (data: Record<string, unknown>) =>
    api.post("/crops/cycles", data),
  getCycle: (cycleId: string) => api.get(`/crops/cycles/${cycleId}`),
  addGrowthLog: (cycleId: string, data: Record<string, unknown>) =>
    api.post(`/crops/cycles/${cycleId}/growth-logs`, data),
  growthLogs: (cycleId: string) =>
    api.get(`/crops/cycles/${cycleId}/growth-logs`),
};

// --- Dashboard API ---
export const dashboardApi = {
  get: (farmId: string) => api.get(`/farms/${farmId}/dashboard/`),
};

// --- Harvest API ---
export const harvestApi = {
  list: (farmId: string, params?: Record<string, unknown>) =>
    api.get(`/farms/${farmId}/harvests/`, { params }),
  create: (farmId: string, data: Record<string, unknown>) =>
    api.post(`/farms/${farmId}/harvests/`, data),
  yieldReport: (farmId: string) =>
    api.get(`/farms/${farmId}/harvests/yield-report`),
  calendar: (farmId: string) =>
    api.get(`/farms/${farmId}/harvests/calendar`),
};

// --- Order API ---
export const orderApi = {
  list: (farmId: string, params?: Record<string, unknown>) =>
    api.get(`/farms/${farmId}/orders/`, { params }),
  create: (farmId: string, data: Record<string, unknown>) =>
    api.post(`/farms/${farmId}/orders/`, data),
  customers: (farmId: string) =>
    api.get(`/farms/${farmId}/orders/customers`),
  createCustomer: (farmId: string, data: Record<string, unknown>) =>
    api.post(`/farms/${farmId}/orders/customers`, data),
};

// --- Task API ---
export const taskApi = {
  list: (farmId: string, params?: Record<string, unknown>) =>
    api.get(`/farms/${farmId}/tasks/`, { params }),
  create: (farmId: string, data: Record<string, unknown>) =>
    api.post(`/farms/${farmId}/tasks/`, data),
  updateStatus: (farmId: string, taskId: string, data: Record<string, unknown>) =>
    api.post(`/farms/${farmId}/tasks/${taskId}/status`, data),
  overdue: (farmId: string) =>
    api.get(`/farms/${farmId}/tasks/overdue`),
};

// --- Finance API ---
export const financeApi = {
  costs: (farmId: string, params?: Record<string, unknown>) =>
    api.get(`/farms/${farmId}/finance/costs`, { params }),
  createCost: (farmId: string, data: Record<string, unknown>) =>
    api.post(`/farms/${farmId}/finance/costs`, data),
  revenueSummary: (farmId: string) =>
    api.get(`/farms/${farmId}/finance/revenue-summary`),
  profitByCrop: (farmId: string) =>
    api.get(`/farms/${farmId}/finance/profit-by-crop`),
};

// --- Inventory API ---
export const inventoryApi = {
  list: (farmId: string, params?: Record<string, unknown>) =>
    api.get(`/farms/${farmId}/inventory/items`, { params }),
  create: (farmId: string, data: Record<string, unknown>) =>
    api.post(`/farms/${farmId}/inventory/items`, data),
  lowStock: (farmId: string) =>
    api.get(`/farms/${farmId}/inventory/items/low-stock`),
  createTransaction: (farmId: string, itemId: string, data: Record<string, unknown>) =>
    api.post(`/farms/${farmId}/inventory/items/${itemId}/transactions`, data),
};

// --- Vision API ---
export const visionApi = {
  scans: (farmId: string, params?: Record<string, unknown>) =>
    api.get(`/farms/${farmId}/vision/scans`, { params }),
  createScan: (farmId: string, data: Record<string, unknown>) =>
    api.post(`/farms/${farmId}/vision/scans`, data),
  advisory: (farmId: string) =>
    api.get(`/farms/${farmId}/vision/advisory`),
  anomalyStats: (farmId: string) =>
    api.get(`/farms/${farmId}/vision/anomaly-stats`),
};
