# utils/logging_setup.py
import logging
import logging.config
import yaml
from pathlib import Path

def setup_logging(
    config_path: str = "config/logging.yaml", 
    default_level=logging.INFO
):
    """Настройка логирования из YAML-конфига"""
    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        logging.warning("Файл конфигурации логов не найден, используется basicConfig")
