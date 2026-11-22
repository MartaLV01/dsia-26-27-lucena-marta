
"""
Coordina el proceso completo de preparación de los datos.
1. Carga los csv
2. Valida los datos
3. construye el dataset "maestro"
4. Guarda el nuevo dataset, el "maestro"
5. Calcula las metricas
6. Entrena y guarda el modelo para recomendar libros (recomendador)
7. Evalua el modelo con las metricas
"""

import json
import logging
from pathlib import Path
from time import perf_counter
from datetime import datetime

from book_recommender.evaluation import evaluate_recommender
from book_recommender.loader import load_data
from book_recommender.validator import DataValidator
from book_recommender.dataset_builder import (
    build_master_dataset,
    save_master_dataset,
)
from book_recommender.metrics import BooksMetrics
from book_recommender.model_training import train_and_save_model


logger = logging.getLogger(__name__)

# Configuración de la evaluación
N_QUERIES = 20
N_RECOMMENDATIONS = 5
RANDOM_STATE = 42

def _save_evaluation_results(
    evaluation_results: dict,
    output_path: Path,
) -> Path:
    """
    Guarda los resultados de evaluación en un archivo JSON

    Se genera uno por ejecucion/dia. En un mismo dia ese archivo se sobreescribe
    """
    # Con este comando el archivo se sobrescribe, da igual que se ejecute otro dia
    # evaluation_path = output_path.parent / "evaluation_results.json"
    # De la actual menera se crea un archivo por ejecucion/dia
    # en un mismo dia el archivo se sobreescribe
    current_date = datetime.now().strftime("%Y-%m-%d")
    evaluation_path = (output_path.parent / f"evaluation_results_{current_date}.json")

    with evaluation_path.open("w", encoding="utf-8") as file:
        json.dump(
            evaluation_results,
            file,
            indent=4,
            ensure_ascii=False,
        )

    logger.info(
        "Resultados de evaluación guardados en: %s",
        evaluation_path,
    )

    return evaluation_path


def run_pipeline(
    data_dir: Path,
    output_path: Path,
    model_path: Path | None = None,
) -> dict[str, object]:
    """
    Ejecuta la carga, validación, construcción, análisis de los datos, entrenamiento del modelo
    y evalua el modelo con las metricas

    Args:
        data_dir: carpeta que contiene los cinco CSV originales.
        output_path: ruta donde se guardará el dataset maestro.
        model_path: ruta opcional donde se guardará el recomendador.

    Returns:
        Diccionario con el dataset maestro, los resultados de validación,
        las métricas calculadas, el recomendador entrenado, 
        los resultados de evaluación y la ruta del archivo generado
    """
    start_time = perf_counter()

    data_dir = Path(data_dir)
    output_path = Path(output_path)

    logger.info(
        "Iniciando pipeline: data_dir=%s, output_path=%s",
        data_dir,
        output_path,
    )

    # 1. Cargar los datos
    logger.info("Etapa 1/7: carga de datos")
    datasets = load_data(data_dir)

    # 2. Validar los datos
    logger.info("Etapa 2/7: validación de datos")
    validator = DataValidator()
    validation_results = validator.validate_all(datasets)

    # Resumen de registros inválidos.
    for name, result in validation_results.items():
        invalid_count = len(result["invalid"])

        if invalid_count > 0:
            logger.warning(
                "Se han descartado registros inválidos: "
                "dataset=%s, count=%s",
                name,
                invalid_count,
            )

    # 3. Construir el dataset maestro
    logger.info("Etapa 3/7: construcción del dataset maestro")
    master_dataset = build_master_dataset(validation_results)

    # 4. Guardar el dataset maestro
    logger.info("Etapa 4/7: guardado del dataset maestro")
    save_master_dataset(master_dataset, output_path)

    # 5. Calcular métricas sobre los libros válidos
    logger.info("Etapa 5/7: cálculo de métricas")
    metrics_calculator = BooksMetrics()
    valid_books = validation_results["books"]["valid"]

    metrics = {
        "total_books": metrics_calculator.total_books(valid_books),
        "average_rating": metrics_calculator.average_rating(valid_books),
        "most_rated_book": metrics_calculator.most_rated_book(valid_books),
    }

    most_rated = metrics["most_rated_book"]

    most_rated_title = (
        most_rated["title"]
        if most_rated is not None
        else None
    )

    logger.info(
        "Métricas calculadas: total_books=%s, average_rating=%.4f, "
        "most_rated_book=%s",
        metrics["total_books"],
        metrics["average_rating"],
        most_rated_title,
    )

    # 6. Entrenar y guardar el recomendador
    logger.info("Etapa 6/7: entrenamiento del recomendador")

    if model_path is None:
        recommender = train_and_save_model(master_dataset)
    else:
        recommender = train_and_save_model( 
            master_dataset,
            output_path=model_path,
        )

    # 7. Evaluar el recomendador
    logger.info("Etapa 7/7: evaluación del recomendador")

    # Variables como globales para una mas facil modificacion
    evaluation_results = evaluate_recommender(
        recommender=recommender,
        n_queries=N_QUERIES,
        n_recommendations=N_RECOMMENDATIONS,
        random_state=RANDOM_STATE,
    )

    # Guardar resultados
    evaluation_path = _save_evaluation_results(
        evaluation_results,
        output_path,
    )

    # Registrar resultados en los logs
    for query_type, results in evaluation_results.items():
        logger.info(
            "Evaluación (%s): "
            "solicitadas=%s, completadas=%s, fallidas=%s, "
            "similitud_media=%s, diversidad=%s, cobertura=%s",
            query_type,
            results["queries_requested"],
            results["queries_succeeded"],
            results["queries_failed"],
            results["average_similarity"],
            results["intra_list_diversity"],
            results["catalog_coverage"],
        )

        for error in results["errors"]:
            logger.warning(
                "Error en evaluación: tipo=%s, consulta=%s, mensaje=%s",
                query_type,
                error["query_number"],
                error["message"],
            )


    elapsed_time = perf_counter() - start_time

    logger.info(
        "Pipeline completado correctamente: books=%s, duration=%.2f segundos",
        len(master_dataset),
        elapsed_time,
    )

    return {
        "master_dataset": master_dataset,
        "validation_results": validation_results,
        "metrics": metrics,
        "output_path": output_path,
        "recommender": recommender,
        "evaluation_results": evaluation_results,
        "evaluation_path": evaluation_path,
    }
