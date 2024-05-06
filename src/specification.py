import copy
from scenic.domains.driving.roads import Network

class Specification:
    def __init__(self, map_file):
        self.map_file = map_file
        self.map = self.parsemap(map_file)
        self.actors = None
        self.constraints = None
        self.tested_junction = None

    def parsemap(self, map_file):
        # TODO leverage Scenic
        return Network.fromFile(map_file)

    def __str__(self):
        return f"""
        Map: {self.map_file}
        Actors: {self.actors}
        Constraints: {self.constraints}
        """


class Specification_Instance:
    def __init__(self, specification):
        self.specification = specification
        # BIG TODO: integrate some kind of traceability to avod copying everything
        self.actors = copy.deepcopy(specification.actors)
        self.constraints = copy.copy(specification.constraints) # will still be connected to meta-actors. copy.deepcopy() is not working for some reason
        self.relink_consraints_to_actors()
        self.map = specification.map

        # post-run gathered data
        self.raw_res = None
        self.n_violations = None
        self.constraint2heuristic = None

    # TODO below is pretty ugly, tbh
    def relink_consraints_to_actors(self):
        for concrete_constraint in self.constraints:
            concrete_actor_list = []
            for meta_actor in concrete_constraint.actors:
                for concrete_actor in self.actors:
                    if concrete_actor.id == meta_actor.id:
                        concrete_actor_list.append(concrete_actor)
            concrete_constraint.actors = concrete_actor_list
