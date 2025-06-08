import logging

from settings import LogLevel, settings


def get_logger(module_name: str, log_level: LogLevel | None = None) -> logging.Logger:
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(process)d | %(name)s | %(levelname)s | %(message)s', datefmt='%Y-%m%d %H:%M:%S %z'
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(module_name)
    logger.addHandler(handler)
    logger.setLevel(log_level or settings.logger.level.value)

    return logger