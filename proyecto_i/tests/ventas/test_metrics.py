import pytest

from ventas_app.metrics import SalesMetrics
from ventas_app.validator import SalesRecord

"""
test que comprueba total by region
"""
def test_calcula_total_por_region():
    # Arrange
    records = [
        SalesRecord("Sur", "Cable", 2, 10),
        SalesRecord("Sur", "Ratón", 3, 5),
        SalesRecord("Norte", "Teclado", 1, 20),
    ]
    metrics = SalesMetrics()

    # Act
    resultado = metrics.total_by_region(records)

    # Assert
    assert resultado == {
        "Sur": 35.0,
        "Norte": 20.0,
    }