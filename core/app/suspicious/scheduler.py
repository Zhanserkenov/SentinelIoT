import logging
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from core.app.core.config import settings
from core.app.core.database import AsyncSessionLocal
from core.app.suspicious.service import export_all_packets_to_telegram_and_clear

logger = logging.getLogger(__name__)

async def run_daily_suspicious_export() -> None:
    if not (settings.TELEGRAM_BOT_TOKEN or "").strip() or not (settings.TELEGRAM_SUSPICIOUS_EXPORT_CHAT_ID or "").strip():
        logger.warning("Daily suspicious export skipped: set TELEGRAM_BOT_TOKEN and TELEGRAM_SUSPICIOUS_EXPORT_CHAT_ID")
        return
    async with AsyncSessionLocal() as db:
        n = await export_all_packets_to_telegram_and_clear(db)
        if n == 0:
            logger.info("Daily suspicious export: no rows to export")


def register_suspicious_export_scheduler(scheduler: AsyncIOScheduler) -> None:
    if settings.SUSPICIOUS_EXPORT_TEST_EVERY_MINUTE:
        trigger = IntervalTrigger(minutes=2)
        logger.warning(
            "Suspicious export scheduler: TEST MODE — every 5 minute "
            "(set SUSPICIOUS_EXPORT_TEST_EVERY_MINUTE=false for production)"
        )
    else:
        tz = ZoneInfo(settings.SCHEDULER_TIMEZONE)
        trigger = CronTrigger(hour=0, minute=0, timezone=tz)

    scheduler.add_job(
        run_daily_suspicious_export,
        trigger,
        id="suspicious_packets_daily_export",
        replace_existing=True,
    )
