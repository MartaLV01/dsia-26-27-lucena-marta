
"""
Preparación de las características textuales de los libros.

Combina título, autores y etiquetas en una nueva columna
llamada 'content'--> hacia esto inicialmente
Ahora solo usa las etiquetas ya que lo que queremos es un
    recomendador de libros por tematica, donde los autores 
    o el titulo no tengan tanto peso
para crear un texto que posteriormente utilizará el recomendador.
"""

import logging

import pandas as pd


logger = logging.getLogger(__name__)

# Columnas que contienen las etiquetas de cada libro.
TAG_COLUMNS = [
    "tag_1",
    "tag_2",
    "tag_3",
    "tag_4",
    "tag_5",
]


def prepare_book_features(books: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara las características textuales de los libros.

    Combina título, autores y etiquetas en una nueva columna
    llamada 'content'--> hacia esto inicialmente
    Ahora solo usa las etiquetas ya que lo que queremos es un
        recomendador de libros por tematica, donde los autores 
        o el titulo no tengan tanto peso

    Args:
        books: DataFrame con los datos del dataset maestro.

    Returns:
        DataFrame con una nueva columna 'content'.

    Raises:
        ValueError: si faltan columnas necesarias.
    """
    # required_columns = {"title", "authors", *TAG_COLUMNS}
    required_columns = set(TAG_COLUMNS)
    
    missing_columns = required_columns - set(books.columns)

    if missing_columns:
        raise ValueError(
            f"Faltan columnas necesarias para preparar las características: "
            f"{sorted(missing_columns)}"
        )

    logger.info(
        "Preparando características textuales: books=%s",
        len(books),
    )

    # Copiamos el DataFrame para no modificar el original.
    features = books.copy()

    # Sustituimos los valores nulos por cadenas vacías
    # No necesito estas dos ya que solo quiero buscar parecidos en cuanto a etiquetas
    #title = features["title"].fillna("").astype(str)
    #authors = features["authors"].fillna("").astype(str)

    tags = (
        features[TAG_COLUMNS]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
    )

    # Unimos título, autores y etiquetas.
    #features["content"] = (
    #    title + " " + authors + " " + tags
    #).str.replace(r"\s+", " ", regex=True).str.strip()
    # dado que solo quiero las etiquetas para mis predicciones
    features["content"] = (
        tags.str.replace(r"\s+", " ", regex=True).str.strip()
    )

    logger.info(
        "Características textuales preparadas: books=%s",
        len(features),
    )

    return features
