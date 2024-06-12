from abc import ABC, abstractmethod
import src.visualization.colors as colors

class Actor(ABC):
    def __init__(self, parent, actor_id, snap=False):
        self.id = actor_id
        self.snap_to_waypoint = snap
        self.assigned_maneuver = None # Constraint object
        self.parent = parent
        
        # Logical parameters
        self.assigned_maneuver_instance = None
        self.current_lane = None

        # Concrete parameters
        self.position = None
        self.heading = None
        self.assigned_exact_path = None # TODO not yet integrated

    @abstractmethod
    def __str__(self):
        pass

    def corners(self):
        x, y = self.position # TODO might need a fix
        w, l = self.width, self.length
        return [(x - w/2, y - l/2), (x + w/2, y - l/2), (x + w/2, y + l/2), (x - w/2, y + l/2)]

    def __repr__(self):
        return str(self)

class Car(Actor):
    def __init__(self, parent, name, snap=False): # TODO: No snap would be given in textX-generated model
        super().__init__(parent, name, snap)
        self.width = 2
        self.length = 5

    def __str__(self):
        return f"Car {self.id}"


class Pedestrian(Actor):
    def __init__(self, parent, name, snap=False):
        super().__init__(parent, name, snap)
        self.width = 1
        self.length = 1

    def __str__(self):
        return f"Pedestrian {self.id}"
