import json
from aiogram import Router, F
from aiogram.types import CallbackQuery
from appwrite_db import (
    get_user_sync,
    get_placement_questions_sync,
    save_placement_answer_sync,
    get_user_placement_score_sync,
    update_user_level_sync,
    clear_placement_answers_sync,
    set_user_temp_state_sync,
    get_user_temp_state_sync,
    clear_temp_state_sync,
)
from keyboards import main_menu_keyboard, answer_options_keyboard

router = Router()

PLACEMENT_QUESTIONS = []


def load_questions():
    global PLACEMENT_QUESTIONS
    PLACEMENT_QUESTIONS = get_placement_questions_sync()


@router.callback_query(F.data == "start_placement")
async def start_placement(callback: CallbackQuery):
    load_questions()
    if not PLACEMENT_QUESTIONS:
        await callback.message.edit_text("❌ سوالات تعیین سطح هنوز تنظیم نشده است.")
        return
    clear_placement_answers_sync(callback.from_user.id)
    set_user_temp_state_sync(callback.from_user.id, {"status": "placement", "q_index": 0})
    await callback.answer()
    await show_question(callback.message, 0)


async def show_question(message, q_index: int):
    if q_index >= len(PLACEMENT_QUESTIONS):
        result = get_user_placement_score_sync(message.chat.id)
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

        update_user_level_sync(message.chat.id, level, status="active")
        clear_temp_state_sync(message.chat.id)
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
async def handle_answer(callback: CallbackQuery):
    state = get_user_temp_state_sync(callback.from_user.id)
    if state.get("status") != "placement":
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

    save_placement_answer_sync(callback.from_user.id, question_id, answer_idx, is_correct)

    q_index = state.get("q_index", 0) + 1
    set_user_temp_state_sync(callback.from_user.id, {"status": "placement", "q_index": q_index})

    await callback.answer("✅ درست" if is_correct else "❌ غلط")
    await show_question(callback.message, q_index)
