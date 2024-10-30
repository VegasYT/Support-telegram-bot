import asyncio
from aiogram import Bot, Dispatcher
from .config import API_TOKEN
from .handlers import register_handlers

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    
    register_handlers(dp)  # Регистрируем обработчики
    
    await dp.start_polling(bot)  # Запускаем поллинг <3

if __name__ == '__main__':
    asyncio.run(main())
