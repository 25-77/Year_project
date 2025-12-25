# Роутер для эндпоинтов истории предсказаний
# Этот роутер обрабатывает GET запросы для истории предсказаний

# Ключевые эндпоинты:
# - GET /history -  Получить историю предсказаний
# - GET /history/stats - Получить статистику


from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Query, HTTPException, status

from ..database import get_db, get_history_count
from ..models import PredictionHistory
from ..schemas import (
    HistoryResponse,
    HistoryItemResponse,
    HistoryStatsResponse
)

router = APIRouter(
    prefix="/history",
    tags=["History"],
    responses={
        404: {"description": "Не найдено"},
        500: {"description": "Внутренняя ошибка сервера"}
    }
)


@router.get(
    "",
    response_model=HistoryResponse,
    summary="Get prediction history",
    description="""
    Получить постраничный список всех запросов предсказаний.
    Параметры:
    - page: Номер страницы (начинается с 1)
    - limit: Элементов на страницу (1-100)
    - status_code: Фильтр по статус коду
    - start_date: Фильтр от даты
    - end_date: Фильтр до даты
    """
)
async def get_history(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Элементов на страницу"),
    status_code: Optional[int] = Query(None, description="Фильтр по статус коду"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата (UTC)"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата (UTC)"),
    db: AsyncSession = Depends(get_db)
) -> HistoryResponse:
    """
    Получить постраничную историю предсказаний

    Паттерн SQLAlchemy 2.0:
    - Использовать execute() с select()
    - Использовать .scalars().all() для получения списка объектов
    """

    try:
        # Построить базовый запрос
        query = select(PredictionHistory)

        # Применить фильтры
        if status_code is not None:
            query = query.where(PredictionHistory.status_code == status_code)

        if start_date is not None:
            query = query.where(PredictionHistory.timestamp >= start_date)

        if end_date is not None:
            query = query.where(PredictionHistory.timestamp <= end_date)

        # Получить общее количество
        total = await get_history_count(db)

        # Применить пагинацию и сортировку
        query = query.order_by(desc(PredictionHistory.timestamp))
        query = query.offset((page - 1) * limit).limit(limit)

        # Выполнить запрос
        result = await db.execute(query)
        history_items = result.scalars().all()

        # Рассчитать общее количество страниц
        total_pages = (total + limit - 1) // limit if total > 0 else 0

        return HistoryResponse(
            items=list(history_items),
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching history: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=HistoryStatsResponse,
    summary="Get prediction statistics",
    description="""
    Получить статистику о запросах предсказаний.

    Возвращает:
    - Всего запросов
    - Успешных запросов
    - Неудачных запросов
    - Уровень успеха
    - Среднее время обработки
    - Запросы за последние 24 часа
    """
)
async def get_history_stats(
    db: AsyncSession = Depends(get_db)
) -> HistoryStatsResponse:
    """
    Получить статистику предсказаний

    Паттерн SQLAlchemy 2.0 с агрегатными функциями:
    - Использовать func.count(), func.avg() для агрегации
    """

    try:
        # Получить текущее время
        now = datetime.utcnow()
        last_24_hours = now - timedelta(hours=24)

        #  Получить общее количество
        total_result = await db.execute(
            select(func.count(PredictionHistory.id))
        )
        total = total_result.scalar_one()

        # Получить количество успешных
        successful_result = await db.execute(
            select(func.count(PredictionHistory.id))
            .where(PredictionHistory.status_code == 200)
        )
        successful = successful_result.scalar_one()

        # Получить количество неудачных
        failed = total - successful

        # Получить среднее время обработки
        avg_time_result = await db.execute(
            select(func.avg(PredictionHistory.processing_time))
            .where(PredictionHistory.processing_time.isnot(None))
        )
        avg_processing_time = avg_time_result.scalar_one()

        # Получить количество за последние 24 часа
        last_24h_result = await db.execute(
            select(func.count(PredictionHistory.id))
            .where(PredictionHistory.timestamp >= last_24_hours)
        )
        last_24h = last_24h_result.scalar_one()

        # Рассчитать уровень успеха
        success_rate = successful / total if total > 0 else 0.0

        return HistoryStatsResponse(
            total_requests=total,
            successful_requests=successful,
            failed_requests=failed,
            success_rate=success_rate,
            average_processing_time=float(avg_processing_time) if avg_processing_time else None,
            last_24_hours=last_24h
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching statistics: {str(e)}"
        )
