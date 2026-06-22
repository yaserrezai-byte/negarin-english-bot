from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from appwrite_db import submit_homework_sync, set_user_temp_state_sync, get_user_temp_state_sync, clear_temp_state_sync
from keyboards import next_lesson_keyboard, confirm_homework_keyboard

router = Router()


@router.callback_query(F.data.startswith("hw_type:"))
async def choose_hw_type(callback: CallbackQuery):
    parts = callback.data.split(":")
    lesson_id = parts[1]
    hw_type = parts[2]
    set_user_temp_state_sync(callback.from_user.id, {
        "status": "homework",
        "lesson_id": lesson_id,
        "hw_type": hw_type,
        "step": "waiting"
    })
    if hw_type == "writing":
        await callback.message.edit_text("✍️ لطفاً تکلیف کتبی خود را ارسال کنید (متن یا فایل):")
    else:
        await callback.message.edit_text("🎙️ لطفاً تکلیف صوتی خود را به صورت ویس ارسال کنید:")
    await callback.answer()


@router.message(F.text | F.document | F.photo)
async def receive_writing(message: Message):
    state = get_user_temp_state_sync(message.from_user.id)
    if state.get("status") != "homework" or state.get("step") != "waiting":
        return

    hw_type = state.get("hw_type")
    if hw_type != "writing":
        await message.answer("❌ این بخش فقط برای تکلیف کتبی است.")
        return

    text = message.text or message.caption
    file_id = None
    file_type = None
    if message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"

    set_user_temp_state_sync(message.from_user.id, {
        **state,
        "step": "confirming",
        "text": text,
        "file_id": file_id,
        "file_type": file_type
    })

    await message.answer(
        "✅ تکلیف دریافت شد. آیا ارسال نهایی می‌کنید؟",
        reply_markup=confirm_homework_keyboard()
    )


@router.message(F.voice)
async def receive_listening(message: Message):
    state = get_user_temp_state_sync(message.from_user.id)
    if state.get("status") != "homework" or state.get("step") != "waiting":
        return

    hw_type = state.get("hw_type")
    if hw_type != "listening":
        await message.answer("❌ نوع تکلیف نامعتبر.")
        return

    file_id = message.voice.file_id
    text = message.caption

    set_user_temp_state_sync(message.from_user.id, {
        **state,
        "step": "confirming",
        "file_id": file_id,
        "file_type": "voice",
        "text": text
    })

    await message.answer(
        "✅ ویس دریافت شد. آیا ارسال نهایی می‌کنید؟",
        reply_markup=confirm_homework_keyboard()
    )


@router.callback_query(F.data == "confirm_hw")
async def confirm_hw(callback: CallbackQuery):
    state = get_user_temp_state_sync(callback.from_user.id)
    if not state or state.get("step") != "confirming":
        await callback.answer("❌ ابتدا تکلیف را ارسال کنید.", show_alert=True)
        return

    submit_homework_sync(
        callback.from_user.id,
        state["lesson_id"],
        state["hw_type"],
        state.get("file_id"),
        state.get("file_type"),
        state.get("text")
    )
    clear_temp_state_sync(callback.from_user.id)
    await callback.message.edit_text(
        "✅ تکلیف شما ثبت شد و در انتظار بررسی است.\n\n"
        "پس از تأیید می‌توانید درس بعدی را بگیرید.",
        reply_markup=next_lesson_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_hw")
async def cancel_hw(callback: CallbackQuery):
    clear_temp_state_sync(callback.from_user.id)
    await callback.message.edit_text("❌ تکلیف لغو شد.")
    await callback.answer()
