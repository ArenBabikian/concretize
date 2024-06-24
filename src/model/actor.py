from abc import ABC, abstractmethod

class Actor(ABC):
    def __init__(self, parent, name, isEgo, color, speed, controller, snap=False):
        self.id = name
        self.isEgo = isEgo
        self.color = color
        self.speed = speed
        self.controller = controller
        self.snap_to_waypoint = snap
        self.assigned_maneuver = None # Constraint object
        self.parent = parent
        self.position = [None, None, None]
        self.heading = None
        self.current_lane = None

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
    def __init__(self, parent, name, isEgo, color, speed, controller, snap=False): # TODO: No snap would be given in textX-generated model
        super().__init__(parent, name, isEgo, color, speed, controller, snap)
        self.width = 2
        self.length = 5

    def __str__(self):
        return f"Car {self.id}"


class Pedestrian(Actor):
    def __init__(self, parent, name, isEgo, color, speed, controller, snap=False):
        super().__init__(parent, name, isEgo, color, speed, controller, snap)
        self.width = 1
        self.length = 1

    def __str__(self):
        return f"Pedestrian {self.id}"
