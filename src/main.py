import json
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import start, placement, lessons, homework, exams, admin

# Initialize bot and dispatcher (global for warm starts)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

dp.include_routers(
    start.router,
    placement.router,
    lessons.router,
    homework.router,
    exams.router,
    admin.router,
)

async def process_update(body_dict: dict):
    update = Update(**body_dict)
    await dp.feed_webhook_update(bot, update)

def main(context):
    try:
        body = context.req.body
        if isinstance(body, str):
            body_dict = json.loads(body)
        elif isinstance(body, bytes):
            body_dict = json.loads(body.decode("utf-8"))
        elif isinstance(body, dict):
            body_dict = body
        else:
            body_dict = json.loads(str(body))
        
        asyncio.run(process_update(body_dict))
    except Exception as e:
        print(f"Error: {e}")
    
    return context.res.send("OK", 200)
