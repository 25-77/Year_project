# Роутер для эндпоинта предсказаний модели
# Этот роутер обрабатывает POST запросы для получения предсказаний

# Ключевые эндпоинты:
# - POST /forward - Получить предсказание для одного объекта

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import load_features_config, load_model
from api.schemas import ForwardRequest, ForwardResponse

router = APIRouter(tags=["Predictions"])


def validate_request_data(data, required_features):
    """
    Валидация JSON данных и преобразование их в DataFrame
    """

    # Проверяем наличие всех необходимых признаков
    missing_features = [
        feature for feature in required_features if feature not in data
    ]
    if missing_features:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Отсутствуют переменные: {missing_features}"
        )

    df = pd.DataFrame([data])[required_features]

    return df


@router.post(
    "/forward",
    response_model=ForwardResponse,
    summary="Формирование прогноза вероятности фрода",
    description="""
    Принимает JSON с данными транзакции и формирует прогноз модели

    Формат запроса:
    {
        "data": {
            "TransactionAmt": 189.0,
            "C1": 1.0,
            "C2": 2.0,
            // ... все остальные переменные
        }
    }

    Все переменные из FINAL_FEATURES обязательны
    """,
    responses={
        403: {"description": "Модель не смогла обработать данные"},
    }
)
async def forward_prediction(
    request: ForwardRequest,
    model=Depends(load_model),
    features_config=Depends(load_features_config)
):
    # Получаем список переменных
    required_features = features_config.get("FINAL_FEATURES", [])

    # Валидация и подготовка данных
    df = validate_request_data(request.data, required_features)

    # Получение предсказания
    try:
        prediction = model.predict(df)
        probabilities = model.predict_proba(df)

        prediction_value = int(prediction[0])
        probability = float(probabilities[0, 1])

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Модель не смогла обработать данные: {str(e)}"
        )

    return ForwardResponse(
        prediction=prediction_value,
        probability=probability
    )
