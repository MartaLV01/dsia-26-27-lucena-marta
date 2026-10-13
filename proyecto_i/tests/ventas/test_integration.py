from pathlib import Path

import pytest

from ventas_app.loader import CsvSalesRepository
from ventas_app.validator import SalesValidator

"""
Este test utiliza el CSV real y comprueba el resultado del checkpoint: 140 filas válidas y 10 inválidas.
"""
@pytest.mark.integration
def test_integracion_csv_real_ventas():
    # Arrange
    ruta_proyecto = Path(__file__).resolve().parents[2]
    ruta_csv = ruta_proyecto / "data" / "ventas.csv"

    repository = CsvSalesRepository(ruta_csv)
    validator = SalesValidator()

    # Act
    frame = repository.load()
    valid_rows, valid_frame, invalid_frame = validator.split(frame)

    # Assert
    assert len(frame) == 150
    assert len(valid_rows) == 140
    assert len(valid_frame) == 140
    assert len(invalid_frame) == 10