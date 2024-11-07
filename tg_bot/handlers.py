import requests
from aiogram import Dispatcher
from aiogram.types import Message
from functools import partial
from tg_bot.config import DJANGO_SERVER_URL, ALLOWED_CHAT_IDS


async def handle_message(message: Message, bot_username: str):
    chat_id = message.chat.id

    # Проверяем, разрешён ли чат
    if chat_id not in ALLOWED_CHAT_IDS:
        return  # Игнорируем сообщение, если чат не в списке разрешённых

    user_message = message.text  # Извлекаем текст сообщения

    # Проверка на команду (если сообщение начинается с '/')
    if user_message.startswith('/query') or user_message.startswith('/q'):
        # Это команда, отправляем на сервер
        pass
    # Проверка на упоминание бота (если сообщение содержит @<bot_username>)
    elif f"@{bot_username}" in user_message:
        # Извлекаем текст после упоминания бота
        user_message = user_message.split(f"@{bot_username}", 1)[1].strip()
    else:
        # Если это не команда и не упоминание, запрос на сервер не отправляется
        return

    user_id = message.from_user.id
    username = message.from_user.username  # Получаем username

    # Отправка запроса на сервер Django
    response = requests.post(DJANGO_SERVER_URL, json={"message": user_message, "user_id": user_id, "username": username})
    
    bot_response = response.json().get('response', 'Ответ не найден')
    await message.answer(bot_response)

def register_handlers(dp: Dispatcher, bot_username: str):
    print("reg")
    # Регистрируем обработчик, который будет вызываться при каждом сообщении
    dp.message.register(partial(handle_message, bot_username=bot_username))
