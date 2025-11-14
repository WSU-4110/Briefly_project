from typing import List, Dict, Any, Optional
import os
import json
import requests


# Step 1: Christians FILTER
def classify_article(article: str) -> str:
    """
    article = string containing title + description + content
    returns: "REMOVE", "IMPORTANT", "NOT IMPORTANT", or "NEUTRAL"
    """
    text = article.lower()

    # 1. Filter OUT non-US content
    non_us_keywords = [
        "china", "india", "russia", "uk", "england", "europe", "africa",
        "asia", "middle east", "mexico", "canada", "brazil", "australia",
        "japan", "south america", "international", "global"
    ]
    for k in non_us_keywords:
        if k in text:
            return "REMOVE"

    # 2. Filter OUT political content
    political_keywords = [
        "election", "vote", "ballot", "president", "senator", "governor",
        "congress", "parliament", "policy", "bill", "legislation",
        "democrat", "republican", "campaign", "white house", "supreme court",
        "lawmaker", "administration"
    ]
    for k in political_keywords:
        if k in text:
            return "REMOVE"

    # 3. Classify IMPORTANT articles
    important_keywords = [
        "breaking", "urgent", "emergency", "crisis", "public safety",
        "severe weather", "health advisory", "recall", "missing person",
        "natural disaster", "major update"
    ]
    for k in important_keywords:
        if k in text:
            return "IMPORTANT"

    # 4. Classify NOT IMPORTANT articles
    not_important_keywords = [
        "celebrity", "gossip", "viral", "meme", "influencer",
        "entertainment", "fashion", "sports rumor", "pop culture"
    ]
    for k in not_important_keywords:
        if k in text:
            return "NOT IMPORTANT"

    # 5. Everything else = Neutral
    return "NEUTRAL"

#Step 2 my filter
class EducationalArticleAnalyzer:
    """
    Uses friend's classify_article + DeepSeek API for ranking.
    Input: list of dicts with id, title, description, content.
    """

    def __init__(self, deepseek_api_key: Optional[str] = None) -> None:
        # Step 2: Store DeepSeek config
        self.deepseek_api_key = deepseek_api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.deepseek_api_key:
            raise ValueError("DeepSeek API key not provided (pass in or set DEEPSEEK_API_KEY).")
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"

        # Simple sector mapping
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

    # Step 3: Normalize + combine article text
    def _normalize_text(self, article: Dict[str, Any]) -> str:
        title = (article.get("title") or "").lower()
        desc = (article.get("description") or "").lower()
        content = (article.get("content") or "").lower()
        return f"{title} {desc} {content}".strip()

    # Step 4: Infer simple sector
    def _infer_sector(self, article: Dict[str, Any]) -> str:
        text = self._normalize_text(article)
        for keyword, sector in self.sector_keywords.items():
            if keyword in text:
                return sector
        return "Unknown"

    # Step 5: Prepare list for DeepSeek (after friend's filter)
    def _prepare_for_deepseek(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        annotated: List[Dict[str, Any]] = []
        simplified: List[Dict[str, Any]] = []

        for art in articles:
            combined = self._normalize_text(art)
            base_label = classify_article(combined)
            if base_label == "REMOVE":
                continue

            sector = self._infer_sector(art)

            a = art.copy()
            a["base_label"] = base_label
            a["sector"] = sector
            annotated.append(a)

            simplified.append(
                {
                    "id": art.get("id"),
                    "title": art.get("title") or "",
                    "description": art.get("description") or "",
                    "sector": sector,
                    "base_label": base_label,
                }
            )

        return {"annotated": annotated, "simplified": simplified}

    # Step 6: Build DeepSeek prompt
    def _build_prompt(self, simplified_articles: List[Dict[str, Any]]) -> str:
        prompt = f"""
You are ranking financial news articles by how EDUCATIONAL they are for a new trader.

Return JSON ONLY in this format:
{{
  "total_analyzed": {len(simplified_articles)},
  "selection_logic": "top_10_or_15",
  "selected_articles": [
    {{"id": 1, "education_score": 9, "rank": 1}},
    {{"id": 2, "education_score": 8, "rank": 2}}
  ]
}}

Scoring (1-10):
- Higher score = more explanation value (what/how/why/impact, macro, sector dynamics, hidden connections).
- Lower score = simple headline, basic company fluff, no real learning.

Articles (list of objects with id, title, description, sector, base_label):
{simplified_articles}
"""
        return prompt

    # Step 7: Call DeepSeek API
    def _call_deepseek(self, prompt: str) -> List[Dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1500,
        }

        resp = requests.post(self.deepseek_url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()

        if content.startswith("```"):
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                content = content[start : end + 1]

        parsed = json.loads(content)
        return parsed.get("selected_articles", [])

    # Step 8: Merge DeepSeek ranking with full articles
    def _merge_results(
        self,
        selected_from_deepseek: List[Dict[str, Any]],
        annotated: List[Dict[str, Any]],
        max_count: int,
    ) -> List[Dict[str, Any]]:
        by_id = {a.get("id"): a for a in annotated}
        result: List[Dict[str, Any]] = []

        selected_sorted = sorted(
            selected_from_deepseek, key=lambda x: x.get("rank", 9999)
        )
        if max_count > 0:
            selected_sorted = selected_sorted[:max_count]

        for item in selected_sorted:
            art = by_id.get(item.get("id"))
            if not art:
                continue
            merged = art.copy()
            merged["deepseek_education_score"] = item.get("education_score")
            merged["rank"] = item.get("rank")
            result.append(merged)

        result.sort(key=lambda a: a.get("rank", 9999))
        return result

    # Step 9: Public entrypoint
    def analyze(
        self, articles: List[Dict[str, Any]], max_count: int = 15
    ) -> Dict[str, Any]:
        prep = self._prepare_for_deepseek(articles)
        annotated = prep["annotated"]
        simplified = prep["simplified"]

        if not simplified:
            return {
                "total_articles": len(articles),
                "filtered_for_deepseek": 0,
                "selected_count": 0,
                "selected": [],
            }

        prompt = self._build_prompt(simplified)
        selected_from_deepseek = self._call_deepseek(prompt)
        final_articles = self._merge_results(
            selected_from_deepseek, annotated, max_count
        )

        return {
            "total_articles": len(articles),
            "filtered_for_deepseek": len(annotated),
            "selected_count": len(final_articles),
            "selected": final_articles,
        }


#quick demo 
if __name__ == "__main__":
    demo_articles = [
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
        {
            "id": 3,
            "title": "AI chips reshape the semiconductor sector",
            "description": "Why GPUs and accelerators are changing technology valuations.",
            "content": "",
        },
    ]

    analyzer = EducationalArticleAnalyzer()
    result = analyzer.analyze(demo_articles, max_count=10)
    print(json.dumps(result, indent=2))
