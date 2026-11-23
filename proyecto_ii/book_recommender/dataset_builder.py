
"""
Construcción del dataset maestro a partir de los datos validados.
"""

import logging
from pathlib import Path

import pandas as pd
from .tag_filter import build_tag_report 
# importación relativa porque ambos módulos están dentro de book_recommender


logger = logging.getLogger(__name__)  # LOGGING


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# donde quiero que se guarde el csv con los datos que realmente necesito
DEFAULT_OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "books_master.csv"
)

# Columnas de books.csv que conservaremos.
BOOK_COLUMNS = [
    "book_id",
    "goodreads_book_id",
    "title",
    "authors",
    "original_publication_year",
    "language_code",
    "average_rating",
    "ratings_count",
    "image_url",
    "small_image_url",
]

# Columnas necesarias para construir las etiquetas.
TAG_COLUMNS = [
    "goodreads_book_id",
    "tag_id",
    "count",
]

TAG_NAMES_COLUMNS = [
    "tag_id",
    "tag_name",
]



def build_master_dataset(
    validation_results: dict[str, dict[str, object]],
) -> pd.DataFrame:
    """
    Construye un dataset con una fila por libro y sus cinco etiquetas
    temáticas más frecuentes, conservando también los libros sin etiquetas.

    Args:
        validation_results: resultados devueltos por validate_all().

    Returns:
        DataFrame con los metadatos de los libros y sus cinco etiquetas.
    """
    logger.info("Iniciando construcción del dataset maestro")

    # Recuperar exclusivamente los DataFrames validados.
    books = validation_results["books"]["valid"]
    book_tags = validation_results["book_tags"]["valid"]
    tags = validation_results["tags"]["valid"]

    logger.info(
        "Datos de entrada: books=%s, book_tags=%s, tags=%s",
        len(books),
        len(book_tags),
        len(tags),
    )

    # Seleccionar los metadatos que necesitamos.
    master = books[BOOK_COLUMNS].copy()

    # Clasificar las etiquetas utilizando el módulo tag_filter.
    tag_report = build_tag_report(tags, book_tags)

    # Recuperar los nombres canónicos y su clasificación.
    tag_classifications = tag_report[
        ["tag_id", "canonical_tag", "classification"]
    ]

    # Relacionar las etiquetas de los libros con su clasificación.
    tag_data = book_tags[TAG_COLUMNS].merge(
        tag_classifications,
        on="tag_id",
        how="inner",
        validate="many_to_one",
    )

    # Conservar únicamente las etiquetas temáticas con frecuencia positiva.
    tag_data = tag_data[
        (tag_data["classification"] == "thematic")
        & (tag_data["count"] > 0)
    ].copy()

    # Agrupar variantes equivalentes y sumar sus frecuencias.
    tag_data = (
        tag_data.groupby(
            ["goodreads_book_id", "canonical_tag"],
            as_index=False,
        )["count"]
        .sum()
    )

    # Ordenar por libro, frecuencia y etiqueta.
    # El orden alfabético resuelve los empates de forma reproducible.
    tag_data = tag_data.sort_values(
        by=[
            "goodreads_book_id",
            "count",
            "canonical_tag",
        ],
        ascending=[
            True,
            False,
            True,
        ],
    )

    # Asignar una posición a cada etiqueta de cada libro.
    tag_data["tag_position"] = (
        tag_data.groupby("goodreads_book_id").cumcount() + 1
    )

    # Conservar únicamente las cinco primeras.
    top_tags = tag_data[
        tag_data["tag_position"] <= 5
    ].copy()

    # Transformar las etiquetas en columnas.
    top_tags = top_tags.pivot(
        index="goodreads_book_id",
        columns="tag_position",
        values="canonical_tag",
    )

    # Garantizar que siempre existan tag_1 hasta tag_5.
    top_tags = top_tags.rename(
        columns={
            position: f"tag_{position}"
            for position in range(1, 6)
        }
    )

    for position in range(1, 6):
        column = f"tag_{position}"

        if column not in top_tags.columns:
            top_tags[column] = pd.NA

    top_tags = top_tags.reset_index()
    top_tags.columns.name = None

    # Incorporar las etiquetas a todos los libros.
    # Los libros sin etiquetas temáticas también se conservan.
    master = master.merge(
        top_tags,
        on="goodreads_book_id",
        how="left",
        validate="one_to_one",
    )

    # Garantizar que existan las cinco columnas de etiquetas.
    for position in range(1, 6):
        column = f"tag_{position}"

        if column not in master.columns:
            master[column] = pd.NA

    logger.info(
        "Dataset maestro construido: books=%s, columns=%s, "
        "books_with_tags=%s",
        len(master),
        len(master.columns),
        master["tag_1"].notna().sum(),
    )

    return master



def save_master_dataset(
    dataset: pd.DataFrame,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> None:
    """
    Guarda el dataset maestro en formato CSV.

    Args:
        dataset: DataFrame que se quiere guardar.
        output_path: ruta donde se guardará el archivo.
    """
    output_path = Path(output_path)

    logger.info(  # LOGGING
        "Iniciando guardado del dataset maestro: path=%s, rows=%s",
        output_path,
        len(dataset),
    )

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dataset.to_csv(output_path, index=False)

    except Exception:
        logger.exception(  # LOGGING
            "Error al guardar el dataset maestro: path=%s",
            output_path,
        )
        raise

    logger.info(  # LOGGING
        "Dataset maestro guardado correctamente: path=%s, rows=%s",
        output_path,
        len(dataset),
    )
