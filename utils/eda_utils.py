import pandas as pd
import numpy as np
from tqdm.notebook import tqdm
from scipy.stats import chi2_contingency

def cramers_v_matrix(data, cat_columns):
    """
    Короткая версия матрицы корреляции Крамера для категориальных переменных.
    """
    n = len(cat_columns)
    corr_matrix = pd.DataFrame(np.eye(n), index=cat_columns, columns=cat_columns)

    for i, col1 in enumerate(cat_columns):
        for j, col2 in enumerate(cat_columns[i+1:], i+1):
            # Фильтруем NaN и вычисляем Cramers V
            mask = data[[col1, col2]].notna().all(axis=1)
            if mask.sum() > 0:
                table = pd.crosstab(data.loc[mask, col1], data.loc[mask, col2])
                chi2 = chi2_contingency(table)[0]
                n_obs = table.sum().sum()
                corr_val = np.sqrt(chi2 / (n_obs * (min(table.shape) - 1)))

                corr_matrix.iloc[i, j] = corr_val
                corr_matrix.iloc[j, i] = corr_val

    return corr_matrix


def get_vars_statistics(data: pd.DataFrame, columns, percentilies_list=None, show_progress=True):
    """
    Получаем статистику по признакам

    Parameters
    ----------
    data : pd.DataFrame
        Датафрейм с данными.
    columns : list
        Список признаков, по которым нужно получить статистику.
    percentilies_list : list, optional
        Список процентилей, которые нужно рассчитать. Если None, то используются 1-й и 99-й процентиль.
    show_progress : bool, optional
        Показывать ли прогресс выполнения. По умолчанию True.

    Returns
    -------
    pd.DataFrame
        Датафрейм со статистикой по признакам.
        Содержит такие метрики, как: медиана, среднее, стандартное отклонение, минимум, максимум,
        количество уникальных значений, мода и количество значений, равных моде,
        количество пропусков, тип данных.
    """


    if percentilies_list is None:
        percentilies = 0.01 * np.array([1, 99])

    else:
        percentilies = 0.01 * np.array(percentilies_list)

    data_length = len(data)
    data_width = len(columns)

    result = data[columns].describe(include='all', percentiles=percentilies).T
    result.rename(columns={
        '50%': '50% (median)'}, inplace=True)

    attributes = pd.DataFrame()
    attributes['attribute'] = columns
    cm = data[columns].isna().sum(axis=0)

    moda = []
    count_distinct = []
    count_value_moda = [] # количество значений, равных моде

    if show_progress == True:
        iterable = tqdm(data[columns].items(), total=data_width, desc='Обработано признаков')

    else:
        iterable = data[columns].items()

    for feature_name, feature_column in iterable:
        vc = feature_column.value_counts(dropna=False)
        count_distinct.append(len(vc))

        if cm[feature_name] == data_length:
            moda.append(np.nan)
            count_value_moda.append(np.nan)
            continue

        if feature_column.dtype == 'object':
            moda.append(vc.index[0])
            count_value_moda.append(vc.iloc[0])
        else:
            moda.append(np.nan)
            count_value_moda.append(np.nan)

    attributes['moda'] = moda
    attributes['count_distinct'] = count_distinct
    attributes['count_value_moda'] = count_value_moda
    attributes['count_nan'] = cm.values
    attributes['type'] = data[columns].dtypes.values

    return pd.merge(attributes, result, left_on='attribute', right_index=True)
