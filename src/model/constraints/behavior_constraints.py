from src.model.constraints import utils
from src.model.constraints.constraint import Constraint

class Behavior_Con(Constraint):
    pass
    
class Danger_Con(Behavior_Con):
    pass

class Does_Maneuver_Con(Behavior_Con):

    def __init__(self, parent, actors, maneuver):
        self.arity = 2
        # self.type_id = ? # TODO
        self.maneuver = maneuver # TODO: Confirm
        super().__init__(parent, "Does_Maneuver", actors, None) # TODO: Confirm

    def get_heuristic_value(self):
        return 0 # TODO

class Collision_Con(Danger_Con):

    def __init__(self, parent, actors):
        self.arity = 2
        # self.type_id = ? # TODO
        super().__init__(parent, "Collision", actors, None) # TODO: Confirm

    def get_heuristic_value(self):
        return 0 # TODO
