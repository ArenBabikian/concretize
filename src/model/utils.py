from src.model.maneuvers import Go_Straight_Man, Left_Turn_Man, Right_Turn_Man, U_Turn_Man
from src.model.road_components import Junction_Type, Road_Type, Drivable_Type


MANEUVER_STRING_TO_CLASS = {
    'right_turn': [Right_Turn_Man()],
    'left_turn': [Left_Turn_Man()],
    'go_straight': [Go_Straight_Man()],
    'u_turn': [U_Turn_Man()],
    'any': [Right_Turn_Man(), Left_Turn_Man(), Go_Straight_Man(), U_Turn_Man()],
    }

# TODO: Map other region(type)s
ROAD_COMPONENT_STRING_TO_CLASS = {
    'Junction': Junction_Type(),
    'Road': Road_Type(),
    'Drivable': Drivable_Type()
    }