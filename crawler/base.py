from abc import ABC, abstractmethod


class BaseCrawler(ABC):
    def __init__(self, user_agents):
        self.user_agents = user_agents

    @abstractmethod
    def crawl(self):
        pass
