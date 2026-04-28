import pandas as pd
import numpy as np


import warnings
warnings.filterwarnings('ignore')

def make_time_window_features(data, group_col='card1'):
    """
    Расчет временных окон по транзакциям для каждой карты (card1)
    за разные окна (1ч, 6ч, 24ч, 7д):
    - количество транзакций по карте 
    - средняя, медианная, максимальная сумма по карте
    - стандартное отклонение суммы по карте
    - время с последней транзакции
    * + производные и временные признаки
    
    """
    
    data = data.sort_values([group_col, 'TransactionDT'])

    # 
    windows = [1, 6, 24, 72, 168]

    for w in windows:
        w_sec = w * 3600
        
        grouped = data.groupby(group_col)
        
        # count
        data[f'count_{w}h'] = grouped['TransactionDT'].transform(
            lambda x: x.rolling(window=w_sec, min_periods=1).count())
        
        # mean
        data[f'amt_mean_{w}h'] = grouped['TransactionAmt'].transform(
            lambda x: x.rolling(window=w_sec, min_periods=1).mean())
        
        # median
        data[f'amt_median_{w}h'] = grouped['TransactionAmt'].transform(
            lambda x: x.rolling(window=w_sec, min_periods=1).median())
        
        # min
        data[f'amt_min_{w}h'] = grouped['TransactionAmt'].transform(
            lambda x: x.rolling(window=w_sec, min_periods=1).min())
        
        # max
        data[f'amt_max_{w}h'] = grouped['TransactionAmt'].transform(
            lambda x: x.rolling(window=w_sec, min_periods=1).max())
        
        # sum
        data[f'amt_sum_{w}h'] = grouped['TransactionAmt'].transform(
            lambda x: x.rolling(window=w_sec, min_periods=1).sum())
        
        # std. 0, если точек меньше 2
        data[f'amt_std_{w}h'] = grouped['TransactionAmt'].transform(
            lambda x: x.rolling(window=w_sec, min_periods=2).std()).fillna(0)
        
        # div trans / mean
        data[f'amt_ratio_to_mean_{w}h'] = data['TransactionAmt'] / (data[f'amt_mean_{w}h'] + 1)
        
        # div trans / median
        data[f'amt_ratio_to_median_{w}h'] = data['TransactionAmt'] / (data[f'amt_median_{w}h'] + 1)
        
        
        # deepseek
        # --- Временные признаки ---
        
        # Время с последней транзакции
        data[f'time_since_last_{w}h'] = grouped['TransactionDT'].transform(
            lambda x: x.diff()).fillna(0)
        
        # Логарифм времени с последней транзакции
        data[f'log_time_since_last_{w}h'] = np.log1p(data[f'time_since_last_{w}h'])
        
        # Средний интервал между транзакциями
        data[f'mean_gap_{w}h'] = grouped['TransactionDT'].transform(
            lambda x: x.diff().rolling(window=w_sec, min_periods=2).mean()).fillna(0)
        
        # Минимальный интервал
        data[f'min_gap_{w}h'] = grouped['TransactionDT'].transform(
            lambda x: x.diff().rolling(window=w_sec, min_periods=2).min()
        ).fillna(0)
        
        # Максимальный интервал
        data[f'max_gap_{w}h'] = grouped['TransactionDT'].transform(
            lambda x: x.diff().rolling(window=w_sec, min_periods=2).max()
        ).fillna(0)

    return data


