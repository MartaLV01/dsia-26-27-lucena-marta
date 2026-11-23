
"""
Generación y evaluación de consultas para el recomendador de libros.
"""

import numpy as np

from book_recommender.recommender import BookRecommender
from book_recommender.metrics import RecommenderMetrics

def generate_evaluation_queries(
    recommender: BookRecommender,
    n_queries: int = 20,
    random_state: int = 42,
) -> dict[str, list[dict]]:
    """
    Genera consultas de evaluación a partir del catálogo del recomendador

    Se generan tres grupos:
    - Consultas basadas en libros
    - Consultas basadas en etiquetas
    - Consultas combinadas

    Args:
        recommender: Recomendador previamente entrenado
        n_queries: Número de consultas por grupo
        random_state: Semilla para garantizar reproducibilidad

    Returns:
        Diccionario con los tres grupos de consultas
    """

    if not recommender.is_fitted_:
        raise RuntimeError("El recomendador todavía no está entrenado")

    if n_queries < 1:
        raise ValueError("El número de consultas debe ser positivo")

    rng = np.random.default_rng(random_state)

    books = recommender.books_

    # Seleccionamos libros que tengan contenido temático
    books_with_content = books[
        books["content"].fillna("").str.strip() != ""
    ]

    if len(books_with_content) < n_queries:
        raise ValueError("No hay suficientes libros con contenido para generar las consultas de evaluación")

    # Recuperamos las etiquetas originales del catálogo
    tag_columns = [
        column for column in books.columns
        if column.startswith("tag_")
    ]

    available_tags = sorted({
        str(tag).strip()
        for column in tag_columns
        for tag in books[column].dropna()
        if str(tag).strip()
    })

    if not available_tags:
        raise ValueError("El catálogo no contiene etiquetas disponibles")

    # Comprobamos qué etiquetas reconoce realmente TF-IDF
    usable_tags = [
        tag for tag in available_tags
        if recommender.vectorizer.transform([tag]).nnz > 0
    ]

    if not usable_tags:
        raise ValueError("Ninguna etiqueta del catálogo está presente en el vocabulario del recomendador")

    # Seleccionamos libros diferentes de forma reproducible
    selected_books = rng.choice(
        books_with_content["book_id"].to_numpy(),
        size=n_queries,
        replace=False,
    )

    # Seleccionamos etiquetas de forma reproducible
    selected_tags = rng.choice(
        usable_tags,
        size=n_queries,
        replace=len(usable_tags) < n_queries,
    )

    book_queries = [
        {"book_ids": [int(book_id)]}
        for book_id in selected_books
    ]

    tag_queries = [
        {"tags": [str(tag)]}
        for tag in selected_tags
    ]

    combined_queries = [
        {
            "book_ids": [int(book_id)],
            "tags": [str(tag)],
        }
        for book_id, tag in zip(selected_books, selected_tags)
    ]

    return {
        "book_queries": book_queries,
        "tag_queries": tag_queries,
        "combined_queries": combined_queries,
    }


def evaluate_recommender(
    recommender: BookRecommender,
    n_queries: int = 20,
    n_recommendations: int = 5,
    random_state: int = 42,
) -> dict:
    """
    Evalúa el recomendador utilizando consultas generadas
    dinámicamente a partir de su propio catálogo

    Evalúa tres modalidades:
    - Consultas basadas en libros
    - Consultas basadas en etiquetas
    - Consultas combinadas

    Args:
        recommender: Recomendador previamente entrenado
        n_queries: Número de consultas por grupo
        n_recommendations: Numero de recomendaciones
        random_state: Semilla para garantizar reproducibilidad

    Returns:
        Devuelve las métricas y un registro de los errores

    """
    queries_by_type = generate_evaluation_queries(
        recommender=recommender,
        n_queries=n_queries,
        random_state=random_state,
    )

    metrics_calculator = RecommenderMetrics()
    evaluation_results = {}

    for query_type, queries in queries_by_type.items():
        recommendations_list = []
        similarities = []
        diversities = []
        errors = []

        for index, query in enumerate(queries, start=1):
            try:
                recommendations = recommender.recommend(
                    **query,
                    n_recommendations=n_recommendations,
                )

                recommendations_list.append(recommendations)

                similarities.append(
                    metrics_calculator.average_similarity(
                        recommendations
                    )
                )

                diversities.append(
                    metrics_calculator.intra_list_diversity(
                        recommendations,
                        recommender,
                    )
                )

            except (ValueError, RuntimeError, KeyError) as error:
                errors.append({
                    "query_number": index,
                    "message": str(error),
                })

        successful_queries = len(recommendations_list)
        failed_queries = len(errors)

        if successful_queries > 0:
            average_similarity = float(np.mean(similarities))
            intra_list_diversity = float(np.mean(diversities))

            catalog_coverage = metrics_calculator.catalog_coverage(
                recommendations_list,
                catalog_size=len(recommender.books_),
            )
        else:
            average_similarity = None
            intra_list_diversity = None
            catalog_coverage = None

        evaluation_results[query_type] = {
            "queries_requested": len(queries),
            "queries_succeeded": successful_queries,
            "queries_failed": failed_queries,
            "average_similarity": average_similarity,
            "intra_list_diversity": intra_list_diversity,
            "catalog_coverage": catalog_coverage,
            "errors": errors,
        }

    return evaluation_results
