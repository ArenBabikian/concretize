from abc import abstractmethod
import logging
from src.model.constraints.constraint import Constraint
from src.model.maneuvers import Go_Straight_Man, Instance_Man, Left_Turn_Man, Right_Turn_Man, U_Turn_Man

class Behavior_Con(Constraint):
    @abstractmethod
    def get_allowed_path_regions(self):
        pass

class Does_Maneuver_Con(Behavior_Con):

    def __init__(self, parent, actors, maneuver):
        super().__init__(parent, "Does_Maneuver", actors, None) # TODO: Confirm
        self.arity = 2
        # self.type_id = ? # TODO
        self.maneuver_str = maneuver
        self.allowed_maneuver_types = self.get_allowed_path_regions(maneuver)
    
    def get_allowed_path_regions(self, maneuver):
        srt_to_cls = {
            'right_turn': [Right_Turn_Man()],
            'left_turn': [Left_Turn_Man()],
            'go_straight': [Go_Straight_Man()],
            'u_turn': [U_Turn_Man()],
            'any': [Right_Turn_Man(), Left_Turn_Man(), Go_Straight_Man(), U_Turn_Man()],
            }
        
        if maneuver in srt_to_cls:
            return srt_to_cls[maneuver]
        else:
            return [Instance_Man(maneuver)]

    def get_all_allowed_maneuver_instances(self, junction):
        all_allowed_maneuver_instances = []
        for man_type in self.allowed_maneuver_types:
            all_allowed_maneuver_instances.extend(man_type.get_scenic_maneuver_instances(junction))
        if all_allowed_maneuver_instances == []:
            allowed_maneuver_types = [x for x in junction.maneuver_type_to_instance.keys() if junction.maneuver_type_to_instance[x] != []]
            logging.error(f"No maneuvers of type <{self.maneuver_str}> are allowed at {junction}. Select among the following types {allowed_maneuver_types} or ids {[x.connectingLane.id for x in junction.all_maneuvers]}")
            exit(1)

        return all_allowed_maneuver_instances

