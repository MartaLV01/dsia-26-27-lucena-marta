
"""
Modelos Pydantic para las entidades de Goodbooks-10k.
Es decir las condiciones que cada uno de los ficheros csv debe cumplir
"""

from pydantic import BaseModel, ConfigDict, Field


class DataRecord(BaseModel):
    """Configuración común de los modelos."""

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


class BookRecord(DataRecord):
    """Representa un libro del dataset books.csv."""

    book_id: int = Field(gt=0) # mayor igual que
    goodreads_book_id: int = Field(gt=0)
    best_book_id: int = Field(gt=0)
    work_id: int = Field(gt=0)
    books_count: int = Field(gt=0)

    isbn: str | None = None # una cadena que es opcional, es decri puede no tener valor
    isbn13: str | None = None

    authors: str = Field(min_length=1) # al menor 1 caracter
    original_publication_year: float | None = None
    original_title: str | None = None
    title: str = Field(min_length=1)
    language_code: str | None = None

    average_rating: float = Field(ge=0, le=5) # mayor que y menor que
    ratings_count: int = Field(ge=0)
    work_ratings_count: int = Field(ge=0)
    work_text_reviews_count: int = Field(ge=0)

    ratings_1: int = Field(ge=0)
    ratings_2: int = Field(ge=0)
    ratings_3: int = Field(ge=0)
    ratings_4: int = Field(ge=0)
    ratings_5: int = Field(ge=0)

    image_url: str | None = None
    small_image_url: str | None = None


class RatingRecord(DataRecord):
    """Representa una valoración de ratings.csv."""

    user_id: int = Field(gt=0)
    book_id: int = Field(gt=0)
    rating: int = Field(ge=1, le=5)


class BookTagRecord(DataRecord):
    """Representa una relación libro-etiqueta de book_tags.csv."""

    goodreads_book_id: int = Field(gt=0)
    tag_id: int = Field(gt=0)
    count: int = Field(ge=0)


class TagRecord(DataRecord):
    """Representa una etiqueta de tags.csv."""

    tag_id: int = Field(gt=0)
    tag_name: str = Field(min_length=1)


class ToReadRecord(DataRecord):
    """Representa un libro que un usuario quiere leer."""

    user_id: int = Field(gt=0)
    book_id: int = Field(gt=0)
