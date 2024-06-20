from abc import ABC, abstractmethod

class Result(ABC):

    def __init__(self, raw_result, specification):
        self.raw_res = raw_result
        self.specification = specification

        self.stats_map = {}

        self.runtime = None
        self.all_solutions = []
        self.ordered_outcomes = []

    @abstractmethod
    def update(self, specification=None):
        pass

    @abstractmethod
    def extend_stats_map(self, stor_all_outcomes=False):
        pass

    def update_stats_map(self, store_all_outcomes=False):
        self.stats_map['success'] = self.success
        self.stats_map['n_solutions'] = self.n_solutions
        self.stats_map['runtime'] = self.runtime
        n_constraints = len(self.specification.constraints)
        self.stats_map['n_constraints'] = n_constraints
        # data['restarts'] = res.restarts # TODO

        self.extend_stats_map(store_all_outcomes)

    @property
    def success(self):
        return self.n_solutions > 0
    
    @property
    def n_solutions(self):
        return len(self.all_solutions)
