# utils/logging_setup.py
import logging
import logging.config
import yaml
from pathlib import Path

def setup_logging(
    config_path: str = "config/logging.yaml",
    default_level=logging.INFO
):
    """Настройка логирования из YAML-конфига с авто-созданием папки logs/"""
    config_file = Path(config_path)

    if config_file.exists():
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

            # --- фикс: создаём папку для всех FileHandler-ов ---
            for handler in config.get("handlers", {}).values():
                filename = handler.get("filename")
                if filename:
                    log_path = Path(filename).parent
                    log_path.mkdir(parents=True, exist_ok=True)

            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        logging.warning("Файл конфигурации логов не найден, используется basicConfig")