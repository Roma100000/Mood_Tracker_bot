from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- Вспомогательные функции ---
def rkb(text: str) -> KeyboardButton:
    return KeyboardButton(text=text)

def rkb_row(*buttons: KeyboardButton) -> list[KeyboardButton]:
    return list(buttons)


# --- Главное меню ---
menu_buttons = ReplyKeyboardMarkup(
    keyboard=[
        rkb_row(rkb("📝 Пройти опрос"), rkb("📖 История")),
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Завершение с заметкой
finish_buttons_note =ReplyKeyboardMarkup(
    keyboard=[
        rkb_row(rkb("✏️ Отредактировать заметку"),rkb("🔁 Пройти опрос заново")),
        rkb_row(rkb("✅ Подтвердить завершение"))
],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Завершение без заметки
finish_buttons_no_note = ReplyKeyboardMarkup(
    keyboard=[
        rkb_row(rkb("✅ Подтвердить завершение"),rkb("🔁 Пройти опрос заново"))],
    resize_keyboard=True,
    one_time_keyboard=True
)