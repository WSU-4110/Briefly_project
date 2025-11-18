import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
from educational_article_analyzer import EducationalArticleAnalyzer


class FakeFilter:
    """
    Fake filter used ONLY for tests so we can fully control the labels.
    """
    def classify_text(self, text: str) -> str:
        text = text.upper()
        if "LABEL_REMOVE" in text:
            return "REMOVE"
        if "LABEL_IMPORTANT" in text:
            return "IMPORTANT"
        if "LABEL_NOT_IMPORTANT" in text:
            return "NOT IMPORTANT"
        return "NEUTRAL"


def make_analyzer_with_fake_filter() -> EducationalArticleAnalyzer:
    fake_filter = FakeFilter()
    return EducationalArticleAnalyzer(base_filter=fake_filter)


def test_normalize_text_combines_title_desc_content():
    analyzer = make_analyzer_with_fake_filter()
    article = {
        "title": "Hello WORLD",
        "description": "This is A Description",
        "content": "And SOME Content",
    }

    result = analyzer.normalize_text(article)

    assert "hello world" in result
    assert "this is a description" in result
    assert "and some content" in result
    assert result == result.lower()


def test_infer_sector_detects_technology_from_keywords():
    analyzer = make_analyzer_with_fake_filter()
    article = {
        "title": "New AI chip released",
        "description": "A breakthrough in semiconductor technology",
        "content": "",
    }

    sector = analyzer.infer_sector(article)

    assert sector == "Technology"


def test_compute_educational_score_uses_triggers_and_length():
    analyzer = make_analyzer_with_fake_filter()
    article = {
        "title": "Why this market impact matters for investors",
        "description": "We explain why the impact is important for everyone involved.",
        "content": "",
    }

    score = analyzer.compute_educational_score(article)

    assert score >= 6  # length + 'why' + 'impact'


def test_annotate_article_adds_expected_fields():
    analyzer = make_analyzer_with_fake_filter()
    article = {
        "id": 1,
        "title": "LABEL_IMPORTANT Tech stock analysis",
        "description": "How AI chips change the industry",
        "content": "",
    }

    annotated = analyzer.annotate_article(article)

    assert annotated["base_label"] == "IMPORTANT"
    assert "sector" in annotated
    assert "educational_score" in annotated
    assert annotated["id"] == 1


def test_filter_with_basic_removes_articles_with_remove_label():
    analyzer = make_analyzer_with_fake_filter()
    articles = [
        {
            "id": 1,
            "title": "LABEL_REMOVE Something we don't care about",
            "description": "",
            "content": "",
        },
        {
            "id": 2,
            "title": "LABEL_IMPORTANT Educational tech analysis",
            "description": "Why this matters for students",
            "content": "",
        },
    ]

    kept = analyzer.filter_with_basic(articles)

    assert len(kept) == 1
    assert kept[0]["id"] == 2
    assert kept[0]["base_label"] == "IMPORTANT"


def test_rank_articles_orders_by_label_then_score():
    analyzer = make_analyzer_with_fake_filter()
    articles = [
        {
            "id": 1,
            "title": "LABEL_IMPORTANT Why the supply chain crisis matters",
            "description": "Impact and implications explained in detail",
            "content": "",
        },
        {
            "id": 2,
            "title": "LABEL_IMPORTANT Short note",
            "description": "Why only",
            "content": "",
        },
        {
            "id": 3,
            "title": "LABEL_NOT_IMPORTANT Fun article",
            "description": "How this meme became viral",
            "content": "",
        },
    ]

    ranked = analyzer.rank_articles(articles)
    ids_in_order = [a["id"] for a in ranked]

    assert ids_in_order[0] == 1
    assert ids_in_order[1] == 2
    assert ids_in_order[2] == 3


def test_select_top_for_deepseek_limits_and_shapes_output():
    analyzer = make_analyzer_with_fake_filter()
    articles = [
        {
            "id": 1,
            "title": "LABEL_IMPORTANT Deep analysis of AI chips",
            "description": "Why this impacts the technology sector",
            "content": "",
        },
        {
            "id": 2,
            "title": "LABEL_NOT_IMPORTANT Some fun story",
            "description": "How this meme spread online",
            "content": "",
        },
        {
            "id": 3,
            "title": "LABEL_IMPORTANT Another educational piece",
            "description": "Impact and implications for investors",
            "content": "",
        },
    ]

    result = analyzer.select_top_for_deepseek(articles, max_count=2)

    assert result["total_articles"] == 3
    assert result["selected_count"] == 2
    assert len(result["selected"]) == 2

    first = result["selected"][0]
    second = result["selected"][1]

    for item in (first, second):
        assert "id" in item
        assert "title" in item
        assert "sector" in item
        assert "base_label" in item
        assert "educational_score" in item
        assert "rank" in item

    assert first["rank"] == 1
    assert second["rank"] == 2
