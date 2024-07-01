from pathlib import Path
from src import utils
from src.language import parser
from src.results.statistics import Statistics_Manager
from src.search.mhs.mhs import MHS_Approach
from src.search.complete.complete import Complete_Approach
from src.visualization.diagram import Scenario_Diagram
from src.simulation.simulation import Scenario_Simulation
from datetime import datetime
import logging

# Cache for solutions
# Key: filename; value: tuple(solution object, result id, concrete solution id)
solutionsCache = {}
ss = Scenario_Simulation(None)


def generateFromSpecs(constraintsStr, args):
    global solutionsCache
    gen_run_id = datetime.now().strftime('%y%m%d%H%M%S')

    spec = parser.parseStr(constraintsStr)
    
    # big TODO refactor to avoid redundant code with main.py
    for actor in spec.actors:
        actor.snap = True

    # initialize arguments
    # args.approach = "mhs"
    args.aggregation_strategy = "actors"
    # args.algorithm_name = "nsga2"
    args.restart_time = -1
    args.history = "none"
    args.num_of_mhs_runs = -1
    # args.num_of_scenarios = 3
    # args.color_scheme = "default"
    args.hide_actors = False
    args.view_diagram = False
    args.show_maneuvers = True
    args.show_exact_paths = True
    # args.timeout = 60
    args.zoom_diagram = True
    # args.map = "Town02"
    args.specification = "WEB EDITOR"
    args.store_all_outcomes = False
    args.output_directory = "../output"
    args.simulate = True
    args.simulation_path = "../output/simResults.xml" # irrelevant
    args.simulation_ip = "host.docker.internal"
    args.simulation_port = 2000
    args.save_simulation_stats = True
    # args.simulation_weather = "CloudyNoon"

    for param in spec.params:
        args.__dict__[param.key] = param.value
        
    Path(args.output_directory).mkdir(parents=True, exist_ok=True)
    args.upload_folder = Path(args.output_directory) / "scenarios"
    Path(args.upload_folder).mkdir(parents=True, exist_ok=True)
    args.save_statistics_file = f"stats_{gen_run_id}.json"

    map_file = utils.get_and_validate_map_file(args.map, "../maps")
    spec.map_file = map_file
    spec.roadmap = spec.parsemap(map_file)
    
    for constraint in spec.constraints:
        constraint.roadmap = spec.roadmap

    # Find appropriate approach 
    approach = None
    str2approach = {'mhs': MHS_Approach, 'complete': Complete_Approach}
    if args.approach not in str2approach:
        raise Exception(f"Invalid approach: {args.approach}")
    approach = str2approach[args.approach](args, spec)
    
    # Generate scenarios
    succRes = []


    stat_man = Statistics_Manager(args, spec)
    stat_man.save()
    
    approach.concretize()
    succRes = approach.all_solutions
    
    if not len(succRes):
        return None
    
    fileNames = []
    
    # Clear solutions cache
    solutionsCache = {}
    # ensure arguments are persisted
    solutionsCache["args"] = args
    
    for res_id, res in enumerate(succRes):
        stat_man.generate_update_save(res_id, res)

        con_sol_id = 0
        for sol_id, sol in enumerate(res.ordered_outcomes):
            if sol.is_concrete_solution:
                con_sol_id += 1
                fileName = f"sol_{gen_run_id}_{res_id}_{sol_id}.png"
                args.save_path_png = f"{args.upload_folder}/{fileName}"
                args.view_diagram = False
                sd = Scenario_Diagram(sol, f"{res_id} {sol_id}", args)
                sd.generate_diagram()
                sd.save_and_show()
                fileNames.append(fileName)
                # Save solution as tuple
                solutionsCache[fileName] = (sol, res_id, con_sol_id)
    return [args.upload_folder, fileNames]

def simulateSolution(filename):
    global solutionsCache
    global ss
    if not filename in solutionsCache:
        raise Exception(f"Could not find {filename} in solutions cache.")
    sol = solutionsCache[filename][0]
    res_id = solutionsCache[filename][1]
    con_sol_id = solutionsCache[filename][2]
    args = solutionsCache["args"]
    ss.update_args(args)
    sim_stats = ss.execute_simulation(sol, f"filename",)
    ss.save_and_update(sim_stats)