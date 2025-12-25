import pandas as pd
import numpy as np
from tqdm.notebook import tqdm
from scipy.stats import chi2_contingency

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
# from tqdm import tqdm


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


def empty_dict(feature, n_obs, missing_pct):
    """
    Словарь с пустыми значениями для sfa_analysis
    """
    return {'feature': feature,
            'feature_group': feature[0],
            'auc': np.nan,
            'gini': np.nan,
            'iv': np.nan,
            'corr_%': np.nan,
            'n_obs': n_obs,
            'missing_pct': missing_pct}

def calculate_simple_iv(data,
                        feature,
                        target: str = 'target',
                        n_bins: int = 5) -> int | float:
    """
    Упрощенный расчет IV

    Parameters:
    -----------
    data : pd.DataFrame
        Исходный DataFrame
    feature: str
        Показатель
    target : str
        Название целевой переменной, default = 'target'
    n_bins : int
        Число бинов для квантильного биннинга, default = 5

    Returns:
    --------
    pd.DataFrame
        Таблица с результатами SFA
    """
    temp_data = data[[feature, target]].dropna()

    x, y = temp_data[feature].values, temp_data[target].values

    try:
        # для числовых признаков - квантильный биннинг
        if len(np.unique(x)) > 20:
            bins = pd.qcut(x, q=n_bins, duplicates='drop')
        else:
            # для категориальных - каждое значение как бин
            bins = pd.Categorical(x)

        # IV
        df_temp = pd.DataFrame({'bin': bins, 'target': y})
        grouped = df_temp.groupby('bin')['target'].agg(['count', 'sum'])
        grouped.columns = ['total', 'fraud']
        grouped['non_fraud'] = grouped['total'] - grouped['fraud']

        # obs
        total_fraud = grouped['fraud'].sum()
        total_non_fraud = grouped['non_fraud'].sum()

        if total_fraud == 0 or total_non_fraud == 0:
            return 0

        # доля "плохих" и "хороших"
        grouped['p_fraud'] = grouped['fraud'] / total_fraud
        grouped['p_non_fraud'] = grouped['non_fraud'] / total_non_fraud

        eps = 1e-10
        # формальный woe, так как биннинг производится с помощью pd.qcut
        grouped['woe'] = np.log((grouped['p_fraud'] + eps) / (grouped['p_non_fraud'] + eps))
        grouped['iv'] = (grouped['p_fraud'] - grouped['p_non_fraud']) * grouped['woe']

        return round(grouped['iv'].sum(), 2)

    except:
        return 0


def sfa_analysis(data: pd.DataFrame,
                 features: list,
                 target: str = 'target') -> pd.DataFrame:
    """
    Краткий однофакторный анализ

    Parameters:
    -----------
    data : pd.DataFrame
        Исходный DataFrame
    features: list
        Список показателей
    target : str
        Название целевой переменной. default = 'target'

    Returns:
    --------
    pd.DataFrame
        Таблица с результатами SFA

    """
    # для записи результатов
    results = []

    for feature in tqdm(features):
        # % miss
        missing_pct = round((data[feature].isnull().sum() / len(data)) * 100, 2)

        # drop miss, count obs
        temp_df = data[[feature, target]].dropna()
        n_obs = len(temp_df)

        # считаем за недостаточное количество наблюдений (не стат. значимый рез-т)
        if n_obs < 100:
            results.append(empty_dict(feature, n_obs, missing_pct))
            continue

        try:
            # стандартизация
            X = temp_df[[feature]].values
            y = temp_df[target].values

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # fit
            model = LogisticRegression()
            model.fit(X_scaled, y)

            y_pred = model.predict_proba(X_scaled)[:, 1]

            auc = round(roc_auc_score(y, y_pred), 2)

            # gini
            gini = 2 * auc - 1

            # iv
            iv = calculate_simple_iv(temp_df, feature, target)
            # corr
            corr_matrix = temp_df[[feature, target]].corr()

            if corr_matrix.empty:
                corr = np.nan
            else:
                corr = round(abs(corr_matrix.iloc[0, 1]), 2)

            # res
            results.append({'feature': feature,
                            'feature_group': feature[0],
                            'auc': auc,
                            'gini': gini,
                            'iv': iv,
                            'corr_%': corr,
                            'n_obs': n_obs,
                            'missing_pct': missing_pct})

        except Exception as e:
            # если например таргет принимает одно значение (после удаления пропусков)
            results.append(empty_dict(feature, n_obs, missing_pct))
            continue

    return pd.DataFrame(results)
