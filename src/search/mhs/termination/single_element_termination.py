from abc import ABC, abstractmethod

class SingleElementTermination(ABC):

    @abstractmethod
    def single_element_validity(self, fitness):
        pass