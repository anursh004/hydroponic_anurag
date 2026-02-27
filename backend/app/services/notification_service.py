"""Notification service for alerts, WebSocket, and email notifications."""
import json
import logging
from uuid import UUID

from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)


class NotificationService:
    """Handles publishing notifications via Redis pub/sub and other channels."""

    CHANNEL_ALERTS = "greenos:notifications:alerts"
    CHANNEL_SENSORS = "greenos:notifications:sensors"
    CHANNEL_DOSING = "greenos:notifications:dosing"
    CHANNEL_TASKS = "greenos:notifications:tasks"

    @staticmethod
    async def publish_alert(farm_id: UUID, alert_data: dict) -> None:
        """Publish alert notification to Redis for WebSocket fanout."""
        if not redis_client:
            logger.warning("Redis not available, skipping alert notification")
            return

        message = json.dumps({
            "type": "alert",
            "farm_id": str(farm_id),
            "data": alert_data,
        })
        try:
            await redis_client.publish(NotificationService.CHANNEL_ALERTS, message)
        except Exception as e:
            logger.error(f"Failed to publish alert notification: {e}")

    @staticmethod
    async def publish_sensor_reading(farm_id: UUID, sensor_data: dict) -> None:
        """Publish real-time sensor reading."""
        if not redis_client:
            return

        message = json.dumps({
            "type": "sensor_reading",
            "farm_id": str(farm_id),
            "data": sensor_data,
        })
        try:
            await redis_client.publish(NotificationService.CHANNEL_SENSORS, message)
        except Exception as e:
            logger.error(f"Failed to publish sensor reading: {e}")

    @staticmethod
    async def publish_dosing_event(farm_id: UUID, dosing_data: dict) -> None:
        """Publish dosing event notification."""
        if not redis_client:
            return

        message = json.dumps({
            "type": "dosing_event",
            "farm_id": str(farm_id),
            "data": dosing_data,
        })
        try:
            await redis_client.publish(NotificationService.CHANNEL_DOSING, message)
        except Exception as e:
            logger.error(f"Failed to publish dosing event: {e}")

    @staticmethod
    async def publish_task_update(farm_id: UUID, task_data: dict) -> None:
        """Publish task update notification."""
        if not redis_client:
            return

        message = json.dumps({
            "type": "task_update",
            "farm_id": str(farm_id),
            "data": task_data,
        })
        try:
            await redis_client.publish(NotificationService.CHANNEL_TASKS, message)
        except Exception as e:
            logger.error(f"Failed to publish task update: {e}")

    @staticmethod
    async def send_email_notification(
        to_email: str,
        subject: str,
        body: str,
    ) -> None:
        """Send email notification (placeholder for SMTP integration)."""
        logger.info(f"Email notification: to={to_email}, subject={subject}")
        # In production, integrate with SMTP or email service (SendGrid, SES, etc.)
        # For now, just log the notification

    @staticmethod
    async def cache_notification(
        user_id: UUID, notification: dict, ttl: int = 86400
    ) -> None:
        """Cache notification in Redis for later retrieval."""
        if not redis_client:
            return

        key = f"greenos:user:{user_id}:notifications"
        try:
            await redis_client.lpush(key, json.dumps(notification))
            await redis_client.ltrim(key, 0, 99)  # Keep last 100 notifications
            await redis_client.expire(key, ttl)
        except Exception as e:
            logger.error(f"Failed to cache notification: {e}")

    @staticmethod
    async def get_user_notifications(user_id: UUID, limit: int = 20) -> list[dict]:
        """Retrieve cached notifications for a user."""
        if not redis_client:
            return []

        key = f"greenos:user:{user_id}:notifications"
        try:
            raw = await redis_client.lrange(key, 0, limit - 1)
            return [json.loads(item) for item in raw]
        except Exception as e:
            logger.error(f"Failed to get notifications: {e}")
            return []
