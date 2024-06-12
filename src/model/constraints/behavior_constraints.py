from src.model.constraints.constraint import Behavior_Con

class Danger_Con(Behavior_Con):
    pass

class Does_Maneuver_Con(Behavior_Con):

    def __init__(self, parent, actors, maneuver):
        self.arity = 2
        # self.type_id = ? # TODO
        self.maneuver = maneuver # TODO: Confirm
        super().__init__(parent, "Does_Maneuver", actors, None) # TODO: Confirm

    def get_heuristic_value(self):
        return 0 # TODO: Delete this method after behavior constraints are supported
    
    def get_possible_paths(self): # TODO: Confirm naming and implement
        return []

class Collision_Con(Danger_Con):

    def __init__(self, parent, actors):
        self.arity = 2
        # self.type_id = ? # TODO
        super().__init__(parent, "Collision", actors, None) # TODO: Confirm

    def get_heuristic_value(self):
        return 0 # TODO: Delete this method after behavior constraints are supported
    
    def get_possible_paths(self): # TODO: Confirm naming and implement
        return []
