from aiogram import Router, F
from aiogram.types import CallbackQuery
from appwrite_db import get_user_sync, get_lesson_sync, get_lessons_by_level_sync, update_user_lesson_sync
from keyboards import (
    main_menu_keyboard,
    next_lesson_keyboard,
    homework_type_keyboard,
    level_exam_keyboard,
)
from utils import can_take_next_lesson

router = Router()


@router.callback_query(F.data == "continue_course")
async def continue_course(callback: CallbackQuery):
    user = get_user_sync(callback.from_user.id)
    if not user or user.get("status") != "active":
        await callback.message.edit_text("❌ شما هنوز دوره‌ای فعال ندارید.")
        return

    level = user.get("level", "")
    current = user.get("current_lesson", 0)

    can_take, remaining = can_take_next_lesson(user.get("last_lesson_at", ""), current)
    if not can_take:
        hours = int(remaining // 3600)
        mins = int((remaining % 3600) // 60)
        await callback.message.edit_text(
            f"⏳ درس بعدی هنوز فعال نشده است.\n"
            f"🕒 زمان باقی‌مانده: {hours} ساعت و {mins} دقیقه\n\n"
            f"دوره به صورت ۳ روز در هفته برگزار می‌شود."
        )
        await callback.answer()
        return

    lesson = get_lesson_sync(level, current + 1)
    if not lesson:
        all_lessons = get_lessons_by_level_sync(level)
        if current >= len(all_lessons):
            await callback.message.edit_text(
                f"🎉 تبریک! تمام درس‌های سطح {level} تمام شد.\n"
                f"برای گرفتن مدرک این سطح، امتحان پایان سطح را بدهید.",
                reply_markup=level_exam_keyboard(level)
            )
            await callback.answer()
            return
        else:
            await callback.message.edit_text(
                "❌ درسی یافت نشد. لطفاً با پشتیبانی تماس بگیرید."
            )
            await callback.answer()
            return

    text = (
        f"📚 <b>{lesson.get('title', '')}</b>\n\n"
        f"📝 محتوا:\n{lesson.get('content', '')}\n\n"
        f"📌 تکلیف: {lesson.get('homework_desc', '')}"
    )

    if lesson.get("video_file_id"):
        await callback.message.answer_video(
            lesson["video_file_id"], caption=text, parse_mode="HTML"
        )
    else:
        await callback.message.answer(text, parse_mode="HTML")

    update_user_lesson_sync(callback.from_user.id, lesson.get("lesson_number", 0))

    await callback.message.answer(
        "✅ درس ارسال شد. لطفاً تکلیف این درس را تحویل دهید:",
        reply_markup=homework_type_keyboard(lesson["$id"])
    )
    await callback.answer()


@router.callback_query(F.data == "next_lesson")
async def next_lesson(callback: CallbackQuery):
    await continue_course(callback)
