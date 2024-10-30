from rest_framework import serializers



class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()
    user_id = serializers.IntegerField()


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=300)  # Максимальная длина сообщения
    user_id = serializers.IntegerField()  # Telegram ID пользователя
    username = serializers.CharField(max_length=30, allow_blank=True, required=False)  # Имя пользователя