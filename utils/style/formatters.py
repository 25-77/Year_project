import pandas as pd

# def k_formatter(x):
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