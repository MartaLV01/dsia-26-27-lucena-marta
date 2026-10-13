
import pandas as pd
import pytest

from books_app.loader import CsvBooksRepository, DataLoadError


def test_load_csv_correctamente(tmp_path):
    """Carga un CSV válido y devuelve un DataFrame."""
    csv_path = tmp_path / "books.csv"
    csv_path.write_text(
        "book_id,title,isbn\n1,El principito,9780156012195\n",
        encoding="utf-8",
    )

    repository = CsvBooksRepository(csv_path)

    result = repository.load()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.loc[0, "title"] == "El principito"
    assert result.loc[0, "isbn"] == "9780156012195"
    assert isinstance(result["isbn"].dtype, pd.StringDtype)


def test_load_falla_si_el_archivo_no_existe(tmp_path):
    """Lanza DataLoadError si no existe el fichero."""
    csv_path = tmp_path / "no_existe.csv"
    repository = CsvBooksRepository(csv_path)

    with pytest.raises(DataLoadError, match="No existe el fichero"):
        repository.load()


def test_load_falla_si_el_csv_esta_mal_formado(tmp_path):
    """Lanza DataLoadError si pandas no puede interpretar el CSV."""
    csv_path = tmp_path / "books.csv"
    csv_path.write_text(
        'book_id,title\n1,"Título sin cerrar\n',
        encoding="utf-8",
    )
    repository = CsvBooksRepository(csv_path)

    with pytest.raises(DataLoadError, match="No se pudo cargar el CSV"):
        repository.load()
