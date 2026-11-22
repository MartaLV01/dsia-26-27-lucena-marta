"""
Su responsabilidad será:
1. Preparar las características textuales.
2. Entrenar el recomendador.
3. Guardarlo en un único .joblib.
4. Permitir cargarlo posteriormente sin volver a entrenar.
"""


"""
Entrenamiento y persistencia del recomendador de libros.
"""

import logging
from pathlib import Path

import joblib
import pandas as pd

from book_recommender.features import prepare_book_features
from book_recommender.recommender import BookRecommender


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_MODEL_PATH = (
    PROJECT_ROOT / "artifacts" / "book_recommender.joblib"
)


def train_and_save_model(
    books: pd.DataFrame,
    output_path: Path = DEFAULT_MODEL_PATH,
) -> BookRecommender:
    """
    Prepara, entrena y guarda el recomendador.

    Args:
        books: DataFrame con el catálogo de libros.
        output_path: ruta donde guardar el modelo.

    Returns:
        Recomendador entrenado.
    """
    output_path = Path(output_path)

    logger.info("Iniciando entrenamiento del modelo.")

    # Preparar los textos de los libros.
    features = prepare_book_features(books)

    # Entrenar el recomendador.
    recommender = BookRecommender()
    recommender.fit(features)

    # Crear el directorio de destino si no existe.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Guardar toda la instancia en un único archivo.
    try:
        joblib.dump(recommender, output_path)
    except Exception:
        logger.exception("Error al guardar el modelo: path=%s", output_path)
        raise

    logger.info(
        "Modelo guardado correctamente: path=%s",
        output_path,
    )

    return recommender


def load_model(
    model_path: Path = DEFAULT_MODEL_PATH,
) -> BookRecommender:
    """
    Carga un recomendador previamente entrenado.

    Args:
        model_path: ruta del archivo joblib.

    Returns:
        Recomendador cargado.
    """
    model_path = Path(model_path)

    if not model_path.is_file():
        raise FileNotFoundError(
            f"No se encuentra el modelo: {model_path}"
        )

    logger.info("Cargando modelo: path=%s", model_path)

    try:
        recommender = joblib.load(model_path)
    except Exception:
        logger.exception("Error al cargar el modelo: path=%s", model_path)
        raise

    if not isinstance(recommender, BookRecommender):
        raise TypeError("El archivo no contiene un BookRecommender.")

    if not recommender.is_fitted_:
        raise ValueError("El recomendador guardado no está entrenado.")

    logger.info("Modelo cargado correctamente.")

    return recommender
