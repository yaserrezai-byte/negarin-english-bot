from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from appwrite_db import get_pending_homework, review_homework, set_lesson_video
from config import ADMIN_IDS
from keyboards import admin_keyboard

router = Router()


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("🛠 پنل مدیریت", reply_markup=admin_keyboard())


@router.callback_query(F.data == "admin_homework")
async def show_pending_homework(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔️")
        return
    homeworks = await get_pending_homework()
    if not homeworks:
        await callback.message.edit_text("📭 تکلیف در انتظاری وجود ندارد.")
        return

    for hw in homeworks[:5]:
        user = hw.get("user", {})
        lesson = hw.get("lesson", {})
        text = (
            f"👤 {user.get('full_name', '---')}\n"
            f"📚 {lesson.get('title', '---')}\n"
            f"📝 نوع: {hw.get('type', '')}\n"
            f"🆔 ID: {hw['$id']}"
        )
        if hw.get("file_id"):
            if hw.get("file_type") == "voice":
                await callback.message.answer_voice(hw["file_id"], caption=text)
            elif hw.get("file_type") == "photo":
                await callback.message.answer_photo(hw["file_id"], caption=text)
            else:
                await callback.message.answer_document(hw["file_id"], caption=text)
        else:
            text += f"\n💬 متن: {hw.get('text_content') or '-'}"
            await callback.message.answer(text)

    await callback.message.answer(
        "برای تصحیح تکلیف دستور زیر را بفرستید:\n"
        "/review <id> <score> <comment>"
    )
    await callback.answer()


@router.message(Command("review"))
async def cmd_review(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer("نحوه استفاده:\n/review <id> <score> <comment>")
        return
    try:
        hw_id = parts[1]
        score = int(parts[2])
        comment = parts[3]
        await review_homework(hw_id, score, comment)
        await message.answer("✅ تکلیف تصحیح و ثبت شد.")
    except Exception as e:
        await message.answer(f"❌ خطا: {e}")


@router.message(F.video)
async def get_video_id(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer(f"📹 Video File ID:\n<code>{message.video.file_id}</code>")


@router.message(F.voice)
async def get_voice_id(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer(f"🎙️ Voice File ID:\n<code>{message.voice.file_id}</code>")


@router.message(Command("set_video"))
async def cmd_set_video(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not message.reply_to_message or not message.reply_to_message.video:
        await message.answer("روی یک ویدیو ریپلای کنید و بنویسید: /set_video <lesson_id>")
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("نحوه استفاده: /set_video <lesson_id>")
        return
    try:
        lesson_id = parts[1]
        file_id = message.reply_to_message.video.file_id
        await set_lesson_video(lesson_id, file_id)
        await message.answer("✅ ویدیو برای درس ثبت شد.")
    except Exception as e:
        await message.answer(f"❌ خطا: {e}")
