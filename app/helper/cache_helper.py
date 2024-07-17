import gc
import pickle
from pathlib import Path
from typing import Any
from app.config.app_config import app_config
from app.helper.logger_helper import logger


class CacheHelper:

    @staticmethod
    def load_cache(filename: str) -> Any:
        cache_path = app_config.TEMP_PATH / filename
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"加载缓存 {filename} 出错：{str(e)}")
        return None

    @staticmethod
    def save_cache(cache: Any, filename: str) -> None:
        try:
            with open(app_config.TEMP_PATH / filename, 'wb') as f:
                pickle.dump(cache, f)
        except Exception as e:
            logger.error(f"保存缓存 {filename} 出错：{str(e)}")
        finally:
            del cache
            gc.collect()

    @staticmethod
    def remove_cache(filename: str) -> None:
        cache_path = app_config.TEMP_PATH / filename
        if cache_path.exists():
            Path(cache_path).unlink()
