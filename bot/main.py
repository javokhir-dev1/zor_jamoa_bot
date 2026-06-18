import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import admin, departments, registration, reports, users_mgmt
from config import settings
from scheduler.setup import create_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni ulash (tartib muhim: admin birinchi)
    dp.include_router(admin.router)
    dp.include_router(departments.router)
    dp.include_router(users_mgmt.router)
    dp.include_router(reports.router)
    dp.include_router(registration.router)

    # Scheduler ishga tushirish
    scheduler = create_scheduler(bot)
    scheduler.start()
    logger.info("Scheduler ishga tushdi.")

    logger.info("Bot ishga tushmoqda...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
