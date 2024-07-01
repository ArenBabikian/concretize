from abc import ABC, abstractmethod
from src.model.speed_profile import Speed_Profile
import src.visualization.colors as colors
from scenic.core.regions import RectangularRegion
from shapely.geometry import Polygon


class Actor(ABC):
    def __init__(self, parent, name, isEgo, color, speed, controller, snap=False):
        self.id = name
        self.isEgo = isEgo
        self.color = colors.get_color_object(color if color else 'random')
        self.snap_to_waypoint = snap
        self.speed_id = speed
        self.controller = controller
        self.parent = parent

        # # Searched parameters
        # Logical parameters
        self.assigned_maneuver_instance = None

        # Concrete parameters
        self.position = None
        self.heading = None
        self.assign_exact_path_for_vis = None

        # Derived parameters
        self.speed_profile = Speed_Profile(self.speed_id)
        self.current_lane = None
        self.end_of_junction_point = None

    @abstractmethod
    def __str__(self):
        pass

    def get_rectangular_region(self, custom_size=None, multiplier=1.0):
        pos, head = self.position, self.heading
        if custom_size is None:
            custom_size = (self.width, self.length)
        width, length = custom_size
        custom_size = [width * multiplier, length + width * (multiplier-1)]
        return RectangularRegion(pos, head, custom_size[0], custom_size[1])

    @property
    def polygon(self):
        # position, heading, hw, hl = self.position, self.heading, self.width, self.length
        # corners = _RotatedRectangle.makeCorners(position.x, position.y, heading, hw, hl)
        return Polygon(self.get_rectangular_region().corners)

    @property
    def corners(self):
        x, y = self.position # TODO might need a fix
        w, l = self.width, self.length
        return [(x - w/2, y - l/2), (x + w/2, y - l/2), (x + w/2, y + l/2), (x - w/2, y + l/2)]
    
    def overlaps_with(self, other):
        self_polygon = self.polygon
        other_polygon = other.polygon
        return self_polygon.intersects(other_polygon)

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
    def __init__(self, parent, name, speed, snap=False):
        super().__init__(parent, name, False, None, speed, None, snap)
        self.width = 1
        self.length = 1

    def __str__(self):
        return f"Pedestrian {self.id}"
