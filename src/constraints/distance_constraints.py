
from src.constraints import utils
from src.constraints.constraint import Constraint

class Is_Close_To_Con(Constraint):

    def __init__(self, actors):
        self.arity = 2
        self.type_id = 40
        super().__init__("Is_Close_To", actors, None)

    def get_heuristic_value(self):
        src_pos = self.actors[0].position
        tgt_pos = self.actors[1].position
        return utils.distance_helper(src_pos, tgt_pos, 0, 10)


class Is_Medium_Distance_From_Con(Constraint):

    def __init__(self, actors):
        self.arity = 2
        self.type_id = 41
        super().__init__("Is_Med_Dist_From", actors, None)

    def get_heuristic_value(self):
        src_pos = self.actors[0].position
        tgt_pos = self.actors[1].position
        return utils.distance_helper(src_pos, tgt_pos, 10, 20)


class Is_Far_From_Con(Constraint):

    def __init__(self, actors):
        self.arity = 2
        self.type_id = 42
        super().__init__("Is_Far_From", actors, None)

    def get_heuristic_value(self):
        src_pos = self.actors[0].position
        tgt_pos = self.actors[1].position
        return utils.distance_helper(src_pos, tgt_pos, 20, 50)
    
