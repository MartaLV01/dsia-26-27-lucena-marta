
from pathlib import Path

import pandas as pd

from book_recommender.logging_config import setup_logging
from book_recommender.tag_filter import build_tag_report


setup_logging()

tags = pd.read_csv("data/raw/tags.csv")
book_tags = pd.read_csv("data/raw/book_tags.csv")

report = build_tag_report(tags, book_tags)

output_path = Path("data/processed/tag_report.csv") # cada vez que esta file se ejecuta el archivo se sobreescribe
output_path.parent.mkdir(parents=True, exist_ok=True)

report.to_csv(output_path, index=False)

print("\nClasificación de etiquetas:")
print(report["classification"].value_counts())

print("\nPrimeras 30 etiquetas:")
print(report.head(30).to_string(index=False))

print(f"\nInforme guardado en: {output_path}")


# Etiquetas inciertas más frecuentes.
uncertain = report[
    report["classification"] == "uncertain"
]

print("\n50 etiquetas inciertas más frecuentes:")
print(
    uncertain.head(50)[
        ["tag_name", "total_assignments", "books_count"]
    ].to_string(index=False)
)

# Etiquetas inciertas que aparecen en muchos libros.
print("\n50 etiquetas inciertas presentes en más libros:")
print(
    uncertain.sort_values(
        "books_count", ascending=False
    ).head(50)[
        ["tag_name", "total_assignments", "books_count"]
    ].to_string(index=False)
)
