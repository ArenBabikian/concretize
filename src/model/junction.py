import logging
from scenic.domains.driving.roads import ManeuverType
from scenic.core.regions import PolygonalRegion

class Junction:

    def __init__(self, junction_id, specification):
        self.junction_id = junction_id
        self.junction_in_network = self.find_junction_in_network(specification.roadmap)
        self.id_in_network = self.junction_in_network.uid

        self.all_maneuvers = self.junction_in_network.maneuvers
        self.maneuver_type_to_instance = self.get_maneuver_to_instance_map()
        self.instance_to_maneuver_type = self.get_instance_to_maneuver_map()
        self.maneuver_type_to_union_region = self.get_maneuver_to_region_map()

        # Stats
        self.n_maneuvers = len(self.all_maneuvers)
        self.n_actors = len(specification.actors)
        self.theoretical_n_scenarios = self.n_maneuvers ** self.n_actors

    def find_junction_in_network(self, network):
        junction_w_id = list(filter(lambda x: x.id == int(self.junction_id), network.intersections))
        if len(junction_w_id) != 1:
            # ids = [x.id for x in network.intersections]
            ids = [f"{x.id}({len(x.maneuvers)} man.s)" for x in network.intersections]
            raise Exception(f"Invalid junction id <{self.junction_id}>. Select among the following ids {ids}")
        junction = junction_w_id[0]
        return junction
    
    def get_maneuver_to_instance_map(self):
        type_to_maneuver_instance = {ManeuverType.RIGHT_TURN:[],
            ManeuverType.LEFT_TURN:[], 
            ManeuverType.STRAIGHT:[],
            ManeuverType.U_TURN:[]}
        for maneuver in self.junction_in_network.maneuvers:
            type_to_maneuver_instance[maneuver.type].append(maneuver)
        return type_to_maneuver_instance
    
    def get_instance_to_maneuver_map(self):
        maneuver_instance_to_type = {}
        for maneuver in self.junction_in_network.maneuvers:
            maneuver_instance_to_type[maneuver] = maneuver.type
        return maneuver_instance_to_type

    def get_maneuver_to_region_map(self):
        maneuverToRegion = {}
        for man_type, all_maneuvers in self.maneuver_type_to_instance.items():
            if len(all_maneuvers) == 0:
                maneuverToRegion[man_type] = None
            else:
                all_regions = [maneuver.connectingLane for maneuver in all_maneuvers]
                maneuverToRegion[man_type] = PolygonalRegion.unionAll(all_regions)
        return maneuverToRegion
    
    def log_stats(self):
        logging.info(f'{self} contains {self.n_maneuvers} possible maneuvers.')
        logging.info(f'There are theoretically {self.theoretical_n_scenarios} lane combinations for {self.n_actors}-actor scenarios.')
    
    def __repr__(self) -> str:
        return f"Junction {self.junction_id}"
