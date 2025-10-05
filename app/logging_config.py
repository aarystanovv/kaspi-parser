import logging
import logging.config
import structlog
from pathlib import Path
from .core.config import settings


def setup_logging() -> None:
    Path(settings.log_dir).mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {"format": "%(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "plain",
                "level": settings.log_level.upper(),
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": str(Path(settings.log_dir) / "log.json"),
                "formatter": "plain",
                "level": settings.log_level.upper(),
                "encoding": "utf-8",
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": settings.log_level.upper(),
        },
    })

    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(settings.log_level.upper())),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "app"):
    return structlog.get_logger(name)
