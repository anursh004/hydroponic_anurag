"""Seed default roles and permissions."""
import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Role, Permission

logger = logging.getLogger(__name__)

PERMISSIONS = [
    # Farm
    "farm:read", "farm:create", "farm:update", "farm:delete",
    # Sensors
    "sensor:read", "sensor:create", "sensor:update", "sensor:delete",
    "sensor:reading:create",
    # Crops
    "crop:read", "crop:create", "crop:update", "crop:delete",
    # Alerts
    "alert:read", "alert:create", "alert:update", "alert:acknowledge", "alert:resolve",
    # Dosing
    "dosing:read", "dosing:create", "dosing:update", "dosing:execute",
    # Inventory
    "inventory:read", "inventory:create", "inventory:update", "inventory:delete",
    "inventory:transaction:create",
    # Harvests
    "harvest:read", "harvest:create",
    # Lighting
    "lighting:read", "lighting:create", "lighting:update", "lighting:command",
    # Orders
    "order:read", "order:create", "order:update",
    "customer:read", "customer:create", "customer:update",
    "subscription:read", "subscription:create", "subscription:update",
    "invoice:read", "invoice:create",
    # Tasks
    "task:read", "task:create", "task:update", "task:delete", "task:status",
    # Finance
    "finance:read", "finance:create", "finance:delete",
    # Vision
    "vision:read", "vision:create",
    # Users
    "user:read", "user:create", "user:update", "user:delete",
    # Dashboard
    "dashboard:read",
]

ROLE_PERMISSIONS = {
    "admin": PERMISSIONS,  # All permissions
    "farm_manager": [
        "farm:read", "farm:create", "farm:update",
        "sensor:read", "sensor:create", "sensor:update", "sensor:reading:create",
        "crop:read", "crop:create", "crop:update",
        "alert:read", "alert:create", "alert:update", "alert:acknowledge", "alert:resolve",
        "dosing:read", "dosing:create", "dosing:update", "dosing:execute",
        "inventory:read", "inventory:create", "inventory:update", "inventory:transaction:create",
        "harvest:read", "harvest:create",
        "lighting:read", "lighting:create", "lighting:update", "lighting:command",
        "order:read", "order:create", "order:update",
        "customer:read", "customer:create", "customer:update",
        "subscription:read", "subscription:create", "subscription:update",
        "invoice:read", "invoice:create",
        "task:read", "task:create", "task:update", "task:status",
        "finance:read", "finance:create",
        "vision:read", "vision:create",
        "dashboard:read",
    ],
    "operator": [
        "farm:read",
        "sensor:read", "sensor:reading:create",
        "crop:read", "crop:create", "crop:update",
        "alert:read", "alert:acknowledge",
        "dosing:read", "dosing:execute",
        "inventory:read", "inventory:transaction:create",
        "harvest:read", "harvest:create",
        "lighting:read", "lighting:command",
        "order:read", "order:create",
        "task:read", "task:status",
        "vision:read", "vision:create",
        "dashboard:read",
    ],
    "viewer": [
        "farm:read", "sensor:read", "crop:read", "alert:read",
        "dosing:read", "inventory:read", "harvest:read", "lighting:read",
        "order:read", "customer:read", "task:read", "finance:read",
        "vision:read", "dashboard:read",
    ],
}


async def seed_roles_and_permissions(session: AsyncSession):
    """Create default roles and permissions."""
    # Create permissions
    perm_objects = {}
    for perm_name in PERMISSIONS:
        existing = await session.execute(
            select(Permission).where(Permission.name == perm_name)
        )
        perm = existing.scalar_one_or_none()
        if not perm:
            perm = Permission(name=perm_name, description=f"Permission: {perm_name}")
            session.add(perm)
            await session.flush()
        perm_objects[perm_name] = perm

    # Create roles with permissions
    for role_name, role_perms in ROLE_PERMISSIONS.items():
        existing = await session.execute(
            select(Role).where(Role.name == role_name)
        )
        role = existing.scalar_one_or_none()
        if not role:
            role = Role(
                name=role_name,
                description=f"{role_name.replace('_', ' ').title()} role",
            )
            session.add(role)
            await session.flush()

        # Assign permissions
        role.permissions = [perm_objects[p] for p in role_perms if p in perm_objects]

    await session.commit()
    logger.info("Seeded default roles and permissions")
