"""Celery tasks for AI vision analysis."""
import asyncio
import logging
from uuid import UUID

from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.core.constants import AnalysisStatus, AnomalyType

logger = logging.getLogger(__name__)


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="tasks.analyze_plant_scan", queue="vision")
def analyze_plant_scan(scan_id: str):
    """Analyze a plant scan image using AI vision model."""

    async def _analyze():
        from app.services.vision_service import VisionService

        async with async_session_factory() as session:
            try:
                service = VisionService(session)

                # Update status to processing
                await service.update_analysis_result(
                    UUID(scan_id),
                    status=AnalysisStatus.PROCESSING,
                )
                await session.commit()

                # In production, call actual ML model API here
                # For now, simulate analysis with placeholder results
                analysis_result = {
                    "model_version": "greenos-vision-v1.0",
                    "processing_time_ms": 1250,
                    "detections": [],
                    "overall_health": "good",
                }

                health_score = 85.0  # Placeholder

                await service.update_analysis_result(
                    UUID(scan_id),
                    status=AnalysisStatus.COMPLETED,
                    result_data=analysis_result,
                    health_score=health_score,
                )
                await session.commit()

                logger.info(f"Plant scan {scan_id} analyzed successfully, health: {health_score}")
                return {"scan_id": scan_id, "health_score": health_score}

            except Exception as e:
                await service.update_analysis_result(
                    UUID(scan_id),
                    status=AnalysisStatus.FAILED,
                    result_data={"error": str(e)},
                )
                await session.commit()
                logger.error(f"Failed to analyze scan {scan_id}: {e}")
                raise

    return run_async(_analyze())


@celery_app.task(name="tasks.batch_scan_analysis", queue="vision")
def batch_scan_analysis(farm_id: str):
    """Process all pending scans for a farm."""

    async def _batch():
        from sqlalchemy import select
        from app.models.vision import PlantScan

        async with async_session_factory() as session:
            result = await session.execute(
                select(PlantScan.id).where(
                    PlantScan.farm_id == UUID(farm_id),
                    PlantScan.analysis_status == AnalysisStatus.PENDING,
                )
            )
            pending_ids = [str(row[0]) for row in result.all()]

            for scan_id in pending_ids:
                analyze_plant_scan.delay(scan_id)

            logger.info(f"Queued {len(pending_ids)} scans for analysis in farm {farm_id}")
            return len(pending_ids)

    return run_async(_batch())
