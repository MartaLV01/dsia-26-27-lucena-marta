
"""
Tests de la interfaz de línea de comandos (CLI).
"""

from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

from book_recommender import cli
from book_recommender.validator import ValidationError


def test_main_uses_default_paths(monkeypatch):
    """Comprueba que se utilizan las rutas predeterminadas."""
    mock_pipeline = Mock()
    mock_logging = Mock()

    monkeypatch.setattr(cli, "run_pipeline", mock_pipeline)
    monkeypatch.setattr(cli, "setup_logging", mock_logging)

    result = cli.main([])

    assert result == 0

    mock_logging.assert_called_once_with(log_level=None)
    mock_pipeline.assert_called_once_with(
        data_dir=cli.RAW_DATA_DIR,
        output_path=cli.DEFAULT_OUTPUT_PATH,
        model_path=cli.DEFAULT_MODEL_PATH,
    )


def test_main_uses_custom_paths(monkeypatch, tmp_path):
    """Comprueba que el CLI acepta rutas personalizadas."""
    mock_pipeline = Mock()
    mock_logging = Mock()

    monkeypatch.setattr(cli, "run_pipeline", mock_pipeline)
    monkeypatch.setattr(cli, "setup_logging", mock_logging)

    data_dir = tmp_path / "raw"
    output_path = tmp_path / "processed" / "books_master.csv"

    result = cli.main([
        "--data-dir", str(data_dir),
        "--output", str(output_path),
    ])

    assert result == 0

    mock_pipeline.assert_called_once_with(
        data_dir=data_dir,
        output_path=output_path,
        model_path=cli.DEFAULT_MODEL_PATH,
    )


def test_main_configures_debug_logging(monkeypatch):
    """Comprueba que se configura correctamente el nivel DEBUG."""
    mock_pipeline = Mock()
    mock_logging = Mock()

    monkeypatch.setattr(cli, "run_pipeline", mock_pipeline)
    monkeypatch.setattr(cli, "setup_logging", mock_logging)

    result = cli.main(["--log-level", "DEBUG"])

    assert result == 0
    mock_logging.assert_called_once_with(log_level="DEBUG")


def test_main_converts_log_level_to_uppercase(monkeypatch):
    """Comprueba que el nivel de logging se convierte a mayúsculas."""
    mock_pipeline = Mock()
    mock_logging = Mock()

    monkeypatch.setattr(cli, "run_pipeline", mock_pipeline)
    monkeypatch.setattr(cli, "setup_logging", mock_logging)

    result = cli.main(["--log-level", "debug"])

    assert result == 0
    mock_logging.assert_called_once_with(log_level="DEBUG")


@pytest.mark.parametrize(
    "error",
    [
        FileNotFoundError("No se encuentra el archivo"),
        ValidationError("Error de validación"),
        OSError("Error de lectura o escritura"),
        pd.errors.ParserError("Error al interpretar el CSV"),
        UnicodeDecodeError("utf-8", b"abc", 0, 1, "error de codificación"),
    ],
)
def test_main_returns_one_when_pipeline_fails(monkeypatch, error):
    """Comprueba que los errores del pipeline devuelven código 1."""
    mock_pipeline = Mock(side_effect=error)
    mock_logging = Mock()

    monkeypatch.setattr(cli, "run_pipeline", mock_pipeline)
    monkeypatch.setattr(cli, "setup_logging", mock_logging)

    result = cli.main([])

    assert result == 1
    mock_pipeline.assert_called_once()
