from src.model.constraints.constraint import Behavior_Con

import logging
from src.model import utils
from src.model.maneuvers import Instance_Man, No_Man
import src.simulation.utils as sim_utils

class Does_Maneuver_Con(Behavior_Con):

    def __init__(self, parent, actors, maneuver):
        super().__init__(parent, "Does_Maneuver", actors, None) # TODO: Confirm
        self.arity = 2
        # self.type_id = ? # TODO
        self.maneuver_str = maneuver
        self.allowed_maneuver_types = self.get_allowed_path_regions(maneuver)
    
    def get_allowed_path_regions(self, maneuver):
        maneuver_str_list = maneuver.split('|')
        allowed_maneuver_list = []
        for m in maneuver_str_list:
            if m == "None":
                allowed_maneuver_list.append(No_Man())
            elif m in utils.MANEUVER_STRING_TO_CLASS:
                allowed_maneuver_list.extend(utils.MANEUVER_STRING_TO_CLASS[m])
            else:
                allowed_maneuver_list.append(Instance_Man(m))
        return allowed_maneuver_list

    def get_all_allowed_maneuver_instances(self, junction, keep_order=False):
        all_allowed_maneuver_instances = []
        if not keep_order:
            # Order by maneuver type
            for man_type in self.allowed_maneuver_types:
                all_allowed_maneuver_instances.extend(man_type.get_scenic_maneuver_instances(junction))
        else:
            # Maintian the order of the maneuver types as specified in the road map
            allowed_scenic_types = [x.get_scenic_maneuver_type() for x in self.allowed_maneuver_types]
            for m in junction.all_maneuvers:
                m_type_scenic = junction.instance_to_maneuver_type[m]
                if m_type_scenic in allowed_scenic_types:
                    all_allowed_maneuver_instances.append(m)

        if all_allowed_maneuver_instances == []:
            allowed_maneuver_types = [x for x in junction.maneuver_type_to_instance.keys() if junction.maneuver_type_to_instance[x] != []]
            raise Exception(f"No maneuvers of type <{self.maneuver_str}> are allowed at {junction}. Select among the following types {allowed_maneuver_types} or ids {[x.connectingLane.id for x in junction.all_maneuvers]}")

        return all_allowed_maneuver_instances

