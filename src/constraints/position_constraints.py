from src.constraints.constraint import Constraint
import src.constraints.utils as utils
import math

class Has_To_Left_Con(Constraint):

    def __init__(self, actors):
        self.arity = 2
        self.type_id = 30
        super().__init__("Has_To_Left", actors, None)

    def get_heuristic_value(self):
        src_pos = self.actors[0].position
        src_heading = self.actors[0].heading
        tgt_pos = self.actors[1].position

        return utils.position_helper(src_pos, src_heading+(math.pi/2), tgt_pos, math.atan(2.5/2))


class Has_To_Right_Con(Constraint):

    def __init__(self, actors):
        self.arity = 2
        self.type_id = 31
        super().__init__("Has_To_Right", actors, None)

    def get_heuristic_value(self):
        src_pos = self.actors[0].position
        src_heading = self.actors[0].heading
        tgt_pos = self.actors[1].position

        return utils.position_helper(src_pos, src_heading-(math.pi/2), tgt_pos, math.atan(2.5/2))


class Has_In_Front_Con(Constraint):

    def __init__(self, actors):
        self.arity = 2
        self.type_id = 33
        super().__init__("Has_In_Front", actors, None)

    def get_heuristic_value(self):
        src_pos = self.actors[0].position
        src_heading = self.actors[0].heading
        tgt_pos = self.actors[1].position

        return utils.position_helper(src_pos, src_heading, tgt_pos, math.atan(2/5))


class Has_Behind_Con(Constraint):

    def __init__(self, actors):
        self.arity = 2
        self.type_id = 32
        super().__init__("Has_Behind", actors, None)

    def get_heuristic_value(self):
        src_pos = self.actors[0].position
        src_heading = self.actors[0].heading
        tgt_pos = self.actors[1].position

        return utils.position_helper(src_pos, src_heading+math.pi, tgt_pos, math.atan(2/5))

