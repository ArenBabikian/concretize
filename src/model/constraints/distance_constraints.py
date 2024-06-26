
from src.model.constraints import utils
from src.model.constraints.constraint import Static_Con

class Is_Close_To_Con(Static_Con):

    def __init__(self, parent, actors):
        self.arity = 2
        self.type_id = 40
        super().__init__(parent, "Is_Close_To", actors, None)

    def get_heuristic_value(self):
        src_pos = self.actors[0].position
        tgt_pos = self.actors[1].position
        # TODO below should be 0..10.
        # Tentatively 3..10 since not_overlaping is not implemented.
        return utils.distance_helper(src_pos, tgt_pos, 3, 10)


class Is_Medium_Distance_From_Con(Static_Con):

    def __init__(self, parent, actors):
        self.arity = 2
        self.type_id = 41
        super().__init__(parent, "Is_Med_Dist_From", actors, None)

    def get_heuristic_value(self):
        src_pos = self.actors[0].position
        tgt_pos = self.actors[1].position
        return utils.distance_helper(src_pos, tgt_pos, 10, 20)


class Is_Far_From_Con(Static_Con):

    def __init__(self, parent, actors):
        self.arity = 2
        self.type_id = 42
        super().__init__(parent, "Is_Far_From", actors, None)

    def get_heuristic_value(self):
        src_pos = self.actors[0].position
        tgt_pos = self.actors[1].position
        return utils.distance_helper(src_pos, tgt_pos, 20, 50)
    
