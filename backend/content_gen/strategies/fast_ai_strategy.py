from typing import Dict
from .strategy_interface import SummarizationStrategy

class FastAIStrategy(SummarizationStrategy):
    def generate(self, article_text: str) -> Dict[str, str]:
        t = " ".join((article_text or "").split())
        if not t:
            return {"title": "", "summary": ""}
        words = t.split()
        title = " ".join(w.capitalize() for w in words[:8])
        parts = [s.strip() for s in t.split(".") if s.strip()]
        summary = ". ".join(parts[:2])
        if summary and not summary.endswith("."):
            summary += "."
        return {"title": title, "summary": summary}
