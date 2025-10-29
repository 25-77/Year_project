import os
import yaml
from functools import lru_cache
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from .schemas import Settings


@lru_cache()
def get_settings(config_dir: Optional[Path] = r'./configs') -> Settings:
    """Функция для получения конфига"""

    if isinstance(config_dir, str):
        config_dir = Path(config_dir) 

    if not os.path.exists(config_dir):
        raise FileNotFoundError(f"Путь \"{config_dir}\" не существует!")
    
    configs = {}

    # Добавляем все .yaml файлы в единый конфинг
    for file in config_dir.glob('*.yaml'):
        with open(file) as file:
            cfg = yaml.safe_load(file)

        configs.update(cfg)

    # Производим замены на переменные окружения
    configs = _replace_to_env_vars(configs)

    return Settings.model_validate(configs)



def _replace_to_env_vars(cfg: dict) -> dict:
    """Рекурсивная функция для подстановки переменных окружения (из .env)"""

    # Подгружаем .env
    load_dotenv()

    # Если значение промаркировано как переменная окружения - заменяем
    for k, v in cfg.items():
        if isinstance(v, str) and v.startswith('${') and v.endswith('}'):
            cfg[k] = os.getenv(v[2: -1])
        elif isinstance(v, dict):
            _replace_to_env_vars(v)

    return cfg





