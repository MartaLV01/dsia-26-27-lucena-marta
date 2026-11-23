import pandas as pd
import pytest

from ventas_app.validator import SalesValidator

"""
test que comprueba que se hace la separacion de valido/invalido
"""
def test_separa_filas_validas_e_invalidas():
    # Arrange
    frame = pd.DataFrame({
        "region": ["Sur", "Norte"],
        "producto": ["Cable", "Ratón"],
        "unidades": [2, 0],
        "precio_unitario": [10, 5],
    })
    validator = SalesValidator()

    # Act
    valid_rows, valid_frame, invalid_frame = validator.split(frame)

    # Assert
    assert len(valid_rows) == 1
    assert len(valid_frame) == 1
    assert len(invalid_frame) == 1
    assert valid_rows[0].product == "Cable"

"""
se parametriza para reliazar el test siguiente varias veces
se comprueba con valores nulos, negativos y =0
Tanto para el precio como para las unidades
"""
@pytest.mark.parametrize(
    "unidades, precio_unitario",
    [
        (0, 10),       # Unidades iguales a cero
        (-1, 10),      # Unidades negativas
        (None, 10),    # Unidades nulas
        (2, 0),        # Precio igual a cero
        (2, -1),       # Precio negativo
        (2, None),     # Precio nulo
    ],
)
def test_rechaza_unidades_o_precios_invalidos(unidades, precio_unitario):
    # Arrange
    frame = pd.DataFrame({
        "region": ["Sur"],
        "producto": ["Cable"],
        "unidades": [unidades],
        "precio_unitario": [precio_unitario],
    })
    validator = SalesValidator()

    # Act
    valid_rows, valid_frame, invalid_frame = validator.split(frame)

    # Assert
    assert len(valid_rows) == 0
    assert len(valid_frame) == 0
    assert len(invalid_frame) == 1