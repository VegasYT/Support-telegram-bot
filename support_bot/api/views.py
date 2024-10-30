from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import MessageSerializer
from .services import get_response, detect_question_and_subquestion, load_data, train_models
from .models import User, QueryHistory

from django.core.cache import cache



class MessageView(APIView):
    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.validated_data['message']
            user_id = serializer.validated_data['user_id']
            username = serializer.validated_data.get('username')  # Получаем юзернейм, если есть

            # Найти или создать пользователя, с сохранением username
            user, created = User.objects.get_or_create(
                telegram_id=user_id,
                defaults={'username': username}  # Сохраняем username при создании
            )

            if not created:  # Если пользователь уже существует, обновляем username, если он изменился
                if username and user.username != username:
                    user.username = username
                    user.save()

            # Загрузка модели и данных
            models = cache.get('models')  # Можно использовать кеш для хранения моделей
            if models is None:
                question_data, subquestion_data = load_data()  # Загружаем данные
                models = train_models(question_data, subquestion_data)  # Обучаем модели
                cache.set('models', models)  # Сохраняем в кеш

            # Обработка сообщения
            question_name, subquestion_name = detect_question_and_subquestion(message, models)
            answer = get_response(question_name, subquestion_name)  # Получаем ответ

            # Сохраняем историю запроса
            QueryHistory.objects.create(user=user, question=message, answer=answer)

            return Response({'response': answer}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
