from scenic.domains.driving.roads import Network

from src.model.actor import Actor

class Specification:
    def __init__(self, params, actors, constraints):
        self.params = params
        self.actors = actors
        self.constraints = constraints

        self.ego_id = self.get_ego_actor_id()

        # Added from CLI or grammar
        self.map_file = None
        self.roadmap = None
        self.junction = None

    def parsemap(self, map_file):
        # TODO leverage Scenic
        return Network.fromFile(map_file)
    
    def get_ego_actor_id(self):
        for i, actor in enumerate(self.actors):
            if actor.isEgo:
                return i
        return None

    def __str__(self):
        return f"""
        Map: {self.map_file}
        Actors: {self.actors}
        Constraints: {self.constraints}
        """


class Specification_Instance:
    def __init__(self, specification):
        self.specification = specification
        # BIG TODO: integrate some kind of traceability to avoid copying everything
        # TODO: copy.deepcopy has some trouble with models generated by textX somehow
        self.actors = self.deepcopy(specification.actors)
        self.constraints = self.deepcopy(specification.constraints) # will still be connected to meta-actors.
        self.relink_consraints_to_actors()
        self.roadmap = specification.roadmap

        # post-run gathered data
        self.raw_res = None
        self.n_violations = None
        self.constraint2heuristic = None

        # For scenario execution and visualisation
        self.is_concrete_solution = False
        self.measured_timeout = None

    def deepcopy(self, list_to_copy):
        # TODO optimize this to only deepcopy the necessary things
        elements = []
        for element in list_to_copy:
            newElement = element.__new__(element.__class__)
            for key, value in element.__dict__.items():
                setattr(newElement, key, value)
            elements.append(newElement)
        return elements
        

    # TODO below is pretty ugly, tbh
    def relink_consraints_to_actors(self):
        for concrete_constraint in self.constraints:
            concrete_actor_list = []
            for meta_actor in concrete_constraint.actors:
                if not isinstance(meta_actor, Actor):
                    concrete_actor_list.append(meta_actor)
                else:
                    for concrete_actor in self.actors:
                        if concrete_actor.id == meta_actor.id:
                            concrete_actor_list.append(concrete_actor)
            concrete_constraint.actors = concrete_actor_list
