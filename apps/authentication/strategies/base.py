from abc import ABC, abstractmethod

class BaseAuthStrategy(ABC):
    @abstractmethod
    def authenticate(self, credentials: dict):
        pass
