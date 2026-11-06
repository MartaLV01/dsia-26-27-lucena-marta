import pandas as pd

from ventas_app.cli import main

"""
Test que prueba el main
"""
def test_cli_procesa_csv_y_genera_salida(tmp_path, monkeypatch):
    # Arrange
    input_path = tmp_path / "entrada.csv"
    output_path = tmp_path / "salida.csv"

    input_path.write_text(
        "region,producto,unidades,precio_unitario\n"
        "Sur,Cable,2,10\n"
        "Norte,Raton,0,5\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "cli",
            "--input", str(input_path),
            "--output", str(output_path),
        ],
    )

    # Act
    main()

    # Assert
    assert output_path.exists()

    resultado = pd.read_csv(output_path)
    assert len(resultado) == 1
    assert resultado.iloc[0]["producto"] == "Cable"