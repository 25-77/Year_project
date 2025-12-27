# Middleware для логирования истории предсказаний

# Этот middleware перехватывает все POST запросы к /api/forward
# и сохраняет их вместе с результатами в базу данных

import time
import json
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

        Шаги:
        1. Проверить, является ли запрос к эндпоинту предсказания
        2. Записать время начала
        3. Обработать запрос
        4. Записать время окончания
        5. Сохранить в базу данных
        """

        # Обрабатывать только POST запросы к /api/forward
        if request.method != "POST" or not request.url.path.endswith("/api/forward"):
            return await call_next(request)

        # Записать время начала
        start_time = time.time()

        # Прочитать тело запроса
        body_bytes = await request.body()

        # Сохранить оригинальное тело для повторного использования
        request._body = body_bytes

        # Разобрать данные запроса
        request_data = {}
        if body_bytes:
            try:
                request_data = json.loads(body_bytes.decode("utf-8"))
            except json.JSONDecodeError:
                request_data = {"error": "Invalid JSON"}

        # Обработать запрос
        response = await call_next(request)

        # Рассчитать время обработки
        processing_time = time.time() - start_time

        # Получить тело ответа
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        # Создать новый ответ с тем же телом
        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )

        result = json.loads(response_body.decode("utf-8"))
        prediction = result.get("prediction")
        probability = result.get("probability")

        # Сохранить в базу данных
        async with AsyncSessionLocal() as session:
            try:
                history_item = PredictionHistory(
                    request_data=request_data,
                    prediction=prediction,
                    probability=probability,
                    processing_time=processing_time
                )

                session.add(history_item)
                await session.commit()

            except Exception as e:
                print(f"Error saving prediction history: {e}")
                await session.rollback()

        return response