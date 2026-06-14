import json
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from appwrite_db import (
    get_user,
    get_placement_questions,
    save_placement_answer,
    get_user_placement_score,
    update_user_level,
    clear_placement_answers,
)
from keyboards import main_menu_keyboard, answer_options_keyboard

router = Router()


class PlacementState(StatesGroup):
    answering = State()


PLACEMENT_QUESTIONS = []


async def load_questions():
    global PLACEMENT_QUESTIONS
    PLACEMENT_QUESTIONS = await get_placement_questions()


@router.callback_query(F.data == "start_placement")
async def start_placement(callback: CallbackQuery, state: FSMContext):
    await load_questions()
    if not PLACEMENT_QUESTIONS:
        await callback.message.edit_text("❌ سوالات تعیین سطح هنوز تنظیم نشده است.")
        return
    await clear_placement_answers(callback.from_user.id)
    await state.set_state(PlacementState.answering)
    await state.update_data(q_index=0)
    await callback.answer()
    await show_question(callback.message, 0)


async def show_question(message, q_index: int):
    if q_index >= len(PLACEMENT_QUESTIONS):
        result = await get_user_placement_score(message.chat.id)
        total = result["total"]
        correct = result["correct"]
        percentage = (correct / total * 100) if total else 0

        if percentage < 30:
            level = "A1"
        elif percentage < 50:
            level = "A2"
        elif percentage < 65:
            level = "B1"
        elif percentage < 80:
            level = "B2"
        elif percentage < 90:
            level = "C1"
        else:
            level = "C2"

        await update_user_level(message.chat.id, level, status="active")
        await message.answer(
            f"✅ تعیین سطح تمام شد!\n\n"
            f"🎯 نمره: {correct} از {total} ({percentage:.0f}%)\n"
            f"📚 سطح شما: <b>{level}</b>\n\n"
            f"می‌توانید دوره خود را شروع کنید.",
            reply_markup=main_menu_keyboard()
        )
        return

    q = PLACEMENT_QUESTIONS[q_index]
    options = json.loads(q.get("options", "[]"))
    text = (
        f"📝 سوال {q_index+1} از {len(PLACEMENT_QUESTIONS)}\n\n"
        f"{q.get('question_text', '')}"
    )
    await message.edit_text(text, reply_markup=answer_options_keyboard(options, q["$id"]))


@router.callback_query(F.data.startswith("placement_answer:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    if not await state.get_state():
        await callback.answer()
        return
    parts = callback.data.split(":")
    question_id = parts[1]
    answer_idx = int(parts[2])

    q = next((x for x in PLACEMENT_QUESTIONS if x["$id"] == question_id), None)
    if not q:
        await callback.answer()
        return

    correct = int(q.get("correct_answer", 0))
    is_correct = (answer_idx == correct)

    await save_placement_answer(callback.from_user.id, question_id, answer_idx, is_correct)

    data = await state.get_data()
    q_index = data.get("q_index", 0) + 1
    await state.update_data(q_index=q_index)

    await callback.answer("✅ درست" if is_correct else "❌ غلط")
    await show_question(callback.message, q_index)
