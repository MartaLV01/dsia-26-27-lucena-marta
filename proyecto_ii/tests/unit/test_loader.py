
"""
Tests unitarios del módulo loader.
"""

import pandas as pd
import pytest

from book_recommender.loader import load_data


def test_load_data(tmp_path):
    """Comprueba que se cargan correctamente los cinco CSV."""

    # Crear cinco CSV temporales
    csv_files = {
        "books.csv": pd.DataFrame({"book_id": [1, 2]}),
        "ratings.csv": pd.DataFrame({"rating": [4, 5]}),
        "book_tags.csv": pd.DataFrame({"tag_id": [10, 20]}),
        "tags.csv": pd.DataFrame({"tag_name": ["fantasy", "romance"]}),
        "to_read.csv": pd.DataFrame({"user_id": [100, 200]}),
    }

    for filename, dataframe in csv_files.items():
        dataframe.to_csv(tmp_path / filename, index=False)

    # Cargar los archivos desde el directorio temporal
    datos = load_data(data_dir=tmp_path)

    # Comprobar que se han cargado los cinco datasets
    assert set(datos.keys()) == {
        "books",
        "ratings",
        "book_tags",
        "tags",
        "to_read",
    }

    # Comprobar que los DataFrames contienen datos
    for df in datos.values():
        assert not df.empty
        assert len(df.columns) > 0


def test_load_data_missing_files(tmp_path):
    """Comprueba que se produce un error si faltan los CSV."""

    with pytest.raises(FileNotFoundError, match="Faltan archivos CSV"):
        load_data(data_dir=tmp_path)

