import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers import start_router, track_router, history_router

print("=== BOT.PY ЗАПУЩЕН ===")
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise Exception("TOKEN не найден в переменных окружения!")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

async def main():
    dp.include_router(start_router)
    dp.include_router(track_router)
    dp.include_router(history_router)
    logger.info("Бот запущен...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Сессия бота завершена.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Отключение бота...")