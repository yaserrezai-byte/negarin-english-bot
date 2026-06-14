import logging
from datetime import datetime, timedelta
from appwrite.query import Query
from appwrite_client import get_databases
import config

db = get_databases()
DATABASE_ID = config.APPWRITE_DATABASE_ID
COL_USERS = "users"


def parse_time(ts):
    if not ts:
        return None
    if isinstance(ts, datetime):
        return ts
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def can_take_next_lesson(last_lesson_at_str, current_lesson_number):
    if current_lesson_number == 0:
        return True, 0
    last = parse_time(last_lesson_at_str)
    if not last:
        return True, 0
    if current_lesson_number % 3 == 0:
        gap = timedelta(days=2)
    else:
        gap = timedelta(days=1)
    now = datetime.now()
    available_at = last + gap
    if now >= available_at:
        return True, 0
    remaining = (available_at - now).total_seconds()
    return False, remaining


async def daily_reminder(bot):
    try:
        res = db.list_documents(DATABASE_ID, COL_USERS, queries=[
            Query.equal("status", "active"),
            Query.limit(100),
        ])
        users = res.get("documents", [])
        for user in users:
            can_take, _ = can_take_next_lesson(
                user.get("last_lesson_at", ""),
                user.get("current_lesson", 0)
            )
            if can_take:
                await bot.send_message(
                    user["telegram_id"],
                    "📚 درس جدید شما آماده است! برای ادامه /start را بزنید یا 'ادامه دوره' را انتخاب کنید."
                )
    except Exception as e:
        logging.error(f"Reminder error: {e}")
