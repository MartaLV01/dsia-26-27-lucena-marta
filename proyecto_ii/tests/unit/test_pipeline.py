
import logging

import pandas as pd
import pytest

from book_recommender import pipeline


@pytest.fixture
def validation_results():
    """Resultados simulados de la validación."""

    books = pd.DataFrame({
        "book_id": [1, 2, 3],
        "title": ["Book A", "Book B", "Book C"],
        "average_rating": [4.0, 3.0, 5.0],
        "ratings_count": [100, 300, 200],
    })

    empty = pd.DataFrame()

    return {
        "books": {
            "valid": books,
            "invalid": pd.DataFrame({"book_id": [4]}),
            "errors": [],
        },
        "ratings": {
            "valid": empty,
            "invalid": empty,
            "errors": [],
        },
        "book_tags": {
            "valid": empty,
            "invalid": empty,
            "errors": [],
        },
        "tags": {
            "valid": empty,
            "invalid": empty,
            "errors": [],
        },
        "to_read": {
            "valid": empty,
            "invalid": empty,
            "errors": [],
        },
    }



def test_run_pipeline_executes_all_steps(
    monkeypatch, validation_results, tmp_path
):
    # Arrange
    data_dir = tmp_path / "raw"
    output_path = tmp_path / "processed" / "books_master.csv"
    model_path = tmp_path / "artifacts" / "test_model.joblib"

    master_dataset = pd.DataFrame({
        "book_id": [1, 2, 3],
        "title": ["Book A", "Book B", "Book C"],
    })

    recommender = object() # es un recomendador ficticio para no tener que entrenar dtodo el rato
    calls = []

    class FakeValidator:
        def validate_all(self, datasets):
            calls.append("validate")
            return validation_results

    def fake_train_model(books, output_path):
        calls.append("train")
        assert books is master_dataset
        assert output_path == model_path
        return recommender

    monkeypatch.setattr(
        pipeline,
        "load_data",
        lambda directory: calls.append("load") or {},
    )
    monkeypatch.setattr(
        pipeline,
        "DataValidator",
        lambda: FakeValidator(),
    )
    monkeypatch.setattr(
        pipeline,
        "build_master_dataset",
        lambda results: calls.append("build") or master_dataset,
    )
    monkeypatch.setattr(
        pipeline,
        "save_master_dataset",
        lambda dataset, path: calls.append("save"),
    )
    monkeypatch.setattr(
        pipeline,
        "train_and_save_model",
        fake_train_model,
    )

    #evaluation_results = {"book_queries": {"errors": []}}
    evaluation_results = {
        "book_queries": {
            "queries_requested": 20,
            "queries_succeeded": 20,
            "queries_failed": 0,
            "average_similarity": 0.85,
            "intra_list_diversity": 0.40,
            "catalog_coverage": 0.15,
            "errors": [],
        }
    }
    
    evaluation_path = tmp_path / "evaluation_results.json"

    def fake_evaluate_recommender(
        recommender,
        n_queries,
        n_recommendations,
        random_state,
    ):
        calls.append("evaluate")
        assert recommender is recommender_expected
        assert n_queries == 20
        assert n_recommendations == 5
        assert random_state == 42
        return evaluation_results

    recommender_expected = recommender

    monkeypatch.setattr(
        pipeline,
        "evaluate_recommender",
        fake_evaluate_recommender,
    )
    monkeypatch.setattr(
        pipeline,
        "_save_evaluation_results",
        lambda results, path: calls.append("save_evaluation") or evaluation_path,
    )

    # Act
    result = pipeline.run_pipeline(
        data_dir,
        output_path,
        model_path=model_path,
    )

    # Assert
    assert calls == ["load", "validate", "build", "save", "train", "evaluate", "save_evaluation"]

    assert result["master_dataset"] is master_dataset
    assert result["validation_results"] is validation_results
    assert result["output_path"] == output_path
    assert result["recommender"] is recommender

    assert result["metrics"]["total_books"] == 3
    assert result["metrics"]["average_rating"] == 4.0
    assert result["metrics"]["most_rated_book"]["title"] == "Book B"
    assert result["evaluation_results"] is evaluation_results
    assert result["evaluation_path"] == evaluation_path



def test_run_pipeline_logs_warning_for_invalid_records(
    monkeypatch, validation_results, tmp_path, caplog
):
    # Arrange
    class FakeValidator:
        def validate_all(self, datasets):
            return validation_results

    monkeypatch.setattr(pipeline, "load_data", lambda directory: {})
    monkeypatch.setattr(
        pipeline, "DataValidator", lambda: FakeValidator()
    )
    monkeypatch.setattr(
        pipeline, "build_master_dataset", lambda results: pd.DataFrame()
    )
    monkeypatch.setattr(
        pipeline, "save_master_dataset", lambda dataset, path: None
    )
    monkeypatch.setattr(
        pipeline, "train_and_save_model", lambda books: object(),
    )

    monkeypatch.setattr(
        pipeline, "evaluate_recommender", lambda **kwargs: {},
    )
    monkeypatch.setattr(
        pipeline, "_save_evaluation_results", lambda results, path: tmp_path / "evaluation_results.json",
    )

    # Act
    with caplog.at_level(logging.WARNING):
        pipeline.run_pipeline(tmp_path, tmp_path / "output.csv")

    # Assert
    assert "registros inválidos" in caplog.text
    assert "books" in caplog.text


def test_run_pipeline_propagates_file_not_found_error(
    monkeypatch, tmp_path
):
    # Arrange
    def fake_load_data(directory):
        raise FileNotFoundError("Faltan archivos CSV")

    monkeypatch.setattr(pipeline, "load_data", fake_load_data)

    # Act & Assert
    with pytest.raises(FileNotFoundError, match="Faltan archivos CSV"):
        pipeline.run_pipeline(
            tmp_path,
            tmp_path / "output.csv",
        )
