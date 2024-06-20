from src.model.constraints.constraint import Static_Con
from src.model.constraints.utils import get_container
import src.model.utils as utils
import logging

class On_Region_Con(Static_Con):

    def __init__(self, parent, actors, region):
        self.predicate_name = "On_Region"
        self.actors.append(self.get_region_from_str(region))
        super().__init__(parent, self.predicate_name, actors, None)
        self.arity = 2
        self.type_id = 0

    def get_heuristic_value(self):
        src_ac = self.actors[0]
        tgt = self.actors[1]
        container = get_container(tgt, self.roadmap)

        maxDist = 0
        # TODO optimize below?
        for corner in src_ac.get_rectangular_region().corners:
            dist = container.distanceTo(corner)
            if dist > maxDist:
                maxDist = dist
        return maxDist

    def get_region_from_str(self, region_str):
        if region_str in utils.ROAD_COMPONENT_STRING_TO_CLASS:
            return utils.ROAD_COMPONENT_STRING_TO_CLASS[region_str]
        else:
            logging.error(f"Invalid region type <{region_str}> in <{self}>. Select among the following types {list(utils.ROAD_COMPONENT_STRING_TO_CLASS.keys())}")
            exit(1)
