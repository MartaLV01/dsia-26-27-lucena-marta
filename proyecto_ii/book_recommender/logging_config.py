
"""
Configuración centralizada del sistema de logging.
"""

import logging
import os
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# esto solo crea un log tiene los log de varios dias
# DEFAULT_LOG_PATH = PROJECT_ROOT / "logs" / "pipeline.log" 

# de esta otra manera se genera un log por ejecucion diaria, con la info
# de tantas ejecuciones ese dia haya habido
# current_date = datetime.now().strftime("%Y-%m-%d")
LOG_DIR = PROJECT_ROOT / "logs"
# DEFAULT_LOG_PATH = LOG_DIR / f"pipeline_{current_date}.log"


def setup_logging(
    log_level: str | None = None,
    #log_file: Path = DEFAULT_LOG_PATH,
    log_file: Path | None = None,
) -> None:
    """
    Configura el logging para consola y archivo.

    Args:
        log_level: nivel de logging (DEBUG, INFO, WARNING, ERROR).
                   Si no se indica, se consulta LOG_LEVEL.
        log_file: ruta del archivo donde se guardarán los logs.
    """
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")

    if log_file is None:
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file = LOG_DIR / f"pipeline_{current_date}.log"

    numeric_level = getattr(logging, log_level.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError(f"Nivel de logging no válido: {log_level}")

    log_file = Path(log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    log_format = (
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    formatter = logging.Formatter(
        log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8",
        mode="a", # se añade al final la nueva info no sobreescribe
    )
    file_handler.setFormatter(formatter)

    logging.basicConfig(
        level=numeric_level,
        handlers=[console_handler, file_handler],
        force=True,
    )
