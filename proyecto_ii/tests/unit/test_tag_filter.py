import pandas as pd

from book_recommender.tag_filter import (
    build_tag_report,
    canonicalize_tag,
    classify_tag,
    normalize_tag,
)


def test_normalize_tag():
    assert normalize_tag("  Ficción  ") == "ficcion"


def test_canonicalize_tag():
    assert canonicalize_tag("sci-fi") == "science-fiction"
    assert canonicalize_tag("ya") == "young-adult"


def test_classify_thematic_tag():
    assert classify_tag("fantasy")[0] == "thematic"
    assert classify_tag("historical-fiction")[0] == "thematic"


def test_classify_non_thematic_tag():
    assert classify_tag("to-read")[0] == "non_thematic"
    assert classify_tag("paperback")[0] == "non_thematic"


def test_classify_uncertain_tag():
    assert classify_tag("adult")[0] == "uncertain"
    assert classify_tag("stephen-king")[0] == "uncertain"


def test_build_tag_report():
    tags = pd.DataFrame({
        "tag_id": [1, 2, 3],
        "tag_name": ["fantasy", "to-read", "adult"],
    })

    book_tags = pd.DataFrame({
        "tag_id": [1, 1, 2, 3],
        "goodreads_book_id": [100, 101, 100, 102],
        "count": [10, 5, 20, 3],
    })

    report = build_tag_report(tags, book_tags)

    assert len(report) == 3
    assert set(report["classification"]) == {
        "thematic",
        "non_thematic",
        "uncertain",
    }

    fantasy = report.loc[report["tag_name"] == "fantasy"].iloc[0]

    assert fantasy["total_assignments"] == 15
    assert fantasy["books_count"] == 2