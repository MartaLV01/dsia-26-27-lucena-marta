
import pandas as pd
import pytest

from book_recommender.validator import DataValidator, ValidationError

# Para validate_books()
def create_valid_books_df():
    """Crea un DataFrame pequeño con un libro válido."""
    return pd.DataFrame([{
        "book_id": 1,
        "goodreads_book_id": 100,
        "best_book_id": 100,
        "work_id": 1000,
        "books_count": 1,
        "isbn": "123456789",
        "isbn13": "1234567890123",
        "authors": "Autor de prueba",
        "original_publication_year": 2000,
        "original_title": "Libro de prueba",
        "title": "Libro de prueba",
        "language_code": "eng",
        "average_rating": 4.5,
        "ratings_count": 100,
        "work_ratings_count": 150,
        "work_text_reviews_count": 20,
        "ratings_1": 5,
        "ratings_2": 5,
        "ratings_3": 10,
        "ratings_4": 30,
        "ratings_5": 50,
        "image_url": None,
        "small_image_url": None,
    }])


def test_validate_books_valid_row():
    """Comprueba que una fila correcta se considera válida."""
    validator = DataValidator()
    frame = create_valid_books_df()

    valid_df, invalid_df, errors = validator.validate_books(frame)

    assert len(valid_df) == 1
    assert len(invalid_df) == 0
    assert errors == []


def test_validate_books_invalid_rating():
    """Comprueba que se rechaza una puntuación fuera de rango."""
    validator = DataValidator()
    frame = create_valid_books_df()

    frame.loc[0, "average_rating"] = 6

    valid_df, invalid_df, errors = validator.validate_books(frame)

    assert len(valid_df) == 0
    assert len(invalid_df) == 1
    assert any("average_rating" in error for error in errors)


def test_validate_books_duplicate_id():
    """Comprueba que se rechazan todas las filas con IDs duplicados."""
    validator = DataValidator()
    frame = create_valid_books_df()

    duplicate = frame.copy()
    duplicate.loc[0, "goodreads_book_id"] = 200

    frame = pd.concat([frame, duplicate], ignore_index=True)

    valid_df, invalid_df, errors = validator.validate_books(frame)

    assert len(valid_df) == 0
    assert len(invalid_df) == 2
    assert any("book_id no puede estar duplicado" in error for error in errors)


def test_validate_books_missing_column():
    """Comprueba que se detecta una columna obligatoria ausente."""
    validator = DataValidator()
    frame = create_valid_books_df()

    frame = frame.drop(columns=["image_url"])

    with pytest.raises(ValidationError):
        validator.validate_books(frame)

def test_validate_books_optional_fields_can_be_null():
    """Comprueba que los campos opcionales pueden estar vacíos."""
    validator = DataValidator()
    frame = create_valid_books_df()

    frame.loc[0, "original_publication_year"] = None
    frame.loc[0, "language_code"] = None
    frame.loc[0, "image_url"] = None
    frame.loc[0, "small_image_url"] = None

    valid_df, invalid_df, errors = validator.validate_books(frame)

    assert len(valid_df) == 1
    assert invalid_df.empty
    assert errors == []


def test_validate_books_empty_optional_fields_are_normalized():
    """Comprueba que las cadenas vacías se convierten en nulos."""
    validator = DataValidator()
    frame = create_valid_books_df()

    # Permitimos introducir cadenas en la columna del año.
    frame["original_publication_year"] = (
        frame["original_publication_year"].astype("object")
    )

    frame.loc[0, "original_publication_year"] = " "
    frame.loc[0, "language_code"] = " "
    frame.loc[0, "image_url"] = ""
    frame.loc[0, "small_image_url"] = "   "

    valid_df, invalid_df, errors = validator.validate_books(frame)

    assert len(valid_df) == 1
    assert invalid_df.empty
    assert errors == []

    assert pd.isna(valid_df.iloc[0]["original_publication_year"])
    assert pd.isna(valid_df.iloc[0]["language_code"])
    assert pd.isna(valid_df.iloc[0]["image_url"])
    assert pd.isna(valid_df.iloc[0]["small_image_url"])


def test_validate_books_invalid_image_url():
    """Comprueba que se rechaza una URL de portada mal formada."""
    validator = DataValidator()
    frame = create_valid_books_df()

    frame.loc[0, "image_url"] = "esto-no-es-una-url"

    valid_df, invalid_df, errors = validator.validate_books(frame)

    assert valid_df.empty
    assert len(invalid_df) == 1
    assert any("image_url" in error for error in errors)


def test_validate_books_valid_image_urls():
    """Comprueba que se aceptan URL HTTP y HTTPS."""
    validator = DataValidator()
    frame = create_valid_books_df()

    frame.loc[0, "image_url"] = "https://example.com/book.jpg"
    frame.loc[0, "small_image_url"] = "http://example.com/book-small.jpg"

    valid_df, invalid_df, errors = validator.validate_books(frame)

    assert len(valid_df) == 1
    assert invalid_df.empty
    assert errors == []


# para validate_ratings()
def create_valid_ratings_df():
    """Crea un DataFrame pequeño con valoraciones válidas."""
    return pd.DataFrame([
        {"user_id": 1, "book_id": 1, "rating": 5},
        {"user_id": 2, "book_id": 1, "rating": 4},
        {"user_id": 1, "book_id": 2, "rating": 3},
    ])


def test_validate_ratings_valid_rows():
    """Comprueba que las valoraciones correctas son válidas."""
    validator = DataValidator()
    ratings = create_valid_ratings_df()

    books = pd.DataFrame({"book_id": [1, 2]})

    valid_df, invalid_df, errors = validator.validate_ratings(
        ratings, books
    )

    assert len(valid_df) == 3
    assert len(invalid_df) == 0
    assert errors == []


def test_validate_ratings_invalid_rating():
    """Comprueba que se rechazan valoraciones fuera de rango."""
    validator = DataValidator()
    ratings = create_valid_ratings_df()

    ratings.loc[0, "rating"] = 6
    books = pd.DataFrame({"book_id": [1, 2]})

    valid_df, invalid_df, errors = validator.validate_ratings(
        ratings, books
    )

    assert len(valid_df) == 2
    assert len(invalid_df) == 1
    assert any("rating debe estar entre 1 y 5" in error for error in errors)


def test_validate_ratings_duplicate_user_book():
    """Comprueba que no se repite la valoración de un mismo libro."""
    validator = DataValidator()
    ratings = create_valid_ratings_df()

    duplicate = ratings.iloc[[0]].copy()
    ratings = pd.concat([ratings, duplicate], ignore_index=True)

    books = pd.DataFrame({"book_id": [1, 2]})

    valid_df, invalid_df, errors = validator.validate_ratings(
        ratings, books
    )

    assert len(valid_df) == 2
    assert len(invalid_df) == 2
    assert any("user_id + book_id" in error for error in errors)


def test_validate_ratings_unknown_book():
    """Comprueba que se rechazan libros inexistentes."""
    validator = DataValidator()
    ratings = create_valid_ratings_df()

    ratings.loc[0, "book_id"] = 999
    books = pd.DataFrame({"book_id": [1, 2]})

    valid_df, invalid_df, errors = validator.validate_ratings(
        ratings, books
    )

    assert len(valid_df) == 2
    assert len(invalid_df) == 1
    assert any("no existe en books.csv" in error for error in errors)


def test_validate_ratings_missing_column():
    """Comprueba que se detectan columnas ausentes."""
    validator = DataValidator()
    ratings = create_valid_ratings_df()

    ratings = ratings.drop(columns=["rating"])
    books = pd.DataFrame({"book_id": [1, 2]})

    with pytest.raises(ValidationError):
        validator.validate_ratings(ratings, books)


# para validate_tags
def create_valid_tags_df():
    return pd.DataFrame([
        {"tag_id": 1, "tag_name": "fantasy"},
        {"tag_id": 2, "tag_name": "romance"},
        {"tag_id": 3, "tag_name": "mystery"},
    ])


def test_validate_tags_valid_rows():
    validator = DataValidator()

    valid, invalid, errors = validator.validate_tags(
        create_valid_tags_df()
    )

    assert len(valid) == 3
    assert invalid.empty
    assert errors == []


def test_validate_tags_duplicate_name_ignoring_case():
    validator = DataValidator()

    frame = pd.DataFrame([
        {"tag_id": 1, "tag_name": "Fantasia"},
        {"tag_id": 2, "tag_name": "FANTASIA"},
        {"tag_id": 3, "tag_name": "romance"},
    ])

    valid, invalid, errors = validator.validate_tags(frame)

    assert len(valid) == 1
    assert len(invalid) == 2
    assert any("tag_name no puede estar duplicado" in e for e in errors)


def test_validate_tags_empty_name():
    validator = DataValidator()

    frame = pd.DataFrame([
        {"tag_id": 1, "tag_name": "fantasy"},
        {"tag_id": 2, "tag_name": "   "},
    ])

    valid, invalid, errors = validator.validate_tags(frame)

    assert len(valid) == 1
    assert len(invalid) == 1
    assert any("tag_name no puede estar vacío" in e for e in errors)


def test_validate_tags_duplicate_id():
    validator = DataValidator()

    frame = pd.DataFrame([
        {"tag_id": 1, "tag_name": "fantasy"},
        {"tag_id": 1, "tag_name": "romance"},
    ])

    valid, invalid, errors = validator.validate_tags(frame)

    assert valid.empty
    assert len(invalid) == 2
    assert any("tag_id no puede estar duplicado" in e for e in errors)


def test_validate_tags_missing_column():
    validator = DataValidator()

    frame = pd.DataFrame([
        {"tag_id": 1},
    ])

    with pytest.raises(ValidationError):
        validator.validate_tags(frame)


# PAra books_tags.csv
def create_valid_book_tags_df():
    return pd.DataFrame([
        {"goodreads_book_id": 100, "tag_id": 1, "count": 20},
        {"goodreads_book_id": 100, "tag_id": 2, "count": 15},
        {"goodreads_book_id": 200, "tag_id": 1, "count": 10},
    ])


def test_validate_book_tags_valid_rows():
    validator = DataValidator()

    books = pd.DataFrame({
        "goodreads_book_id": [100, 200],
    })
    tags = pd.DataFrame({
        "tag_id": [1, 2],
    })

    valid, invalid, errors = validator.validate_book_tags(
        create_valid_book_tags_df(), books, tags
    )

    assert len(valid) == 3
    assert invalid.empty
    assert errors == []


def test_validate_book_tags_negative_count():
    validator = DataValidator()

    frame = create_valid_book_tags_df()
    frame.loc[0, "count"] = -1

    books = pd.DataFrame({"goodreads_book_id": [100, 200]})
    tags = pd.DataFrame({"tag_id": [1, 2]})

    valid, invalid, errors = validator.validate_book_tags(
        frame, books, tags
    )

    assert len(valid) == 2
    assert len(invalid) == 1
    assert any("count no puede ser negativo" in e for e in errors)


def test_validate_book_tags_duplicate_relation():
    validator = DataValidator()

    frame = pd.DataFrame([
        {"goodreads_book_id": 100, "tag_id": 1, "count": 20},
        {"goodreads_book_id": 100, "tag_id": 1, "count": 15},
    ])

    books = pd.DataFrame({"goodreads_book_id": [100]})
    tags = pd.DataFrame({"tag_id": [1]})

    valid, invalid, errors = validator.validate_book_tags(
        frame, books, tags
    )

    assert valid.empty
    assert len(invalid) == 2
    assert any("no puede estar duplicada" in e for e in errors)


def test_validate_book_tags_unknown_book():
    validator = DataValidator()

    frame = create_valid_book_tags_df()
    frame.loc[0, "goodreads_book_id"] = 999

    books = pd.DataFrame({"goodreads_book_id": [100, 200]})
    tags = pd.DataFrame({"tag_id": [1, 2]})

    valid, invalid, errors = validator.validate_book_tags(
        frame, books, tags
    )

    assert len(valid) == 2
    assert len(invalid) == 1
    assert any("no existe en books.csv" in e for e in errors)


def test_validate_book_tags_unknown_tag():
    validator = DataValidator()

    frame = create_valid_book_tags_df()
    frame.loc[0, "tag_id"] = 999

    books = pd.DataFrame({"goodreads_book_id": [100, 200]})
    tags = pd.DataFrame({"tag_id": [1, 2]})

    valid, invalid, errors = validator.validate_book_tags(
        frame, books, tags
    )

    assert len(valid) == 2
    assert len(invalid) == 1
    assert any("no existe en tags.csv" in e for e in errors)


def test_validate_book_tags_missing_column():
    validator = DataValidator()

    frame = pd.DataFrame({
        "goodreads_book_id": [100],
        "tag_id": [1],
    })

    books = pd.DataFrame({"goodreads_book_id": [100]})
    tags = pd.DataFrame({"tag_id": [1]})

    with pytest.raises(ValidationError):
        validator.validate_book_tags(frame, books, tags)

# Para to_read.csv
def create_valid_to_read_df():
    return pd.DataFrame([
        {"user_id": 1, "book_id": 1},
        {"user_id": 2, "book_id": 1},
        {"user_id": 1, "book_id": 2},
    ])


def test_validate_to_read_valid_rows():
    validator = DataValidator()
    books = pd.DataFrame({"book_id": [1, 2]})

    valid, invalid, errors = validator.validate_to_read(
        create_valid_to_read_df(), books
    )

    assert len(valid) == 3
    assert invalid.empty
    assert errors == []


def test_validate_to_read_invalid_user_id():
    validator = DataValidator()
    frame = create_valid_to_read_df()
    frame.loc[0, "user_id"] = 0

    books = pd.DataFrame({"book_id": [1, 2]})

    valid, invalid, errors = validator.validate_to_read(
        frame, books
    )

    assert len(valid) == 2
    assert len(invalid) == 1
    assert any("user_id debe ser mayor que cero" in e for e in errors)


def test_validate_to_read_duplicate_user_book():
    validator = DataValidator()

    frame = pd.DataFrame([
        {"user_id": 1, "book_id": 1},
        {"user_id": 1, "book_id": 1},
    ])

    books = pd.DataFrame({"book_id": [1]})

    valid, invalid, errors = validator.validate_to_read(
        frame, books
    )

    assert valid.empty
    assert len(invalid) == 2
    assert any("no puede estar duplicada" in e for e in errors)


def test_validate_to_read_unknown_book():
    validator = DataValidator()
    frame = create_valid_to_read_df()
    frame.loc[0, "book_id"] = 999

    books = pd.DataFrame({"book_id": [1, 2]})

    valid, invalid, errors = validator.validate_to_read(
        frame, books
    )

    assert len(valid) == 2
    assert len(invalid) == 1
    assert any("book_id no existe en books.csv" in e for e in errors)


def test_validate_to_read_missing_column():
    validator = DataValidator()

    frame = pd.DataFrame({
        "user_id": [1],
    })

    books = pd.DataFrame({"book_id": [1]})

    with pytest.raises(ValidationError):
        validator.validate_to_read(frame, books)


# Para la union de todas la validaciones
def create_valid_datasets():
    """
    Crea cinco datasets pequeños con referencias coherentes.
    Es decir, que las entradas que se crean estan correctamente realcionadas unas con otras.
    """

    books = create_valid_books_df()
    tags = create_valid_tags_df()

    # Utilizamos identificadores que realmente existen.
    first_book = books.iloc[0]
    first_tag = tags.iloc[0]

    ratings = create_valid_ratings_df().iloc[:2].copy()
    ratings["book_id"] = first_book["book_id"]
    ratings["user_id"] = [1, 2]

    book_tags = create_valid_book_tags_df().iloc[[0]].copy()
    book_tags["goodreads_book_id"] = first_book["goodreads_book_id"]
    book_tags["tag_id"] = first_tag["tag_id"]

    to_read = create_valid_to_read_df().iloc[[0]].copy()
    to_read["book_id"] = first_book["book_id"]

    return {
        "books": books,
        "ratings": ratings,
        "book_tags": book_tags,
        "tags": tags,
        "to_read": to_read,
    }

def test_validate_all_returns_all_datasets():
    # Arrange
    validator = DataValidator()
    datasets = create_valid_datasets()

    # Act
    results = validator.validate_all(datasets)

    # Assert
    assert set(results.keys()) == {
        "books",
        "ratings",
        "book_tags",
        "tags",
        "to_read",
    }

    for result in results.values():
        assert not result["valid"].empty
        assert result["invalid"].empty
        assert result["errors"] == []


def test_validate_all_keeps_valid_rows_and_separates_invalid_rows():
    # Arrange
    validator = DataValidator()
    datasets = create_valid_datasets()

    # Introducimos una valoración con un rating fuera de rango.
    datasets["ratings"].loc[
        datasets["ratings"].index[0], "rating"
    ] = 6

    # Act
    results = validator.validate_all(datasets)

    # Assert
    assert len(results["ratings"]["invalid"]) == 1
    assert len(results["ratings"]["valid"]) > 0
    assert results["ratings"]["errors"]


def test_validate_all_raises_error_when_dataset_is_missing():
    # Arrange
    validator = DataValidator()
    datasets = create_valid_datasets()
    del datasets["tags"]

    # Act & Assert
    with pytest.raises(ValidationError):
        validator.validate_all(datasets)