
"""
Carga los CSV necesarios para la aplicación.
"""

import logging
from pathlib import Path

import pandas as pd


logger = logging.getLogger(__name__)

# Ruta raíz del proyecto: proyecto_ii/
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Carpeta que contiene los CSV originales
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# Archivos necesarios para ejecutar el proyecto
# name: filename
REQUIRED_FILES = {
    "books": "books.csv",
    "ratings": "ratings.csv",
    "book_tags": "book_tags.csv",
    "tags": "tags.csv",
    "to_read": "to_read.csv",
}


def load_data(data_dir: Path = RAW_DATA_DIR) -> dict[str, pd.DataFrame]:
    """
    Carga los cinco archivos CSV originales de Goodbooks-10k.

    Args:
        data_dir: carpeta donde se encuentran los archivos CSV.

    Returns:
        Diccionario con un DataFrame para cada archivo.

    Raises:
        FileNotFoundError: si falta alguno de los archivos.
    """
    data_dir = Path(data_dir)

    logger.info("Iniciando carga de datos desde %s", data_dir)

    # Comprobar que existen todos los archivos necesarios
    missing_files = [
        filename
        for filename in REQUIRED_FILES.values()
        if not (data_dir / filename).is_file()
    ]

    if missing_files:
        missing = ", ".join(missing_files)

        logger.error(
            "Faltan archivos CSV en %s: %s",
            data_dir,
            missing,
        )

        raise FileNotFoundError(
            f"Faltan archivos CSV en {data_dir}: {missing}"
        )

    # Cargar los archivos
    data = {}

    for name, filename in REQUIRED_FILES.items():
        file_path = data_dir / filename

        try:
            data[name] = pd.read_csv(file_path)

        except (OSError, UnicodeDecodeError, pd.errors.ParserError):
            logger.exception(
                "Error al leer el archivo %s",
                file_path,
            )
            raise

        logger.info(
            "Archivo cargado: name=%s, rows=%s",
            name,
            len(data[name]),
        )

    logger.info(
        "Carga completada: files=%s",
        len(data),
    )

    return data
