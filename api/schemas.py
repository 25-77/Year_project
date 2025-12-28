# Pydantic схемы для валидации API запросов и ответов

# Этот файл определяет структуру данных для:
# - Входящих запросов к API
# - Исходящих ответов от API

# Основные принципы:
# - Каждый эндпоинт имеет свою схему запроса и ответа
# - Все схемы наследуются от BaseModel
# - Field() используется для добавления метаданных и валидации
# - ConfigDict настраивает поведение Pydantic

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ForwardRequest(BaseModel):
    """
    Схема для запроса данных для прогноза

    Используется: POST /api/forward
    Проверяет что в запросе есть поле 'data' типа словарь
    """
    data: Dict[str, Any] = Field(
        ...,
        description="JSON объект с переменными для предсказания модели",
        examples=[
            {
                "TransactionAmt": 189.0,
                "C1": 1.0,
                "C2": 2.0,
                "C4": 1.0,
                "C6": 0.5,
                "C11": 0.0,
                "C13": 1.0,
                "C14": 1.0,
                "D2": 10.0,
                "D3": 5.0,
                "D8": 2.0,
                "V34": 0.1,
                "V57": 0.2,
                "V91": 0.3,
                "V200": 0.4,
                "V281": 0.5,
                "V283": 0.6,
                "V294": 0.7,
                "addr1": 150,
                "card1": 15000,
                "card2": 226,
                "card3": 150,
                "card4": "visa",
                "card5": 226,
                "card6": "debit",
                "DeviceInfo": "Windows Chrome",
                "P_emaildomain": "gmail.com",
                "R_emaildomain": "gmail.com",
                "M4": "M0",
                "M5": "M0"
            }
        ]
    )


class ForwardResponse(BaseModel):
    """
    Схема для ответа с прогнозом модели

    Используется: ответ POST /api/forward
    Определяет структуру успешного ответа модели
    """
    success: bool = Field(
        default=True,
        description="Успешно ли выполнен запрос"
    )
    prediction: int = Field(
        ...,
        ge=0,
        le=1,
        description="Предсказание модели"
    )
    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Вероятность положительного класса"
    )


class HistoryItemResponse(BaseModel):
    """
    Схема для ответа с элементом истории

    Используется: ответ GET /api/history
    Возвращает поля из базы данных
    """
    id: int = Field(
        ...,
        description="Уникальный идентификатор записи в базе данных"
    )
    request_data: Dict[str, Any] = Field(
        ...,
        description="Исходные данные запроса"
    )
    prediction: Optional[int] = Field(
        None,
        description="Предсказание модели"
    )
    probability: Optional[float] = Field(
        None,
        description="Вероятность положительного класса"
    )
    processing_time: Optional[float] = Field(
        None,
        description="Время обработки запроса в секундах"
    )

    # Конфигурация для работы с SQLAlchemy моделями
    model_config = ConfigDict(from_attributes=True)


class HistoryStatsResponse(BaseModel):
    """
    Схема для статистики истории

    Используется: ответ GET /api/history/stats
    Содержит агрегированные данные по всем запросам
    """
    total_requests: int = Field(
        ...,
        ge=0,
        description="Общее количество обработанных запросов"
    )
    average_prediction: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Среднее значение предсказаний (от 0.0 до 1.0)"
    )
    average_probability: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Средняя вероятность положительного класса (от 0.0 до 1.0)"
    )
    average_processing_time: Optional[float] = Field(
        None,
        ge=0.0,
        description="Среднее время обработки запроса в секундах"
    )
