// =============================================
// GreenOS Type Definitions
// =============================================

// --- Common ---
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface MessageResponse {
  message: string;
}

// --- Auth ---
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// --- User ---
export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  role?: Role;
  created_at: string;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
}

export interface Permission {
  id: string;
  name: string;
}

// --- Farm ---
export interface Farm {
  id: string;
  name: string;
  location: string;
  latitude?: number;
  longitude?: number;
  timezone: string;
  owner_id: string;
  settings?: Record<string, unknown>;
  created_at: string;
}

export interface Zone {
  id: string;
  name: string;
  farm_id: string;
  zone_type: string;
  environment_type: string;
  position: number;
}

// --- Sensor ---
export type SensorType = "ph" | "ec" | "temperature" | "humidity" | "co2" | "light" | "water_level" | "dissolved_oxygen" | "water_temperature";

export interface Sensor {
  id: string;
  name: string;
  farm_id: string;
  zone_id?: string;
  sensor_type: SensorType;
  mqtt_topic: string;
  is_active: boolean;
  last_value?: number;
  last_reading_at?: string;
  calibration_offset: number;
}

export interface SensorReading {
  id: number;
  sensor_id: string;
  value: number;
  recorded_at: string;
}

export interface SensorSummary {
  sensor_type: SensorType;
  count: number;
  avg_value: number | null;
  min_value: number | null;
  max_value: number | null;
}

// --- Alert ---
export type AlertSeverity = "info" | "warning" | "critical";
export type AlertStatus = "active" | "acknowledged" | "resolved";
export type AlertCondition = "above" | "below" | "outside_range";

export interface AlertRule {
  id: string;
  name: string;
  farm_id: string;
  sensor_type: SensorType;
  condition: AlertCondition;
  threshold_min?: number;
  threshold_max?: number;
  severity: AlertSeverity;
  cooldown_minutes: number;
  is_active: boolean;
}

export interface Alert {
  id: string;
  farm_id: string;
  alert_rule_id?: string;
  sensor_id?: string;
  triggered_value: number;
  status: AlertStatus;
  message: string;
  acknowledged_by_id?: string;
  acknowledged_at?: string;
  resolved_at?: string;
  created_at: string;
}

// --- Crop ---
export interface CropProfile {
  id: string;
  name: string;
  species: string;
  variety?: string;
  growth_days: number;
  germination_days: number;
  ideal_ph_min: number;
  ideal_ph_max: number;
  ideal_ec_min: number;
  ideal_ec_max: number;
  ideal_temp_min: number;
  ideal_temp_max: number;
  ideal_humidity_min: number;
  ideal_humidity_max: number;
  ideal_light_hours: number;
  is_system_default: boolean;
}

export type CropCycleStatus = "seeded" | "germinating" | "vegetative" | "flowering" | "harvested" | "failed";

export interface CropCycle {
  id: string;
  batch_code: string;
  farm_id: string;
  crop_profile_id: string;
  crop_profile?: CropProfile;
  status: CropCycleStatus;
  seeded_at: string;
  tray_count: number;
  seed_batch?: string;
}

export interface GrowthLog {
  id: string;
  crop_cycle_id: string;
  health_rating: number;
  height_cm?: number;
  leaf_count?: number;
  notes?: string;
  created_at: string;
}

// --- Harvest ---
export interface Harvest {
  id: string;
  crop_cycle_id: string;
  weight_kg: number;
  grade: string;
  waste_kg?: number;
  harvested_at: string;
  harvested_by_id: string;
}

// --- Inventory ---
export interface InventoryItem {
  id: string;
  farm_id: string;
  name: string;
  category: string;
  unit: string;
  current_stock: number;
  reorder_threshold: number;
  reorder_quantity?: number;
}

// --- Order ---
export type OrderStatus = "pending" | "confirmed" | "processing" | "shipped" | "delivered" | "cancelled";

export interface Customer {
  id: string;
  name: string;
  email: string;
  phone?: string;
  customer_type: string;
  company?: string;
}

export interface Order {
  id: string;
  order_number: string;
  farm_id: string;
  customer_id: string;
  status: OrderStatus;
  total_amount: number;
  delivery_date?: string;
  created_at: string;
}

// --- Task ---
export type TaskStatus = "pending" | "in_progress" | "completed" | "blocked" | "cancelled";
export type TaskPriority = "low" | "medium" | "high" | "urgent";

export interface Task {
  id: string;
  title: string;
  description?: string;
  farm_id: string;
  task_type: string;
  priority: TaskPriority;
  status: TaskStatus;
  assigned_to_id?: string;
  due_date?: string;
  completed_at?: string;
  photo_proof_required: boolean;
  photos: TaskPhoto[];
}

export interface TaskPhoto {
  id: string;
  task_id: string;
  photo_url: string;
}

// --- Finance ---
export interface Cost {
  id: string;
  farm_id: string;
  category: string;
  description: string;
  amount: number;
  date: string;
  crop_cycle_id?: string;
}

export interface RevenueSummary {
  total_revenue: number;
  total_costs: number;
  net_profit: number;
  profit_margin: number;
}

// --- Dashboard ---
export interface DashboardData {
  sensor_summary: SensorSummary[];
  alerts: { active_count: number };
  crops: { active_count: number };
  tasks: { pending_count: number; overdue_count: number };
  harvests: { recent: HarvestSummary[] };
  orders: { today_count: number };
  dosing: { events_24h: number };
  environment: Record<string, number | null>;
  generated_at: string;
}

export interface HarvestSummary {
  id: string;
  weight_kg: number;
  grade: string;
  harvested_at: string;
}
