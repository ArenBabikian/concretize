from abc import ABC, abstractmethod
import logging
from src.model import utils
import src.simulation.utils as sim_utils
from scenic.domains.driving.roads import ManeuverType

class Maneuver(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_scenic_maneuver_type(self):
        pass
    
    @abstractmethod
    def get_scenic_maneuver_instances(self, junction):
        pass

    def helper_scenic_mapping(self, junction, scenic_maneuver_type):
        if scenic_maneuver_type in junction.maneuver_type_to_instance:
            # if len(junction.maneuver_type_to_instance[scenic_maneuver_type]) != 0:
            return junction.maneuver_type_to_instance[scenic_maneuver_type]
        # # error handling
        # allowed_maneuver_types = [x for x in junction.maneuver_type_to_instance.keys() if junction.maneuver_type_to_instance[x] != []]
        # logging.error(f"No <{scenic_maneuver_type}> maneuvers are allowed at {junction}. Select among the following types {allowed_maneuver_types} or ids {[x.connectingLane.id for x in junction.all_maneuvers]}")
        # exit(1)

class Left_Turn_Man(Maneuver):
    def get_scenic_maneuver_type(self):
        return ManeuverType.LEFT_TURN
    
    def get_scenic_maneuver_instances(self, junction):
        return self.helper_scenic_mapping(junction, ManeuverType.LEFT_TURN)

class Right_Turn_Man(Maneuver):
    def get_scenic_maneuver_type(self):
        return ManeuverType.RIGHT_TURN
    
    def get_scenic_maneuver_instances(self, junction):
        return self.helper_scenic_mapping(junction, ManeuverType.RIGHT_TURN)

class Go_Straight_Man(Maneuver):
    def get_scenic_maneuver_type(self):
        return ManeuverType.STRAIGHT
    
    def get_scenic_maneuver_instances(self, junction):
        return self.helper_scenic_mapping(junction, ManeuverType.STRAIGHT)

class U_Turn_Man(Maneuver):
    def get_scenic_maneuver_type(self):
        return ManeuverType.U_TURN
    
    def get_scenic_maneuver_instances(self, junction):
        return self.helper_scenic_mapping(junction, ManeuverType.U_TURN)

class Instance_Man(Maneuver):
    def __init__(self, maneuver_id):
        self.maneuver_id = maneuver_id

    def get_scenic_maneuver_type(self):
        return None

    def get_scenic_maneuver_instances(self, junction):
        maneuver_w_id = list(filter(lambda x: x.connectingLane.uid == self.maneuver_id, junction.all_maneuvers))
        if len(maneuver_w_id) != 1:
            allowed_maneuver_ids = [f"{x.connectingLane.id}({sim_utils.get_type_string(x.type)})" for x in junction.all_maneuvers]
            raise Exception(f"Invalid maneuver <{self.maneuver_id}> at {junction}. Select among the following types {list(utils.MANEUVER_STRING_TO_CLASS.keys())} or maneuver ids {allowed_maneuver_ids}")
        return [maneuver_w_id[0]]

class No_Man(Maneuver):
    def get_scenic_maneuver_type(self):
        return None
    
    def get_scenic_maneuver_instances(self, _):
        return [None]