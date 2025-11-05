from abc import ABC, abstractmethod

class NewsFetcherStrategy(ABC):
    @abstractmethod
    def fetch_news(self):
        #Fetch news data from API
        pass
    
    @abstractmethod
    def save_news_to_file(self):
        #Save fetched data to a file
        pass