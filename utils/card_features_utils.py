import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')

def make_card_features(data, group_col='card1'):
    """
    Агрегация сумм транзакций по картам, отношения сумм транзакций к среднему и медиане
    
    + комбинации с категориальными и другими показателями
    
    """
    grouped = data.groupby(group_col)
    
    data['card_amt_mean'] = grouped['TransactionAmt'].transform('mean')
    data['card_amt_median'] = grouped['TransactionAmt'].transform('median')
    data['card_amt_std'] = grouped['TransactionAmt'].transform('std').fillna(0)
    data['card_amt_max'] = grouped['TransactionAmt'].transform('max')
    data['card_amt_min'] = grouped['TransactionAmt'].transform('min')
    
    # отношение к среднему / медиане
    data['card_amt_ratio_to_mean'] = data['TransactionAmt'] / (data['card_amt_mean'] + 1)
    data['card_amt_ratio_to_median'] = data['TransactionAmt'] / (data['card_amt_median'] + 1)
    
    # флаги
    data['card_amt_more_2x_mean'] = (data['TransactionAmt'] > 2 * data['card_amt_mean']).astype(int)
    data['card_amt_more_3x_mean'] = (data['TransactionAmt'] > 3 * data['card_amt_mean']).astype(int)
    data['card_amt_is_max'] = (data['TransactionAmt'] == data['card_amt_max']).astype(int)
    
    
    # уникальные email на карту
    data['card_unique_P_email'] = grouped['P_emaildomain_new'].transform('nunique')
    data['card_unique_R_email'] = grouped['R_emaildomain_new'].transform('nunique')
    
    data['card_unique_P_email_gr'] = grouped['P_emaildomain_grouped'].transform('nunique')
    data['card_unique_R_email_gr'] = grouped['R_emaildomain_grouped'].transform('nunique')
    
    
    # комбинации
    data['card_email_p'] = data[group_col].astype(str) + '_' + data['P_emaildomain_new']
    data['card_email_r'] = data[group_col].astype(str) + '_' + data['R_emaildomain_new']
    
    
    
    # deepseek
    # Типичный час использования
    def get_mode(x):
        return x.mode().iloc[0] if not x.mode().empty else -1
    
    data['card_mode_hour'] = grouped['hour'].transform(get_mode)
    data['card_hour_changed'] = (data['hour'] != data['card_mode_hour']).astype(int)
    
    # Доля ночных транзакций на карте
    data['is_night'] = ((data['hour'] < 6) | (data['hour'] > 22)).astype(int)
    data['card_night_ratio'] = grouped['is_night'].transform('mean')
    
    # Аномалия: ночная транзакция на карте, которая обычно не активна ночью
    data['card_unusual_night'] = ((data['is_night'] == 1) & (data['card_night_ratio'] < 0.1)).astype(int)
    
    # Выходные vs будни
    data['is_weekend'] = (data['day'] >= 5).astype(int)
    data['card_weekend_ratio'] = grouped['is_weekend'].transform('mean')
    
    # Типичный адрес для карты
    def get_mode(x):
        return x.mode().iloc[0] if not x.mode().empty else -1
    
    # карты + адреса
    data['addr1_new'] = data['addr1'].fillna(999)
    data['addr2_new'] = data['addr1'].fillna(999)
    
    data['card_mode_addr1'] = grouped['addr1_new'].transform(get_mode)
    data['card_mode_addr2'] = grouped['addr2_new'].transform(get_mode)
    
    # Сменился ли адрес
    data['card_addr1_changed'] = (data['addr1_new'] != data['card_mode_addr1']).astype(int)
    data['card_addr2_changed'] = (data['addr2_new'] != data['card_mode_addr2']).astype(int)
    
    # Количество уникальных адресов для карты
    data['card_unique_addr1'] = grouped['addr1_new'].transform('nunique')
    data['card_unique_addr2'] = grouped['addr2_new'].transform('nunique')
    
    # Комбинация карта + адрес
    data['card_addr1_pair'] = data[group_col].astype(str) + '_' + data['addr1'].astype(str)
    data['card_addr2_pair'] = data[group_col].astype(str) + '_' + data['addr2'].astype(str)
    
    
    return data
