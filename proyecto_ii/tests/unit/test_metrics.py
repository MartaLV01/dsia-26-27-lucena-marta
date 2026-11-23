
import pandas as pd
import pytest

from book_recommender.metrics import BooksMetrics
from book_recommender.metrics import RecommenderMetrics
from book_recommender.recommender import BookRecommender

@pytest.fixture
def metrics():
    return BooksMetrics()

@pytest.fixture
def recommender_metrics():
    return RecommenderMetrics()

@pytest.fixture
def books():
    return pd.DataFrame({
        "book_id": [1, 2, 3],
        "title": ["Book A", "Book B", "Book C"],
        "average_rating": [4.0, 3.0, 5.0],
        "ratings_count": [100, 300, 200],
    })

@pytest.fixture
def trained_recommender():
    books = pd.DataFrame({
        "book_id": [1, 2, 3],
        "title": ["Book A", "Book B", "Book C"],
        "content": [
            "dragon magic adventure",
            "dragon magic adventure",
            "spaceship galaxy science",
        ],
    })

    recommender = BookRecommender()
    recommender.fit(books)

    return recommender

def test_total_books_returns_number_of_books(metrics, books):
    # Arrange
    expected = 3

    # Act
    result = metrics.total_books(books)

    # Assert
    assert result == expected


def test_average_rating_returns_mean(metrics, books):
    # Arrange
    expected = 4.0

    # Act
    result = metrics.average_rating(books)

    # Assert
    assert result == expected


def test_average_rating_returns_zero_for_empty_dataframe(metrics):
    # Arrange
    empty_books = pd.DataFrame(
        columns=["average_rating", "ratings_count"]
    )

    # Act
    result = metrics.average_rating(empty_books)

    # Assert
    assert result == 0.0


def test_most_rated_book_returns_book_with_most_ratings(metrics, books):
    # Arrange
    expected_title = "Book B"
    expected_ratings_count = 300

    # Act
    result = metrics.most_rated_book(books)

    # Assert
    assert result is not None
    assert result["title"] == expected_title
    assert result["ratings_count"] == expected_ratings_count


def test_most_rated_book_returns_none_for_empty_dataframe(metrics):
    # Arrange
    empty_books = pd.DataFrame(
        columns=["average_rating", "ratings_count"]
    )

    # Act
    result = metrics.most_rated_book(empty_books)

    # Assert
    assert result is None


@pytest.mark.parametrize(
    "ratings, expected",
    [
        ([4.0, 4.0], 4.0),
        ([2.0, 4.0], 3.0),
        ([1.0, 3.0, 5.0], 3.0),
    ],
)
def test_average_rating_with_different_values(metrics, ratings, expected):
    # Arrange
    books = pd.DataFrame({"average_rating": ratings})

    # Act
    result = metrics.average_rating(books)

    # Assert
    assert result == expected

# para RecommenderMetrics: average_similarity
def test_average_similarity_returns_mean(recommender_metrics):
    # Arrange
    recommendations = pd.DataFrame({
        "book_id": [1, 2, 3],
        "similarity": [0.85, 0.78, 0.72],
    })
    expected = 0.7833333333

    # Act
    result = recommender_metrics.average_similarity(recommendations)

    # Assert
    assert result == pytest.approx(expected)


def test_average_similarity_returns_zero_for_empty_dataframe(
    recommender_metrics,
):
    # Arrange
    recommendations = pd.DataFrame()

    # Act
    result = recommender_metrics.average_similarity(recommendations)

    # Assert
    assert result == 0.0


def test_average_similarity_raises_error_without_similarity_column(
    recommender_metrics,
):
    # Arrange
    recommendations = pd.DataFrame({
        "book_id": [1, 2, 3],
    })

    # Act / Assert
    with pytest.raises(ValueError, match="similarity"):
        recommender_metrics.average_similarity(recommendations)

# para RecommenderMetrics: intra_list_diversity
def test_intra_list_diversity_returns_zero_for_identical_books(
    recommender_metrics,
    trained_recommender,
):
    # Arrange
    recommendations = pd.DataFrame({
        "book_id": [1, 2],
    })

    # Act
    result = recommender_metrics.intra_list_diversity(
        recommendations,
        trained_recommender,
    )

    # Assert
    assert result == pytest.approx(0.0)


def test_intra_list_diversity_returns_one_for_different_books(
    recommender_metrics,
    trained_recommender,
):
    # Arrange
    recommendations = pd.DataFrame({
        "book_id": [1, 3],
    })

    # Act
    result = recommender_metrics.intra_list_diversity(
        recommendations,
        trained_recommender,
    )

    # Assert
    assert result == pytest.approx(1.0)


def test_intra_list_diversity_returns_mean_for_multiple_books(
    recommender_metrics,
    trained_recommender,
):
    # Arrange
    recommendations = pd.DataFrame({
        "book_id": [1, 2, 3],
    })

    # Las distancias entre parejas son:
    # Libro 1 - Libro 2: 0.0
    # Libro 1 - Libro 3: 1.0
    # Libro 2 - Libro 3: 1.0
    # Media: 2 / 3

    expected = 2 / 3

    # Act
    result = recommender_metrics.intra_list_diversity(
        recommendations,
        trained_recommender,
    )

    # Assert
    assert result == pytest.approx(expected)


def test_intra_list_diversity_returns_zero_for_empty_dataframe(
    recommender_metrics,
    trained_recommender,
):
    # Arrange
    recommendations = pd.DataFrame()

    # Act
    result = recommender_metrics.intra_list_diversity(
        recommendations,
        trained_recommender,
    )

    # Assert
    assert result == 0.0


def test_intra_list_diversity_returns_zero_for_one_book(
    recommender_metrics,
    trained_recommender,
):
    # Arrange
    recommendations = pd.DataFrame({
        "book_id": [1],
    })

    # Act
    result = recommender_metrics.intra_list_diversity(
        recommendations,
        trained_recommender,
    )

    # Assert
    assert result == 0.0


def test_intra_list_diversity_raises_error_without_book_id(
    recommender_metrics,
    trained_recommender,
):
    # Arrange
    recommendations = pd.DataFrame({
        "title": ["Book A", "Book B"],
    })

    # Act / Assert
    with pytest.raises(ValueError, match="book_id"):
        recommender_metrics.intra_list_diversity(
            recommendations,
            trained_recommender,
        )


def test_intra_list_diversity_raises_error_for_unknown_ids(
    recommender_metrics,
    trained_recommender,
):
    # Arrange
    recommendations = pd.DataFrame({
        "book_id": [1, 999],
    })

    # Act / Assert
    with pytest.raises(ValueError, match="999"):
        recommender_metrics.intra_list_diversity(
            recommendations,
            trained_recommender,
        )


def test_intra_list_diversity_raises_error_for_unfitted_recommender(
    recommender_metrics,
):
    # Arrange
    recommendations = pd.DataFrame({
        "book_id": [1, 2],
    })
    recommender = BookRecommender()

    # Act / Assert
    with pytest.raises(RuntimeError, match="no está entrenado"):
        recommender_metrics.intra_list_diversity(
            recommendations,
            recommender,
        )

def test_intra_list_diversity_raises_error_for_duplicate_ids(
    recommender_metrics,
    trained_recommender,
):
    # Arrange
    recommendations = pd.DataFrame({
        "book_id": [1, 1],
    })

    # Act / Assert
    with pytest.raises(ValueError, match="duplicados"):
        recommender_metrics.intra_list_diversity(
            recommendations,
            trained_recommender,
        )

# para RecommenderMetrics: catalog_coverage
def test_catalog_coverage(recommender_metrics):
    recommendations_list = [
        pd.DataFrame({"book_id": [1, 2, 3]}),
        pd.DataFrame({"book_id": [3, 4, 5]}),
    ]

    result = recommender_metrics.catalog_coverage(
        recommendations_list,
        catalog_size=10,
    )

    assert result == 0.5


def test_catalog_coverage_with_repeated_books(recommender_metrics):
    recommendations_list = [
        pd.DataFrame({"book_id": [1, 2, 3]}),
        pd.DataFrame({"book_id": [1, 2, 3]}),
    ]

    result = recommender_metrics.catalog_coverage(
        recommendations_list,
        catalog_size=10,
    )

    assert result == 0.3


def test_catalog_coverage_with_empty_recommendations(recommender_metrics):
    result = recommender_metrics.catalog_coverage(
        [],
        catalog_size=10,
    )

    assert result == 0.0


def test_catalog_coverage_with_empty_dataframes(recommender_metrics):
    recommendations_list = [
        pd.DataFrame({"book_id": []}),
        pd.DataFrame({"book_id": []}),
    ]

    result = recommender_metrics.catalog_coverage(
        recommendations_list,
        catalog_size=10,
    )

    assert result == 0.0


def test_catalog_coverage_raises_error_for_invalid_catalog_size(
    recommender_metrics,
):
    with pytest.raises(ValueError, match="mayor que cero"):
        recommender_metrics.catalog_coverage([], catalog_size=0)


def test_catalog_coverage_raises_error_without_book_id(
    recommender_metrics,
):
    recommendations_list = [
        pd.DataFrame({"title": ["Book A"]}),
    ]

    with pytest.raises(ValueError, match="book_id"):
        recommender_metrics.catalog_coverage(
            recommendations_list,
            catalog_size=10,
        )
