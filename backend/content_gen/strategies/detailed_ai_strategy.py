from typing import Dict
from .strategy_interface import SummarizationStrategy

class DetailedAIStrategy(SummarizationStrategy):
    def generate(self, article_text: str) -> Dict[str, str]:
        t = " ".join((article_text or "").split())
        if not t:
            return {"title": "", "summary": ""}
        words = t.split()
        base = " ".join(words[:10]).strip()
        title = (base + " Update").strip()
        parts = [s.strip() for s in t.split(".") if s.strip()]
        picked = parts[:5]
        if not picked:
            return {"title": title, "summary": ""}
        out = []
        for i, s in enumerate(picked):
            if i == 0:
                out.append(s)
            elif i == 1:
                out.append(" Meanwhile, " + (s[0].lower() + s[1:] if len(s) > 1 else s))
            elif i == 2:
                out.append(" Additionally, " + (s[0].lower() + s[1:] if len(s) > 1 else s))
            elif i == 3:
                out.append(" As a result, " + (s[0].lower() + s[1:] if len(s) > 1 else s))
            else:
                out.append(" Looking ahead, " + (s[0].lower() + s[1:] if len(s) > 1 else s))
        summary = ". ".join(out)
        if summary and not summary.endswith("."):
            summary += "."
        return {"title": title, "summary": summary}
