import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
from utils import daily_reminder
from handlers import start, placement, lessons, homework, exams, admin


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_routers(
        start.router,
        placement.router,
        lessons.router,
        homework.router,
        exams.router,
        admin.router,
    )

    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_reminder, "cron", hour=9, minute=0, args=[bot])
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
