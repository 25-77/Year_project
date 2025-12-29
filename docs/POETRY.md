# Инструкция по работе с Poetry

Poetry — это инструмент для управления зависимостями и виртуальными окружениями в Python-проектах.

## Быстрый старт
```bash
# Переход в папку проекта
cd your-project-name

# Установка зависимостей
poetry install

# Активировать окружение
source $(poetry env info --path)/bin/activate
```
# Дополнительные команды

## Управление окружением
```bash
# Активация
source $(poetry env info --path)/bin/activate

# Деактивация
deactivate

# Информация об окружении
poetry env info
```

## Управление пакетами
По умолчанию не делим пакеты на отдельные группы

```bash
# Добавить пакет
poetry add pandas numpy

# Добавить dev-пакет
poetry add --group dev pytest jupyter

# Установить только то, что нужно для работы приложения
poetry install --without dev

# Удалить пакет
poetry remove package-name

# Обновить все пакеты
poetry update
```

## Просмотр зависимостей
```bash
# Все зависимости
poetry show

# Дерево зависимостей
poetry show --tree
```