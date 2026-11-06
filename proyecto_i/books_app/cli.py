from pathlib import Path

from books_app.loader import CsvBooksRepository, BooksRepository, DataLoadError
from books_app.validator import BookValidator, ValidationError
from books_app.metrics import BooksMetrics

import argparse


def main() -> None:
    
    parser = argparse.ArgumentParser(
        description="Procesa los datos de los libros."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Ruta del CSV de entrada.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Ruta del CSV limpio de salida.",
    )

    args = parser.parse_args()

    try:
        # CARGAR LOS DATOS
        repo: BooksRepository = CsvBooksRepository(args.input)
        frame = repo.load()

        # VALIDAR LOS DATOS
        validator = BookValidator()
        records, clean_frame, errors = validator.split(frame)

        # GUARDAR LOS DATOS LIMPIOS
        args.output.parent.mkdir(parents=True, exist_ok=True)
        clean_frame.to_csv(args.output, index=False)

        #CALCULAR LAS METRICAS
        metrics = BooksMetrics()

        total = metrics.total_books(records)
        average = metrics.average_rating(records)
        most_rated = metrics.most_rated_book(records)

        print(f"Registros válidos: {len(records)} | inválidos: {len(errors)}")
        
        print(f"Valoración media: {average:.2f}")

        if most_rated is not None:
            print(f"Libro con más valoraciones: {most_rated.title}")
            print(f"Número de valoraciones: {most_rated.ratings_count}")
        else:
            print("No hay libros válidos para calcular las métricas.")

        print(f"CSV limpio guardado en: {args.output}")

    except (DataLoadError, ValidationError) as error:
        print(f"Error: {error}")
        raise SystemExit(1)


    
if __name__ == "__main__":
    main()