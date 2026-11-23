
"""
Comprueba la calidad de los datos
Validación de los datasets de Goodbooks-10k.
"""

import logging
import pandas as pd
from urllib.parse import urlparse


logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Error de estructura en los datos que impide realizar la validación."""


# Columnas esperadas en books.csv
REQUIRED_BOOK_COLUMNS = {
    "book_id",
    "goodreads_book_id",
    "best_book_id",
    "work_id",
    "books_count",
    "isbn",
    "isbn13",
    "authors",
    "original_publication_year",
    "original_title",
    "title",
    "language_code",
    "average_rating",
    "ratings_count",
    "work_ratings_count",
    "work_text_reviews_count",
    "ratings_1",
    "ratings_2",
    "ratings_3",
    "ratings_4",
    "ratings_5",
    "image_url",
    "small_image_url",
}

# Columnas que deben contener números enteros positivos
# no se permite el 0
POSITIVE_INTEGER_COLUMNS = [
    "book_id",
    "goodreads_book_id",
    "best_book_id",
    "work_id",
    "books_count",
]

# Columnas que deben contener números enteros no negativos
# se permite el 0
NON_NEGATIVE_INTEGER_COLUMNS = [
    "ratings_count",
    "work_ratings_count",
    "work_text_reviews_count",
    "ratings_1",
    "ratings_2",
    "ratings_3",
    "ratings_4",
    "ratings_5",
]

# Para ratings.csv
REQUIRED_RATING_COLUMNS = {
    "user_id",
    "book_id",
    "rating",
}

# Para tags.csv
REQUIRED_TAG_COLUMNS = {
    "tag_id",
    "tag_name",
}

# para book_tags
REQUIRED_BOOK_TAG_COLUMNS = {
    "goodreads_book_id",
    "tag_id",
    "count",
}

# para to_read.csv
REQUIRED_TO_READ_COLUMNS = {
    "user_id",
    "book_id",
}

# se indica que datasets se necesitan
REQUIRED_DATASETS = {
    "books",
    "ratings",
    "book_tags",
    "tags",
    "to_read",
}

def is_valid_image_url(value: object) -> bool:
    """
    Comprueba que una URL de imagen tenga un formato HTTP o HTTPS válido.

    Los valores nulos se consideran válidos porque la URL es opcional.
    """
    if pd.isna(value):
        return True

    if not isinstance(value, str):
        return False

    # si no lo cumple, no se para la ejecucion si no que devuelve False
    try:
        parsed = urlparse(value.strip())
    except ValueError:
        return False

    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.netloc)
    )

class DataValidator:
    """Valida la estructura y la calidad de los datasets."""

    def validate_books(self, frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
        """
        Valida el contenido de books.csv.

        Returns:
            Una tupla con:
            - DataFrame de filas válidas.
            - DataFrame de filas inválidas.
            - Lista con los errores detectados.

        Raises:
            ValidationError: si faltan columnas necesarias.
        """
        missing_columns = REQUIRED_BOOK_COLUMNS - set(frame.columns)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValidationError(
                f"Faltan columnas obligatorias en books.csv: {missing}"
            )

        work = frame.copy()

        # Normalizar los campos opcionales vacíos.
        # Pasa como valores nulos aquellas columnas que puedan ser vacias
        # han recibido un "" o " "  
        optional_columns = [
            "original_publication_year",
            "language_code",
            "image_url",
            "small_image_url",
        ]

        for column in optional_columns:
            work[column] = work[column].replace(
                r"^\s*$",
                pd.NA,
                regex=True,
            )

        # Una mask (máscara) es una estructura de valores booleanos
        # (True o False) que utilizamos para seleccionar filas de un DataFrame.
        valid_mask = pd.Series(True, index=work.index) # consideramos todas las filas válidas.
        errors = []

        def apply_rule(mask: pd.Series, message: str) -> None:
            """Aplica una regla y registra cuántas filas la incumplen."""
            nonlocal valid_mask 
            # con nonlocal se le dice a python que 
            # no cree esta variable si no que use la de
            # "fuera" (la creada fuera de esta def)

            mask = mask.fillna(False)
            invalid_count = int((~mask).sum())

            if invalid_count > 0:
                errors.append(f"{message}: {invalid_count} filas")

            valid_mask &= mask

        # Comprobar que las columnas enteras contienen números enteros.
        integer_columns = (
            POSITIVE_INTEGER_COLUMNS + NON_NEGATIVE_INTEGER_COLUMNS
        )

        for column in integer_columns:
            work[column] = pd.to_numeric(
                work[column], errors="coerce"
            )

            numeric_values = work[column]

            apply_rule(
                numeric_values.notna()
                & numeric_values.mod(1).eq(0),
                f"{column} debe contener números enteros",
            )

        # Comprobar que los identificadores y books_count son positivos.
        for column in POSITIVE_INTEGER_COLUMNS:
            apply_rule(
                work[column] > 0,
                f"{column} debe ser mayor que cero",
            )

        # Comprobar que los contadores no son negativos.
        for column in NON_NEGATIVE_INTEGER_COLUMNS:
            apply_rule(
                work[column] >= 0,
                f"{column} no puede ser negativo",
            )

        # Comprobar el rango de average_rating.
        work["average_rating"] = pd.to_numeric(
            work["average_rating"], errors="coerce"
        )

        apply_rule(
            work["average_rating"].notna()
            & work["average_rating"].between(0, 5),
            "average_rating debe estar entre 0 y 5",
        )

        # El año es opcional, pero si aparece debe ser numérico.
        original_year = work["original_publication_year"]
        numeric_year = pd.to_numeric(original_year, errors="coerce")

        apply_rule(
            original_year.isna() | numeric_year.notna(),
            "original_publication_year debe ser numérico o nulo",
        )

        work["original_publication_year"] = numeric_year

        # El idioma es opcional, pero si aparece debe ser texto no vacío.
        apply_rule(
            work["language_code"].map(
                lambda value: (
                    pd.isna(value)
                    or (
                        isinstance(value, str)
                        and bool(value.strip())
                    )
                )
            ),
            "language_code debe ser texto o nulo",
        )

        # Las URL son opcionales, pero si aparecen deben ser válidas.
        for column in ["image_url", "small_image_url"]:
            apply_rule(
                work[column].map(is_valid_image_url),
                f"{column} debe ser una URL HTTP/HTTPS válida o nula",
            )

        # Comprobar que autores y títulos no están vacíos.
        for column in ["authors", "title"]:
            text_values = work[column].astype("string").str.strip()

            apply_rule(
                work[column].notna()
                & text_values.ne("").fillna(False),
                f"{column} no puede estar vacío",
            )

        # Comprobar que los identificadores principales son únicos.
        for column in ["book_id", "goodreads_book_id"]:
            # ~work[column].duplicated(keep=False),
            # Esto marca como False todas las filas que tienen un 
            # identificador repetido, incluidas la primera aparición y las siguientes.
            apply_rule(
                ~work[column].duplicated(keep=False),
                f"{column} no puede estar duplicado",
            )

        # utilizamos la máscara para separar los datos
        # Obtenemos 2 DataFrames: uno con las filas válidas y otro con las inválidas.
        valid_df = work.loc[valid_mask].copy()
        invalid_df = work.loc[~valid_mask].copy()

        return valid_df, invalid_df, errors


    def validate_ratings(self, frame: pd.DataFrame,
        books: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
        """
        Valida el contenido de ratings.csv.

        Args:
            frame: DataFrame con las valoraciones.
            books: DataFrame con los libros válidos.

        Returns:
            Una tupla con:
            - DataFrame de valoraciones válidas.
            - DataFrame de valoraciones inválidas.
            - Lista con los errores detectados.

        Raises:
            ValidationError: si faltan columnas necesarias.
        """
        missing_columns = REQUIRED_RATING_COLUMNS - set(frame.columns)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValidationError(
                f"Faltan columnas obligatorias en ratings.csv: {missing}"
            )

        if "book_id" not in books.columns:
            raise ValidationError("El DataFrame de libros debe contener book_id")

        work = frame.copy()
        valid_mask = pd.Series(True, index=work.index)
        errors = []

        def apply_rule(mask: pd.Series, message: str) -> None:
            """Aplica una regla y registra cuántas filas la incumplen."""
            nonlocal valid_mask

            mask = mask.fillna(False)
            invalid_count = int((~mask).sum())

            if invalid_count > 0:
                errors.append(f"{message}: {invalid_count} filas")

            valid_mask &= mask

        # Comprobar que los identificadores son enteros.
        for column in ["user_id", "book_id"]:
            work[column] = pd.to_numeric(
                work[column], errors="coerce"
            )

            apply_rule(
                work[column].notna()
                & work[column].mod(1).eq(0),
                f"{column} debe contener números enteros",
            )

            apply_rule(
                work[column] > 0,
                f"{column} debe ser mayor que cero",
            )

        # Comprobar que rating es un número entero.
        work["rating"] = pd.to_numeric(
            work["rating"], errors="coerce"
        )

        apply_rule(
            work["rating"].notna()
            & work["rating"].mod(1).eq(0),
            "rating debe contener números enteros",
        )

        # Comprobar que las valoraciones están entre 1 y 5.
        apply_rule(
            work["rating"].between(1, 5),
            "rating debe estar entre 1 y 5",
        )

        # Comprobar que cada usuario valora un libro una sola vez.
        apply_rule(
            ~work.duplicated(
                subset=["user_id", "book_id"],
                keep=False,
            ),
            "La combinación user_id + book_id no puede repetirse",
        )

        # Comprobar que todos los libros existen.
        # Convertimos los identificadores a un conjunto (set)
        valid_book_ids = set(books["book_id"].dropna())

        apply_rule(
            work["book_id"].isin(valid_book_ids),
            "book_id no existe en books.csv",
        )

        valid_df = work.loc[valid_mask].copy()
        invalid_df = work.loc[~valid_mask].copy()

        return valid_df, invalid_df, errors

    def validate_tags(self, frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
        """
        Valida el contenido de tags.csv.

        Returns:
            DataFrame de filas válidas, DataFrame de filas inválidas
            y lista de errores detectados.
        """
        missing_columns = REQUIRED_TAG_COLUMNS - set(frame.columns)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValidationError(
                f"Faltan columnas obligatorias en tags.csv: {missing}"
            )

        work = frame.copy()
        valid_mask = pd.Series(True, index=work.index)
        errors = []

        def apply_rule(mask: pd.Series, message: str) -> None:
            nonlocal valid_mask

            mask = mask.fillna(False)
            invalid_count = int((~mask).sum())

            if invalid_count > 0:
                errors.append(f"{message}: {invalid_count} filas")

            valid_mask &= mask

        # Comprobar que tag_id contiene números enteros positivos.
        work["tag_id"] = pd.to_numeric(
            work["tag_id"], errors="coerce"
        )

        apply_rule(
            work["tag_id"].notna()
            & work["tag_id"].mod(1).eq(0),
            "tag_id debe contener números enteros",
        )

        apply_rule(
            work["tag_id"] > 0,
            "tag_id debe ser mayor que cero",
        )

        # Comprobar que tag_name no está vacío.
        text_values = work["tag_name"].astype("string").str.strip() # strip elimina espacios exteriores

        apply_rule(
            work["tag_name"].notna()
            & text_values.ne("").fillna(False),
            "tag_name no puede estar vacío",
        )

        # Normalizar los nombres para detectar duplicados.
        # casefold() parecido a lower() pero mas "agresivo" 
        # tiene transformaciones de mas caracteres
        normalized_names = (
            text_values.str.casefold()
        )

        apply_rule(
            ~normalized_names.duplicated(keep=False),
            "tag_name no puede estar duplicado",
        )

        # Comprobar que tag_id es único.
        apply_rule(
            ~work["tag_id"].duplicated(keep=False),
            "tag_id no puede estar duplicado",
        )

        valid_df = work.loc[valid_mask].copy()
        invalid_df = work.loc[~valid_mask].copy()

        return valid_df, invalid_df, errors

    def validate_book_tags( self, frame: pd.DataFrame,
        books: pd.DataFrame, tags: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
        """
        Valida las relaciones entre libros y etiquetas.

        Comprueba los tipos, rangos, duplicados y referencias
        a libros y etiquetas existentes.
        """
        missing_columns = REQUIRED_BOOK_TAG_COLUMNS - set(frame.columns)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValidationError(
                f"Faltan columnas obligatorias en book_tags.csv: {missing}"
            )

        if "goodreads_book_id" not in books.columns:
            raise ValidationError(
                "El DataFrame de libros debe contener goodreads_book_id"
            )

        if "tag_id" not in tags.columns:
            raise ValidationError(
                "El DataFrame de etiquetas debe contener tag_id"
            )

        work = frame.copy()
        valid_mask = pd.Series(True, index=work.index)
        errors = []

        def apply_rule(mask: pd.Series, message: str) -> None:
            nonlocal valid_mask

            mask = mask.fillna(False)
            invalid_count = int((~mask).sum())

            if invalid_count > 0:
                errors.append(f"{message}: {invalid_count} filas")

            valid_mask &= mask

        # Comprobar que las columnas contienen números enteros.
        for column in [
            "goodreads_book_id",
            "tag_id",
            "count",
        ]:
            work[column] = pd.to_numeric(
                work[column], errors="coerce"
            )

            apply_rule(
                work[column].notna()
                & work[column].mod(1).eq(0),
                f"{column} debe contener números enteros",
            )

        # Los identificadores deben ser positivos.
        for column in ["goodreads_book_id", "tag_id"]:
            apply_rule(
                work[column] > 0,
                f"{column} debe ser mayor que cero",
            )

        # count no puede ser negativo.
        apply_rule(
            work["count"] >= 0,
            "count no puede ser negativo",
        )

        # Un libro no puede tener dos relaciones con la misma etiqueta.
        apply_rule(
            ~work.duplicated(
                subset=["goodreads_book_id", "tag_id"],
                keep=False,
            ),
            "La relación libro-etiqueta no puede estar duplicada",
        )

        # Comprobar que los libros existen.
        valid_book_ids = set(
            books["goodreads_book_id"].dropna()
        )

        # goodreads_book_id porque esa es la clave que 
        # conecta book_tags.csv con books.csv
        apply_rule(
            work["goodreads_book_id"].isin(valid_book_ids),
            "goodreads_book_id no existe en books.csv",
        )

        # Comprobar que las etiquetas existen.
        valid_tag_ids = set(
            tags["tag_id"].dropna()
        )

        apply_rule(
            work["tag_id"].isin(valid_tag_ids),
            "tag_id no existe en tags.csv",
        )

        valid_df = work.loc[valid_mask].copy()
        invalid_df = work.loc[~valid_mask].copy()

        return valid_df, invalid_df, errors

    def validate_to_read(
        self,
        frame: pd.DataFrame,
        books: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
        """
        Valida el contenido de to_read.csv.

        Comprueba tipos, rangos, duplicados y referencias
        a libros existentes.
        """
        missing_columns = REQUIRED_TO_READ_COLUMNS - set(frame.columns)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValidationError(
                f"Faltan columnas obligatorias en to_read.csv: {missing}"
            )

        if "book_id" not in books.columns:
            raise ValidationError(
                "El DataFrame de libros debe contener book_id"
            )

        work = frame.copy()
        valid_mask = pd.Series(True, index=work.index)
        errors = []

        def apply_rule(mask: pd.Series, message: str) -> None:
            nonlocal valid_mask

            mask = mask.fillna(False)
            invalid_count = int((~mask).sum())

            if invalid_count > 0:
                errors.append(f"{message}: {invalid_count} filas")

            valid_mask &= mask

        # Comprobar que los identificadores son números enteros.
        for column in ["user_id", "book_id"]:
            work[column] = pd.to_numeric(
                work[column], errors="coerce"
            )

            apply_rule(
                work[column].notna()
                & work[column].mod(1).eq(0),
                f"{column} debe contener números enteros",
            )

            apply_rule(
                work[column] > 0,
                f"{column} debe ser mayor que cero",
            )

        # Un usuario no puede repetir un libro en su lista.
        apply_rule(
            ~work.duplicated(
                subset=["user_id", "book_id"],
                keep=False,
            ),
            "La relación usuario-libro no puede estar duplicada",
        )

        # Comprobar que los libros existen.
        valid_book_ids = set(books["book_id"].dropna())

        apply_rule(
            work["book_id"].isin(valid_book_ids),
            "book_id no existe en books.csv",
        )

        valid_df = work.loc[valid_mask].copy()
        invalid_df = work.loc[~valid_mask].copy()

        return valid_df, invalid_df, errors


    # agrupamos las validaciones
    def validate_all(
        self,
        datasets: dict[str, pd.DataFrame],
    ) -> dict[str, dict[str, object]]:
        """
        Coordina la validación de los cinco datasets de Goodbooks-10k.

        Primero valida libros y etiquetas, ya que los otros datasets
        dependen de ellos para comprobar sus referencias.

        Args:
            datasets: diccionario con los DataFrames originales.

        Returns:
            Diccionario con los DataFrames válidos, inválidos y los
            errores detectados para cada dataset.

        Raises:
            ValidationError: si falta algún dataset o existe un
            problema estructural que impide validarlo.
        """

        logger.info(
            "Iniciando validación de datasets: datasets=%s",
            len(datasets),
        )

        # Comprobar que se han proporcionado todos los datasets.
        missing_datasets = REQUIRED_DATASETS - datasets.keys()

        if missing_datasets:
            missing = ", ".join(sorted(missing_datasets))
            logger.error(
                "Faltan datasets necesarios para validar: %s",
                missing,
            )
            raise ValidationError(
                f"Faltan datasets necesarios para validar: {missing}"
            )

        # Comprobar que todos los elementos son DataFrames.
        for name in REQUIRED_DATASETS:
            if not isinstance(datasets[name], pd.DataFrame):
                logger.error(
                    "El dataset '%s' no es un DataFrame de pandas",
                    name,
                )

                raise ValidationError(
                    f"El dataset '{name}' debe ser un DataFrame de pandas."
                )

        try:
            # 1. Validar primero libros y etiquetas.
            valid_books, invalid_books, books_errors = self.validate_books(
                datasets["books"]
            )

            valid_tags, invalid_tags, tags_errors = self.validate_tags(
                datasets["tags"]
            )

            # 2. Validar los datasets que dependen de libros y etiquetas.
            valid_ratings, invalid_ratings, ratings_errors = (
                self.validate_ratings(
                    datasets["ratings"],
                    valid_books,
                )
            )

            valid_book_tags, invalid_book_tags, book_tags_errors = (
                self.validate_book_tags(
                    datasets["book_tags"],
                    valid_books,
                    valid_tags,
                )
            )

            valid_to_read, invalid_to_read, to_read_errors = (
                self.validate_to_read(
                    datasets["to_read"],
                    valid_books,
                )
            )
        except ValidationError:
            logger.exception(
                "Error estructural durante la validación de los datasets"
            )
            raise

        # 3. Organizar los resultados.
        results = {
            "books": {
                "valid": valid_books,
                "invalid": invalid_books,
                "errors": books_errors,
            },
            "ratings": {
                "valid": valid_ratings,
                "invalid": invalid_ratings,
                "errors": ratings_errors,
            },
            "book_tags": {
                "valid": valid_book_tags,
                "invalid": invalid_book_tags,
                "errors": book_tags_errors,
            },
            "tags": {
                "valid": valid_tags,
                "invalid": invalid_tags,
                "errors": tags_errors,
            },
            "to_read": {
                "valid": valid_to_read,
                "invalid": invalid_to_read,
                "errors": to_read_errors,
            },
        }

        # Gaurda en el logger las filas de mis csv que han pasado la validacion
        # Tambien guarda con WARNING las filas que no cumplian los requisitos
        for name, result in results.items():
            valid_count = len(result["valid"])
            invalid_count = len(result["invalid"])

            logger.info(
                "Dataset validado: name=%s, valid=%s, invalid=%s",
                name,
                valid_count,
                invalid_count,
            )

            if invalid_count > 0:
                logger.warning(
                    "Se han encontrado filas inválidas: dataset=%s, count=%s",
                    name,
                    invalid_count,
                )

        logger.info(
            "Validación completada correctamente: datasets=%s",
            len(results),
        )

        return results