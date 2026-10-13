from pathlib import Path
from typing import Protocol

import pandas as pd


class DataLoadError(Exception):
    """Error al cargar datos de origen."""

class BooksRepository(Protocol):
    """Abstracción de lectura (Dependency Inversion)."""

    def load(self) -> pd.DataFrame: ...

class CsvBooksRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> pd.DataFrame:
        if not self._path.exists():
            raise DataLoadError(f"No existe el fichero: {self._path}")
        try:
            return pd.read_csv(self._path, dtype={"isbn": "string"}) #esto hace que el isbn se lea como string
        except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
            raise DataLoadError(f"No se pudo cargar el CSV: {self._path}") from exc