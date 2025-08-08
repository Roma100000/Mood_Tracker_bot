
from aiogram import Router
from aiogram.types import Message
from keyboards.inline import start_button_keyboard
from keyboards.reply import menu_buttons

router=Router()
@router.message(lambda message: message.text and message.text.lower() in ["/start", "🔁 пройти опрос заново","📝 пройти опрос"])
async def start_bot(message:Message):
    name=message.from_user.first_name
    await message.answer(f'Привет,{name}! Я помогу тебе отслеживать твоё настроение 🧠💬', reply_markup=start_button_keyboard)
