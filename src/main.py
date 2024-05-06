from pprint import pprint
from src.constraints.constraint import Actor
from src.constraints.position_constraints import Has_Behind_Con, Has_To_Left_Con, Has_In_Front_Con
import src.args as get_args
from src.search.mhs.mhs import MHS_Approach
import logging

from src.search.results2json import generate_json
from src.specification import Specification

def concretize():
    
    # 0 parse args
    args = get_args.parse_args()
    
    # 1 setup
    logging_map = {0: logging.CRITICAL, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
    logging.basicConfig(level=logging_map[args.verbosity])

    # 1.1 parse the map file
    map_file = args.map

    # 2 read scenario specification (constraints)
    specification_file = args.specification

    # TODO  1 parse the specification file
    #       return a list of constraints over objects
    #       Validation would also be integrated here

    # TODO MAP INTEGRATION

    # INFO as a sample, there would be an output like this as a result of the file parsing
    a0 = Actor(0, True)
    a1 = Actor(1)
    a2 = Actor(2)

    c1 = Has_In_Front_Con([a0, a1])
    c2 = Has_Behind_Con([a0, a2])

    #potentialy
    # c3 = TurnsLeft([a0]) # which would setthe a0.assigned_maneuver to TurnsLeft

    # out: a Specification object
    spec = Specification(map_file)
    spec.actors = [a0, a1, a2]
    spec.constraints = [c1, c2]

    # get the approach
    if args.approach == 'mhs':
        # TODO generalise this
        approach = MHS_Approach(args)
    elif args.approach == 'brute':
        exit(1)

    for run_id in range(args.num_of_runs):
        #   3 call the search approach
        res = approach.concretize(spec)

        #   4 save the result
        json_data = generate_json(res, args.store_all_outcomes)

        pprint(json_data)

    #     save the result
    #   4 visualize result
    #   5 simulate
    #   6 evaluate simulation run
    #   7 visualize the evaluation result
        pass