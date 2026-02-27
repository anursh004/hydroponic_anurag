"""Celery tasks for alert processing."""
import asyncio
import logging
from uuid import UUID

from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.services.alert_service import AlertService
from app.services.notification_service import NotificationService
from app.schemas.sensor import SensorReadingCreate

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async code in synchronous Celery tasks."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="tasks.evaluate_sensor_reading", queue="alerts")
def evaluate_sensor_reading(sensor_id: str, value: float, sensor_type: str, farm_id: str):
    """Evaluate a sensor reading against alert rules."""

    async def _evaluate():
        async with async_session_factory() as session:
            try:
                service = AlertService(session)
                alerts = await service.evaluate_reading(
                    sensor_id=UUID(sensor_id),
                    value=value,
                    sensor_type=sensor_type,
                    farm_id=UUID(farm_id),
                )
                await session.commit()

                # Publish notifications for triggered alerts
                for alert in alerts:
                    await NotificationService.publish_alert(
                        UUID(farm_id),
                        {
                            "alert_id": str(alert.id),
                            "sensor_type": sensor_type,
                            "triggered_value": value,
                            "severity": alert.severity if hasattr(alert, "severity") else "warning",
                            "message": alert.message if hasattr(alert, "message") else f"Alert triggered for {sensor_type}",
                        },
                    )

                logger.info(f"Evaluated sensor {sensor_id}: {len(alerts)} alerts triggered")
                return len(alerts)
            except Exception as e:
                await session.rollback()
                logger.error(f"Error evaluating sensor reading: {e}")
                raise

    return run_async(_evaluate())


@celery_app.task(name="tasks.check_stale_sensors", queue="alerts")
def check_stale_sensors():
    """Check for sensors that haven't reported recently."""

    async def _check():
        from datetime import datetime, timedelta
        from sqlalchemy import select, and_
        from app.models.sensor import Sensor

        async with async_session_factory() as session:
            stale_threshold = datetime.utcnow() - timedelta(minutes=15)
            result = await session.execute(
                select(Sensor).where(
                    and_(
                        Sensor.is_active.is_(True),
                        Sensor.last_reading_at < stale_threshold,
                    )
                )
            )
            stale_sensors = result.scalars().all()
            for sensor in stale_sensors:
                logger.warning(
                    f"Stale sensor detected: {sensor.id} ({sensor.sensor_type}), "
                    f"last reading: {sensor.last_reading_at}"
                )
                await NotificationService.publish_alert(
                    sensor.farm_id,
                    {
                        "type": "stale_sensor",
                        "sensor_id": str(sensor.id),
                        "sensor_type": sensor.sensor_type,
                        "last_reading_at": sensor.last_reading_at.isoformat() if sensor.last_reading_at else None,
                    },
                )
            return len(stale_sensors)

    return run_async(_check())


@celery_app.task(name="tasks.cleanup_old_alerts", queue="alerts")
def cleanup_old_alerts(days: int = 90):
    """Archive/delete alerts older than specified days."""

    async def _cleanup():
        from datetime import datetime, timedelta
        from sqlalchemy import delete, and_
        from app.models.alert import Alert
        from app.core.constants import AlertStatus

        async with async_session_factory() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)
            result = await session.execute(
                delete(Alert).where(
                    and_(
                        Alert.created_at < cutoff,
                        Alert.status == AlertStatus.RESOLVED,
                    )
                )
            )
            await session.commit()
            logger.info(f"Cleaned up {result.rowcount} old resolved alerts")
            return result.rowcount

    return run_async(_cleanup())
