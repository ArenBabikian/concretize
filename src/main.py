import src.args as get_args
from src.results.statistics import Statistics_Manager
from src.search.complete.complete import Complete_Approach
from src.search.mhs.mhs import MHS_Approach
from src.language import parser
import logging

from src.model.specification import Specification
from src.simulation.simulation import Scenario_Simulation
from src.visualization.diagram import Scenario_Diagram

def concretize():
    
    # 0 parse args
    args = get_args.parse_args()
    
    # 1 setup
    logging_map = {0: logging.CRITICAL, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
    logging.root.setLevel(logging_map[args.verbosity])
    logging.warning("Fix the map integration in command-line options") # TEMP

    # 2.0 read the scenario specification (constraints)
    # TODO address the case of a file being editted on a web-based editor

    specification_file = args.specification
    spec = parser.parse(specification_file)

    for param in spec.params:
        args.__dict__[param.key] = param.value

    # 1.1 parse the map file
    map_file = args.map

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
    # TODO check duplicate actor IDs

    # 3.0 get the approach
    str2approach = {'mhs': MHS_Approach, 'complete': Complete_Approach}

    if args.approach not in str2approach:
        raise Exception(f"Invalid approach: {args.approach}")
    else:
        approach = str2approach[args.approach](args, spec)

    # Prepare the statistics container
    stat_man = Statistics_Manager(args, spec)
    stat_man.save()

    # 4.0 call the search approach
    approach.concretize()

    for res_id, res in enumerate(approach.all_solutions):
        #   5 save the result
        stat_man.generate_update_save(res_id, res)

        #   6 visualize 
        # TODO handle the case where many results are reurned by the same run
        # see also TODO in MHS_Apprach.concretize.'CRETE RESULT OBJECT'
        # TODO case where MHS oes not find a soolution, it is saving all partial solutions
        con_sol_id=0
        for sol_id, sol in enumerate(res.ordered_outcomes):
            if sol.is_concrete_solution:
                sd = Scenario_Diagram(sol, f"{res_id}_{con_sol_id}", args)
                sd.generate_diagram()
                sd.save_and_show()
                con_sol_id+=1

                # TODO do we want to simulate every generated scenario?
                ss = Scenario_Simulation(sol, f"{res_id}_{con_sol_id}", args)
                if args.simulation_path:
                    ss.save_executable()
                if args.simulate:
                    ss.execute_simulation()

                # logging.warning("No save path provided. The scenario is not simulated")

    #   5 simulate
    #   6 evaluate simulation run
    #   7 visualize the evaluation result
        pass

    # save json for all