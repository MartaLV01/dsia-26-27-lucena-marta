"""
Test que prueba el main
"""

import pandas as pd
import pytest

from books_app.cli import main


@pytest.fixture
def books_csv(tmp_path):
    """Crea un CSV temporal con un libro válido y otro inválido."""
    data = [
        {
            "book_id": 1,
            "goodreads_book_id": 101,
            "best_book_id": 101,
            "work_id": 1001,
            "books_count": 5,
            "isbn": "1234567890",
            "authors": "Autor Uno",
            "title": "Libro válido",
            "average_rating": 4.0,
            "ratings_count": 100,
        },
        {
            "book_id": 2,
            "goodreads_book_id": 102,
            "best_book_id": 102,
            "work_id": 1002,
            "books_count": 3,
            "isbn": None,
            "authors": "Autor Dos",
            "title": "Libro inválido",
            "average_rating": 7.0,
            "ratings_count": 50,
        },
    ]

    path = tmp_path / "books.csv"
    pd.DataFrame(data).to_csv(path, index=False)
    return path

""" Todo el flujo """
def test_cli_procesa_csv_y_muestra_metricas(
    books_csv, tmp_path, monkeypatch, capsys
):
    output = tmp_path / "salida" / "books_clean.csv"

    monkeypatch.setattr(
        "sys.argv",
        ["cli.py", "--input", str(books_csv), "--output", str(output)],
    )

    main()

    captured = capsys.readouterr()

    assert "Registros válidos: 1 | inválidos: 1" in captured.out
    assert "Valoración media: 4.00" in captured.out
    assert "Libro con más valoraciones: Libro válido" in captured.out
    assert output.exists()

    clean_df = pd.read_csv(output)
    assert len(clean_df) == 1
    assert clean_df.iloc[0]["title"] == "Libro válido"

""" error cuando el archivo de entrada no existe """
def test_cli_falla_si_no_existe_el_csv(tmp_path, monkeypatch, capsys):
    input_path = tmp_path / "no_existe.csv"
    output_path = tmp_path / "salida.csv"

    monkeypatch.setattr(
        "sys.argv",
        ["cli.py", "--input", str(input_path), "--output", str(output_path)],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    assert "Error:" in capsys.readouterr().out
    assert not output_path.exists()

""" error cuando el CSV no contiene las columnas """
def test_cli_falla_si_faltan_columnas(
    tmp_path, monkeypatch, capsys
):
    input_path = tmp_path / "incompleto.csv"
    output_path = tmp_path / "salida.csv"

    pd.DataFrame({"book_id": [1], "title": ["Libro"]}).to_csv(
        input_path, index=False
    )

    monkeypatch.setattr(
        "sys.argv",
        ["cli.py", "--input", str(input_path), "--output", str(output_path)],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    assert "Faltan columnas obligatorias" in capsys.readouterr().out
    assert not output_path.exists()