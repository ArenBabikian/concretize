from src.language import parser
from src.search.mhs.mhs import MHS_Approach
from src.visualization.diagram import Scenario_Diagram
import time

def generateFromSpecs(constraintsStr, args):
    spec = parser.parseStr(constraintsStr)
    
    
    # TODO refactor to avoid redundant code with main.py
    for actor in spec.actors:
        actor.snap = True
    for param in spec.params:
        args.__dict__[param.key] = param.value


    spec.map_file = args.map_file
    spec.roadmap = spec.parsemap(args.map_file)
    
    for constraint in spec.constraints:
        constraint.roadmap = spec.roadmap

        
    approach = None
    if args.approach == 'mhs':
        # TODO implement other approaches when ready
        approach = MHS_Approach(args, spec)
    else:
        return None

    succRes = []
    approach.concretize()
    succRes = approach.all_solutions
    
    if not len(succRes):
        return None
    
    fileNames = []
    for idx, res in enumerate(succRes):
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
    