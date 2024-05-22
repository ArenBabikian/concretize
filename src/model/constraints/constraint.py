from abc import ABC, abstractmethod

# TODO some work here and in specification.py to clarify the conceptual abstrcation levels (what is meta, what is instance)

class Constraint(ABC):
    def __init__(self, name, actors, roadmap):
        self.predicate_name = name
        self.actors = actors
        self.roadmap = roadmap
        self.arity = None # TODO Might be irrelevant
        self.type_id = None # TODO remove this in the future
        # self.is_priority = None # Futurue Work

    @abstractmethod
    def get_heuristic_value(self):
        pass

    def is_satisfied(self):
        return self.get_heuristic_value() == 0

    def __str__(self):
        return f"{self.predicate_name}{self.actors}"

    def __repr__(self):
        return f"{self.predicate_name}{self.actors}"
