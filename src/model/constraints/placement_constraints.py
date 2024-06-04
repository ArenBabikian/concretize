from src.model.road_components import Junction_Type
from src.model.constraints.static_constraints import Static_Con
import src.model.constraints.utils as utils

class On_Region_Con(Static_Con):

    def __init__(self, parent, actors, region):
        self.actors.append(get_region_from_str(region))
        super().__init__(parent, "On_Region", actors, None)
        self.arity = 2
        self.type_id = 0

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

def get_region_from_str(region_str):
    if region_str == 'Junction':
        return Junction_Type()
    # TODO: Map other region(type)s
