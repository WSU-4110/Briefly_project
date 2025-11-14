from abc import ABC, abstractmethod

class NewsFetcherStrategy(ABC):
    """Strategy interface for different news providers."""

    @abstractmethod
    def fetch_news(self, ticker=None):
        """Fetch data from the specific API."""
        pass

    @abstractmethod
    def save_news_to_file(self):
        """Fetch and save data to a file."""
        pass
