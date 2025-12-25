# Модели для таблиц базы данных с использованием SQLAlchemy

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, JSON, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy
    Все модели должны наследоваться от этого класса.
    """
    pass


class PredictionHistory(Base):
    """
    Модель SQLAlchemy для таблицы истории предсказаний
    Имя таблицы: prediction_history
    Эта модель хранит все запросы предсказаний и их результаты.
    Стиль SQLAlchemy 2.0: Использует Mapped[] и mapped_column()
    """
    __tablename__ = "prediction_history"

    # Первичный ключ
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Уникальный идентификатор"
    )

    # Временная метка запроса
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="Временная метка запроса (UTC)"
    )

    # Данные запроса (JSON формат)
    request_data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="Исходные данные запроса"
    )

    # Результат предсказания модели
    prediction: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Предсказание модели"
    )

    # Вероятность предсказания
    probability: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Вероятность предсказания"
    )

    # HTTP статус код
    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=200,
        index=True,
        comment="HTTP статус код ответа"
    )

    # Сообщение об ошибке (если есть)
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Сообщение об ошибке (если запрос не удался)"
    )

    # IP адрес клиента
    client_ip: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="IP адрес клиента"
    )

    # Версия модели
    model_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="1.0.0",
        comment="Model version / Версия модели"
    )

    # Время обработки запроса (в секундах)
    processing_time: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Время обработки запроса в секундах"
    )

    def __repr__(self) -> str:
        """Строковое представление модели"""
        return f"<PredictionHistory(id={self.id}, timestamp={self.timestamp}, status={self.status_code})>"
