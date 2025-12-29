# Точка входа FastAPI приложения и управление жизненным циклом.

# Этот файл определяет:
# - Конфигурацию и создание FastAPI приложения
# - Управление событиями запуска/остановки (lifespan)
# - Регистрацию всех маршрутов (роутеров)
# - Middleware для логирования

from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from api.database import engine, init_db
from api.middleware import PredictionHistoryMiddleware
from api.routers import forward, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекст жизненного цикла для событий запуска/остановки приложения
    Управляет инициализацией и закрытием ресурсов
    """

    print("Запуск ML Prediction Service")

    # Инициализируем базу данных (создаем таблицы если не существуют)
    await init_db()
    print("База данных инициализирована")

    yield  # Приложение работает здесь

    # События при остановке приложения
    await engine.dispose()
    print("Соединение с базой данных закрыто")
    print("Приложение остановлено")


# Создаем FastAPI приложение с контекстом жизненного цикла
app = FastAPI(
    title="ML Prediction Service",
    description="Сервис для прогнозирования вероятности транзакционного фрода",
    version="1.0.0",
    lifespan=lifespan  # Добавляем управление жизненным циклом
)


# Добавляем middleware для логирования запросов
app.add_middleware(PredictionHistoryMiddleware)


@app.get("/", tags=["Root"])
async def root():
    """
    Корневой эндпоинт - базовый GET запрос
    """
    return {
        "message": "ML Prediction Service",
        "version": "1.0.0",
        "endpoints": {
            "prediction": {
                "method": "POST",
                "path": "/api/forward",
                "description": "Получить предсказание модели"
            },
            "history_all": {
                "method": "GET",
                "path": "/api/history",
                "description": "Получить историю всех запросов"
            },
            "history_stats": {
                "method": "GET",
                "path": "/api/history/stats",
                "description": "Получить статистику по истории запросов"
            },
            "health": {
                "method": "GET",
                "path": "/health",
                "description": "Проверка работоспособности сервиса"
            }
        },
        "database": {
            "type": "SQLite (асинхронная)",
            "file": "prediction_history.db"
        }
    }


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """
    Эндпоинт проверки здоровья приложения
    """
    return {
        "status": "healthy",
        "service": "ml-prediction-service"
    }


# Регистрируем роутер для формирования прогноза
app.include_router(forward.router, prefix="/api")

# Регистрируем роутер для получения истории запросов
app.include_router(history.router, prefix="/api")
