from pathlib import Path
from src import utils
import src.args as get_args
from src.results.statistics import Statistics_Manager
from src.search.complete.complete import Complete_Approach
from src.search.mhs.mhs import MHS_Approach
from src.language import parser
import logging

from src.model.specification import Specification
from src.simulation.json import Openscenario_Json
from src.simulation.simulation import Scenario_Simulation
from src.visualization.diagram import Scenario_Diagram
from src.simulation.xml import Openscenario_Xml

def concretize():
    
    # 0 parse args
    args = get_args.parse_args()
    
    # 1 setup
    logging_map = {0: logging.CRITICAL, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
    logging.root.setLevel(logging_map[args.verbosity])
    logging.warning("Fix the map integration in command-line options") # TEMP

    if args.output_directory is not None:
        Path(args.output_directory).mkdir(parents=True, exist_ok=True)

    # 2.0 read the scenario specification (constraints)
    # TODO address the case of a file being editted on a web-based editor

    specification_file = args.specification
    spec = parser.parse(specification_file)

    # TODO create a 'set_default_args' function
    for param in spec.params:
        args.__dict__[param.key] = param.value

    # 1.1 parse the map file
    map_file = utils.get_and_validate_map_file(args.map, "maps")
    spec.map_file = map_file
    spec.roadmap = spec.parsemap(map_file)

    # TODO: Make them optional attributes in the grammar
    for actor in spec.actors:
        actor.snap = True
    for constraint in spec.constraints:
        constraint.roadmap = spec.roadmap
    
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

    # Prepare the simulation container
    ss = Scenario_Simulation(args)

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
                # DIAGRAM
                scenario_id = f"{res_id}_{con_sol_id}"
                if args.view_diagram or args.save_diagram:
                    sd = Scenario_Diagram(sol, scenario_id, args)
                    sd.generate_diagram()
                    sd.save_and_show()

                con_sol_id+=1

                # TODO do we want to simulate every generated scenario?
                # TODO integrate the number of simulations
                # TODO below
                # if args.simulation_path:
                #     ss.save_executable()
                if args.simulate:
                    for sim_i in range(args.num_simulation_runs):
                        sim_stats = ss.execute_simulation(sol, f"{res_id}_{con_sol_id}_{sim_i}")
                        ss.save_and_update(sim_stats)

                # logging.warning("No save path provided. The scenario is not simulated")

    # 7 Save a single XML file for all scenarios
    if args.save_xml_json:
        scenario_id = f"all_scenarios"
        osxml = Openscenario_Xml(approach.all_solutions, args)
        osxml.generate_xml()
        osxml.save()

        osjson = Openscenario_Json(spec, approach.all_solutions, approach.collisions_in_order, args)
        osjson.generate_json()
        osjson.save()
    #   5 simulate
    #   6 evaluate simulation run
    #   7 visualize the evaluation result
        pass

    # save json for all