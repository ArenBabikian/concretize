
import logging
import time
import matplotlib.pyplot as plt
from scenic.domains.driving.workspace import Workspace

from src.model.constraints.danger_constraints import Collision_Con
import src.visualization.utils as utils
import src.visualization.colors as colors
from pathlib import Path

class Scenario_Diagram:

    def __init__(self, instance, diagram_id, args):
        self.spec = instance
        self.workspace = Workspace(instance.roadmap.drivableRegion)
        self.diagram = None # TODO remove this?

        #TODO improve below, avoid the "hasattr"
        self.view = args.view_diagram
        if hasattr(args, "save_path_png"):
            self.save_path = args.save_path_png
        else:
            self.save_path = Path(args.output_directory) / "scenarios" / f"{diagram_id}.png"
        self.zoom = args.zoom_diagram

        self.color_scheme = args.color_scheme
        self.hide_actors = args.hide_actors
        self.show_maneuvers = args.show_maneuvers
        self.show_exact_paths = args.show_exact_paths

    def show_road_map(self):
        if self.color_scheme == 'default':
            self.spec.roadmap.show()
        elif self.color_scheme == 'alternate':
            utils.show_alt_network(plt, self.spec.roadmap)


    def generate_diagram(self):
        fig = plt.figure(figsize=(10, 10), dpi=200)
        plt.gca().set_aspect('equal')
        
        # display map
        self.show_road_map()

        for i, ac in enumerate(self.spec.actors):
            # color = colors.COLOR_SEQ[i]
            color = ac.color

            # draw actors
            if not self.hide_actors:
                # TODO display actor ID on the image?
                logging.debug(f'{ac} positioned at {ac.position}')
                utils.show_object(plt, ac, color.default, size=(2, 4))

            if ac.assigned_maneuver_instance:
                region = ac.assigned_maneuver_instance.connectingLane
                # draw maneuver regions
                if self.show_maneuvers:
                    utils.show_region(plt, region, color.light)
                    if not self.show_exact_paths:
                        utils.show_arrows(plt, region.centerline, 'w', pointsDelts=-1, size=1.5)

                # draw exact paths
                if self.show_exact_paths:
                    utils.show_cl(plt, ac.assign_exact_path_for_vis, color.dark, '-', 2)
                    utils.show_arrows(plt, ac.assign_exact_path_for_vis, color.dark, pointsDelts=5, size=5)
        
        # draw overlap regions
        for c in self.spec.constraints:
            if isinstance(c, Collision_Con):
                if self.show_maneuvers:
                    r1 = c.actors[0].assigned_maneuver_instance.connectingLane
                    r2 = c.actors[1].assigned_maneuver_instance.connectingLane
                    utils.showPairwiseCollidingRegions(plt, [r1, r2], colors.gray, None)
                # if self.show_exact_paths:
                    # TODO handle visualization for the case where the exact paths are overlapping


        if self.zoom:
            if self.spec.specification.junction:
                utils.zoom_to_junction(plt, self.spec.specification.junction, margin=10)
            else:
                self.workspace.zoomAround(plt, self.spec.actors, expansion=1)

        self.diagram = None

    def save_and_show(self):
        if self.save_path:
            plt.savefig(self.save_path)
            print(f"Save at {self.save_path}")
            logging.info(f'Saved diagram at {self.save_path}')
        if self.view:
            logging.debug('Showing diagram of the initial scene')
            plt.show()
        plt.close()
    