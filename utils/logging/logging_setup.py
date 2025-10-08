# utils/logging_setup.py
import logging
import logging.config
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def setup_logging(config_path: str = "config/system/logging.yaml", default_level=logging.INFO):
    """
    Настройка логирования из YAML-конфига.
    - Если logging.yaml найден → используем dictConfig.
    - Если нет → basicConfig (stdout).
    - Автоматически создаёт директории для файлов логов.
    """
    config_file = Path(config_path)

    if yaml and config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Создаём папки для FileHandler-ов
            for handler in config.get("handlers", {}).values():
                filename = handler.get("filename")
                if isinstance(filename, str):
                    try:
                        Path(filename).parent.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        logging.basicConfig(level=default_level)
                        logging.warning(f"⚠️ Не удалось создать директорию для {filename}: {e}")

            logging.config.dictConfig(config)
        except Exception as e:
            logging.basicConfig(level=default_level)
            logging.error(f"❌ Ошибка при загрузке конфигурации логов {config_path}: {e}")
    else:
        logging.basicConfig(
            level=default_level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        logging.warning("⚠️ Файл конфигурации логов не найден, используется basicConfig")
