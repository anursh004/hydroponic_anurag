"""Seed default crop profiles for hydroponic farming."""
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crop import CropProfile

logger = logging.getLogger(__name__)

DEFAULT_CROP_PROFILES = [
    {
        "name": "Butterhead Lettuce",
        "species": "Lactuca sativa",
        "variety": "Butterhead",
        "growth_days": 35,
        "germination_days": 3,
        "ideal_ph_min": 5.5, "ideal_ph_max": 6.5,
        "ideal_ec_min": 0.8, "ideal_ec_max": 1.2,
        "ideal_temp_min": 15.0, "ideal_temp_max": 22.0,
        "ideal_humidity_min": 50.0, "ideal_humidity_max": 70.0,
        "ideal_co2_min": 400, "ideal_co2_max": 1200,
        "ideal_light_hours": 16,
        "ideal_light_intensity_min": 200, "ideal_light_intensity_max": 400,
        "nutrient_recipe": {"n": 150, "p": 50, "k": 200, "ca": 150, "mg": 50},
        "is_system_default": True,
    },
    {
        "name": "Romaine Lettuce",
        "species": "Lactuca sativa",
        "variety": "Romaine",
        "growth_days": 40,
        "germination_days": 3,
        "ideal_ph_min": 5.5, "ideal_ph_max": 6.5,
        "ideal_ec_min": 0.8, "ideal_ec_max": 1.2,
        "ideal_temp_min": 15.0, "ideal_temp_max": 22.0,
        "ideal_humidity_min": 50.0, "ideal_humidity_max": 70.0,
        "ideal_co2_min": 400, "ideal_co2_max": 1200,
        "ideal_light_hours": 16,
        "ideal_light_intensity_min": 200, "ideal_light_intensity_max": 400,
        "nutrient_recipe": {"n": 150, "p": 50, "k": 200, "ca": 150, "mg": 50},
        "is_system_default": True,
    },
    {
        "name": "Basil (Sweet)",
        "species": "Ocimum basilicum",
        "variety": "Genovese",
        "growth_days": 28,
        "germination_days": 5,
        "ideal_ph_min": 5.5, "ideal_ph_max": 6.5,
        "ideal_ec_min": 1.0, "ideal_ec_max": 1.6,
        "ideal_temp_min": 18.0, "ideal_temp_max": 27.0,
        "ideal_humidity_min": 40.0, "ideal_humidity_max": 60.0,
        "ideal_co2_min": 400, "ideal_co2_max": 1500,
        "ideal_light_hours": 16,
        "ideal_light_intensity_min": 300, "ideal_light_intensity_max": 600,
        "nutrient_recipe": {"n": 180, "p": 50, "k": 220, "ca": 160, "mg": 50},
        "is_system_default": True,
    },
    {
        "name": "Cherry Tomato",
        "species": "Solanum lycopersicum",
        "variety": "Cherry",
        "growth_days": 75,
        "germination_days": 7,
        "ideal_ph_min": 5.5, "ideal_ph_max": 6.5,
        "ideal_ec_min": 2.0, "ideal_ec_max": 5.0,
        "ideal_temp_min": 18.0, "ideal_temp_max": 28.0,
        "ideal_humidity_min": 50.0, "ideal_humidity_max": 70.0,
        "ideal_co2_min": 400, "ideal_co2_max": 1500,
        "ideal_light_hours": 14,
        "ideal_light_intensity_min": 400, "ideal_light_intensity_max": 800,
        "nutrient_recipe": {"n": 200, "p": 60, "k": 350, "ca": 190, "mg": 50},
        "is_system_default": True,
    },
    {
        "name": "Strawberry",
        "species": "Fragaria × ananassa",
        "variety": "Everbearing",
        "growth_days": 90,
        "germination_days": 14,
        "ideal_ph_min": 5.5, "ideal_ph_max": 6.2,
        "ideal_ec_min": 1.0, "ideal_ec_max": 1.5,
        "ideal_temp_min": 15.0, "ideal_temp_max": 26.0,
        "ideal_humidity_min": 60.0, "ideal_humidity_max": 75.0,
        "ideal_co2_min": 400, "ideal_co2_max": 1000,
        "ideal_light_hours": 12,
        "ideal_light_intensity_min": 300, "ideal_light_intensity_max": 600,
        "nutrient_recipe": {"n": 80, "p": 80, "k": 300, "ca": 120, "mg": 40},
        "is_system_default": True,
    },
    {
        "name": "Kale",
        "species": "Brassica oleracea",
        "variety": "Curly",
        "growth_days": 45,
        "germination_days": 4,
        "ideal_ph_min": 5.5, "ideal_ph_max": 6.5,
        "ideal_ec_min": 1.2, "ideal_ec_max": 2.0,
        "ideal_temp_min": 12.0, "ideal_temp_max": 22.0,
        "ideal_humidity_min": 40.0, "ideal_humidity_max": 60.0,
        "ideal_co2_min": 400, "ideal_co2_max": 1200,
        "ideal_light_hours": 14,
        "ideal_light_intensity_min": 250, "ideal_light_intensity_max": 500,
        "nutrient_recipe": {"n": 200, "p": 60, "k": 240, "ca": 180, "mg": 50},
        "is_system_default": True,
    },
    {
        "name": "Spinach",
        "species": "Spinacia oleracea",
        "variety": "Bloomsdale",
        "growth_days": 30,
        "germination_days": 5,
        "ideal_ph_min": 6.0, "ideal_ph_max": 7.0,
        "ideal_ec_min": 1.8, "ideal_ec_max": 2.3,
        "ideal_temp_min": 12.0, "ideal_temp_max": 20.0,
        "ideal_humidity_min": 40.0, "ideal_humidity_max": 60.0,
        "ideal_co2_min": 400, "ideal_co2_max": 1200,
        "ideal_light_hours": 14,
        "ideal_light_intensity_min": 200, "ideal_light_intensity_max": 400,
        "nutrient_recipe": {"n": 170, "p": 50, "k": 230, "ca": 150, "mg": 50},
        "is_system_default": True,
    },
    {
        "name": "Cucumber",
        "species": "Cucumis sativus",
        "variety": "English",
        "growth_days": 55,
        "germination_days": 3,
        "ideal_ph_min": 5.5, "ideal_ph_max": 6.0,
        "ideal_ec_min": 1.7, "ideal_ec_max": 2.5,
        "ideal_temp_min": 20.0, "ideal_temp_max": 30.0,
        "ideal_humidity_min": 60.0, "ideal_humidity_max": 80.0,
        "ideal_co2_min": 400, "ideal_co2_max": 1500,
        "ideal_light_hours": 16,
        "ideal_light_intensity_min": 400, "ideal_light_intensity_max": 700,
        "nutrient_recipe": {"n": 190, "p": 60, "k": 310, "ca": 170, "mg": 50},
        "is_system_default": True,
    },
    {
        "name": "Bell Pepper",
        "species": "Capsicum annuum",
        "variety": "California Wonder",
        "growth_days": 70,
        "germination_days": 8,
        "ideal_ph_min": 5.5, "ideal_ph_max": 6.5,
        "ideal_ec_min": 2.0, "ideal_ec_max": 3.5,
        "ideal_temp_min": 18.0, "ideal_temp_max": 28.0,
        "ideal_humidity_min": 50.0, "ideal_humidity_max": 70.0,
        "ideal_co2_min": 400, "ideal_co2_max": 1500,
        "ideal_light_hours": 14,
        "ideal_light_intensity_min": 400, "ideal_light_intensity_max": 700,
        "nutrient_recipe": {"n": 180, "p": 60, "k": 280, "ca": 150, "mg": 50},
        "is_system_default": True,
    },
    {
        "name": "Mint",
        "species": "Mentha spicata",
        "variety": "Spearmint",
        "growth_days": 25,
        "germination_days": 7,
        "ideal_ph_min": 5.5, "ideal_ph_max": 6.5,
        "ideal_ec_min": 1.2, "ideal_ec_max": 1.6,
        "ideal_temp_min": 15.0, "ideal_temp_max": 25.0,
        "ideal_humidity_min": 50.0, "ideal_humidity_max": 70.0,
        "ideal_co2_min": 400, "ideal_co2_max": 1200,
        "ideal_light_hours": 14,
        "ideal_light_intensity_min": 200, "ideal_light_intensity_max": 400,
        "nutrient_recipe": {"n": 160, "p": 40, "k": 200, "ca": 130, "mg": 40},
        "is_system_default": True,
    },
]


async def seed_crop_profiles(session: AsyncSession):
    """Create default crop profiles."""
    for profile_data in DEFAULT_CROP_PROFILES:
        existing = await session.execute(
            select(CropProfile).where(
                CropProfile.name == profile_data["name"],
                CropProfile.is_system_default.is_(True),
            )
        )
        if existing.scalar_one_or_none():
            continue

        profile = CropProfile(**profile_data)
        session.add(profile)

    await session.commit()
    logger.info(f"Seeded {len(DEFAULT_CROP_PROFILES)} default crop profiles")
