# Middleware для логирования запросов предсказаний
# Этот middleware перехватывает все POST запросы к /api/forward
# и логирует их в базу данных

import time
import json
from typing import Dict, Any
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .database import AsyncSessionLocal
from .models import PredictionHistory


class PredictionHistoryMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования истории предсказаний
    Логирует каждый POST запрос к эндпоинту /api/forward
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
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

        # Получить IP клиента
        client_ip = request.client.host if request.client else "unknown"

        # Прочитать тело запроса
        body_bytes = await request.body()

        # Сохранить оригинальное тело для повторного использования
        request._body = body_bytes

        # Разобрать данные запроса
        request_data: Dict[str, Any] = {}
        if body_bytes:
            try:
                request_data = json.loads(body_bytes.decode("utf-8"))
            except json.JSONDecodeError:
                request_data = {"error": "Invalid JSON"}

        # Обработать запрос
        response = await call_next(request)

        # Рассчитать время обработки
        processing_time = time.time() - start_time

        # Разобрать данные ответа
        prediction = None
        probability = None
        error_message = None

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

        # Разобрать ответ если успешно
        if response.status_code == 200:
            try:
                result = json.loads(response_body.decode("utf-8"))
                prediction = result.get("prediction")
                probability = result.get("probability")
            except (json.JSONDecodeError, KeyError):
                error_message = "Failed to parse successful response"
        else:
            # Разобрать сообщение об ошибке
            try:
                error_result = json.loads(response_body.decode("utf-8"))
                error_message = error_result.get("detail", str(error_result))
            except json.JSONDecodeError:
                error_message = f"HTTP {response.status_code}"

        # Сохранить в базу данных
        async with AsyncSessionLocal() as session:
            try:
                history_item = PredictionHistory(
                    timestamp=datetime.utcnow(),
                    request_data=request_data,
                    prediction=prediction,
                    probability=probability,
                    status_code=response.status_code,
                    error_message=error_message,
                    client_ip=client_ip,
                    model_version="1.0.0",
                    processing_time=processing_time
                )

                session.add(history_item)
                await session.commit()

            except Exception as e:
                # Залогировать ошибку, но не проваливать запрос
                print(f"Error saving prediction history: {e}")
                await session.rollback()

        return response
