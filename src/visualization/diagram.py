
import logging
import time
import matplotlib.pyplot as plt
from scenic.core.object_types import Object
from scenic.domains.driving.workspace import Workspace


class Scenario_Diagram:

    def __init__(self, instance, args):
        self.spec = instance
        self.workspace = Workspace(instance.roadmap.drivableRegion)
        self.diagram = None

        self.view = args.view_diagram
        self.save_path = args.save_path_diagram
        self.zoom = args.zoom_diagram

    def generate_diagram(self):
        fig = plt.figure()
        plt.gca().set_aspect('equal')
        # display map
        self.spec.roadmap.show()
        # self.workspace.show(plt)

        # draw objects
        for ac in self.spec.actors:
            logging.debug(f'{ac} positioned atr {ac.position}')
            scenic_object = Object(position=ac.position, heading=ac.heading, width=ac.width, length=ac.length)
            scenic_object.show(self.workspace, plt, True)

        # TODO this is from revious version
        # if region_to_show is not None:
        #     region_to_show.show(plt, color='k')

        # TODO this is from revious version
        # if params.get('view_path'):
        #     import scenic.core.map.map_backwards_utils as map_utils
        #     # Below is OLD. for when we were generating vehicles far from the intersection
        #     # import scenic.core.evol.map_utils as map_utils
        #     map_utils.handle_paths(scene, params, plt, includeLongPathToIntersection=False)

        if self.zoom:
            # TODO Add support for zooming to specific junction
            # if scene.params.get('intersectiontesting') != None:
            #     zoomToIntersection(scene, plt)
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