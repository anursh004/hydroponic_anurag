"""Celery tasks for automated dosing."""
import asyncio
import logging
from uuid import UUID

from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="tasks.auto_dose_check", queue="dosing")
def auto_dose_check(farm_id: str):
    """Check if auto-dosing is needed based on current sensor readings and recipes."""

    async def _check():
        from sqlalchemy import select, and_
        from app.models.dosing import DosingRecipe, DosingPump
        from app.models.sensor import Sensor
        from app.core.constants import SensorType

        async with async_session_factory() as session:
            try:
                # Get active recipes for the farm
                recipes = await session.execute(
                    select(DosingRecipe).where(
                        and_(
                            DosingRecipe.farm_id == UUID(farm_id),
                            DosingRecipe.is_active.is_(True),
                        )
                    )
                )
                active_recipes = recipes.scalars().all()

                dosing_actions = []
                for recipe in active_recipes:
                    # Get latest pH reading
                    ph_sensor = await session.execute(
                        select(Sensor).where(
                            and_(
                                Sensor.farm_id == UUID(farm_id),
                                Sensor.sensor_type == SensorType.PH,
                                Sensor.is_active.is_(True),
                            )
                        ).limit(1)
                    )
                    ph = ph_sensor.scalar_one_or_none()

                    # Get latest EC reading
                    ec_sensor = await session.execute(
                        select(Sensor).where(
                            and_(
                                Sensor.farm_id == UUID(farm_id),
                                Sensor.sensor_type == SensorType.EC,
                                Sensor.is_active.is_(True),
                            )
                        ).limit(1)
                    )
                    ec = ec_sensor.scalar_one_or_none()

                    if ph and ph.last_value is not None:
                        if recipe.target_ph_min and float(ph.last_value) < float(recipe.target_ph_min):
                            dosing_actions.append({
                                "recipe_id": str(recipe.id),
                                "action": "ph_up",
                                "current_ph": float(ph.last_value),
                                "target": float(recipe.target_ph_min),
                            })
                        elif recipe.target_ph_max and float(ph.last_value) > float(recipe.target_ph_max):
                            dosing_actions.append({
                                "recipe_id": str(recipe.id),
                                "action": "ph_down",
                                "current_ph": float(ph.last_value),
                                "target": float(recipe.target_ph_max),
                            })

                    if ec and ec.last_value is not None:
                        if recipe.target_ec_min and float(ec.last_value) < float(recipe.target_ec_min):
                            dosing_actions.append({
                                "recipe_id": str(recipe.id),
                                "action": "nutrient_up",
                                "current_ec": float(ec.last_value),
                                "target": float(recipe.target_ec_min),
                            })

                for action in dosing_actions:
                    await NotificationService.publish_dosing_event(
                        UUID(farm_id), action
                    )

                logger.info(f"Auto-dose check for farm {farm_id}: {len(dosing_actions)} actions needed")
                return dosing_actions

            except Exception as e:
                logger.error(f"Error in auto dose check: {e}")
                raise

    return run_async(_check())


@celery_app.task(name="tasks.calibration_reminder", queue="dosing")
def calibration_reminder():
    """Check for dosing pumps due for calibration."""

    async def _check():
        from datetime import datetime, timedelta
        from sqlalchemy import select, and_
        from app.models.dosing import DosingPump

        async with async_session_factory() as session:
            threshold = datetime.utcnow() - timedelta(days=30)
            result = await session.execute(
                select(DosingPump).where(
                    and_(
                        DosingPump.is_active.is_(True),
                        DosingPump.last_calibrated_at < threshold,
                    )
                )
            )
            pumps = result.scalars().all()
            for pump in pumps:
                logger.info(f"Pump {pump.id} due for calibration (last: {pump.last_calibrated_at})")
            return len(pumps)

    return run_async(_check())
