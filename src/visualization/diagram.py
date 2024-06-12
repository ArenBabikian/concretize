
import logging
import time
import matplotlib.pyplot as plt
from scenic.core.object_types import Object
from scenic.domains.driving.workspace import Workspace

from src.model.constraints.danger_constraints import Collision_Con
import src.visualization.utils as utils
import src.visualization.colors as colors
from pathlib import Path

class Scenario_Diagram:

    def __init__(self, instance, diagram_id, args):
        self.spec = instance
        self.workspace = Workspace(instance.roadmap.drivableRegion)
        self.diagram = None

        self.view = args.view_diagram
        self.save_path = Path(args.output_directory) / "scenarios" / f"{diagram_id}.png"
        self.zoom = args.zoom_diagram

        self.hide_actors = args.hide_actors
        self.show_maneuvers = args.show_maneuvers
        self.show_exact_paths = args.show_exact_paths

    def generate_diagram(self):
        fig = plt.figure()
        plt.gca().set_aspect('equal')
        # display map
        self.spec.roadmap.show()
        # self.workspace.show(plt)

        if self.show_maneuvers:
            # draw maneuver regions
            for i, ac in enumerate(self.spec.actors):
                if ac.assigned_maneuver_instance:
                    color = colors.COLOR_SEQ[i].light
                    region = ac.assigned_maneuver_instance.connectingLane
                    utils.show_region(plt, region, color)
            
            # draw overlap regions
            for c in self.spec.constraints:
                if isinstance(c, Collision_Con):
                    r1 = c.actors[0].assigned_maneuver_instance.connectingLane
                    r2 = c.actors[1].assigned_maneuver_instance.connectingLane
                    utils.showPairwiseCollidingRegions(plt, [r1, r2], colors.gray, None)

        # draw actors
        # TODO handle ego special case
        if not self.hide_actors:
            for i, ac in enumerate(self.spec.actors):
                color = colors.COLOR_SEQ[i].default
                logging.debug(f'{ac} positioned at {ac.position}')
                scenic_object = Object(position=ac.position, heading=ac.heading, width=ac.width, length=ac.length)
                scenic_object.color = color
                scenic_object.show(self.workspace, plt, False)

        # TODO this is from revious version
        # if params.get('view_path'):
        #     import scenic.core.map.map_backwards_utils as map_utils
        #     # Below is OLD. for when we were generating vehicles far from the intersection
        #     # import scenic.core.evol.map_utils as map_utils
        #     map_utils.handle_paths(scene, params, plt, includeLongPathToIntersection=False)

        if self.zoom:
            if self.spec.specification.junction:
                utils.zoom_to_junction(plt, self.spec.specification.junction, margin=3)
            else:
                self.workspace.zoomAround(plt, self.spec.actors, expansion=1)

        self.diagram = None

    def save_and_show(self):
        if self.save_path:
            plt.savefig(self.save_path)
            logging.info(f'Saved diagram at {self.save_path}')
        if self.view:
            logging.debug('Showing diagram of the initial scene')
            plt.show()
        plt.close()