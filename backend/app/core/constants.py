from enum import Enum


class SensorType(str, Enum):
    PH = "ph"
    EC = "ec"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    CO2 = "co2"
    DISSOLVED_OXYGEN = "dissolved_oxygen"
    WATER_LEVEL = "water_level"
    LIGHT = "light"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"


class AlertCondition(str, Enum):
    ABOVE = "above"
    BELOW = "below"
    OUTSIDE_RANGE = "outside_range"


class CropCycleStatus(str, Enum):
    SEEDED = "seeded"
    GERMINATING = "germinating"
    GROWING = "growing"
    FLOWERING = "flowering"
    READY_TO_HARVEST = "ready_to_harvest"
    HARVESTED = "harvested"
    FAILED = "failed"


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    HARVESTING = "harvesting"
    PACKED = "packed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class UserRole(str, Enum):
    ADMIN = "admin"
    FARM_MANAGER = "farm_manager"
    OPERATOR = "operator"
    VIEWER = "viewer"


class DosingTrigger(str, Enum):
    AUTO = "auto"
    MANUAL = "manual"
    SCHEDULE = "schedule"


class InventoryCategory(str, Enum):
    SEEDS = "seeds"
    NUTRIENTS = "nutrients"
    SUBSTRATES = "substrates"
    PACKAGING = "packaging"
    EQUIPMENT = "equipment"


class TransactionType(str, Enum):
    PURCHASE = "purchase"
    USAGE = "usage"
    ADJUSTMENT = "adjustment"
    WASTE = "waste"


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class CustomerType(str, Enum):
    RESTAURANT = "restaurant"
    HOTEL = "hotel"
    RETAILER = "retailer"
    INDIVIDUAL = "individual"
    WHOLESALER = "wholesaler"


class HarvestGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    REJECT = "reject"


class ZoneType(str, Enum):
    GERMINATION = "germination"
    GROWING = "growing"
    FLOWERING = "flowering"
    HARVEST = "harvest"


class EnvironmentType(str, Enum):
    NFT = "nft"
    DWC = "dwc"
    DRIP = "drip"
    AEROPONICS = "aeroponics"
    TOWER = "tower"


class PumpType(str, Enum):
    PH_UP = "ph_up"
    PH_DOWN = "ph_down"
    NUTRIENT_A = "nutrient_a"
    NUTRIENT_B = "nutrient_b"
    NUTRIENT_C = "nutrient_c"


class LightFixtureType(str, Enum):
    LED_FULL_SPECTRUM = "led_full_spectrum"
    LED_RED_BLUE = "led_red_blue"
    HPS = "hps"


class ScanType(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    ALERT_TRIGGERED = "alert_triggered"


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnomalyType(str, Enum):
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"
    PEST = "pest"
    DISEASE = "disease"
    LIGHT_STRESS = "light_stress"
    TIP_BURN = "tip_burn"


class DosingEventStatus(str, Enum):
    PENDING = "pending"
    DISPENSING = "dispensing"
    COMPLETED = "completed"
    FAILED = "failed"


class SubscriptionFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class CostCategory(str, Enum):
    SEEDS = "seeds"
    NUTRIENTS = "nutrients"
    LABOR = "labor"
    ELECTRICITY = "electricity"
    WATER = "water"
    EQUIPMENT = "equipment"
    OTHER = "other"


class TaskType(str, Enum):
    SEEDING = "seeding"
    TRANSPLANTING = "transplanting"
    HARVESTING = "harvesting"
    CLEANING = "cleaning"
    MAINTENANCE = "maintenance"
    DOSING_CHECK = "dosing_check"
    INSPECTION = "inspection"
