# Структура проекта

```bash
.
├── api                             # Fast API
│   ├── main.py                     # Точка входа в приложение FastAPI
│   ├── database.py                 # Настройки и подключение к базе данных
│   ├── dependencies.py             # Зависимости для загрузки моделей и переменных
│   ├── middleware.py               # Middleware для логирования запросов
│   ├── models.py                   # SQLAlchemy модели базы данных
│   ├── schemas.py                  # Pydantic схемы для валидации данных
│   └── routers/                    # Маршрутизаторы API
│       ├── forward.py              # Роутер для получения предсказаний
│       └── history.py              # Роутер для работы с историей запросов
├── config                          # Конфигурационные файлы
├── data                            # Данные
│   ├── preprocessed
│   └── raw
├── docs                            # Документация проекта
│   ├── DEVELOPMENT.md
│   ├── POETRY.md
│   └── STRUCTURE.md
├── notebooks                       # Jupyter notebooks
│   └── 1. EDA.ipynb                # Разведочный анализ данных
├── reports                         # Отчеты
├── src                             # Исходный код (API, бот, модели БД)
├── utils                           # Утилиты для этого проекта
├── pyproject.toml                  # Конфигурация Python проекта
└── README.md

```
