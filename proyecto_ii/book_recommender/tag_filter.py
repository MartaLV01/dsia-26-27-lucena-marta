
"""
Clasificación y análisis de etiquetas de libros.
"""

import logging
import re
import unicodedata

import pandas as pd

logger = logging.getLogger(__name__)


# Etiquetas conocidas relacionadas con géneros, subgéneros
# y características del contenido de los libros.
THEMATIC_TAGS = {
    "fiction",
    "non-fiction",
    "nonfiction",
    "fantasy",
    "urban-fantasy",
    "high-fantasy",
    "romance",
    "mystery",
    "horror",
    "thriller",
    "historical-fiction",
    "science-fiction",
    "sci-fi",
    "paranormal",
    "contemporary",
    "young-adult",
    "ya",
    "new-adult",
    "classics",
    "history",
    "crime",
    "biography",
    "memoir",
    "vampires",
    "children",
    "childrens",
    "graphic-novel",
    "graphic-novels",
    "comics",
    "short-stories",
    "humor",
    "chick-lit",
    "dystopia",
    "dystopian",
    "adventure",
    "poetry",
    "philosophy",
    "psychology",
    "religion",
    "politics",
    "classic",
    "historical",
    "literature",
    "magic",
    "supernatural",
    "vampire",
    "suspense",
    "action",
    "drama",
    "manga",
    "picture-books",
    "middle-grade",
    "childrens-books",
    "children-s-books",
    "plays",
    "childhood",
    "science-fiction",
    "fantasy-sci-fi",
    "children-books",
    
    # Temáticas, ambientaciones y subgéneros
    "mythology",
    "war",
    "coming-of-age",
    "comedy",
    "erotica",
    "angels",
    "self-help",
    "post-apocalyptic",
    "werewolves",
    "travel",
    "animals",
    "steampunk",
    "time-travel",
    "friendship",
    "magical-realism",
    "action-adventure",
    "mystery-crime",
    "family",

    # Otras temáticas y características del contenido
    "detective",
    "lgbt",
    "dragons",
    "witches",
    "zombies",
    "feminism",
    "relationships",
    "autobiography",
    "biography-memoir",
    "alpha-male",
    "children-s-literature",
    "children-s-lit",
    "american-literature",

    # Géneros, temas y ambientaciones adicionales
    "fairy-tales",
    "demons",
    "gothic",
    "murder",
    "food",
    "art",
    "women",
    "dark",
    "middle-school",
    "ya-lit",
    "fantasy-scifi",

}


# Patrones de etiquetas que no describen el contenido del libro.
NON_THEMATIC_PATTERNS = {
    "reading_status": [
        r"^(to[- ]read|currently[- ]reading|read|currently[- ]listening)$",
        r"^(currently[- ]reading|to[- ]read)[- ].*",
        r"^(want-to-read|unread|tbr|didn-t-finish|on-hold|listened-to)$",
        r"^(couldn-t-finish|gave-up-on)$",
        r"^(to-re-read|to-read-again)$",
    ],
    "ownership": [
        r"^(owned|own|books[- ]i[- ]own|borrowed|wishlist)$",
    ],
    "personal_rating": [
        r"^(favorites?|favourites?|five[- ]stars?)$",
        r"^\d+[- ]star[- ]rating$",
        r"^\d+[- ]stars?$",
    ],
    "format": [
        r"^(paperback|hardcover|kindle|ebook|e[- ]book|audiobook)$",
        r"^(audiobooks?|audio[- ]books?|audio|audible)$",
        r"^(ebooks?|e[- ]books?)$",
        r"^(arc|overdrive|nook|calibre|kindle-books|on-kindle)$",
    ],
    "page_count": [
        r"^\d+[- ]\d+[- ]pages?$",
        r"^\d+[- ]pages?$",
    ],
    "personal_lists": [
        r"^(to[- ]buy|wishlist|default|library)$",
        r"^(owned[- ]books|books[- ]owned)$",
        r"^(my[- ]books|my[- ]library|home[- ]library)$",
        r"^(library[- ]books|shelfari[- ]favorites)$",
        r"^(all[- ]time[- ]favorites|favorite[- ]books)$",
        r"^(wish[- ]list|wish-list)$",
        r"^(own[- ]it|i[- ]own|have)$",
        r"^(recommended|favorite-authors|favorite-series|bookshelf|on-my-shelf|books-i-have|own-to-read|need-to-buy)$",
        r"^(my-favorites|faves|mine|personal-library|my-bookshelf|shelfari-wishlist)$",
        r"^rory-gilmore-reading-challenge$",
        r"^(1001|1001-books|1001-books-to-read-before-you-die|classics-to-read|childhood-favorites)$",
        r"^(want|must-read|stand-alone|first-in-series|part-of-a-series)$",
        r"^(201\d-books|201\d-reads)$",
    ],
    "social_context": [
        r"^book[- ]?club$",
        r"^(book[- ]?club[- ]books?|book[- ]group)$",
    ],
    "series": [
        r"^series$",
    ],
    "reading_history": [
        r"^read[- ]in[- ]\d{4}$",
        r"^read[- ]\d{4}$",
        r"^finished[- ]\d{4}$",
        r"^(re[- ]read|reread|dnf|did[- ]not[- ]finish)$",
        r"^(abandoned|unfinished|finished|reviewed)$",
        r"^\d{4}-reads$",
        r"^(read-for-school|for-school)$",
    ],
     "generic": [
        r"^(books?|novels?)$",
    ],
}


TAG_ALIASES = {
    # funny no se une con humor: puede describir el tono de una obra
    # historical no se une con historical-fiction: puede referirse a otras características históricas
    # literary no es necesariamente lo mismo que literature
    # adult no se une con ninguna categoría: es demasiado ambiguo

    # Ficción y ciencia ficción
    "non-fiction": "nonfiction",
    "sci-fi": "science-fiction",
    "scifi": "science-fiction",
    "sf": "science-fiction",

    # Público infantil y juvenil
    "ya": "young-adult",
    "ya-books": "young-adult",
    "children": "children",
    "childrens": "children",
    "kids": "children",
    "children-s": "children",

    # Libros infantiles
    "childrens-books": "children-books",
    "children-s-books": "children-books",
    "kids-books": "children-books",

    # Formatos de novela gráfica
    "graphic-novels": "graphic-novel",

    # Géneros y variantes
    "mysteries": "mystery",
    "thrillers": "thriller",
    "memoirs": "memoir",
    "humour": "humor",
    "classic": "classics",
    "vampires": "vampire",

    "biographies": "biography",
    "picture-book": "picture-books",
    "ya-lit": "young-adult",
    "fantasy-scifi": "fantasy-sci-fi",
}


def normalize_tag(tag_name: str) -> str:
    """Normaliza una etiqueta para facilitar su clasificación."""
    normalized = unicodedata.normalize("NFKD", str(tag_name))
    normalized = "".join(
        character for character in normalized
        if not unicodedata.combining(character)
    )
    return normalized.lower().strip()


def canonicalize_tag(tag_name: str) -> str:
    """
    Convierte las variantes de una etiqueta en un concepto común.
    """
    normalized = normalize_tag(tag_name)
    return TAG_ALIASES.get(normalized, normalized)


def classify_tag(tag_name: str) -> tuple[str, str]:
    """
    Clasifica una etiqueta como temática, no temática o incierta.
    """
    normalized = canonicalize_tag(tag_name)

    if not normalized or normalized in {"-", "--"}:
        return "non_thematic", "empty_or_invalid"

    # Reconocimiento de etiquetas temáticas conocidas.
    if normalized in THEMATIC_TAGS:
        return "thematic", "known_thematic_tag"

    # Reconocimiento de subgéneros compuestos.
    thematic_patterns = [
        r"^.+-fantasy$",
        r"^.+-fiction$",
        r"^.+-romance$",
        r"^.+-mystery$",
        r"^.+-thriller$",
        r"^.+-horror$",
    ]

    for pattern in thematic_patterns:
        if re.fullmatch(pattern, normalized):
            return "thematic", "thematic_subgenre"

    # Reglas de exclusión.
    for category, patterns in NON_THEMATIC_PATTERNS.items():
        for pattern in patterns:
            if re.fullmatch(pattern, normalized):
                return "non_thematic", category

    return "uncertain", "no_matching_rule"



def build_tag_report(tags: pd.DataFrame, book_tags: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un informe de clasificación y frecuencia de las etiquetas.
    """
    required_tags = {"tag_id", "tag_name"}
    required_book_tags = {"tag_id", "goodreads_book_id", "count"}

    if not required_tags.issubset(tags.columns):
        raise ValueError("El DataFrame tags no contiene las columnas necesarias.")

    if not required_book_tags.issubset(book_tags.columns):
        raise ValueError("El DataFrame book_tags no contiene las columnas necesarias.")

    logger.info("Iniciando análisis de etiquetas: tags=%s", len(tags))

    usage = (
        book_tags.groupby("tag_id")
        .agg(
            total_assignments=("count", "sum"),
            books_count=("goodreads_book_id", "nunique"),
        )
        .reset_index()
    )

    report = tags[["tag_id", "tag_name"]].merge(
        usage,
        on="tag_id",
        how="left",
        validate="one_to_one",
    )

    report[["total_assignments", "books_count"]] = (
        report[["total_assignments", "books_count"]].fillna(0)
    )

    report["canonical_tag"] = report["tag_name"].apply(canonicalize_tag)

    classifications = report["canonical_tag"].apply(classify_tag)
    
    report["classification"] = classifications.apply(lambda result: result[0])
    report["reason"] = classifications.apply(lambda result: result[1])

    report = report.sort_values(
        by=["total_assignments", "tag_name"],
        ascending=[False, True],
    ).reset_index(drop=True)

    logger.info(
        "Análisis terminado: thematic=%s, non_thematic=%s, uncertain=%s",
        (report["classification"] == "thematic").sum(),
        (report["classification"] == "non_thematic").sum(),
        (report["classification"] == "uncertain").sum(),
    )

    return report
