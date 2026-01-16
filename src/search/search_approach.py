from abc import ABC, abstractmethod

class Search_Approach(ABC):

    def __init__(self, args, specification) -> None:
        self.specification = specification
        self.solutions_found = 0
        self.num_required_solutions = args.num_of_scenarios
        self.validate_input_specification()

        self.all_solutions = []
        self.collisions_in_order = []
    
    @abstractmethod
    def validate_input_specification(self):
        pass

    @abstractmethod
    def concretize(self):
        pass

    def all_sols_found(self):
        return (not self.num_required_solutions == -1) and self.solutions_found >= self.num_required_solutions
