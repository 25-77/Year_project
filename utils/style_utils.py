import pandas as pd
from IPython.display import HTML, display
from functools import partial

def print_html(base_text, higlighted_text):
    """
    Выводит текст в одну строку, где higlighted_text оранжевый и жирный.
    Сохраняет все пробелы.
    """

    html_output = f"""
    <b style='white-space: pre;'>{base_text}</b>
    <b style='color:orange;'>{higlighted_text}</b>
    """

    display(HTML(html_output))

def print_multiple_html(*text_pairs, px_margin=1.4):
    html_pairs = []
    for base, highlighted in text_pairs:
        html_pairs.append(
            f"""<div style='margin-bottom: {px_margin}px;'>
                <b style='white-space: pre;'>{base}</b>
                <b style='color:orange;'>{highlighted}</b>
            </div>""")

    display(HTML("".join(html_pairs)))



# def k_formatter(x, precision=None):
#     if isinstance(x, (int, float)):
#         return f"{x // 1000:g}k"
#     return x

def k_formatter(precision=None):
    def formatter(x):
        if isinstance(x, (int, float)):
            if precision is not None:
                return f"{x / 1000:.{precision}f}k".replace('.0', '')
            else:
                return f"{x // 1000:g}k"
        return x
    return formatter


def m_formatter(x):
    if isinstance(x, (int, float)):
        return f"{x / 1_000_000:.1f}M".replace('.0', '')
    return x

def format_int_with_spaces(x):
    """Форматирование целых чисел с пробелами"""
    if pd.isna(x):
        return ""
    return f"{x:,.0f}".replace(",", " ")
