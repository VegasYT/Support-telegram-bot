import os
import whisper
import numpy as np
import pymorphy2
from pydub import AudioSegment
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from .models import Question, Subquestion, Phrase  # Импортируйте ваши модели Django


# Путь к папке с моделями
MODEL_DIR = "models"
# Создание папки, если она не существует
os.makedirs(MODEL_DIR, exist_ok=True)  

# Указание пути к ffmpeg для работы с библиотекой pydub
ffmpeg_path = r'C:\vs_code\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe'
# Добавление пути к ffmpeg в переменную окружения
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

# Инициализация морфологического анализатора для обработки русского языка
morph = pymorphy2.MorphAnalyzer()


# Функция для конвертации аудиофайлов формата .ogg в .wav
def convert_to_wav(audio_path):
    if audio_path.endswith(".ogg"):
        audio = AudioSegment.from_ogg(audio_path)  # Загружаем .ogg файл
        wav_path = audio_path.replace(".ogg", ".wav")  # Задаем путь для .wav
        audio.export(wav_path, format="wav")  # Экспортируем в формате .wav
        return wav_path
    return audio_path  # Возвращаем оригинальный путь, если не .ogg

# Функция для лемматизации текста
def lemmatize_text(text):
    words = text.split()  # Разделение текста на слова
    # Возвращаем лемматизированные слова, объединенные в строку
    return ' '.join(morph.parse(word)[0].normal_form for word in words)

# Проверка функции get_response
def get_response(question_name, subquestion_name=None):
    # Проверка получения ответа поднамерения
    if subquestion_name:
        response = Subquestion.objects.filter(name=subquestion_name, question__name=question_name).values_list('answer', flat=True).first()
    else:
        # Получение ответа намерения
        response = Question.objects.filter(name=question_name).values_list('answer', flat=True).first()
    
    return response if response else "Ответ не найден."

# Функция для загрузки данных намерений и поднамерений из базы данных
def load_data():
    question_data = {}  # Словарь для хранения намерений
    subquestion_data = {}  # Словарь для хранения поднамерений

    questions = Question.objects.all()  # Запрос на получение всех намерений

    for question in questions:
        # Получение фраз, связанных с намерением
        question_phrases = Phrase.objects.filter(question=question).values_list('text', flat=True)
        question_data[question.name] = list(question_phrases)  # Сохраняем фразы в словарь

        # Получение поднамерений для текущего намерения
        subquestions = Subquestion.objects.filter(question=question)
        for subquestion in subquestions:
            subquestion_phrases = Phrase.objects.filter(subquestion=subquestion).values_list('text', flat=True)
            # Сохраняем поднамерения и их фразы в словаре
            if question.name not in subquestion_data:
                subquestion_data[question.name] = {}
            subquestion_data[question.name][subquestion.name] = list(subquestion_phrases)

    return question_data, subquestion_data  # Возвращаем данные намерений и поднамерений

# Лемматизация данных и создание маппинга {лемматизированное: исходное}
def create_lemmatized_mapping(data):
    lemmatized_data = {}  # Словарь для хранения лемматизированных данных
    lemmatized_to_original = {}  # Словарь для маппинга лемматизированных форм к оригинальным
    for key, phrases in data.items():
        lemmatized_key = lemmatize_text(key)  # Лемматизация ключа
        lemmatized_phrases = [lemmatize_text(phrase) for phrase in phrases]  # Лемматизация фраз
        lemmatized_data[lemmatized_key] = lemmatized_phrases  # Сохраняем в словарь
        lemmatized_to_original[lemmatized_key] = key  # Сохраняем маппинг
    return lemmatized_data, lemmatized_to_original  # Возвращаем лемматизированные данные и маппинг

# Функция для обучения моделей для намерений и поднамерений
def train_models(question_data, subquestion_data):
    models = {}  # Словарь для хранения обученных моделей

    # Обучение основной модели намерений
    question_lemmatized, question_map = create_lemmatized_mapping(question_data)  # Лемматизация намерений
    question_model = Pipeline([('tfidf', TfidfVectorizer()), ('classifier', LogisticRegression())])  # Создаем пайплайн
    question_model.fit(
        [q for phrases in question_lemmatized.values() for q in phrases],  # Входные данные для обучения
        [key for key, phrases in question_lemmatized.items() for _ in phrases]  # Метки для обучения
    )
    models['question'] = {'model': question_model, 'map': question_map}  # Сохраняем модель намерений

    # Обучение моделей для поднамерений
    for question_name, subquestions in subquestion_data.items():
        subquestion_lemmatized, subquestion_map = create_lemmatized_mapping(subquestions)  # Лемматизация поднамерений
        if len(subquestion_map) > 1:  # Обучаем модель только если есть несколько классов
            subquestion_model = Pipeline([('tfidf', TfidfVectorizer()), ('classifier', LogisticRegression())])  # Создаем пайплайн для поднамерений
            subquestion_model.fit(
                [q for phrases in subquestion_lemmatized.values() for q in phrases],  # Входные данные
                [key for key, phrases in subquestion_lemmatized.items() for _ in phrases]  # Метки
            )
            models[question_name] = {'model': subquestion_model, 'map': subquestion_map}  # Сохраняем модель поднамерений

    return models  # Возвращаем все обученные модели
 
# Функция для загрузки модели Whisper
def load_model(model_name):
    model_path = os.path.join(MODEL_DIR, model_name)  # Определяем путь к модели
    # Если модель не существует, загружаем и сохраняем её
    if not os.path.exists(os.path.join(MODEL_DIR, model_name + ".pt")):
        model = whisper.load_model(model_name)  # Загрузка модели
        model.save_pretrained(MODEL_DIR)  # Сохранение модели
    return whisper.load_model(model_name)  # Возвращаем загруженную модель

# Функция для транскрипции аудио
def transcribe_audio(audio_path):
    model = load_model("medium")  # Загружаем модель Whisper
    audio_path = convert_to_wav(audio_path)  # Конвертируем аудио в .wav
    result = model.transcribe(audio_path, verbose=True, language="ru")  # Транскрибируем аудио
    return result['text'].strip()  # Возвращаем текст транскрипции

# Функция для обнаружения намерения и поднамерения
def detect_question_and_subquestion(user_message, models):
    lemmatized_message = lemmatize_text(user_message)  # Лемматизируем пользовательское сообщение
    
    # Получаем модель и маппинг намерений
    question_model = models['question']['model']
    question_map = models['question']['map']
    
    # Предсказание намерения с вероятностями
    question_probas = question_model.predict_proba([lemmatized_message])[0]
    question_prediction_index = question_probas.argmax()
    question_prediction = question_model.classes_[question_prediction_index]
    question_name = question_map.get(question_prediction, question_prediction)
    question_confidence = question_probas[question_prediction_index]

    print(question_name)
    print(question_confidence)
    
    # Получаем минимальный коэффициент уверенности для намерения
    min_confidence = Question.objects.get(name=question_name).min_confidence
    
    if question_confidence < min_confidence:  # Если уверенность ниже минимального порога
        return question_name, None  # Возвращаем только намерение, поднамерение не определяем

    # Получаем модель поднамерений для предсказанного намерения
    if question_name in models:
        subquestion_model = models[question_name]['model']
        subquestion_map = models[question_name]['map']
        
        # Предсказание поднамерения
        subquestion_probas = subquestion_model.predict_proba([lemmatized_message])[0]
        subquestion_prediction_index = subquestion_probas.argmax()
        subquestion_prediction = subquestion_model.classes_[subquestion_prediction_index]
        subquestion_name = subquestion_map.get(subquestion_prediction, subquestion_prediction)
        subquestion_confidence = subquestion_probas[subquestion_prediction_index]

        print(subquestion_prediction)
        print(subquestion_confidence)
        
        min_subquestion_confidence = Subquestion.objects.get(name=subquestion_name, question__name=question_name).min_confidence
        
        if subquestion_confidence >= min_subquestion_confidence:  # Если уверенность поднамерения достаточна
            return question_name, subquestion_name  # Возвращаем намерение и поднамерение
        
    return question_name, None  # Возвращаем только намерение, если поднамерение не определено

