from catboost import Pool


def get_pool(data, target, subset_mask, features, cat_features, weight=None):
    """Создаем и возвращаем pool для CatBoost"""
    
    pool = Pool(
        data=data.loc[subset_mask][features],
        label=data.loc[subset_mask][target],
        feature_names=list(features),
        cat_features=list(cat_features),
        weight=weight,
    )
    return pool