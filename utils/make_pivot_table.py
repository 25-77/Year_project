import pandas as pd

import warnings
warnings.filterwarnings('ignore')


def pvt_table(data: pd.DataFrame,
              index_name: str | list,
              values_name: str = 'target',
              lst_agg: list = [pd.Series.count, pd.Series.sum, pd.Series.mean],
              dropna_values: bool = True) -> pd.DataFrame:
    """
    Функция для отображения сводной таблицы.
    Группировка производится по категориальному показателю (списку) и рассчетному (по дефолту используется целевая переменная)

    Parameters:
    -----------
    data : pd.DataFrame
        Исходный DataFrame
    index_name: str | list
        Название поля(-ей), по которым производится группировка  
    values_name : str
        Название поля, по которому производится расчет. default = 'target'
    lst_agg : list
        Список агрегирующих функций

    Returns:
    --------
    pd.DataFrame
        Сводная таблица
    """
    pvt_table = pd.pivot_table(data=data,
                               index=index_name,
                               values=values_name,
                               aggfunc=lst_agg,
                               dropna=dropna_values).round(4)

    pvt_table.columns = ['_'.join(x) for x in pvt_table.columns]
    
    pvt_table = pvt_table.reset_index()

    return pvt_table