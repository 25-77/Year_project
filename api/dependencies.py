# Загрузка модели и конфигов

import yaml
from catboost import CatBoostClassifier
from pathlib import Path
from functools import lru_cache

BASE_DIR = Path(__file__).parent.parent


@lru_cache()
def load_model():
    """Загрузка CatBoost модели"""
    model_path = BASE_DIR / "models" / "final_model.cbm"
    model = CatBoostClassifier()
    model.load_model(str(model_path))
    return model


@lru_cache()
def load_features_config():
    """Загрузка списка переменных модели"""
    features_path = BASE_DIR / "models" / "params" / "features.yaml"
    with open(features_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
