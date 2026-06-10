from abc import ABC, abstractmethod

class BaseOTPProvider(ABC):
    @abstractmethod
    def send_otp(self, destination: str, code: str, purpose: str = 'verification') -> bool:
        pass
