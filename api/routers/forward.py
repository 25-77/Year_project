import pandas as pd
from fastapi import APIRouter, HTTPException, Depends, status
from api.dependencies import load_model, load_features_config
from api.schemas import ForwardRequest, ForwardResponse

router = APIRouter(tags=["Predictions"])

def validate_request_data(data, required_features):
    """
    Валидация JSON данных и преобразование в DataFrame
    """
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty data object"
        )

    # Проверяем, что data это словарь
    if not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data format"
        )

    # Проверяем наличие всех необходимых признаков
    missing_features = [feature for feature in required_features if feature not in data]
    if missing_features:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required features: {missing_features}"
        )

    # Создаем DataFrame с правильным порядком колонок
    df = pd.DataFrame([data])

    # Убеждаемся, что порядок признаков соответствует required_features
    try:
        df = df[required_features]
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Feature error: {str(e)}"
        )

    return df


@router.post(
    "/forward",
    response_model=ForwardResponse,
    summary="Получить предсказание для одного объекта",
    description="""
    Принимает JSON с одним объектом и возвращает предсказание модели.

    Формат запроса:
    {
        "data": {
            "TransactionAmt": 189.0,
            "C1": 1.0,
            "C2": 2.0,
            // ... все остальные признаки
        }
    }

    Все признаки из FINAL_FEATURES в features.yaml обязательны.
    """,
    responses={
        400: {"description": "Неверный формат данных"},
        403: {"description": "Модель не смогла обработать данные"},
    }
)
async def forward_prediction(
    request: ForwardRequest,
    model=Depends(load_model),
    features_config=Depends(load_features_config)
):
    try:
        # Получаем список обязательных признаков
        required_features = features_config.get("FINAL_FEATURES", [])
        if not required_features:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Модель не смогла обработать данные"
            )

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

    except HTTPException:
        # Перебрасываем HTTP исключения
        raise
    except Exception as e:
        # Ловим все остальные исключения
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
