from typing import List, Dict, Any, Optional


class BasicArticleFilter:
    """
    Minimal version of your friend's classifier, wrapped as a class.
    """

    def classify_text(self, text: str) -> str:
        t = text.lower()

        # 1. Filter OUT non-US content
        non_us_keywords = [
            "china", "india", "russia", "uk", "england", "europe", "africa",
            "asia", "middle east", "mexico", "canada", "brazil", "australia",
            "japan", "south america", "international", "global",
        ]
        for k in non_us_keywords:
            if k in t:
                return "REMOVE"

        # 2. Filter OUT political content
        political_keywords = [
            "election", "vote", "ballot", "president", "senator", "governor",
            "congress", "parliament", "policy", "bill", "legislation",
            "democrat", "republican", "campaign", "white house",
            "supreme court", "lawmaker", "administration",
        ]
        for k in political_keywords:
            if k in t:
                return "REMOVE"

        # 3. IMPORTANT articles
        important_keywords = [
            "breaking", "urgent", "emergency", "crisis", "public safety",
            "severe weather", "health advisory", "recall", "missing person",
            "natural disaster", "major update",
        ]
        for k in important_keywords:
            if k in t:
                return "IMPORTANT"

        # 4. NOT IMPORTANT articles
        not_important_keywords = [
            "celebrity", "gossip", "viral", "meme", "influencer",
            "entertainment", "fashion", "sports rumor", "pop culture",
        ]
        for k in not_important_keywords:
            if k in t:
                return "NOT IMPORTANT"

        # 5. Everything else
        return "NEUTRAL"


class EducationalArticleAnalyzer:
    """
    Simple, unit-test-friendly analyzer.

    Responsibilities:
    - Use BasicArticleFilter to ignore "REMOVE" articles.
    - Infer a sector label (Technology, Energy, etc.).
    - Compute an educational score for each article.
    - Rank articles by educational value.
    - Select top N in a DeepSeek-style list.
    """

    def __init__(self, base_filter: Optional[BasicArticleFilter] = None) -> None:
        self.base_filter = base_filter or BasicArticleFilter()

        self.sector_keywords = {
            "technology": "Technology",
            "ai": "Technology",
            "chip": "Technology",
            "semiconductor": "Technology",
            "software": "Technology",
            "bank": "Financials",
            "credit": "Financials",
            "loan": "Financials",
            "insurance": "Financials",
            "oil": "Energy",
            "gas": "Energy",
            "opec": "Energy",
            "solar": "Energy",
            "wind": "Energy",
            "retail": "Consumer",
            "consumer": "Consumer",
            "pharma": "Healthcare",
            "drug": "Healthcare",
            "vaccine": "Healthcare",
            "hospital": "Healthcare",
            "shipping": "Industrials",
            "factory": "Industrials",
            "manufacturing": "Industrials",
        }

        self.educational_triggers = {
            "why": 2,
            "how": 2,
            "explained": 3,
            "analysis": 2,
            "impact": 3,
            "implications": 3,
            "consequences": 3,
            "supply chain": 3,
            "regulatory": 3,
            "geopolitical": 4,
            "crisis": 4,
        }

    # 1) Normalize article text
    def normalize_text(self, article: Dict[str, Any]) -> str:
        title = (article.get("title") or "").lower()
        desc = (article.get("description") or "").lower()
        content = (article.get("content") or "").lower()
        return f"{title} {desc} {content}".strip()

    # 2) Sector inference
    def infer_sector(self, article: Dict[str, Any]) -> str:
        text = self.normalize_text(article)
        for keyword, sector in self.sector_keywords.items():
            if keyword in text:
                return sector
        return "Unknown"

    # 3) Educational score
    def compute_educational_score(self, article: Dict[str, Any]) -> int:
        text = self.normalize_text(article)
        score = 0

        if len(text.split()) > 10:
            score += 1

        for trigger, points in self.educational_triggers.items():
            if trigger in text:
                score += points

        return score

    # 4) Annotate ONE article
    def annotate_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        text = self.normalize_text(article)
        base_label = self.base_filter.classify_text(text)
        sector = self.infer_sector(article)
        score = self.compute_educational_score(article)

        annotated = article.copy()
        annotated["base_label"] = base_label
        annotated["sector"] = sector
        annotated["educational_score"] = score
        return annotated

    # 5) Filter using BasicArticleFilter
    def filter_with_basic(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        kept: List[Dict[str, Any]] = []
        for article in articles:
            annotated = self.annotate_article(article)
            if annotated["base_label"] != "REMOVE":
                kept.append(annotated)
        return kept

    # 6) Rank articles by label + score
    def rank_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered = self.filter_with_basic(articles)
        label_priority = {"IMPORTANT": 0, "NEUTRAL": 1, "NOT IMPORTANT": 2}

        filtered.sort(
            key=lambda a: (
                label_priority.get(a["base_label"], 3),
                -a["educational_score"],
            )
        )
        return filtered

    # 7) Select top N
    def select_top_for_deepseek(
        self,
        articles: List[Dict[str, Any]],
        max_count: int = 15,
    ) -> Dict[str, Any]:
        ranked = self.rank_articles(articles)
        top = ranked[:max_count]

        selected: List[Dict[str, Any]] = []
        for idx, art in enumerate(top, start=1):
            selected.append(
                {
                    "id": art.get("id"),
                    "title": art.get("title"),
                    "description": art.get("description"),
                    "sector": art.get("sector"),
                    "base_label": art.get("base_label"),
                    "educational_score": art.get("educational_score"),
                    "rank": idx,
                }
            )

        return {
            "total_articles": len(articles),
            "selected_count": len(selected),
            "selected": selected,
        }


if __name__ == "__main__":
    articles = [
        {
            "id": 1,
            "title": "Federal Reserve analysis: how rate cuts impact bank stocks",
            "description": "Deep dive into monetary policy and its effect on financials.",
            "content": "",
        },
        {
            "id": 2,
            "title": "Local mayor opens new park",
            "description": "Community event draws hundreds of residents.",
            "content": "",
        },
    ]

    analyzer = EducationalArticleAnalyzer()
    result = analyzer.select_top_for_deepseek(articles, max_count=10)
    print(result)
