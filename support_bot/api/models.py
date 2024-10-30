from django.db import models



class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)  # Уникальный идентификатор пользователя в Telegram
    username = models.CharField(max_length=255, blank=True, null=True)  # Имя пользователя (если доступно)
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания пользователя

    def __str__(self):
        return f"{self.username} ({self.telegram_id})"


class QueryHistory(models.Model):
    user = models.ForeignKey(User, related_name='query_history', on_delete=models.CASCADE)  # Связь с пользователем
    question = models.CharField(max_length=255)  # Вопрос, который задал пользователь
    answer = models.TextField()  # Ответ, который получил пользователь
    created_at = models.DateTimeField(auto_now_add=True)  # Дата и время запроса

    def __str__(self):
        return f"{self.user.username} asked: {self.question} - Answered: {self.answer}"


class Question(models.Model):
    name = models.CharField(max_length=255)
    answer = models.TextField()
    min_confidence = models.FloatField(default=0.2)  # Минимальная уверенность для определения вопроса

    def __str__(self):
        return self.name


class Subquestion(models.Model):
    question = models.ForeignKey(Question, related_name='subquestions', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    answer = models.TextField()
    min_confidence = models.FloatField(default=0.4)  # Минимальная уверенность для определения поднамерения

    def __str__(self):
        return self.name


class Phrase(models.Model):
    question = models.ForeignKey(Question, related_name='phrases', on_delete=models.CASCADE)
    subquestion = models.ForeignKey(Subquestion, related_name='phrases', on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()

    def __str__(self):
        return self.text