from src.language import parser
from src.results.statistics import Statistics_Manager
from src.search.mhs.mhs import MHS_Approach
from src.search.complete.complete import Complete_Approach
from src.visualization.diagram import Scenario_Diagram
import time
import logging

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
        logging.error(f"Invalid approach: {args.approach}")
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
    for idx, res in enumerate(succRes):
        stat_man.generate_update_save(idx, res)

        for sol_id, sol in enumerate(res.ordered_outcomes):
            if sol.is_concrete_solution:
                fileName = f"temp_diagram_{time.time()}_{idx}_{sol_id}.png"
                args.save_path = f"{args.upload_folder}/{fileName}"
                args.view_diagram = False
                sd = Scenario_Diagram(sol, f"{idx} {sol_id}", args)
                sd.generate_diagram()
                sd.save_and_show()
                fileNames.append(fileName)
    return fileNames
    