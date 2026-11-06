import pandas as pd
import pytest

from ventas_app.loader import CsvSalesRepository, DataLoadError

"""
Test que prueba que los csv se leen correctamnte
"""
def test_load_csv_correctamente(tmp_path):
    # Arrange
    csv_path = tmp_path / "ventas.csv"
    csv_path.write_text(
        "region,producto,unidades,precio_unitario\n"
        "Sur,Cable Kit,7,12.5\n",
        encoding="utf-8",
    )
    repository = CsvSalesRepository(csv_path)

    # Act
    frame = repository.load()

    # Assert
    assert len(frame) == 1
    assert frame.loc[0, "region"] == "Sur"
    assert frame.loc[0, "unidades"] == 7

"""
test que comprueba que si el csv no existe lanza error
por eso no se le declaran datos al csv
"""
def test_load_path_inexistente_lanza_error(tmp_path):
    # Arrange
    csv_path = tmp_path / "no_existe.csv"
    repository = CsvSalesRepository(csv_path)

    # Act + Assert
    with pytest.raises(DataLoadError):
        repository.load()
