from abc import ABC, abstractmethod
from typing import Dict

class SummarizationStrategy(ABC):
    @abstractmethod
    def generate(self, article_text: str) -> Dict[str, str]:
        pass
