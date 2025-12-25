# Pydantic схемы

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class ForwardRequest(BaseModel):
    """Запрос для предсказания"""
    data: Dict[str, Any] = Field(
        ...,
        description="Объект с переменными для предсказания"
    )


class ForwardResponse(BaseModel):
    """Ответ с предсказаниями"""
    success: bool = True
    prediction: int = Field(
        ...,
        description="Предсказанный класс (0 или 1)",
        ge=0,
        le=1
    )
    probability: float = Field(
        ...,
        description="Вероятность положительного класса",
        ge=0.0,
        le=1.0
    )


class HistoryItemBase(BaseModel):
    """
    Базовая схема для элемента истории (общие поля)
    """
    timestamp: datetime = Field(
        ...,
        description="Временная метка запроса"
    )
    request_data: Dict[str, Any] = Field(
        ...,
        description="Исходные данные запроса"
    )
    status_code: int = Field(
        ...,
        description="HTTP статус код"
    )


class HistoryItemCreate(HistoryItemBase):
    """
    Схема для создания записи истории (из middleware)
    Используется при сохранении результатов предсказания в БД
    """
    prediction: Optional[int] = Field(
        None,
        ge=0,
        le=1,
        description="Предсказание модели (0 или 1)"
    )
    probability: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Вероятность предсказания"
    )
    error_message: Optional[str] = Field(
        None,
        description="Сообщение об ошибке (если есть)"
    )
    client_ip: Optional[str] = Field(
        None,
        description="IP адрес клиента"
    )
    model_version: Optional[str] = Field(
        "1.0.0",
        description="Версия модели"
    )
    processing_time: Optional[float] = Field(
        None,
        ge=0.0,
        description="Время обработки в секундах"
    )


class HistoryItemResponse(HistoryItemBase):
    """
    Схема для ответа элемента истории (вывод API)
    Используется в: ответ GET /api/history
    """
    id: int = Field(
        ...,
        description="ID записи"
    )
    prediction: Optional[int] = Field(
        None,
        description="Предсказание модели"
    )
    probability: Optional[float] = Field(
        None,
        description="Вероятность предсказания"
    )
    error_message: Optional[str] = Field(
        None,
        description="Сообщение об ошибке"
    )
    client_ip: Optional[str] = Field(
        None,
        description="IP клиента"
    )
    model_version: Optional[str] = Field(
        "1.0.0",
        description="Версия модели"
    )
    processing_time: Optional[float] = Field(
        None,
        description="Время обработки"
    )

    # Настроить Pydantic для работы с SQLAlchemy моделями
    model_config = ConfigDict(from_attributes=True)


class HistoryResponse(BaseModel):
    """
    Схема для ответа списка истории
    Используется в: ответ GET /api/history
    """
    items: List[HistoryItemResponse] = Field(
        ...,
        description="List of history records / Список записей истории"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of records / Общее количество записей"
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number / Номер текущей страницы"
    )
    limit: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of items per page / Количество элементов на странице"
    )
    total_pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages / Общее количество страниц"
    )


class HistoryStatsResponse(BaseModel):
    """
    Схема для ответа статистики истории
    Используется в: ответ GET /api/history/stats
    """
    total_requests: int = Field(
        ...,
        description="Общее количество запросов"
    )
    successful_requests: int = Field(
        ...,
        description="Количество успешных запросов (статус 200)"
    )
    failed_requests: int = Field(
        ...,
        description="Количество неудачных запросов (статус >= 400)"
    )
    success_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Уровень успеха (от 0.0 до 1.0)"
    )
    average_processing_time: Optional[float] = Field(
        None,
        description="Среднее время обработки в секундах"
    )
    last_24_hours: int = Field(
        ...,
        description="Запросы за последние 24 часа"
    )
