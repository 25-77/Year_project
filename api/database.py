
# Конфигурация базы данных и управление сессиями

# Этот модуль обрабатывает:
# - Создание асинхронного движка
# - Настройка фабрики сессий
# - Внедрение зависимостей для сессий
# - Инициализация базы данных

from typing import AsyncGenerator
from pathlib import Path
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy import select
from .models import Base, PredictionHistory


# Асинхронная строка подключения SQLite
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/prediction_history.db"

# Создание асинхронного движка
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,  # True для логирования SQL запросов
    future=True,  # Использовать стиль SQLAlchemy 2.0
    pool_pre_ping=True  # Проверять соединение перед использованием
)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Не истекать объекты после commit
    autocommit=False,
    autoflush=False
)


# ЗАВИСИМОСТЬ БАЗЫ ДАННЫХ
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость, предоставляющая сессию базы данных

    Паттерн зависимости FastAPI:
    1. Создать сессию
    2. Передать в эндпоинт
    3. Закрыть после использования

    Использование:
    ```
    @app.get("/history")
    async def get_history(db: AsyncSession = Depends(get_db)):
        # Использовать сессию db здесь
    ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ
async def init_db() -> None:
    """
    Инициализировать таблицы базы данных
    Создает все таблицы определенные в моделях
    """
    async with engine.begin() as conn:
        # Создать все таблицы
        await conn.run_sync(Base.metadata.create_all)


async def get_history_count(db: AsyncSession) -> int:
    """
    Получить общее количество записей истории

    Паттерн SQLAlchemy 2.0:
    - Использовать execute() с select() и count()
    """
    from sqlalchemy import func
    result = await db.execute(
        select(func.count(PredictionHistory.id))
    )
    return result.scalar_one()


async def cleanup_old_records(db: AsyncSession, days_to_keep: int = 30) -> int:
    """
    Очистить старые записи истории

    Удаляет записи старше указанного количества дней

    Возвращает количество удаленных записей
    """
    from datetime import datetime, timedelta
    from sqlalchemy import delete

    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

    result = await db.execute(
        delete(PredictionHistory)
        .where(PredictionHistory.timestamp < cutoff_date)
    )

    await db.commit()
    return result.rowcount
