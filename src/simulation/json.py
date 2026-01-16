import logging
from pathlib import Path

from src.simulation import utils
from scenic.domains.driving.roads import ManeuverType
import json

MANTYPE2ID = {}
for k, v in utils.MANTYPE2ID.items():
    if v == 'straight':
       v = 'ahead'  # TODO: this is a workaround, maybe not necessary 
    MANTYPE2ID[k] = v

class Openscenario_Json:

    def __init__(self, specification, all_instances, ordered_list_of_encounters, args):
        self.all_instances = all_instances
        self.specification = specification
        self.ordered_list_of_encounters = ordered_list_of_encounters
        self.args = args

        self.to_save = args.save_xml_json
        self.save_path = Path(args.output_directory) / args.save_json_file

        self.json_content = {}


    def generate_initial_json(self):
        # initializations
        num_actors = len(self.specification.actors)
        junction = self.specification.junction
        all_possible_maneuvers = junction.all_maneuvers

        # SET UP ABSTRACT SCENARIOS
        maneuver_ids = [m.connectingLane.uid for m in all_possible_maneuvers]

        # define relationships between roads
        road_pair_relations = {}
        for m in all_possible_maneuvers:
            road_pair = (m.startLane.road.uid, m.endLane.road.uid)
            if road_pair not in road_pair_relations:
                road_pair_relations[road_pair] = MANTYPE2ID[m.type] # TODO: replace with utils.MANTYPE2ID[m.type]
            else:
                assert road_pair_relations[road_pair] == MANTYPE2ID[m.type]

        # determine relationships between lanes
        def get_relationship_map(lane_collection):
            relationships = {}
            for l1 in lane_collection:
                uid_l1 = l1.uid
                rd_l1 = l1.road.uid
                relationships[uid_l1] = {}
                for l2 in lane_collection:
                    uid_l2 = l2.uid
                    rd_l2 = l2.road.uid
                    lane_pair = (uid_l1, uid_l2)
                    if l1 == l2:
                        relation = 'same'
                    elif rd_l1 == rd_l2:
                        relation = 'adjacent'
                    else:
                        relation = road_pair_relations[(rd_l1, rd_l2)]
                    relationships[uid_l1][uid_l2] = relation
                    # rela = {'pair':lane_pair, 'relation':relation}
            return relationships

        lane_relationships = get_relationship_map(junction.junction_in_network.incomingLanes)
        lane_relationships.update(get_relationship_map(junction.junction_in_network.outgoingLanes))
        self.json_content = {'map_name' : self.args.map[:1].lower() + self.args.map[1:], # TODO Uncapitalization might be unnecessary
                                'junction_id' : f"intersection{junction.junction_id}", # TODO addint 'intersection' might not be necessary
                                'num_actors' : num_actors,
                                'all_maneuvers' : maneuver_ids,
                                'lane_relationships' : lane_relationships,
                                'all_scenarios' : []
                                }


    def add_abstract_scenarios(self):
        for result in self.all_instances:
            for scenario_id, instance in enumerate(result.ordered_outcomes):

            # , self.specification, abstractScenarioDetails, scenario_id, ordered_list_of_encounters):
                scenario_dict = {'scenario_id' : scenario_id,
                                    'actors' : [],
                                    'initial_relations' : {},
                                    'encounter_order' : [e['actor'].name for e in self.ordered_list_of_encounters],
                                    'final_relations' : {}}
                # MANEUVERS
                for i_o, o in enumerate(instance.actors):
                    m = o.assigned_maneuver_instance
                    maneuver_desc = {'id' :m.connectingLane.uid,
                                        'type':utils.MANTYPE2ID[m.type],
                                        'start_lane_id':m.startLane.uid,
                                        'end_lane_id':m.endLane.uid
                                        }
                    actor_spec = {'id' : i_o,
                                    'maneuver' : maneuver_desc
                                    }
                    scenario_dict['actors'].append(actor_spec)

                # RELATIONS
                for i_o1, o1 in enumerate(instance.actors):
                    startLane1 = o1.assigned_maneuver_instance.startLane.uid
                    endLane1 = o1.assigned_maneuver_instance.endLane.uid
                    scenario_dict['initial_relations'][i_o1] = {}
                    scenario_dict['final_relations'][i_o1] = {}
                    for i_o2, o2 in enumerate(instance.actors):
                        if o1 == o2:
                            continue
                        startLane2 = o2.assigned_maneuver_instance.startLane.uid
                        endLane2 = o2.assigned_maneuver_instance.endLane.uid

                        start_relation = self.json_content['lane_relationships'][startLane1][startLane2]
                        scenario_dict['initial_relations'][i_o1][i_o2] = start_relation

                        end_relation = self.json_content['lane_relationships'][endLane1][endLane2]
                        scenario_dict['final_relations'][i_o1][i_o2] = end_relation

                self.json_content['all_scenarios'].append(scenario_dict)

    def generate_json(self):
        self.generate_initial_json()
        self.add_abstract_scenarios()

    def save(self):
        if self.to_save:
            with open(self.save_path, 'w') as f:
                json.dump(self.json_content, f, indent=2)
            logging.info(f'Saved JSON content at {self.save_path}')