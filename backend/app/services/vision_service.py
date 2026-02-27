"""AI Vision analysis service."""
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import AnalysisStatus, AnomalyType
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.vision import PlantScan, AnomalyDetection
from app.schemas.vision import PlantScanCreate


class VisionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_scan(self, data: PlantScanCreate, scanned_by: UUID) -> PlantScan:
        scan = PlantScan(
            **data.model_dump(),
            scanned_by_id=scanned_by,
            analysis_status=AnalysisStatus.PENDING,
        )
        self.db.add(scan)
        await self.db.flush()
        await self.db.refresh(scan)
        return scan

    async def get_scan(self, scan_id: UUID) -> PlantScan:
        result = await self.db.execute(
            select(PlantScan)
            .options(selectinload(PlantScan.anomalies))
            .where(PlantScan.id == scan_id)
        )
        scan = result.scalar_one_or_none()
        if not scan:
            raise NotFoundException("PlantScan", scan_id)
        return scan

    async def list_scans(
        self,
        farm_id: UUID,
        skip: int = 0,
        limit: int = 20,
        crop_cycle_id: UUID | None = None,
    ) -> tuple[list[PlantScan], int]:
        query = select(PlantScan).where(PlantScan.farm_id == farm_id)
        count_q = select(func.count()).select_from(PlantScan).where(PlantScan.farm_id == farm_id)

        if crop_cycle_id:
            query = query.where(PlantScan.crop_cycle_id == crop_cycle_id)
            count_q = count_q.where(PlantScan.crop_cycle_id == crop_cycle_id)

        total = (await self.db.execute(count_q)).scalar()
        result = await self.db.execute(
            query.options(selectinload(PlantScan.anomalies))
            .order_by(PlantScan.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def update_analysis_result(
        self,
        scan_id: UUID,
        status: AnalysisStatus,
        result_data: dict | None = None,
        health_score: float | None = None,
    ) -> PlantScan:
        scan = await self.get_scan(scan_id)
        scan.analysis_status = status
        if result_data:
            scan.analysis_result = result_data
        if health_score is not None:
            scan.health_score = health_score
        await self.db.flush()
        await self.db.refresh(scan)
        return scan

    async def add_anomaly(
        self,
        scan_id: UUID,
        anomaly_type: AnomalyType,
        confidence: float,
        bounding_box: dict | None = None,
        description: str | None = None,
    ) -> AnomalyDetection:
        await self.get_scan(scan_id)
        anomaly = AnomalyDetection(
            scan_id=scan_id,
            anomaly_type=anomaly_type,
            confidence=confidence,
            bounding_box=bounding_box,
            description=description,
        )
        self.db.add(anomaly)
        await self.db.flush()
        await self.db.refresh(anomaly)
        return anomaly

    async def get_anomaly_stats(self, farm_id: UUID) -> list[dict]:
        """Get anomaly type frequency for a farm."""
        result = await self.db.execute(
            select(
                AnomalyDetection.anomaly_type,
                func.count().label("count"),
                func.avg(AnomalyDetection.confidence).label("avg_confidence"),
            )
            .join(PlantScan, AnomalyDetection.scan_id == PlantScan.id)
            .where(PlantScan.farm_id == farm_id)
            .group_by(AnomalyDetection.anomaly_type)
            .order_by(func.count().desc())
        )
        return [
            {
                "anomaly_type": row.anomaly_type,
                "count": row.count,
                "avg_confidence": round(float(row.avg_confidence), 3),
            }
            for row in result.all()
        ]

    async def get_ai_advisory(self, farm_id: UUID) -> dict:
        """Generate advisory based on recent scans."""
        recent_scans = await self.db.execute(
            select(PlantScan)
            .options(selectinload(PlantScan.anomalies))
            .where(
                PlantScan.farm_id == farm_id,
                PlantScan.analysis_status == AnalysisStatus.COMPLETED,
            )
            .order_by(PlantScan.created_at.desc())
            .limit(20)
        )
        scans = list(recent_scans.scalars().all())

        if not scans:
            return {
                "summary": "No recent scans available for analysis.",
                "recommendations": [],
                "health_trend": "unknown",
            }

        health_scores = [s.health_score for s in scans if s.health_score is not None]
        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0

        all_anomalies = []
        for scan in scans:
            for anomaly in scan.anomalies:
                all_anomalies.append(anomaly.anomaly_type)

        anomaly_counts = {}
        for a in all_anomalies:
            anomaly_counts[a] = anomaly_counts.get(a, 0) + 1

        recommendations = []
        if AnomalyType.NUTRIENT_DEFICIENCY in anomaly_counts:
            recommendations.append("Review nutrient solution concentrations - deficiency detected in recent scans.")
        if AnomalyType.PEST_DAMAGE in anomaly_counts:
            recommendations.append("Inspect plants for pest activity and consider biological control measures.")
        if AnomalyType.DISEASE in anomaly_counts:
            recommendations.append("Isolate affected plants and check humidity levels to prevent disease spread.")
        if AnomalyType.LIGHT_STRESS in anomaly_counts:
            recommendations.append("Adjust light intensity or duration - light stress symptoms detected.")
        if avg_health < 60:
            recommendations.append("Overall plant health is below target. Conduct a comprehensive environment review.")

        health_trend = "stable"
        if len(health_scores) >= 4:
            first_half = sum(health_scores[len(health_scores)//2:]) / (len(health_scores) // 2)
            second_half = sum(health_scores[:len(health_scores)//2]) / (len(health_scores) // 2)
            if second_half > first_half + 5:
                health_trend = "improving"
            elif second_half < first_half - 5:
                health_trend = "declining"

        return {
            "summary": f"Analyzed {len(scans)} recent scans. Average health score: {avg_health:.1f}/100.",
            "avg_health_score": round(avg_health, 1),
            "total_anomalies": len(all_anomalies),
            "anomaly_breakdown": anomaly_counts,
            "health_trend": health_trend,
            "recommendations": recommendations,
        }
