from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def can_handle(self, task_type: str) -> bool:
        pass

    @abstractmethod
    def perform_task(self, data: dict, context: dict = None):
        pass
