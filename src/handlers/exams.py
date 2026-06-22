import json
from aiogram import Router, F
from aiogram.types import CallbackQuery
from appwrite_db import get_user_sync, get_exam_sync, save_exam_result_sync, update_user_level_sync, set_user_temp_state_sync, get_user_temp_state_sync, clear_temp_state_sync
from keyboards import main_menu_keyboard, exam_options_keyboard, exam_start_keyboard, level_exam_keyboard

router = Router()


@router.callback_query(F.data.startswith("level_exam:"))
async def prompt_start_exam(callback: CallbackQuery):
    await callback.message.edit_text(
        "📋 امتحان پایان سطح\n\n"
        "تعداد سوالات: ۴ (نمونه)\n"
        "حداقل نمره قبولی: ۷۰\n\n"
        "آماده‌اید؟",
        reply_markup=exam_start_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "start_exam")
async def start_exam(callback: CallbackQuery):
    user = get_user_sync(callback.from_user.id)
    if not user:
        await callback.answer()
        return
    level = user.get("level", "")
    exam = get_exam_sync(level, "level_exit")
    if not exam:
        await callback.message.edit_text("❌ امتحانی برای این سطح تعریف نشده است.")
        return

    questions = json.loads(exam.get("questions_json", "[]"))
    set_user_temp_state_sync(callback.from_user.id, {
        "status": "exam",
        "exam_id": exam["$id"],
        "q_index": 0,
        "score": 0,
        "questions": questions
    })
    await callback.answer()
    await show_exam_question(callback.message, 0)


async def show_exam_question(message, q_index: int, edit: bool = False):
    state = get_user_temp_state_sync(message.chat.id)
    questions = state.get("questions", [])

    if q_index >= len(questions):
        score = state.get("score", 0)
        total = len(questions)
        percentage = int(score / total * 100) if total else 0
        passed = percentage >= 70
        exam_id = state.get("exam_id")

        save_exam_result_sync(message.chat.id, exam_id, percentage, passed)
        clear_temp_state_sync(message.chat.id)

        if passed:
            levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
            user = get_user_sync(message.chat.id)
            current_idx = levels.index(user.get("level", "")) if user.get("level") in levels else -1
            text = f"🎉 تبریک! نمره شما: {percentage}%\n"
            if current_idx < len(levels) - 1:
                next_level = levels[current_idx + 1]
                update_user_level_sync(message.chat.id, next_level, status="active")
                text += f"✅ شما به سطح {next_level} ارتقا یافتید."
            else:
                text += "🎓 شما دوره کامل را با موفقیت به پایان رساندید!"
        else:
            text = f"❌ نمره شما {percentage}% است. حداقل نمره ۷۰ است. می‌توانید دوباره تلاش کنید."

        await message.answer(text, reply_markup=main_menu_keyboard())
        return

    q = questions[q_index]
    options = q["options"]
    text = f"📋 سوال {q_index+1} از {len(questions)}\n\n{q['q']}"
    kb = exam_options_keyboard(options, q_index)
    if edit:
        await message.edit_text(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("exam_answer:"))
async def handle_exam_answer(callback: CallbackQuery):
    state = get_user_temp_state_sync(callback.from_user.id)
    if state.get("status") != "exam":
        await callback.answer()
        return

    parts = callback.data.split(":")
    q_index = int(parts[1])
    answer_idx = int(parts[2])

    questions = state.get("questions", [])
    correct = questions[q_index]["correct"]

    is_correct = (answer_idx == correct)
    new_score = state.get("score", 0) + (1 if is_correct else 0)

    set_user_temp_state_sync(callback.from_user.id, {
        **state,
        "q_index": q_index + 1,
        "score": new_score
    })
    await callback.answer("✅" if is_correct else "❌")
    await show_exam_question(callback.message, q_index + 1, edit=True)
