from logging.config import dictConfig

LOG_FILE = "app.log"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOG_FILE,
            "formatter": "default",
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "fastapi": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "auto_review_tool": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


def setup_logging() -> None:
    """
    Initializes the logging configuration.
    """
    dictConfig(LOGGING_CONFIG)
