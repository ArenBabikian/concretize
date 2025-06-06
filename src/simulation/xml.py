import logging
from pathlib import Path

from src.simulation import utils
from scenic.domains.driving.roads import ManeuverType

MANTYPE2ID = {ManeuverType.LEFT_TURN:'left',
              ManeuverType.RIGHT_TURN:'right',
              ManeuverType.STRAIGHT:'straight'}

class Openscenario_Xml:

    def __init__(self, all_instances, args):
        self.all_instances = all_instances
        self.args = args

        self.to_save = args.save_xml
        self.save_path = Path(args.output_directory) / args.save_xml_file

        self.xml_lines = []


    def getScenarioDesc(self, instance, route_id):
        # SETUP
        town = self.args.map
        intersection_id = self.args.junction
        num_actors = len(instance.actors)
        timeout = instance.measured_timeout
        route_name = f'scen_{town}_{intersection_id}_{num_actors}ac_{route_id}'
        
        ego = instance.specification.actors[instance.specification.ego_id]

        scenario_desc = []
        scenario_desc.append(f"    <route id='{route_name}' town='{town}' intersection_id='{intersection_id}' timeout='{timeout}'>")
        # ACTOR INITIALIZATION
        actors_with_positions = [ac for ac in instance.actors if ac.position is not None]
        for ac in actors_with_positions:
            pos = utils.posToCarlaLocation(ac.position, 0.0)
            rot = utils.posToCarlaRotation(ac.heading)
            man = MANTYPE2ID[ac.assigned_maneuver_instance.type]

            if ac.isEgo:
                scenario_desc.append(f"        <waypoint x='{pos.x}' y='{pos.y}' z='0.0' maneuver='{man}' color='(17,37,103)'/>")
            else:
                # TODO speed is hard coded for now...
                if ac.pre_junc_position == None:
                    pre_junc_pos = pos
                    pre_junc_rot = rot
                else:
                    pre_junc_pos = utils.posToCarlaLocation(ac.pre_junc_position, 0.0)
                    pre_junc_rot = utils.posToCarlaRotation(ac.pre_junc_heading)

                scenario_desc.append(f"        <other_actor x='{pos.x}' y='{pos.y}' z='0.0'  yaw='{rot.yaw}' speed='{'transfuser'}' maneuver='{man}' model='vehicle.tesla.model3' color='75,87,173' pre_x='{pre_junc_pos.x}' pre_y='{pre_junc_pos.y}' pre_yaw='{pre_junc_rot.yaw}'/>")

        # Below is the default weather for Town05
        scenario_desc.append("        <weather id='Custom' cloudiness='10.000000' precipitation='0.000000' precipitation_deposits='0.000000' wind_intensity='5.000000' sun_azimuth_angle='170.000000' sun_altitude_angle='30.000000' fog_density='10.000000' fog_distance='75.000000' fog_falloff='0.900000' wetness='0.000000'/>")
        
        scenario_desc.append("    </route>")
        return scenario_desc


    def generate_xml(self):
        self.xml_lines.append("<?xml version='1.0' encoding='UTF-8'?>")
        self.xml_lines.append("<routes>")
        for res_id, res in enumerate(self.all_instances):
            con_sol_id=0
            for sol in res.ordered_outcomes:
                if sol.is_concrete_solution:
                    scenario_id = f"{res_id}.{con_sol_id}"
                    scenario_description = self.getScenarioDesc(sol, scenario_id)
                    self.xml_lines.extend(scenario_description)
                    con_sol_id+=1
        self.xml_lines.append("</routes>")


    def save(self):
        if self.to_save:
            with open(self.save_path, 'w') as f:
                f.write('\n'.join(self.xml_lines))
            logging.info(f'Saved executable xml at {self.save_path}')