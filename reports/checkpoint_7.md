## Инфраструктура версионирования экспериментов
**Файлы:**
[docker-compose.yaml](../docker-compose.yaml)
[pyproject.toml](../pyproject.toml)

1. Поднят локальный стенд через Docker Compose:
   - **PostgreSQL** — backend-store для MLflow
   - **MLflow** (`http://localhost:5050`) — трекинг экспериментов и Model Registry
   - **MinIO** (`http://localhost:9000`, UI `:9001`) — S3-совместимое хранилище артефактов (`mlflow-bucket`)

2. В `pyproject.toml` добавлены зависимости для чекпоинта: `mlflow`, `boto3`, `python-dotenv`.

3. Локальные данные контейнеров (`data/mlflow/`, `data/minio_data/`) добавлены в `.gitignore`.

## Выбор финальной модели
**Файл:** [notebooks/3.2. Nonlinear_models.ipynb](../notebooks/3.2.%20Nonlinear_models.ipynb)

1. Сравнивались RF, LightGBM, XGBoost и CatBoost (базовый и с Optuna по топ-30 признакам).
2. **Финальная модель — CatBoost** (`final_model_preds`):
   - лучшие GINI / ROC-AUC на **TEST** и **OOT** среди нелинейных моделей;
   - признаки и гиперпараметры зафиксированы в `models/params/features.yaml` и `models/params/best_params.yaml`.
3. Версия для продакшена помечена тегом **PRD** в MLflow Model Registry.

## Логирование эксперимента в MLflow
**Файл:** [notebooks/DL_Experiments.ipynb](../notebooks/DL_Experiments.ipynb)

1. Переобучена финальная CatBoost-модель и залогирован один PRD-эксперимент:
   - experiment: `year-project-fraud-catboost`
   - registered model: `year_project_fraud_catboost` (alias `prd`)

2. **Залогированные параметры:** гиперпараметры из `best_params.yaml`, `random_seed=42`, число финальных признаков.

3. **Метрики качества (GINI / ROC-AUC):**

| sample_type | baseline GINI | final GINI | baseline ROC-AUC | final ROC-AUC |
|-------------|---------------|------------|------------------|---------------|
| TRAIN       | 92.0%         | 96.0%      | 96.0%            | 98.0%         |
| TEST        | 88.6%         | 91.7%      | 94.0%            | 95.5%         |
| OOT         | 82.1%         | 84.6%      | 91.0%            | 92.3%         |

4. **Артефакты в S3 (MinIO):**
   - обученная модель (Model Registry + run artifacts);
   - графики ROC и динамики Gini;
   - примеры предсказаний (`predictions_sample.csv`);
   - таблица ошибок классификации (`error_examples.csv`).

5. **Воспроизводимость:**
   - seed: `42` (CatBoost, Optuna в 3.2);
   - данные: `./data/processed/data.pqt` (пайплайн из `notebooks/1. Data_prepararation.ipynb`);
   - сплиты: `sample_type` (TRAIN / TEST / OOT), обучение на `competition_sample_type == TRAIN`.

## Анализ ошибок модели

1. На выборке **TEST** (порог 0.5) выделены категории:
   - **FP** — ложная тревога (target=0, pred=1);
   - **FN** — пропуск мошенничества (target=1, pred=0).

2. Разобрано **20 примеров** неверных предсказаний (см. `error_examples` в ноутбуке и артефакты MLflow).

3. **Типичные причины ошибок:**
   - **FP на крупных суммах** — модель реагирует на аномальную активность; без бизнес-калибровки порога на OOT корректировка ограничена.
   - **FN при MISSING / редких категориальных значениях** — недостаточно сигнала в M- и email-признаках; требуются новые фичи, а не только переобучение.
   - **Пограничные скоры (0.45–0.55)** — компромисс precision/recall; смена порога улучшает одну метрику за счёт другой.

## Сравнение с baseline

**Baseline** — CatBoost на тех же 30 признаках с дефолтными гиперпараметрами (до Optuna в 3.2).

| sample_type | Δ GINI (final − baseline) |
|-------------|---------------------------|
| TRAIN       | +4.0 п.п.                 |
| TEST        | +3.1 п.п.                 |
| OOT         | +2.5 п.п.                 |

Финальная модель стабильно лучше baseline на всех сплитах; наибольший прирост на TRAIN/TEST, на OOT — умеренный (+2.5 п.п.), что ожидаемо для out-of-time.

## Проверка устойчивости (robustness)

На 500 наблюдениях TEST к числовым признакам добавлен шум ~1% от std. Наблюдения:
- среднее абсолютное изменение скора — небольшое;
- доля объектов с |Δ score| > 0.05 — ограниченная доля выборки;
- модель не «ломается» от малых возмущений, но чувствительна к сумме транзакции и email-признакам (согласуется с SHAP в 3.2).

## Демонстрация загрузки PRD-модели
**Файл:** [notebooks/DL_Demonstration.ipynb](../notebooks/DL_Demonstration.ipynb)

1. Загрузка модели из MLflow: `models:/year_project_fraud_catboost@prd`.
2. Тестовый predict на 15 наблюдениях из TEST (категориальные признаки приведены к `string` для совместимости с pyfunc-схемой MLflow).

## Выводы

1. Инфраструктура MLflow + MinIO настроена; эксперименты и артефакты версионируются локально.
2. **CatBoost** зафиксирован как финальная PRD-модель с воспроизводимыми параметрами и метриками train/test/oot.
3. По сравнению с baseline финальная модель даёт прирост GINI **+2.5–4.0 п.п.**; основные ошибки объясняются порогом, редкими категориями и пограничными скорами.
4. Чекпоинт закрыт двумя ноутбуками: `DL_Experiments.ipynb` (обучение + MLflow + анализ) и `DL_Demonstration.ipynb` (инференс из реестра).
