from textx import metamodel_from_file
import pathlib
from src.model.constraints.danger_constraints import Collision_Con, Danger_Con
from src.model.constraints.constraint import Constraint
from src.model.constraints.distance_constraints import *
from src.model.constraints.placement_constraints import On_Region_Con
from src.model.constraints.position_constraints import *
from src.model.param import *
from src.model.constraints.behavior_constraints import *
from src.model.actor import Actor, Car, Pedestrian
from src.model.road_components import Drivable_Type, Junction_Type, Road_Type
from src.model.specification import Specification

COMPONENT_CLASSES = [Specification,
                         Param,
                         Actor,
                         Car, Pedestrian,
                         Constraint,
                         Static_Con,
                         Has_To_Left_Con, Has_To_Right_Con, Has_Behind_Con, Has_In_Front_Con, Is_Close_To_Con, Is_Medium_Distance_From_Con, Is_Far_From_Con,
                         On_Region_Con,
                         Behavior_Con, Does_Maneuver_Con, Danger_Con, Collision_Con]

baseFile = pathlib.Path(__file__).parent.resolve()

def parseStr(specification_str):
	metamodel = metamodel_from_file(f'{baseFile}/grammar.tx', classes = COMPONENT_CLASSES)
	model = metamodel.model_from_str(specification_str)
	return model

def parse(specification_file):
	metamodel = metamodel_from_file(f'{baseFile}/grammar.tx', classes = COMPONENT_CLASSES)
	model = metamodel.model_from_file(specification_file)
	# Also possible to just take a string:
	# model = metamodel.model_from_str(str)

	# TODO remove below?
	# for o in model.actors:
	# 	print(f"{type(o).__name__}: {o.__dict__}\n")
	# for o in model.constraints:
	# 	print(f"{type(o).__name__}: {o.__dict__}\n")

	return model
