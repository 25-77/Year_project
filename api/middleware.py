# Middleware для логирования истории предсказаний

# Middleware - это промежуточный слой между запросом и ответом
# Этот middleware перехватывает все POST запросы к /api/forward
# и сохраняет их вместе с результатами в базу данных

# Логика работы Middleware на примере 1 запроса:

# Шаг 1: Клиент отправляет запрос
# POST http://localhost:8000/api/forward

# Шаг 2: Middleware перехватывает (но НЕ обрабатывает)
# PredictionHistoryMiddleware.dispatch() запускается
#   → читает тело запроса
#   → запоминает время start_time
#   → вызывает call_next(request)

# Шаг 3: call_next вызывает основной роутер
# call_next(request) → FastAPI → forward.router → forward_prediction()
#   → load_model()
#   → model.predict()
#   → возвращает ответ

# Шаг 4: Middleware получает ответ от роутера
# middleware получает response с прогнозом
#   → читает prediction и probability из ответа
#   → считает время processing_time
#   → сохраняет в БД
#   → возвращает ответ клиенту

import json
import time

from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware

from .database import AsyncSessionLocal
from .models import PredictionHistory


class PredictionHistoryMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования истории предсказаний
    Логирует каждый POST запрос к эндпоинту /api/forward
    """
    
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        """
        Обработать каждый запрос

        Args:
            request: HTTP запрос от клиента
            call_next: Функция для вызова следующего обработчика

        Returns:
            Response: HTTP ответ клиенту
        """

        # 1. Проверяем, нужно ли логировать этот запрос
        # Логируем только POST запросы к /api/forward
        if request.method != "POST" or not request.url.path.endswith("/api/forward"):
            # Если это не наш запрос - просто пропускаем дальше
            return await call_next(request)

        # 2. Запоминаем время начала обработки
        start_time = time.time()

        # 3. Читаем тело запроса
        body_bytes = await request.body()

        # 4. Сохраняем тело для повторного использования
        request._body = body_bytes

        # 5. Преобразуем данные из JSON в словарь Python
        request_data = {}
        if body_bytes:
            try:
                request_data = json.loads(body_bytes.decode("utf-8"))
            except json.JSONDecodeError:
                # Если клиент прислал невалидный JSON
                request_data = {"error": "Invalid JSON"}

        # 6. Передаем запрос основному обработчику (нашему роутеру)
        # Здесь вызывается функция forward_prediction из forward.py
        response = await call_next(request)

        # 7. Вычисляем сколько времени заняла обработка
        processing_time = time.time() - start_time

        # 8. Читаем ответ от обработчика
        # Ответ приходит частями, собираем их вместе
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        # 9. Создаем новый ответ с тем же содержимым
        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )

        # 10. Извлекаем данные из ответа
        try:
            result = json.loads(response_body.decode("utf-8"))
            prediction = result.get("prediction")
            probability = result.get("probability")
        except (json.JSONDecodeError, KeyError):
            prediction = None
            probability = None

        # 11. Сохраняем все в базу данных
        # async with автоматически управляет соединением
        async with AsyncSessionLocal() as session:
            try:
                # Создаем новую запись истории
                history_item = PredictionHistory(
                    request_data=request_data,
                    prediction=prediction,
                    probability=probability,
                    processing_time=processing_time
                )

                # Добавляем запись в сессию
                session.add(history_item)

                # Сохраняем в базу данных
                await session.commit()

            except Exception as e:
                print(f"Ошибка сохранения истории: {e}")
                # Отменяем изменения
                await session.rollback()

        # 12. Возвращаем ответ клиенту
        return response
