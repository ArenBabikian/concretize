from abc import abstractmethod
import logging
from src.model.constraints.constraint import Constraint
from scenic.core.regions import EmptyRegion, PointSetRegion, PolylineRegion

class Danger_Con(Constraint):
    @abstractmethod
    def evaluate_logical_condition(self):
        pass

    @abstractmethod
    def evaluate_concrete_condition(self):
        pass

class Collision_Con(Danger_Con):

    def __init__(self, parent, actors):
        self.arity = 2
        # self.type_id = ? # TODO
        self.ensure_centerline_intersection = True # TODO make customizable
        self.size_threshold = 2*4.5

        self.coll_region = None
        self.coll_heuristic = None

        super().__init__(parent, "Collision", actors, None)

    def evaluate_logical_condition(self):
        reg, heu = self.get_logical_condition_results()
        self.coll_region = reg
        self.coll_heuristic = heu
        return reg, heu

    def get_logical_condition_results(self):
        """Returns the collision region between the regions assigned to the actors, if any, and a (preliminary, dichotomous) heuristic value (0 if collision, 1 otherwise)"""

        reg1 = self.actors[0].assigned_maneuver_instance.connectingLane
        reg2 = self.actors[1].assigned_maneuver_instance.connectingLane

        try:
            collision_reg = reg1.intersect(reg2)
        except:
            return EmptyRegion(''), 1
        
        # CASE 1: one of the regions if None
        if isinstance(collision_reg, EmptyRegion):
            return collision_reg, 1
        
        # CASE 2: false positive: overlap is a line or a point
        if isinstance(collision_reg, PointSetRegion) or isinstance(collision_reg, PolylineRegion):
            logging.debug('Overlap is a line or point.')
            return EmptyRegion(''), 1
        
        # CASE 3: overlap is a very small region
        areaOverapprox = sum(collision_reg.cumulativeTriangleAreas)
        if areaOverapprox < self.size_threshold:
            logging.debug('Overlap is too small to be considered a collision.')
            return EmptyRegion(''), 1
        
        if self.ensure_centerline_intersection:
            cl1 = reg1.centerline
            cl2 = reg2.centerline
            cl1_collision = cl1.intersect(collision_reg)
            cl2_collision = cl2.intersect(collision_reg)
            if isinstance(cl1_collision, EmptyRegion) and isinstance(cl2_collision, EmptyRegion):
                return collision_reg, 1
        
        return collision_reg, 0
    
    def evaluate_concrete_condition(self):
        # TODO
        pass