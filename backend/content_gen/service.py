import json, os
from pathlib import Path
from typing import List, Dict

from .strategies.strategy_interface import SummarizationStrategy
from .strategies.fast_ai_strategy import FastAIStrategy
from .strategies.detailed_ai_strategy import DetailedAIStrategy

INPUT_JSON = Path("backend/data/filtered_articles.json")
OUTPUT_JSON = Path("backend/out/enriched_articles.json")

class ContentGenService:
    def __init__(self, strategy: SummarizationStrategy):
        self.strategy = strategy

    def run(self) -> None:
        articles: List[Dict] = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
        out: List[Dict] = []
        for a in articles:
            text = a.get("text", "")
            res = self.strategy.generate(text)
            out.append({
                "id": a.get("id"),
                "source": a.get("source"),
                "ticker": a.get("ticker"),
                "genre": a.get("genre"),
                "published_at": a.get("published_at"),
                "title_ai": res.get("title", ""),
                "summary_ai": res.get("summary", ""),
                "strategy": type(self.strategy).__name__,
            })
        OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote: {OUTPUT_JSON} using {type(self.strategy).__name__}")

def _pick_strategy() -> SummarizationStrategy:
    name = (os.getenv("STRATEGY", "detailed") or "").lower()
    if name == "fast":
        return FastAIStrategy()
    return DetailedAIStrategy()

if __name__ == "__main__":
    svc = ContentGenService(_pick_strategy())
    svc.run()
