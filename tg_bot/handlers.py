import requests
from aiogram import Dispatcher
from aiogram.types import Message
from aiogram import F
from .config import DJANGO_SERVER_URL

async def handle_message(message: Message):
    user_message = message.text
    user_id = message.from_user.id
    username = message.from_user.username  # Получаем username

    # Отправка запроса на сервер Django
    response = requests.post(DJANGO_SERVER_URL, json={"message": user_message, "user_id": user_id, "username": username})
    
    bot_response = response.json().get('response', 'Ответ не найден')
    await message.answer(bot_response)

def register_handlers(dp: Dispatcher):
    dp.message(F.text)(handle_message)  # Регистрируем обработчик сообщений с текстом
