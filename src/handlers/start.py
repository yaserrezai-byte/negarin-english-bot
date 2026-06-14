from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from appwrite_db import get_user, register_user
from keyboards import main_menu_keyboard, placement_start_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await register_user(
            message.from_user.id,
            message.from_user.full_name,
            message.from_user.username
        )
        await message.answer(
            f"👋 سلام {message.from_user.full_name}!")
        await message.answer(
            "به <b>ربات آموزش زبان انگلیسی</b> خوش آمدید.\n\n"
            "📌 در این ربات:\n"
            "• سطح شما تعیین می‌شود\n"
            "• دوره ۳ روز در هفته طی می‌شود\n"
            "• تکالیف صوتی و کتبی دریافت می‌شود\n"
            "• امتحان پایان سطح و پایان دوره دارد\n\n"
            "برای شروع، روی دکمه زیر بزنید:",
            reply_markup=placement_start_keyboard()
        )
    else:
        status = user.get("status", "placement")
        if status == "placement":
            await message.answer(
                "⏳ شما هنوز تعیین سطح را کامل نکرده‌اید.",
                reply_markup=placement_start_keyboard()
            )
        elif status == "active":
            await message.answer(
                "📚 به منوی اصلی خوش آمدید:",
                reply_markup=main_menu_keyboard()
            )
        else:
            await message.answer("وضعیت شما نامشخص است. با پشتیبانی تماس بگیرید.")


@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    await callback.message.edit_text("📚 منوی اصلی:", reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "my_status")
async def my_status(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer()
        return
    text = (
        f"📊 وضعیت شما:\n\n"
        f"👤 نام: {user.get('full_name', '')}\n"
        f"📚 سطح: {user.get('level') or 'تعیین نشده'}\n"
        f"📖 درس فعلی: {user.get('current_lesson', 0)}\n"
        f"📅 وضعیت: {user.get('status', '')}\n"
    )
    if user.get("last_lesson_at"):
        text += f"🕒 آخرین درس: {user.get('last_lesson_at')}\n"
    await callback.message.edit_text(text, reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    await callback.message.edit_text(
        "🧑‍🏫 برای پشتیبانی می‌توانید با ادمین تماس بگیرید.\n"
        "آیدی: @admin_username"
    )
    await callback.answer()


@router.callback_query(F.data == "submit_homework_menu")
async def homework_menu_hint(callback: CallbackQuery):
    await callback.message.edit_text(
        "📌 برای ارسال تکلیف، ابتدا باید درسی را دریافت کرده باشید.\n"
        "از منوی اصلی 'ادامه دوره' را انتخاب کنید.",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()
