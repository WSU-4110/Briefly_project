from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urlparse

class NewsHelper:
    def _extract_domain(self, url: str) -> str:
        try:
            net = urlparse(url).netloc.lower()
            return net.replace("www.", "")
        except Exception:
            return "unknown"

    def _normalize(
        self, source_name: str, title: str, url: str,
        description: str = "", published: str = "", image_url: str = "",
        language: str = "en", raw: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        return {
            "title": title or "",
            "description": description or "",
            "url": url or "",
            "source": source_name or "",
            "published_at": published or "",
            "api_source": source_name.lower(),
            "source_domain": self._extract_domain(url or ""),
            "image_url": image_url or "",
            "language": language or "en",
            "raw_api_data": raw or {},
        }

    def _basic_valid(self, a: Dict[str, Any]) -> bool:
        if not a.get("title") or not a.get("url"):
            return False
        t = (a.get("title") or "").lower()
        banned = ["celebrity", "horoscope", "lottery", "gossip"]
        return not any(b in t for b in banned)

    def _dedup(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out = []
        seen_urls = set()
        seen_title_pub = set()
        for it in items:
            link = (it.get("url") or "").strip().lower()
            key2 = ((it.get("title") or "").strip().lower(), (it.get("published_at") or "").strip())
            if link:
                if link in seen_urls:
                    continue
                seen_urls.add(link)
                out.append(it)
            else:
                if key2 in seen_title_pub:
                    continue
                seen_title_pub.add(key2)
                out.append(it)
        return out

    def _today_filename(self, prefix: str = "RAW_NEWS", ext: str = "json") -> str:
        stamp = datetime.today().strftime("%m%d%Y")
        return f"{prefix}_{stamp}.{ext}"

    def _title_contains_keyword(self, title: str, keyword: str) -> bool:
        return keyword.lower() in (title or "").lower()
