from pathlib import Path

from ventas_app.loader import CsvSalesRepository, SalesRepository, DataLoadError
from ventas_app.validator import SalesValidator, ValidationError
from ventas_app.metrics import SalesMetrics

import argparse


def main() -> None:
    
    parser = argparse.ArgumentParser(
        description="Procesa los datos de ventas."
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
        #data_path = Path(__file__).resolve().parent.parent / "data" / "ventas.csv"
        #repo: SalesRepository = CsvSalesRepository(data_path)
        repo: SalesRepository = CsvSalesRepository(args.input)
        frame = repo.load()

        # VALIDAR LOS DATOS
        validator = SalesValidator()
        records, clean_frame, errors = validator.split(frame)

        # GUARDAR LOS DATOS LIMPIOS
        args.output.parent.mkdir(parents=True, exist_ok=True)
        clean_frame.to_csv(args.output, index=False)

        #CALCULAR LAS METRICAS
        metrics = SalesMetrics()

        #frame = repo.load()
        #records, errors = validator.split(frame)
        print(f"Registros válidos: {len(records)} | inválidos: {len(errors)}")
        print("Importe por región:")
        for region, total in metrics.total_by_region(records).items():
            print(f"  {region}: {total:.2f}")

    except (DataLoadError, ValidationError) as error:
        print(f"Error: {error}")

    
if __name__ == "__main__":
    main()