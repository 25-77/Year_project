# Модели базы данных SQLAlchemy

# Этот файл определяет структуру таблиц в базе данных.

from typing import Optional

from sqlalchemy import JSON, Float, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy
    """
    pass


class PredictionHistory(Base):
    """
    Модель SQLAlchemy для таблицы истории предсказаний
    Имя таблицы: prediction_history
    Эта модель хранит все запросы предсказаний и их результаты
    """
    __tablename__ = "prediction_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Уникальный идентификатор"
    )

    request_data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="Входящие данные запроса"
    )

    prediction: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Предсказание модели"
    )

    probability: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Вероятность положительного класса"
    )

    processing_time: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Время обработки запроса в секундах"
    )
