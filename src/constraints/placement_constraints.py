from src.model.road_components import Junction_Type
from src.constraints.constraint import Constraint
import src.constraints.utils as utils

class On_Region_Con(Constraint):

    def __init__(self, parent, actors, region):
        self.parent = parent
        self.arity = 2
        self.type_id = 0
        if region == 'Junction':
            self.actors.append(Junction_Type())
        # TODO: Map other region(type)s
        super().__init__("On_Region", actors, None)

    def get_heuristic_value(self):
        src_ac = self.actors[0]
        tgt = self.actors[1]
        container = utils.get_container(tgt, self.roadmap)

        maxDist = 0
        for corner in src_ac.corners():
            dist = container.distanceTo(corner)
            if dist > maxDist:
                maxDist = dist
        return maxDist

