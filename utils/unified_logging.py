"""
Unified Logging System for PulseAI.

This module provides a standardized logging system across the entire project,
ensuring consistent log formatting, levels, and handlers.
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

try:
    import yaml
except ImportError:
    yaml = None


class UnifiedLogger:
    """
    Unified logger class providing consistent logging across the project.
    """
    
    _configured = False
    _loggers: Dict[str, logging.Logger] = {}
    
    @classmethod
    def setup_logging(
        cls,
        config_path: Optional[str] = None,
        level: str = "INFO",
        log_to_file: bool = True,
        log_to_console: bool = True
    ) -> bool:
        """
        Setup unified logging system.
        
        Args:
            config_path: Path to YAML logging configuration
            level: Default logging level
            log_to_file: Whether to log to files
            log_to_console: Whether to log to console
            
        Returns:
            True if setup successful, False otherwise
        """
        try:
            if cls._configured:
                return True
            
            # Try to load from YAML config first
            if config_path and yaml:
                config_file = Path(config_path)
                if config_file.exists():
                    success = cls._setup_from_yaml(config_file, level)
                    if success:
                        cls._configured = True
                        return True
            
            # Fallback to programmatic configuration
            cls._setup_programmatic(level, log_to_file, log_to_console)
            cls._configured = True
            return True
            
        except Exception as e:
            print(f"⚠️ Ошибка настройки логирования: {e}")
            # Fallback to basic logging
            logging.basicConfig(level=getattr(logging, level.upper()))
            return False
    
    @classmethod
    def _setup_from_yaml(cls, config_file: Path, default_level: str) -> bool:
        """Setup logging from YAML configuration file."""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            
            # Create log directories
            for handler in config.get("handlers", {}).values():
                filename = handler.get("filename")
                if isinstance(filename, str):
                    try:
                        Path(filename).parent.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        print(f"⚠️ Не удалось создать директорию для {filename}: {e}")
            
            # Apply configuration
            logging.config.dictConfig(config)
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке конфигурации логов {config_file}: {e}")
            return False
    
    @classmethod
    def _setup_programmatic(
        cls, 
        level: str, 
        log_to_file: bool, 
        log_to_console: bool
    ):
        """Setup logging programmatically."""
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, level.upper()))
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler
        if log_to_file:
            file_handler = logging.FileHandler(
                logs_dir / "app.log",
                encoding="utf-8"
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            
            # Error file handler
            error_handler = logging.FileHandler(
                logs_dir / "errors.log",
                encoding="utf-8"
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            root_logger.addHandler(error_handler)
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get logger instance with unified configuration.
        
        Args:
            name: Logger name (typically __name__)
            
        Returns:
            Configured logger instance
        """
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            
            # Add custom formatting for specific modules
            cls._configure_module_logger(logger, name)
            
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @classmethod
    def _configure_module_logger(cls, logger: logging.Logger, name: str):
        """Configure logger for specific modules."""
        # Add module-specific formatting
        if "database" in name:
            # Database operations get special formatting
            logger.addFilter(DatabaseLogFilter())
        elif "telegram" in name:
            # Telegram operations get special formatting
            logger.addFilter(TelegramLogFilter())
        elif "ai" in name:
            # AI operations get special formatting
            logger.addFilter(AILogFilter())
        elif "parser" in name:
            # Parser operations get special formatting
            logger.addFilter(ParserLogFilter())
    
    @classmethod
    def log_performance(cls, operation: str, duration: float, **kwargs):
        """Log performance metrics."""
        logger = cls.get_logger("performance")
        extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
        logger.info(f"⏱️ {operation} took {duration:.3f}s {extra_info}")
    
    @classmethod
    def log_database_operation(cls, operation: str, table: str, count: int = 0, **kwargs):
        """Log database operations."""
        logger = cls.get_logger("database.operations")
        extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
        logger.info(f"🗄️ {operation} on {table}: {count} records {extra_info}")
    
    @classmethod
    def log_telegram_operation(cls, operation: str, user_id: int = None, **kwargs):
        """Log Telegram operations."""
        logger = cls.get_logger("telegram.operations")
        user_info = f"user_id={user_id}" if user_id else ""
        extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
        logger.info(f"📱 {operation} {user_info} {extra_info}")
    
    @classmethod
    def log_ai_operation(cls, operation: str, model: str = None, **kwargs):
        """Log AI operations."""
        logger = cls.get_logger("ai.operations")
        model_info = f"model={model}" if model else ""
        extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
        logger.info(f"🤖 {operation} {model_info} {extra_info}")
    
    @classmethod
    def log_parser_operation(cls, operation: str, source: str = None, count: int = 0, **kwargs):
        """Log parser operations."""
        logger = cls.get_logger("parser.operations")
        source_info = f"source={source}" if source else ""
        extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
        logger.info(f"📰 {operation} {source_info}: {count} items {extra_info}")


class DatabaseLogFilter(logging.Filter):
    """Custom filter for database log messages."""
    
    def filter(self, record):
        # Add database-specific formatting
        if not hasattr(record, 'formatted'):
            record.msg = f"🗄️ {record.msg}"
            record.formatted = True
        return True


class TelegramLogFilter(logging.Filter):
    """Custom filter for Telegram log messages."""
    
    def filter(self, record):
        # Add Telegram-specific formatting
        if not hasattr(record, 'formatted'):
            record.msg = f"📱 {record.msg}"
            record.formatted = True
        return True


class AILogFilter(logging.Filter):
    """Custom filter for AI log messages."""
    
    def filter(self, record):
        # Add AI-specific formatting
        if not hasattr(record, 'formatted'):
            record.msg = f"🤖 {record.msg}"
            record.formatted = True
        return True


class ParserLogFilter(logging.Filter):
    """Custom filter for parser log messages."""
    
    def filter(self, record):
        # Add parser-specific formatting
        if not hasattr(record, 'formatted'):
            record.msg = f"📰 {record.msg}"
            record.formatted = True
        return True


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation: str, logger: Optional[logging.Logger] = None):
        self.operation = operation
        self.logger = logger or UnifiedLogger.get_logger("performance")
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            UnifiedLogger.log_performance(self.operation, duration)


# Convenience functions
def setup_logging(
    config_path: Optional[str] = "config/logging.yaml",
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True
) -> bool:
    """Setup unified logging system."""
    return UnifiedLogger.setup_logging(config_path, level, log_to_file, log_to_console)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance with unified configuration."""
    return UnifiedLogger.get_logger(name)


def log_performance(operation: str, duration: float, **kwargs):
    """Log performance metrics."""
    UnifiedLogger.log_performance(operation, duration, **kwargs)


def log_database_operation(operation: str, table: str, count: int = 0, **kwargs):
    """Log database operations."""
    UnifiedLogger.log_database_operation(operation, table, count, **kwargs)


def log_telegram_operation(operation: str, user_id: int = None, **kwargs):
    """Log Telegram operations."""
    UnifiedLogger.log_telegram_operation(operation, user_id, **kwargs)


def log_ai_operation(operation: str, model: str = None, **kwargs):
    """Log AI operations."""
    UnifiedLogger.log_ai_operation(operation, model, **kwargs)


def log_parser_operation(operation: str, source: str = None, count: int = 0, **kwargs):
    """Log parser operations."""
    UnifiedLogger.log_parser_operation(operation, source, count, **kwargs)


def time_operation(operation: str, logger: Optional[logging.Logger] = None):
    """Context manager for timing operations."""
    return PerformanceTimer(operation, logger)


# Initialize logging on import
setup_logging()
