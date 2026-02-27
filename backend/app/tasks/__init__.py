"""Celery tasks package."""
from app.tasks.alert_tasks import *  # noqa: F401,F403
from app.tasks.dosing_tasks import *  # noqa: F401,F403
from app.tasks.inventory_tasks import *  # noqa: F401,F403
from app.tasks.report_tasks import *  # noqa: F401,F403
from app.tasks.vision_tasks import *  # noqa: F401,F403
