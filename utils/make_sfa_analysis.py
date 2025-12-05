import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import roc_auc_score
from tqdm import tqdm


import warnings
warnings.filterwarnings('ignore')


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