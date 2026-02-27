"""Run all seed scripts."""
import asyncio
import logging
import sys

from app.core.database import async_session_factory, init_db
from app.seeds.default_roles import seed_roles_and_permissions
from app.seeds.crop_profiles import seed_crop_profiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_all_seeds():
    """Execute all seed functions."""
    await init_db()

    async with async_session_factory() as session:
        logger.info("Starting database seeding...")

        logger.info("Seeding roles and permissions...")
        await seed_roles_and_permissions(session)

        logger.info("Seeding crop profiles...")
        await seed_crop_profiles(session)

        logger.info("Database seeding completed successfully!")


def main():
    asyncio.run(run_all_seeds())


if __name__ == "__main__":
    main()
