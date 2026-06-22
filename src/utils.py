from datetime import datetime, timedelta


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
