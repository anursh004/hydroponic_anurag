"""Alert management endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.core.constants import AlertStatus
from app.models.user import User
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.alert import (
    AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse,
    AlertResponse, AlertAcknowledge,
    EscalationPolicyCreate, EscalationPolicyResponse,
)
from app.services.alert_service import AlertService

router = APIRouter()


# --- Alert Rules ---
@router.post("/rules", response_model=AlertRuleResponse, status_code=201)
async def create_alert_rule(
    farm_id: UUID,
    data: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = AlertService(db)
    return await service.create_rule(farm_id, data)


@router.get("/rules", response_model=list[AlertRuleResponse])
async def list_alert_rules(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = AlertService(db)
    return await service.get_rules(farm_id)


@router.patch("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    farm_id: UUID,
    rule_id: UUID,
    data: AlertRuleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = AlertService(db)
    return await service.update_rule(rule_id, data)


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_alert_rule(
    farm_id: UUID,
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    service = AlertService(db)
    await service.delete_rule(rule_id)


# --- Alerts ---
@router.get("/", response_model=PaginatedResponse[AlertResponse])
async def list_alerts(
    farm_id: UUID,
    status: AlertStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = AlertService(db)
    alerts, total = await service.get_alerts(farm_id, status=status, skip=skip, limit=limit)
    return PaginatedResponse(items=alerts, total=total, skip=skip, limit=limit)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    farm_id: UUID,
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = AlertService(db)
    return await service.get_alert(alert_id)


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    farm_id: UUID,
    alert_id: UUID,
    data: AlertAcknowledge,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = AlertService(db)
    return await service.acknowledge_alert(alert_id, current_user.id, data.notes)


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    farm_id: UUID,
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = AlertService(db)
    return await service.resolve_alert(alert_id, current_user.id)


@router.get("/count/active", response_model=dict)
async def count_active_alerts(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = AlertService(db)
    count = await service.count_active_alerts(farm_id)
    return {"count": count}


# --- Escalation Policies ---
@router.post("/escalation-policies", response_model=EscalationPolicyResponse, status_code=201)
async def create_escalation_policy(
    farm_id: UUID,
    data: EscalationPolicyCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = AlertService(db)
    return await service.create_escalation_policy(farm_id, data)
