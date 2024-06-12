from src.language import parser
from src.search.mhs.mhs import MHS_Approach
from src.visualization.diagram import Scenario_Diagram
import time

def generateFromSpecs(constraintsStr, args, mapFileLoc = "../maps/town02.xodr"):
    model = parser.parseStr(constraintsStr)
    model.map_file = mapFileLoc
    model.roadmap = model.parsemap(mapFileLoc)
    
    # TODO refactor to avoid redundant code with main.py
    for actor in model.actors:
        actor.snap = True
    for constraint in model.constraints:
        constraint.roadmap = model.roadmap
    for param in model.params:
        args.__dict__[param.key] = param.value
        
    approach = None
    if args.approach == 'mhs':
        # TODO implement other approaches when ready
        approach = MHS_Approach(args)
    else:
        return None

    succRes = None
    for run_id in range(args.num_of_runs):
        res = approach.concretize(model)
        if res.success:
            succRes = res
            break
    
    if succRes is None:
        return None
    

    fileName = f"temp_diagram_{time.time()}.png"
    args.save_path_diagram = f"{args.upload_folder}/{fileName}"
    args.view_diagram = False
    sd = Scenario_Diagram(succRes.ordered_outcomes[0], args)
    sd.generate_diagram()
    sd.save_and_show()
    return fileName
    