from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 ادامه دوره", callback_data="continue_course")
    builder.button(text="📝 ارسال تکلیف", callback_data="submit_homework_menu")
    builder.button(text="📊 وضعیت من", callback_data="my_status")
    builder.button(text="🧑‍🏫 پشتیبانی", callback_data="support")
    builder.adjust(1)
    return builder.as_markup()


def placement_start_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 شروع تعیین سطح", callback_data="start_placement")
    builder.adjust(1)
    return builder.as_markup()


def answer_options_keyboard(options: list, question_id: str):
    builder = InlineKeyboardBuilder()
    for idx, opt in enumerate(options):
        builder.button(text=opt, callback_data=f"placement_answer:{question_id}:{idx}")
    builder.adjust(1)
    return builder.as_markup()


def homework_type_keyboard(lesson_id: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ تکلیف کتبی", callback_data=f"hw_type:{lesson_id}:writing")
    builder.button(text="🎙️ تکلیف صوتی", callback_data=f"hw_type:{lesson_id}:listening")
    builder.adjust(1)
    return builder.as_markup()


def confirm_homework_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ ارسال تکلیف", callback_data="confirm_hw")
    builder.button(text="❌ انصراف", callback_data="cancel_hw")
    return builder.as_markup()


def next_lesson_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ درس بعدی", callback_data="next_lesson")
    builder.adjust(1)
    return builder.as_markup()


def exam_start_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 شروع امتحان", callback_data="start_exam")
    builder.adjust(1)
    return builder.as_markup()


def level_exam_keyboard(level_code: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 امتحان پایان سطح", callback_data=f"level_exam:{level_code}")
    builder.adjust(1)
    return builder.as_markup()


def admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📥 بررسی تکالیف", callback_data="admin_homework")
    builder.adjust(1)
    return builder.as_markup()


def exam_options_keyboard(options: list, q_index: int):
    builder = InlineKeyboardBuilder()
    for idx, opt in enumerate(options):
        builder.button(text=opt, callback_data=f"exam_answer:{q_index}:{idx}")
    builder.adjust(1)
    return builder.as_markup()
