# metrics_styler.py
import pandas as pd
from typing import Dict, List, Callable, Any
from pandas.io.formats.style import Styler

from .formatters import format_int_with_spaces

def style_metrics(data: pd.DataFrame, config: Dict[str, Any], axis: int=0) -> Styler:
    """
    Универсальная функция для стилизации метрик с dict-конфигом


    Parameters
    ----------
    data : pd.DataFrame
        DataFrame с метриками для стилизации
    config : Dict[str, Any]
        Словарь конфигурации со следующими возможными ключами:

        - 'percent_cols': List[str] - список колонок для форматирования в процентах
        - 'int_cols': List[str] - список колонок для форматирования как целые числа
        - 'float_cols': List[str] - список колонок для форматирования как float
        - 'float_precision': int - точность для float колонок (по умолчанию 1)
        - 'custom_format': Dict[str, Callable] - кастомные форматтеры для конкретных колонок
        - 'gradient_cols': List[str] - список колонок для градиентной заливки
        - 'gradient_cmap': str - цветовая карта для градиента (по умолчанию 'RdYlGn')
        - 'bar_cols': List[str] - список колонок для отображения bar charts
        - 'bar_color': str - цвет для bar charts (по умолчанию 'lightblue')
        - 'bold_cols': List[str] - список колонок для жирного шрифта
        - 'border_cols': List[str] - список колонок для добавления границ

    Returns
    -------
    pd.io.formats.style.Styler
        Объект Styler с примененными стилями
    """

    styler = data.style

    # Форматирование процентов
    if 'percent_cols' in config:
        available = [col for col in config['percent_cols'] if col in data.columns]
        styler = styler.format("{:.1%}", subset=available)

    # Форматирование целых чисел
    if 'int_cols' in config:
        available = [col for col in config['int_cols'] if col in data.columns]
        styler = styler.format(format_int_with_spaces, subset=available)

    # Форматирование float с точностью
    if 'float_cols' in config:
        precision = config.get('float_precision', 1)
        available = [col for col in config['float_cols'] if col in data.columns]
        styler = styler.format(f"{{:.{precision}f}}", subset=available)

    # Кастомные форматтеры для конкретных колонок
    if 'custom_format' in config:
        for col, formatter in config['custom_format'].items():
            if col in data.columns:
                styler = styler.format(formatter, subset=[col])

    # Градиентная заливка
    if 'gradient_cols' in config:
        available = [col for col in config['gradient_cols'] if col in data.columns]
        cmap = config.get('gradient_cmap', 'RdYlGn')
        styler = styler.background_gradient(cmap=cmap, subset=available, axis=axis)

    # Bar charts в ячейках
    if 'bar_cols' in config:
        available = [col for col in config['bar_cols'] if col in data.columns]
        color = config.get('bar_color', 'lightblue')
        styler = styler.bar(subset=available, color=color)

    # Жирный шрифт
    if 'bold_cols' in config:
        available = [col for col in config['bold_cols'] if col in data.columns]
        styler = styler.map(lambda x: "font-weight: bold", subset=available)

    # Границы
    if 'border_cols' in config:
        available = [col for col in config['border_cols'] if col in data.columns]
        styler = styler.map(lambda x: "border: 1px solid black", subset=available)

    # Допом можно реализовать:
    #   Скрытие колонок
    #   Подсветка максимумов
    #   Подсветка минимумов
    #   Цвет текста
    return styler
