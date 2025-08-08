import json
import os
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from datetime import datetime

from questions import questions
from keyboards.inline import generate_keyboard
from keyboards.reply import finish_buttons_no_note, finish_buttons_note, menu_buttons

RESULTS_FILE = "mood_data_json.json"
router = Router()

# --- Состояния ---

class Reg(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    confimation = State()
    note = State()

# --- Вспомогательные функции ---

async def append_to_json_file(data: dict, user_id: int):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = {}
    else:
        all_data = {}

    user_key = str(user_id)
    if user_key not in all_data:
        all_data[user_key] = {}
    if date_str not in all_data[user_key]:
        all_data[user_key][date_str] = {}

    all_data[user_key][date_str][time_str] = data

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

async def save_answer_and_update_state(state: FSMContext, q_index: int, opt_index: int):
    data = await state.get_data()
    data[f"q{q_index + 1}"] = questions[q_index]["options"][opt_index]
    await state.update_data(**data)

async def get_selected_option_index(data: dict, q_index: int):
    answer_key = f"q{q_index + 1}"
    if answer_key in data:
        selected_option = data[answer_key]
        return questions[q_index]["options"].index(selected_option)
    return None

async def send_question(message_obj, q_index: int, selected: int = None):
    await message_obj.edit_text(
        text=questions[q_index]["text"],
        reply_markup=generate_keyboard(questions[q_index]["options"], q_index, selected)
    )


# --- Обработчики ---

@router.callback_query(F.data == "start_tracker")
async def start_tracker(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()
    if current_state in [Reg.q1.state, Reg.q2.state, Reg.q3.state, Reg.note.state]:
        return

    await state.set_state(Reg.q1)
    await state.update_data(current_question=0)
    await callback.message.answer(
        text=questions[0]["text"],
        reply_markup=generate_keyboard(questions[0]["options"], 0)
    )

@router.callback_query(F.data.startswith("answer_"))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split("_")
    q_index = int(parts[1])
    opt_index = int(parts[2])

    await save_answer_and_update_state(state, q_index, opt_index)
    data = await state.get_data()

    if q_index + 1 < len(questions):
        next_q_index = q_index + 1
        selected = await get_selected_option_index(data, next_q_index)
        await state.update_data(current_question=next_q_index)
        await send_question(callback.message, next_q_index, selected)
    else:
        await callback.message.edit_text("Спасибо за ответы! Всё сохранено.")

@router.callback_query(F.data.startswith("prev_"))
async def go_prev(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    q_index = int(callback.data.split("_")[1]) - 1

    await state.update_data(current_question=q_index)
    data = await state.get_data()

    selected = await get_selected_option_index(data, q_index)
    await send_question(callback.message, q_index, selected)

@router.callback_query(F.data.startswith("final_"))
async def handle_final_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split("_")
    q_index = int(parts[1])
    opt_index = int(parts[2])

    await save_answer_and_update_state(state, q_index, opt_index)
    if opt_index == 0:
        await state.set_state(Reg.note)
        await callback.message.edit_text('Введите что хотите написать:')
    else:
        await callback.message.answer(
            "Хотите сделать что-то ещё?",
            reply_markup=finish_buttons_no_note
        )
        await state.set_state(Reg.confimation)

@router.message(Reg.note)
async def save_note(message: Message, state: FSMContext):
    await state.update_data(note=message.text)
    data = await state.get_data()
    print("Все ответы + заметка:", data)
    await message.answer(
        "Спасибо! Твоя заметка сохранена, завершаем?",
        reply_markup=finish_buttons_note)
    await state.set_state(Reg.confimation)

@router.message(Reg.confimation)
async def handle_confirmation(message: Message, state: FSMContext):
    if message.text == "✅ Подтвердить завершение":
        data = await state.get_data()
        print("Финальные данные:", data)
        await append_to_json_file(data, message.from_user.id)
        await message.answer("Спасибо за участие!", reply_markup=menu_buttons)
        await state.clear()

    elif message.text == "✏️ Отредактировать заметку":
        await message.answer("Введите новую заметку:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Reg.note)

    else:
        await message.answer("Пожалуйста, выбери один из вариантов.")