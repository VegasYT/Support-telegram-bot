import asyncio
from aiogram import Bot, Dispatcher
from tg_bot.config import API_TOKEN
from tg_bot.handlers import register_handlers

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    # Получаем информацию о боте и его имя пользователя
    bot_info = await bot.get_me()
    bot_username = bot_info.username

    register_handlers(dp, bot_username)  # Передаем имя пользователя бота в обработчики

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
