# File: daily_content_generator.py
#
# Purpose:
#   - Take final filtered articles (DEEPSEEKLISTFOR_MMDDYYYY.json)
#   - Use DeepSeek to generate a creative title + short description
#   - Keep sector + date from input
#   - Output DAILY_CONTENT_MMDDYYYY.json with top 10 articles

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests


class DailyContentGenerator:
    """
    Watered-down content generator:

    INPUT:
      - DEEPSEEKLISTFOR_MMDDYYYY.json
        {
          "metadata": { ... },
          "articles": [
            {
              "id": ...,
              "title": "...",
              "description": "...",
              "published_at": "...",
              "sector": "...",         # if present
              "educational_ranking": { "rank": 1, ... },
              ...
            },
            ...
          ]
        }

    OUTPUT:
      - DAILY_CONTENT_MMDDYYYY.json
        {
          "generation_date": "YYYY-MM-DD",
          "total_articles": 10,
          "articles": [
            {
              "id": ...,
              "sector": "...",
              "date": "YYYY-MM-DD",
              "title": "...",         # DeepSeek creative title
              "description": "..."    # DeepSeek short description
            },
            ...
          ]
        }
    """

    def __init__(self, deepseek_api_key: Optional[str] = None) -> None:
        # Use env var if present, else fallback to your provided key
        self.deepseek_api_key: str = (
            deepseek_api_key
            or os.environ.get("DEEPSEEK_API_KEY")
            or "HERE GOES THE DEEP KEY"
        )
        if not self.deepseek_api_key:
            raise ValueError("DeepSeek API key is not set")

        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"

        # Today’s stamp (MMDDYYYY) for filenames
        stamp = datetime.today().strftime("%m%d%Y")
        self.input_filename = f"DEEPSEEKLISTFOR{stamp}.json"
        self.output_filename = f"DAILY_CONTENT_{stamp}.json"

        print("🚀 Daily Content Generator (simplified)")
        print(f"📁 Input:  {self.input_filename}")
        print(f"📁 Output: {self.output_filename}")
        print("=" * 60)

    # --------------------------------------------------
    # I/O helpers
    # --------------------------------------------------
    def load_final_articles(self) -> List[Dict[str, Any]]:
        try:
            with open(self.input_filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Input file not found: {self.input_filename}")
            return []
        except Exception as e:
            print(f"❌ Error reading {self.input_filename}: {e}")
            return []

        articles = data.get("articles", [])
        print(f"📚 Loaded {len(articles)} final articles from filter step")
        return articles

    @staticmethod
    def _sort_and_take_top10(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        def rank_of(a: Dict[str, Any]) -> int:
            return a.get("educational_ranking", {}).get("rank", 9999)

        sorted_articles = sorted(articles, key=rank_of)
        top10 = sorted_articles[:10]
        print(f"🎯 Taking top {len(top10)} articles by educational_ranking.rank")
        return top10

    # --------------------------------------------------
    # DeepSeek call
    # --------------------------------------------------
    def _build_prompt(self, article: Dict[str, Any]) -> str:
        original_title = article.get("title", "") or ""
        original_desc = article.get("description", "") or ""
        sector = article.get("sector", "Unknown") or "Unknown"
        published_at = article.get("published_at", "") or ""

        return f"""
You are rewriting a finance/news article for a student project.

You are given:
- Original title: {original_title}
- Original description: {original_desc}
- Sector: {sector}
- Published at: {published_at}

Your job:
- Keep the meaning of the article.
- Make the title more creative, engaging, and curiosity-inducing.
- Make the description 2–3 natural sentences, clear and educational.
- No bullet points, no lists, no hashtags, no emojis.
- Simple language. No jargon-heavy phrases.

Return ONLY a JSON object in this exact shape:

{{
  "title": "<new creative title>",
  "description": "<2–3 sentence explanation, plain text>"
}}
"""

    def _call_deepseek_for_article(self, article: Dict[str, Any]) -> Dict[str, str]:
        """
        Call DeepSeek to generate {title, description} for a single article.
        On failure, falls back to a simple local rewrite.
        """
        prompt = self._build_prompt(article)

        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.5,
            "max_tokens": 400,
        }

        try:
            resp = requests.post(
                self.deepseek_url, headers=headers, json=payload, timeout=40
            )
        except Exception as e:
            print(f"❌ DeepSeek request error (id={article.get('id')}): {e}")
            return self._fallback_content(article)

        if resp.status_code != 200:
            print(
                f"❌ DeepSeek HTTP {resp.status_code} "
                f"for id={article.get('id')} -> {resp.text[:200]}"
            )
            return self._fallback_content(article)

        try:
            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"❌ DeepSeek response parse error (id={article.get('id')}): {e}")
            return self._fallback_content(article)

        # Strip optional ```json fences
        if content.startswith("```"):
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                content = content[start : end + 1]

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            print(f"⚠️ DeepSeek returned non-JSON content (id={article.get('id')})")
            print(content)
            return self._fallback_content(article)

        new_title = parsed.get("title") or article.get("title", "")
        new_desc = parsed.get("description") or article.get("description", "")

        return {
            "title": new_title.strip(),
            "description": new_desc.strip(),
        }

    @staticmethod
    def _fallback_content(article: Dict[str, Any]) -> Dict[str, str]:
        """
        Very simple fallback if DeepSeek fails.
        """
        base_title = article.get("title", "") or ""
        base_desc = article.get("description", "") or ""
        return {
            "title": f"Explainer: {base_title[:80]}",
            "description": base_desc or "This article covers an important development in the markets.",
        }

    # --------------------------------------------------
    # Final assembly
    # --------------------------------------------------
    @staticmethod
    def _extract_date(published_at: str) -> str:
        """
        Returns just YYYY-MM-DD if possible, else the raw string.
        """
        if not published_at:
            return ""
        # Try ISO-like first 10 chars: "YYYY-MM-DD"
        if len(published_at) >= 10 and published_at[4] == "-" and published_at[7] == "-":
            return published_at[:10]
        # Fallback: just return as-is
        return published_at

    def generate_daily_content(self) -> None:
        articles = self.load_final_articles()
        if not articles:
            print("❌ No articles available. Exiting.")
            return

        top_articles = self._sort_and_take_top10(articles)

        final_items: List[Dict[str, Any]] = []

        for art in top_articles:
            aid = art.get("id")
            print(f"\n📝 Processing article id={aid}")
            deepseek_result = self._call_deepseek_for_article(art)

            sector = art.get("sector", "Unknown") or "Unknown"
            date_str = self._extract_date(art.get("published_at", "") or "")

            final_items.append(
                {
                    "id": aid,
                    "sector": sector,
                    "date": date_str,
                    "title": deepseek_result["title"],
                    "description": deepseek_result["description"],
                }
            )

        out = {
            "generation_date": datetime.utcnow().date().isoformat(),
            "total_articles": len(final_items),
            "articles": final_items,
        }

        try:
            with open(self.output_filename, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2, ensure_ascii=False)
            print("\n✅ DAILY CONTENT GENERATED")
            print(f"💾 Saved -> {self.output_filename}")
        except Exception as e:
            print(f"❌ Error saving {self.output_filename}: {e}")


def main() -> None:
    gen = DailyContentGenerator()
    gen.generate_daily_content()


if __name__ == "__main__":
    main()

def lambda_handler(event, context):
    import boto3
    import os
    from datetime import datetime

    try:
        bucket = os.environ.get("BUCKET_NAME", "universityprojectbucket")
        filt_prefix = "Filteration/"
        final_prefix = "FinalArticles/"

        s3 = boto3.client("s3")

        # Use same date stamp style as the generator
        stamp = datetime.today().strftime("%m%d%Y")

        # 1) Ensure we write/read in /tmp
        os.chdir("/tmp")

        # 2) Download DEEPSEEKLISTFORMMDDYYYY.json from S3
        input_name = f"DEEPSEEKLISTFOR{stamp}.json"
        input_key = f"{filt_prefix}{input_name}"
        local_input = os.path.join("/tmp", input_name)

        s3.download_file(bucket, input_key, local_input)

        # 3) Run daily content generator (it will read DEEPSEEKLISTFOR... from CWD)
        gen = DailyContentGenerator()
        gen.generate_daily_content()

        # 4) Upload DAILY_CONTENT_MMDDYYYY.json to FinalArticles/
        output_name = gen.output_filename  # already set in __init__
        local_output = os.path.join("/tmp", output_name)
        output_key = f"{final_prefix}{output_name}"

        s3.upload_file(local_output, bucket, output_key)

        return {
            "statusCode": 200,
            "body": f"Uploaded {output_name} to s3://{bucket}/{output_key}",
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error in daily_content_generator lambda_handler: {e}",
        }
