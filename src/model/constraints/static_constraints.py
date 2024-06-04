from abc import abstractmethod
from src.model.constraints.constraint import Constraint

class Static_Con(Constraint):
    @abstractmethod
    def get_heuristic_value(self):
        pass

    def is_satisfied(self):
        return self.get_heuristic_value() == 0
