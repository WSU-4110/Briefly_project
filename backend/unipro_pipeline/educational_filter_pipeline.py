"""
Educational Article Filtering System (File 2)

Workflow:
1. Load RAW_NEWS_MMDDYYYY.json produced by raw_news.py
2. Manual keyword filtering & basic classification (BasicArticleFilter)
3. Simple educational scoring
4. Save candidates -> FILTERSFORDEEPSEEK_MMDDYYYY.json
5. DeepSeek AI:
   - Selects best articles
   - Assigns `sector` (one of 12)
   - Assigns `section` (subsector, 2–4 words)
6. Save final DEEPSEEKLISTFORMMDDYYYY.json
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests


# --------------------------------------------------------
# BASIC MANUAL FILTER 
# --------------------------------------------------------
class BasicArticleFilter:
    def __init__(self) -> None:
        # 1) Filter OUT non-US content
        self.non_us_keywords = [
            "china", "india", "russia", "uk", "england", "europe", "africa",
            "asia", "middle east", "mexico", "canada", "brazil", "australia",
            "japan", "south america", "international", "global",
        ]

        # 2) Filter OUT political content
        self.political_keywords = [
            "election", "vote", "ballot", "president", "senator", "governor",
            "congress", "parliament", "policy", "bill", "legislation",
            "democrat", "republican", "campaign", "white house",
            "supreme court", "lawmaker", "administration",
        ]

        # 3) IMPORTANT articles
        self.important_keywords = [
            "breaking", "urgent", "emergency", "crisis", "public safety",
            "severe weather", "health advisory", "recall", "missing person",
            "natural disaster", "major update",
        ]

        # 4) NOT IMPORTANT articles
        self.not_important_keywords = [
            "celebrity", "gossip", "viral", "meme", "influencer",
            "entertainment", "fashion", "sports rumor", "pop culture",
        ]

    def classify_text(self, text: str) -> str:
        t = (text or "").lower()

        # 1) Non-US
        for k in self.non_us_keywords:
            if k in t:
                return "REMOVE"

        # 2) Political
        for k in self.political_keywords:
            if k in t:
                return "REMOVE"

        # 3) Important
        for k in self.important_keywords:
            if k in t:
                return "IMPORTANT"

        # 4) Not important
        for k in self.not_important_keywords:
            if k in t:
                return "NOT IMPORTANT"

        return "NEUTRAL"


def classify_article(article: str) -> str:
    """
    Compatibility helper (same idea as your friend's function).
    """
    return BasicArticleFilter().classify_text(article)


# --------------------------------------------------------
# PIPELINE
# --------------------------------------------------------
class EducationalFilterPipeline:
    """
    - Manual keyword filtering (BasicArticleFilter)
    - Simple educational scoring
    - DeepSeek: final ranking + sector + section
    """

    def __init__(self, deepseek_api_key: Optional[str] = None) -> None:
        # Use env var if present, else your provided key
        self.deepseek_api_key: str = (
            deepseek_api_key
            or os.environ.get("DEEPSEEK_API_KEY")
            or "HERE GOES THE DEEPSEEK KEY"
        )
        if not self.deepseek_api_key:
            raise ValueError("DeepSeek API key is not set")

        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"
        self.base_filter = BasicArticleFilter()

    # ---------- file helpers ----------

    @staticmethod
    def _today_raw_filename() -> str:
        stamp = datetime.today().strftime("%m%d%Y")
        return f"RAW_NEWS_{stamp}.json"

    @staticmethod
    def _today_filters_filename() -> str:
        stamp = datetime.today().strftime("%m%d%Y")
        return f"FILTERSFORDEEPSEEK_{stamp}.json"

    @staticmethod
    def _today_final_filename() -> str:
        stamp = datetime.today().strftime("%m%d%Y")
        return f"DEEPSEEKLISTFOR{stamp}.json"

    # ---------- basic text / scoring ----------

    @staticmethod
    def _normalize_text(article: Dict[str, Any]) -> str:
        title = (article.get("title") or "").lower()
        desc = (article.get("description") or "").lower()
        content = (article.get("content") or "").lower()

        raw = article.get("raw_api_data") or {}
        raw_content = (
            (raw.get("content") or "")
            or (raw.get("summary") or "")
        ).lower()

        return f"{title} {desc} {content} {raw_content}".strip()

    @staticmethod
    def _simple_educational_score(text: str) -> int:
        """
        Very light scoring: longer + 'why/how/explained/impact/analysis'.
        Just extra signal for DeepSeek, not the main ranking.
        """
        words = text.split()
        score = 0

        if len(words) > 30:
            score += 1
        if len(words) > 80:
            score += 1

        triggers = {
            "why": 2,
            "how": 2,
            "explained": 3,
            "analysis": 2,
            "impact": 3,
            "implications": 3,
            "consequences": 3,
            "crisis": 4,
            "geopolitical": 4,
            "supply chain": 3,
        }
        for kw, pts in triggers.items():
            if kw in text:
                score += pts

        return score

    # ---------- load + candidate selection ----------

    def load_raw_articles(self, path: str) -> List[Dict[str, Any]]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict) and "articles" in data:
            articles = data["articles"]
        elif isinstance(data, list):
            articles = data
        else:
            articles = []

        print(f"[IO] Loaded {len(articles)} raw articles from {path}")
        return articles

    def build_candidates(
        self,
        articles: List[Dict[str, Any]],
        max_candidates: int = 30,
    ) -> Dict[str, Any]:
        """
        Apply manual filter + simple scoring, return top `max_candidates`.
        """
        annotated: List[Dict[str, Any]] = []

        for art in articles:
            text = self._normalize_text(art)
            base_label = self.base_filter.classify_text(text)

            if base_label == "REMOVE":
                continue

            score = self._simple_educational_score(text)

            annotated.append(
                {
                    "id": art.get("id"),
                    "title": art.get("title"),
                    "description": art.get("description"),
                    "base_label": base_label,
                    "educational_score": score,
                }
            )

        # rank: IMPORTANT first, then score
        label_priority = {"IMPORTANT": 0, "NEUTRAL": 1, "NOT IMPORTANT": 2}
        annotated.sort(
            key=lambda a: (
                label_priority.get(a.get("base_label", "NEUTRAL"), 3),
                -a.get("educational_score", 0),
            )
        )

        top = annotated[:max_candidates]

        summary = {
            "total_articles": len(articles),
            "selected_count": len(top),
            "articles": top,
        }

        print(
            f"[FILTER] Candidates for DeepSeek: {summary['selected_count']} "
            f"out of {summary['total_articles']}"
        )
        return summary

    def save_filters_for_deepseek(self, summary: Dict[str, Any]) -> str:
        filename = self._today_filters_filename()
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"[IO] Saved DeepSeek prep file -> {filename}")
        return filename

    # ---------- DeepSeek prompt + call ----------

    def _build_deepseek_prompt(self, summary: Dict[str, Any]) -> str:
        candidates = summary.get("articles", [])

        allowed_sectors = [
            "Markets", "Economy", "Technology", "Finance",
            "Crypto", "Energy", "Politics", "Sustainability",
            "Business", "Health", "Transport", "Industrials",
        ]

        return f"""
You are helping choose the most educational business/finance news articles
for beginner readers.

Each candidate article has:
- id
- title
- description
- base_label  ("IMPORTANT", "NEUTRAL", "NOT IMPORTANT")
- educational_score  (integer, rough complexity signal)

You MUST:
1) Pick the best 10–15 articles for learning.
2) For each selected article:
   - Assign **sector**: EXACTLY ONE of:
     {allowed_sectors}
   - Assign **section**: a short newspaper-style subsection string (2–4 words),
     for example:
       "AI & Software"
       "Banking & Markets"
       "Economy & Policy"
       "Crypto & Regulation"
       "Energy & Climate"
       "Healthcare & Pharma"
       "Industrial & Supply Chain"
       "Transport & Logistics"

DIVERSITY RULE:
- The final selection MUST include articles from **at least 4 different sectors**
  if the content allows. Avoid concentrating everything in a single sector.

RETURN JSON ONLY in EXACTLY this shape (no explanations, no markdown, no extra keys):

{{
  "selected_articles": [
    {{"id": 1, "final_rank": 1, "sector": "Technology", "section": "AI & Software"}},
    {{"id": 5, "final_rank": 2, "sector": "Finance", "section": "Banking & Markets"}}
  ]
}}

Here are the candidate articles:

{json.dumps(candidates, indent=2)}
"""

    def call_deepseek(self, filters_file: str) -> List[Dict[str, Any]]:
        with open(filters_file, "r", encoding="utf-8") as f:
            prep = json.load(f)

        candidates = prep.get("articles", [])
        if not candidates:
            print("[DeepSeek] No candidates to rank.")
            return []

        prompt = self._build_deepseek_prompt(prep)

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

        print("[DeepSeek] Sending request to DeepSeek API...")
        try:
            r = requests.post(
                self.deepseek_url, headers=headers, json=payload, timeout=60
            )
        except Exception as e:
            print(f"[DeepSeek] Request failed: {e}")
            return []

        if r.status_code != 200:
            print(f"[DeepSeek] HTTP {r.status_code}: {r.text}")
            return []

        try:
            result = r.json()
            content = result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[DeepSeek] Error reading response JSON: {e}")
            return []

        # handle optional ```json fences
        if content.startswith("```"):
            # remove ```json ... ``` wrapper
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                content = content[start : end + 1]

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"[DeepSeek] Could not parse JSON: {e}")
            print("[DeepSeek] Raw content was:")
            print(content)
            return []

        selected = parsed.get("selected_articles", [])
        print(f"[DeepSeek] Selected {len(selected)} articles.")
        return selected

    # ---------- final output ----------

    def create_final_output_file(
        self,
        deepseek_results: List[Dict[str, Any]],
        original_articles: List[Dict[str, Any]],
    ) -> str:
        if not deepseek_results:
            print("[FINAL] No DeepSeek results to save.")
            return ""

        # build mapping from id -> {sector, section, rank}
        id_to_meta: Dict[int, Dict[str, Any]] = {}
        for item in deepseek_results:
            if item.get("id") is None:
                continue
            try:
                aid = int(item["id"])
            except (TypeError, ValueError):
                continue

            meta = {
                "sector": item.get("sector"),
                "ai_section": item.get("section"),
                "rank": int(item.get("final_rank", 0)),
            }
            id_to_meta[aid] = meta

        final_articles: List[Dict[str, Any]] = []
        for art in original_articles:
            aid = art.get("id")
            if aid in id_to_meta:
                meta = id_to_meta[aid]
                copy = art.copy()
                if meta.get("sector"):
                    copy["sector"] = meta["sector"]
                if meta.get("ai_section"):
                    copy["ai_section"] = meta["ai_section"]
                copy["educational_ranking"] = {
                    "rank": meta.get("rank", 0),
                    "selected_by": "deepseek_ai",
                }
                final_articles.append(copy)

        final_articles.sort(
            key=lambda x: x.get("educational_ranking", {}).get("rank", 9999)
        )

        filename = self._today_final_filename()
        output = {
            "metadata": {
                "version": "education_v1_deepseek_sector",
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "total_final_articles": len(final_articles),
                "notes": (
                    "Manual keyword filter + simple scoring; "
                    "DeepSeek assigns sector + section"
                ),
            },
            "articles": final_articles,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"[FINAL] Saved final article list -> {filename}")
        print(f"[FINAL] Final articles: {len(final_articles)}")
        return filename

    # ---------- top-level orchestration ----------

    def run_complete_pipeline(self, input_path: Optional[str] = None) -> None:
        if input_path is None:
            input_path = self._today_raw_filename()

        print("=" * 70)
        print("🚀 Educational Filter Pipeline (DeepSeek = sectors)")
        print("=" * 70)
        print(f"[STEP 1] Reading input file: {input_path}")

        if not os.path.exists(input_path):
            print(f"[ERROR] Input file not found: {input_path}")
            return

        raw_articles = self.load_raw_articles(input_path)
        if not raw_articles:
            print("[ERROR] No articles loaded, aborting.")
            return

        print(f"[INFO] Starting with {len(raw_articles)} raw articles.")

        print("[STEP 2] Manual keyword filtering + simple scoring...")
        summary = self.build_candidates(raw_articles, max_candidates=30)

        print("[STEP 3] Saving candidates for DeepSeek...")
        filters_file = self.save_filters_for_deepseek(summary)

        print("[STEP 4] Calling DeepSeek for final ranking + sectors...")
        deepseek_results = self.call_deepseek(filters_file)
        if not deepseek_results:
            print("[ERROR] DeepSeek did not return a valid ranking, aborting.")
            return

        print("[STEP 5] Creating final output file...")
        self.create_final_output_file(deepseek_results, raw_articles)

        print("=" * 70)
        print("✅ Pipeline complete. Ready for content generation.")
        print("=" * 70)

def lambda_handler(event, context):
    import boto3
    import os
    from datetime import datetime

    try:
        bucket = os.environ.get("BUCKET_NAME", "universityprojectbucket")
        news_prefix = "NewsCollector/"
        filt_prefix = "Filteration/"

        s3 = boto3.client("s3")

        # Use same date stamp convention as the rest of the pipeline
        stamp = datetime.today().strftime("%m%d%Y")

        # 1) Download RAW_NEWS_MMDDYYYY.json from S3 to /tmp
        raw_name = f"RAW_NEWS_{stamp}.json"
        raw_key = f"{news_prefix}{raw_name}"
        local_raw_path = os.path.join("/tmp", raw_name)

        s3.download_file(bucket, raw_key, local_raw_path)

        # 2) Run pipeline in /tmp so all new files are created there
        os.chdir("/tmp")
        pipeline = EducationalFilterPipeline()
        pipeline.run_complete_pipeline(input_path=local_raw_path)

        # 3) Figure out output filenames (pipeline uses these naming helpers)
        filters_name = pipeline._today_filters_filename()
        final_name = pipeline._today_final_filename()

        filters_path = os.path.join("/tmp", filters_name)
        final_path = os.path.join("/tmp", final_name)

        # 4) Upload FILTERS file (this SHOULD always exist)
        if not os.path.exists(filters_path):
            raise FileNotFoundError(f"Expected filters file not found: {filters_path}")

        filters_key = f"{filt_prefix}{filters_name}"
        s3.upload_file(filters_path, bucket, filters_key)

        uploaded = [f"s3://{bucket}/{filters_key}"]

        # 5) Upload final DeepSeek file ONLY if it was created
        if os.path.exists(final_path):
            final_key = f"{filt_prefix}{final_name}"
            s3.upload_file(final_path, bucket, final_key)
            uploaded.append(f"s3://{bucket}/{final_key}")

        return {
            "statusCode": 200,
            "body": "Uploaded: " + ", ".join(uploaded),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error in educational_filter_pipeline lambda_handler: {e}",
        }
