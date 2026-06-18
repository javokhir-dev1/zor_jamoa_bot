"""
APScheduler sozlash va ishga tushirish.
Bot ishga tushganda scheduler ham yonadi (bir process ichida).
"""
import logging

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduler.jobs import send_final_distribution_report, send_reminders

logger = logging.getLogger(__name__)

TZ = pytz.timezone("Asia/Tashkent")

# Eslatma vaqtlari: (soat, daqiqa, tartib_raqami)
REMINDER_TIMES = [
    (12,  0, 1),
    (12, 30, 2),
    (13,  0, 3),
    (13, 30, 4),
    (13, 50, 5),
]


def create_scheduler(bot) -> AsyncIOScheduler:
    """
    Schedulerni yaratadi va barcha joblarni ro'yxatdan o'tkazadi.
    bot — aiogram Bot obyekti (jobga uzatiladi).
    """
    scheduler = AsyncIOScheduler(timezone=TZ)

    for hour, minute, num in REMINDER_TIMES:
        scheduler.add_job(
            send_reminders,
            trigger="cron",
            hour=hour,
            minute=minute,
            id=f"reminder_{num}",
            name=f"Eslatma #{num} ({hour:02d}:{minute:02d})",
            kwargs={"bot": bot, "reminder_num": num},
            replace_existing=True,
            misfire_grace_time=60,   # 1 daqiqa kechikishga ruxsat
        )
        logger.info(f"Job qo'shildi: Eslatma #{num} — {hour:02d}:{minute:02d} (Toshkent)")

    # 20:00 — yakuniy tarqatish hisoboti
    scheduler.add_job(
        send_final_distribution_report,
        trigger="cron",
        hour=20,
        minute=0,
        id="final_report",
        name="Yakuniy tarqatish hisoboti (20:00)",
        kwargs={"bot": bot},
        replace_existing=True,
        misfire_grace_time=300,
    )
    logger.info("Job qo'shildi: Yakuniy hisobot — 20:00 (Toshkent)")

    return scheduler
