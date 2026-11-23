
"""
Interfaz de línea de comandos para ejecutar el pipeline.
"""

import argparse
import logging
from pathlib import Path

import pandas as pd

from book_recommender.dataset_builder import DEFAULT_OUTPUT_PATH
from book_recommender.loader import RAW_DATA_DIR
from book_recommender.logging_config import setup_logging
from book_recommender.pipeline import run_pipeline
from book_recommender.validator import ValidationError
from book_recommender.model_training import DEFAULT_MODEL_PATH

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    """
    Ejecuta el pipeline a partir de los argumentos recibidos.

    Args:
        argv: argumentos opcionales. Permite probar el CLI sin
              utilizar directamente los argumentos del terminal.

    Returns:
        0 si el pipeline termina correctamente, 1 si ocurre un error.
    """
    parser = argparse.ArgumentParser(
        description="Prepara el dataset maestro de Goodbooks-10k."
    )

    # uso --data-dir en vez de --input (como hice en proyecto_i) 
    # ya que lo que tengo es un direrctorio con varias files (5 csv, en data/raw)
    parser.add_argument(
        "--data-dir", 
        type=Path,
        default=RAW_DATA_DIR,
        help="Directorio que contiene los cinco CSV originales.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Ruta del CSV maestro de salida.",
    )

    parser.add_argument(
        "--model-output",
        type=Path,
        default=DEFAULT_MODEL_PATH,
        help="Ruta del archivo donde se guardará el modelo de recomendación.",
    )

    parser.add_argument(
        "--log-level",
        type=str.upper,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=None,
        help="Nivel de logging. Por defecto utiliza LOG_LEVEL o INFO.",
    )

    args = parser.parse_args(argv)

    # Configurar el logging antes de ejecutar el pipeline.
    setup_logging(log_level=args.log_level)

    try:
        run_pipeline(
            data_dir=args.data_dir,
            output_path=args.output,
            model_path=args.model_output,
        )

        logger.info("Ejecución del CLI finalizada correctamente.")
        return 0

    except (
        FileNotFoundError,
        ValidationError,
        OSError,
        pd.errors.ParserError,
        UnicodeDecodeError,
    ) as error:
        logger.error("No se ha podido ejecutar el pipeline: %s", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
