from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from appwrite_db import submit_homework
from keyboards import next_lesson_keyboard, confirm_homework_keyboard

router = Router()


class HomeworkState(StatesGroup):
    waiting = State()
    confirming = State()


@router.callback_query(F.data.startswith("hw_type:"))
async def choose_hw_type(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    lesson_id = parts[1]
    hw_type = parts[2]

    await state.set_state(HomeworkState.waiting)
    await state.update_data(lesson_id=lesson_id, hw_type=hw_type)

    if hw_type == "writing":
        await callback.message.edit_text("✍️ لطفاً تکلیف کتبی خود را ارسال کنید (متن یا فایل):")
    else:
        await callback.message.edit_text("🎙️ لطفاً تکلیف صوتی خود را به صورت ویس ارسال کنید:")
    await callback.answer()


@router.message(StateFilter(HomeworkState.waiting), F.text | F.document | F.photo)
async def receive_writing(message: Message, state: FSMContext):
    data = await state.get_data()
    hw_type = data["hw_type"]
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

    await state.update_data(text=text, file_id=file_id, file_type=file_type)
    await state.set_state(HomeworkState.confirming)
    await message.answer(
        "✅ تکلیف دریافت شد. آیا ارسال نهایی می‌کنید؟",
        reply_markup=confirm_homework_keyboard()
    )


@router.message(StateFilter(HomeworkState.waiting), F.voice)
async def receive_listening(message: Message, state: FSMContext):
    data = await state.get_data()
    hw_type = data["hw_type"]
    if hw_type != "listening":
        await message.answer("❌ نوع تکلیف نامعتبر.")
        return

    file_id = message.voice.file_id
    text = message.caption
    file_type = "voice"

    await state.update_data(file_id=file_id, file_type=file_type, text=text)
    await state.set_state(HomeworkState.confirming)
    await message.answer(
        "✅ ویس دریافت شد. آیا ارسال نهایی می‌کنید؟",
        reply_markup=confirm_homework_keyboard()
    )


@router.message(StateFilter(HomeworkState.waiting))
async def wrong_hw_format(message: Message):
    await message.answer(
        "❌ لطفاً فرمت صحیح را ارسال کنید.\n"
        "✍️ متن یا فایل / 🎙️ ویس"
    )


@router.callback_query(F.data == "confirm_hw", StateFilter(HomeworkState.confirming))
async def confirm_hw(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await submit_homework(
        callback.from_user.id,
        data["lesson_id"],
        data["hw_type"],
        data.get("file_id"),
        data.get("file_type"),
        data.get("text")
    )
    await state.clear()
    await callback.message.edit_text(
        "✅ تکلیف شما ثبت شد و در انتظار بررسی است.\n\n"
        "پس از تأیید می‌توانید درس بعدی را بگیرید.",
        reply_markup=next_lesson_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_hw", StateFilter(HomeworkState.confirming))
async def cancel_hw(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ تکلیف لغو شد.")
    await callback.answer()
