import json
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import start, placement, lessons, homework, exams, admin

# Initialize bot and dispatcher once (module level for warm starts)
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


async def process_update(update_data: dict):
    update = Update(**update_data)
    await dp.feed_webhook_update(bot, update)


# Appwrite Function entry point
def main(context):
    """
    context.req -> incoming request
    context.res -> response builder
    """
    try:
        # Handle different Appwrite versions
        if hasattr(context, 'req'):
            body = context.req.body
        elif hasattr(context, 'request'):
            body = context.request.body
        else:
            body = context

        # Parse body
        if isinstance(body, str):
            update_data = json.loads(body)
        elif isinstance(body, dict):
            update_data = body
        else:
            try:
                body_str = body.decode('utf-8')
            except AttributeError:
                body_str = str(body)
            update_data = json.loads(body_str)

        # Process Telegram update
        asyncio.run(process_update(update_data))

        # Return 200 OK to Telegram (always return 200 to avoid retries)
        if hasattr(context, 'res'):
            return context.res.send("OK", 200)
        else:
            return {"body": "OK", "statusCode": 200}

    except Exception as e:
        # Always return 200 to Telegram to prevent endless retries
        if hasattr(context, 'res'):
            return context.res.send("OK", 200)
        else:
            return {"body": "OK", "statusCode": 200}
