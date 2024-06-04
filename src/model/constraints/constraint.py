from abc import ABC

# TODO some work here and in specification.py to clarify the conceptual abstrcation levels (what is meta, what is instance)

class Constraint(ABC):
    def __init__(self, parent, name, actors, roadmap):
        self.predicate_name = name
        self.parent = parent
        self.actors = actors
        self.roadmap = roadmap
        self.arity = None # TODO Might be irrelevant
        self.type_id = None # TODO remove this in the future
        # self.is_priority = None # Futurue Work

    def __str__(self):
        return f"{self.predicate_name}{self.actors}"

    def __repr__(self):
        return f"{self.predicate_name}{self.actors}"
