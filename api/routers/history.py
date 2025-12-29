# Роутер для эндпоинтов истории предсказаний
# Этот роутер обрабатывает GET запросы для истории предсказаний

# Ключевые эндпоинты:
# - GET /history -  Получить историю предсказаний
# - GET /history/stats - Получить статистику

from typing import List
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from ..database import get_db
from ..models import PredictionHistory
from ..schemas import HistoryItemResponse, HistoryStatsResponse

router = APIRouter(
    prefix="/history",
    tags=["History"],
    responses={
        500: {"description": "Внутренняя ошибка сервера"}
    }
)


@router.get(
    "",
    response_model=List[HistoryItemResponse],
    summary="История запросов",
    description="""
    Возвращает список всех запросов
    """
)
async def get_history(
    db: AsyncSession = Depends(get_db)
) -> List[HistoryItemResponse]:
    try:
        # Простой запрос - все записи отсортированные по id
        query = select(PredictionHistory).order_by(desc(PredictionHistory.id))

        # Выполнить запрос
        result = await db.execute(query)
        history_items = result.scalars().all()

        return list(history_items)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении истории: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=HistoryStatsResponse,
    summary="Статистика запросов",
    description="""
    Возвращает основные статистики по запросам

    Статистики:
        - Кол-во запросов
        - Средний прогноз
        - Среднее время обработки запросов
    """)
async def get_history_stats(db: AsyncSession = Depends(get_db)):
    try:
        # Общее количество
        total_result = await db.execute(
            select(func.count(PredictionHistory.id))
        )
        total = total_result.scalar_one()

        # Среднее предсказание
        avg_pred_result = await db.execute(
            select(func.avg(PredictionHistory.prediction))
            .where(PredictionHistory.prediction.isnot(None))
        )
        avg_prediction = avg_pred_result.scalar_one()

        # Средняя вероятность
        avg_prob_result = await db.execute(
            select(func.avg(PredictionHistory.probability))
            .where(PredictionHistory.probability.isnot(None))
        )
        avg_probability = avg_prob_result.scalar_one()

        # Среднее время обработки
        avg_time_result = await db.execute(
            select(func.avg(PredictionHistory.processing_time))
            .where(PredictionHistory.processing_time.isnot(None))
        )
        avg_processing_time = avg_time_result.scalar_one()

        return HistoryStatsResponse(
            total_requests=total,
            average_prediction=float(avg_prediction),
            average_probability=float(avg_probability),
            average_processing_time=float(avg_processing_time)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
