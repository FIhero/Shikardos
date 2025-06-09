import logging
from pathlib import Path


def setup_logging() -> None:
    """Настройка системы логирования для всего проекта"""
    logs_dir = Path("../logs")
    logs_dir.mkdir(exist_ok=True)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[])


def get_logger(name: str) -> logging.Logger:
    """Возвращает настроенный логгер для модуля"""
    logger = logging.getLogger(name)

    log_file = f"logs/{name}.log"
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    logger.addHandler(file_handler)
    return logger
