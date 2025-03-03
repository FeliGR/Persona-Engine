import sys
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Union


class LoggerFactory:

    _loggers: Dict[str, logging.Logger] = {}

    @classmethod
    def get_logger(
        cls,
        name: str = "persona-engine",
        log_level: Union[str, int] = "INFO",
        log_to_file: bool = False,
        log_file_path: Optional[str] = None,
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        max_bytes: int = 10485760,
        backup_count: int = 5,
    ) -> logging.Logger:
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.handlers.clear()

        try:
            if isinstance(log_level, str):
                logger.setLevel(getattr(logging, log_level.upper()))
            else:
                logger.setLevel(log_level)
        except (AttributeError, TypeError) as e:
            print(f"Invalid log level: {log_level}. Using INFO instead. Error: {e}")
            logger.setLevel(logging.INFO)

        formatter = logging.Formatter(log_format)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if log_to_file:
            try:
                if not log_file_path:
                    log_dir = Path("logs")
                    log_dir.mkdir(exist_ok=True)
                    log_file_path = str(log_dir / f"{name}.log")

                file_handler = logging.handlers.RotatingFileHandler(
                    log_file_path, maxBytes=max_bytes, backupCount=backup_count
                )
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                console_handler.setLevel(logging.WARNING)
                logger.warning(f"Failed to set up file logging: {e}")

        cls._loggers[name] = logger
        return logger


def setup_logger(config=None):
    if config is None:
        from config import Config

        config = Config

    return LoggerFactory.get_logger(
        name="persona-engine",
        log_level=getattr(config, "LOG_LEVEL", "INFO"),
        log_to_file=getattr(config, "LOG_TO_FILE", False),
        log_file_path=getattr(config, "LOG_FILE_PATH", None),
    )


logger = setup_logger()
