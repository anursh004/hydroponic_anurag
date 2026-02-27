"""Tests for notification service."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from app.services.notification_service import NotificationService


class TestNotificationService:
    """Test notification publishing and caching."""

    @pytest.mark.asyncio
    async def test_publish_alert_no_redis(self):
        """Should handle missing Redis gracefully."""
        with patch("app.services.notification_service.redis_client", None):
            await NotificationService.publish_alert(
                uuid4(), {"message": "test alert"}
            )
            # Should not raise

    @pytest.mark.asyncio
    async def test_publish_sensor_reading_no_redis(self):
        with patch("app.services.notification_service.redis_client", None):
            await NotificationService.publish_sensor_reading(
                uuid4(), {"value": 6.5}
            )

    @pytest.mark.asyncio
    async def test_publish_dosing_event_no_redis(self):
        with patch("app.services.notification_service.redis_client", None):
            await NotificationService.publish_dosing_event(
                uuid4(), {"action": "ph_up"}
            )

    @pytest.mark.asyncio
    async def test_publish_task_update_no_redis(self):
        with patch("app.services.notification_service.redis_client", None):
            await NotificationService.publish_task_update(
                uuid4(), {"task_id": str(uuid4())}
            )

    @pytest.mark.asyncio
    async def test_publish_alert_with_redis(self):
        mock_redis = AsyncMock()
        with patch("app.services.notification_service.redis_client", mock_redis):
            farm_id = uuid4()
            alert_data = {"message": "pH too high"}
            await NotificationService.publish_alert(farm_id, alert_data)
            mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_sensor_with_redis(self):
        mock_redis = AsyncMock()
        with patch("app.services.notification_service.redis_client", mock_redis):
            await NotificationService.publish_sensor_reading(
                uuid4(), {"sensor_type": "ph", "value": 6.5}
            )
            mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_notification(self):
        mock_redis = AsyncMock()
        with patch("app.services.notification_service.redis_client", mock_redis):
            user_id = uuid4()
            notif = {"type": "alert", "message": "Test"}
            await NotificationService.cache_notification(user_id, notif)
            mock_redis.lpush.assert_called_once()
            mock_redis.ltrim.assert_called_once()
            mock_redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_notifications_no_redis(self):
        with patch("app.services.notification_service.redis_client", None):
            result = await NotificationService.get_user_notifications(uuid4())
            assert result == []

    @pytest.mark.asyncio
    async def test_get_user_notifications_with_redis(self):
        import json
        mock_redis = AsyncMock()
        notifs = [json.dumps({"type": "alert", "msg": "test"})]
        mock_redis.lrange.return_value = notifs
        with patch("app.services.notification_service.redis_client", mock_redis):
            result = await NotificationService.get_user_notifications(uuid4(), limit=10)
            assert len(result) == 1
            assert result[0]["type"] == "alert"

    @pytest.mark.asyncio
    async def test_send_email_notification(self):
        """Email notification should log without error."""
        await NotificationService.send_email_notification(
            "test@example.com", "Test Subject", "Test Body"
        )
        # Should complete without error

    @pytest.mark.asyncio
    async def test_publish_alert_redis_error(self):
        """Should handle Redis errors gracefully."""
        mock_redis = AsyncMock()
        mock_redis.publish.side_effect = Exception("Redis connection lost")
        with patch("app.services.notification_service.redis_client", mock_redis):
            # Should not raise
            await NotificationService.publish_alert(
                uuid4(), {"message": "test"}
            )
