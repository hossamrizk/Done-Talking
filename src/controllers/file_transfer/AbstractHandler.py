from abc import ABC, abstractmethod

class AbstractHandler(ABC):
    """
    Abstract base class for file transfer handlers.
    """

    @abstractmethod
    def get_file_path(self, *args, **kwargs) -> str:
        
        pass