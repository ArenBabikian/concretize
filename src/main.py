from src.constraints.constraint import Constraint
from src.constraints.distance_constraints import Is_Close_To_Con
from src.constraints.placement_constraints import On_Region_Con
from src.constraints.position_constraints import *
from src.model.actor import Actor, Car, Pedestrian
from src.model.road_components import Drivable_Type, Junction_Type, Road_Type
import src.args as get_args
from src.results.statistics import Statistics_Manager
from src.search.mhs.mhs import MHS_Approach
from src.language import parser
import logging
import pathlib

from src.model.specification import Specification
from src.visualization.diagram import Scenario_Diagram

def concretize():
    
    # 0 parse args
    args = get_args.parse_args()
    
    # 1 setup
    logging_map = {0: logging.CRITICAL, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
    logging.root.setLevel(logging_map[args.verbosity])
    logging.warning("Fix the map integration in command-line options") # TEMP 

    # 1.1 parse the map file
    map_file = args.map

    # 2.0 read the scenario specification (constraints)
    # TODO address the case of a file being editted on a web-based editor

    specification_file = args.specification
    spec = parser.parse(specification_file,
                        [Specification, Actor, Constraint,
                         Car, Pedestrian,
                         Has_To_Left_Con, Has_To_Right_Con, Has_Behind_Con, Has_In_Front_Con,
                         On_Region_Con])
    spec.map_file = map_file
    spec.roadmap = spec.parsemap(map_file)

    # TODO: Make them optional attributes in the grammar
    for actor in spec.actors:
        actor.snap = True
    for constraint in spec.constraints:
        constraint.roadmap = spec.roadmap

    # spec = Specification(map_file)

    # acs = []
    # acs.append(Car(0, True))
    # acs.append(Pedestrian(1, True))

    # cons = []
    # cons.append(Has_In_Front_Con([acs[0], acs[1]]))
    # cons.append(Is_Close_To_Con([acs[0], acs[1]]))
    # cons.append(On_Region_Con([acs[1], Junction_Type()], spec.roadmap))
    # cons.append(On_Region_Con([acs[0], Road_Type()], spec.roadmap))

    #potentialy
    # c3 = TurnsLeft([a0]) # which would setthe a0.assigned_maneuver to TurnsLeft
    # spec.actors = acs
    # spec.constraints = cons
    
    # 2.1 validate the scenario specification
    # TODO

    # 3.0 get the approach
    if args.approach == 'mhs':
        # TODO generalise this
        approach = MHS_Approach(args)
    elif args.approach == 'brute':
        exit(1)

    # Prepare the statistics container
    stat_man = Statistics_Manager(args, spec)
    stat_man.save()

    for run_id in range(args.num_of_runs):
        #   3 call the search approach
        res = approach.concretize(spec)
        logging.info(f"{'SUCC' if res.success else 'FAIL'}: Run {run_id} generated {res.n_solutions} solutions in {res.runtime} seconds.")

        #   4 save the result
        stat_man.generate_update_save(run_id, res)

        #   5 visualize 
        sd = Scenario_Diagram(res.ordered_outcomes[0], args)
        sd.generate_diagram()
        sd.save_and_show()

    #   5 simulate
    #   6 evaluate simulation run
    #   7 visualize the evaluation result
        pass

    # save json for all