from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from questions import questions
# --- Вспомогательные функции ---

def make_button(text: str, cb: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=cb)

def ikb_row(*buttons: InlineKeyboardButton) -> list:
    return list(buttons)

# --- Клавиатура запуска ---

start_button_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [make_button("Начать опрос", "start_tracker")]
    ]
)

# --- Генератор основной клавиатуры опроса ---

def generate_keyboard(options, q_index, selected_index=None):
    keyboard = []
    for i in range(0, len(options), 2):  # по 2 кнопки в ряд
        row = []
        for j in range(i, min(i + 2, len(options))):
            text = options[j]
            if selected_index == j:
                text = f"✅ {text}"
            prefix = "final" if q_index == len(questions) - 1 else "answer"
            cb = f"{prefix}_{q_index}_{j}"
            row.append(make_button(text, cb))
        keyboard.append(row)
    if q_index > 0:
        keyboard.append([make_button("⬅️ Назад", f"prev_{q_index}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- Клавиатура истории: даты ---

def history_keyboard(dates: dict):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [make_button(date, f"date:{date}")]
            for date in dates
        ]
    )

# --- Клавиатура истории: время по дате ---

def time_keyboard (date: str, times: dict):
    kb = [
        [make_button(time, f"view_entry:{date}:{time}")]
        for time in times
    ]
    kb.append([make_button("⬅️ Назад", f"back_to_dates:")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# --- Кнопки при просмотре записи ---

def note_button(date: str, time: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [make_button("📝 Посмотреть заметку", f"view_note:{date}:{time}")],
            ikb_row(
                make_button("⬅️ Назад", f"back_to_times:{date}"),
                make_button("🗑 Удалить", f"delete:{date}:{time}")
            )
        ]
    )

def back_to_entry_button( date: str, time: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            ikb_row(
                make_button("⬅️ Назад",f"view_entry:{date}:{time}" ),
                make_button("🗑 Удалить",f"delete:note:{date}:{time}" )
            )
        ]
    )

def back_to_times_button( date: str, time: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            ikb_row(
                make_button("⬅️ Назад",f"back_to_times:{date}"),
                make_button("🗑 Удалить", f"delete_data:{date}:{time}" )
            )
        ]
    )