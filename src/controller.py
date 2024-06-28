from src.language import parser
from src.results.statistics import Statistics_Manager
from src.search.mhs.mhs import MHS_Approach
from src.search.complete.complete import Complete_Approach
from src.visualization.diagram import Scenario_Diagram
from src.simulation.simulation import Scenario_Simulation
import datetime
import logging

# Cache for solutions
# Key: filename; value: tuple(solution object, result id, concrete solution id)
solutionsCache = {}

def generateFromSpecs(constraintsStr, args):
    spec = parser.parseStr(constraintsStr)
    
    
    # TODO refactor to avoid redundant code with main.py
    for actor in spec.actors:
        actor.snap = True
    for param in spec.params:
        args.__dict__[param.key] = param.value


    spec.map_file = args.map
    spec.roadmap = spec.parsemap(args.map)
    
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
        stat_man.generate_update_save(idx, res)

        con_sol_id = 0
        for sol_id, sol in enumerate(res.ordered_outcomes):
            if sol.is_concrete_solution:
                con_sol_id += 1
                fileName = f"sol_{datetime.now.strftime("%y%m%d%H%M%S")}_{res_id}_{sol_id}.png"
                args.save_path_png = f"{args.upload_folder}/{fileName}"
                args.view_diagram = False
                sd = Scenario_Diagram(sol, f"{res_id} {sol_id}", args)
                sd.generate_diagram()
                sd.save_and_show()
                fileNames.append(fileName)
                # Save solution as tuple
                solutionsCache[fileName] = (sol, res_id, con_sol_id)
    return fileNames

def simulateSolution(filename):
    if not filename in solutionsCache:
        raise Exception(f"Could not find {filename} in solutions cache.")
    sol = solutionsCache[filename][0]
    res_id = solutionsCache[filename][1]
    con_sol_id = solutionsCache[filename][2]
    args = solutionsCache["args"]
    ss = Scenario_Simulation(sol, f"{res_id}_{con_sol_id}", args)
    ss.execute_simulation()