import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.inline import (
    history_keyboard,
    time_keyboard,
    note_button,
    back_to_entry_button,
    back_to_times_button,
)
from keyboards.reply import menu_buttons

router = Router()

# --- Вспомогательные функции ---

def load_data():
    try:
        with open("mood_data_json.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    with open("mood_data_json.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- Обработчики ---

@router.message(lambda message: message.text and message.text.lower() in ["/history", "📖 история"])
async def show_history(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    if user_id not in data or not data[user_id]:
        await message.answer("У тебя ещё нет записей.")
        return

    kb = history_keyboard(data[user_id])
    await message.answer("🕓 Выбери дату:", reply_markup=kb)

@router.callback_query(F.data.startswith("date:"))
async def show_times(callback: CallbackQuery):
    _, date = callback.data.split(":")
    user_id=str(callback.from_user.id)
    data = load_data()
    times = data.get(user_id, {}).get(date)
    if not times:
        await callback.answer("Нет записей на эту дату.", show_alert=True)
        return

    kb = time_keyboard(date, times)
    await callback.message.edit_text(f"📅 <b>{date}</b>\nВыбери время:", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("view_entry:"))
async def handle_view_entry(callback: CallbackQuery):
    parts = callback.data.split(":")
    user_id = str(callback.from_user.id)
    date = parts[1]
    time = ":".join(parts[2:])
    data = load_data()

    entry = data.get(user_id, {}).get(date, {}).get(time)
    if not entry:
        await callback.answer("Запись не найдена.", show_alert=True)
        return

    text = (
        f"<b>Дата:</b> {date}\n"
        f"<b>Время:</b> {time}\n"
        f"<b>1. Настроение:</b> {entry.get('q1', '-')}\n"
        f"<b>2. Оценка дня:</b> {entry.get('q2', '-')}\n"
        f"<b>3. Причина:</b> {entry.get('q3', '-')}\n"
    )

    if "note" in entry:
        reply_markup = note_button(date, time)
    else:
        reply_markup = back_to_times_button( date, time)
    await callback.message.edit_text(text, reply_markup=reply_markup)
    await callback.answer()

@router.callback_query(F.data.startswith("view_note:"))
async def handle_note(callback: CallbackQuery):
    parts = callback.data.split(":")
    user_id = str(callback.from_user.id)
    date = parts[1]
    time = ":".join(parts[2:])
    data = load_data()

    note_text = data.get(user_id, {}).get(date, {}).get(time, {}).get("note",{})
    if not note_text:
        await callback.answer("Заметка не найдена.", show_alert=True)
        return

    kb = back_to_entry_button(date, time)
    await callback.message.edit_text(f"📝 <b>Заметка:</b>\n{note_text}", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("back_to_dates:"))
async def back_to_dates(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    data = load_data()

    kb = history_keyboard(data.get(user_id, {}))
    await callback.message.edit_text("🕓 Выбери дату:", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("back_to_times:"))
async def back_to_times(callback: CallbackQuery):
    parts = callback.data.split(":")
    user_id = str(callback.from_user.id)
    date = parts[1]

    data = load_data()
    times = data.get(user_id, {}).get(date, {})

    kb = time_keyboard(date, times)
    await callback.message.edit_text(f"📅 <b>{date}</b>\nВыбери время:", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("delete:note"))
async def delete_note(callback: CallbackQuery):
    parts = callback.data.split(":")
    user_id = str(callback.from_user.id)
    date = parts[2]
    time = ":".join(parts[3:])
    data = load_data()

    if (
        user_id in data
    and date in data[user_id]
    and time in data[user_id][date]
    and "note" in data[user_id][date][time]):
        del data[user_id][date][time]["note"]
        save_data(data)
        
        await callback.message.delete()
        
        await callback.message.answer(f"✅ Заметка на {date} {time} успешно удалена.",reply_markup=menu_buttons)
    else:
        await callback.answer("❗ Заметка не найдена", show_alert=True)

@router.callback_query(F.data.startswith("delete_data:"))
async def delete_entry(callback: CallbackQuery):
    parts = callback.data.split(":")
    user_id = str(callback.from_user.id)
    date = parts[1]
    time = ":".join(parts[2:])
    data = load_data()

    if user_id in data and date in data[user_id] and time in data[user_id][date]:
        del data[user_id][date][time]
        if not data[user_id][date]:
            del data[user_id][date]
        save_data(data)
        
        await callback.message.delete()
        
        await callback.message.answer(f"✅ Запись на {date} {time} успешно удалена.",reply_markup=menu_buttons)
    else:
        await callback.answer("❗ Запись не найдена", show_alert=True)
