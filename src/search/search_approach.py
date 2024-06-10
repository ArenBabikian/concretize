from abc import ABC, abstractmethod

class Search_Approach(ABC):

    def __init__(self, args) -> None:
        self.solutions_found = 0
        self.num_required_solutions = args.num_of_scenarios

    @abstractmethod
    def concretize(self, specification):
        pass

    def all_sols_found(self):
        return (not self.num_required_solutions == -1) and self.solutions_found >= self.num_required_solutions
