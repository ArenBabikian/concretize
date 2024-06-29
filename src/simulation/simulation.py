
import logging
import pandas as pd
from scenic.domains.driving.workspace import Workspace

from pathlib import Path

import carla

import time
# from scenario_runner.scenario_runner import ScenarioRunner
from agents.navigation.constant_velocity_agent import ConstantVelocityAgent
import src.simulation.utils as utils



class Scenario_Simulation:

    def __init__(self, args):

        #TODO improve below, avoid the "hasattr"
        self.simulate = args.simulate
        self.carla_map = args.map
        self.weather = args.simulation_weather

        self.ip = args.simulation_ip
        self.port = args.simulation_port

        # stats        
        self.save = args.save_simulation_stats
        if self.save:
            self.save_dir = Path(args.output_directory) / "simulation"
        self.stats_df = pd.DataFrame()


    def execute_simulation(self, instance, simulation_id):
        logging.info(f'Executing scenario in simulation')

        # Connect to CARLA
        client = carla.Client(self.ip, self.port)
        client.set_timeout(10.0)
        world = client.get_world()
        
        try:
            # Set configuration
            utils.fix_map(client, self.carla_map, self.ip, self.port )
            world.set_weather(getattr(carla.WeatherParameters, self.weather))

            # Actors
            xs, ys = [], []
            carla_actors = {}
            for i, ac in enumerate(instance.actors):

                # Spawn actors at initial positions
                xs.append(ac.position.x)
                ys.append(-ac.position.y) # TEMP
                carla_actor = utils.spawn_fixed_actors(world, ac)
                carla_actors[ac] = carla_actor

            # set the camera to the top of the scenario
            utils.fix_spectator(world, instance.specification.junction, xs, ys)

            # alows time for actors to spawn and drop on the road
            time.sleep(2)

            # assign behaviors
            run_behavior = False
            carla_agents = {}
            for ac in instance.actors:
                carla_actor = carla_actors[ac]
                if ac.assigned_maneuver_instance is not None:
                    run_behavior = True

                    # Add collision sensor
                    # given for free with the ConstantVelocityAgent

                    # define agent
                    opt_dict = {'ignore_traffic_light': True, 'ignore_stop_signs': True}
                    agent = ConstantVelocityAgent(carla_actor, 
                                                  target_speed=ac.speed_profile.speed_on_road, 
                                                  opt_dict=opt_dict) # TODO temporary
                    if not ac.isEgo:
                        agent.ignore_vehicles()
                    target = utils.posToCarlaLocation(ac.end_of_junction_point)
                    agent.set_destination(target)
                    carla_agents[ac] = agent

            # Run behaviors untill timeout or collision
            timeout = 10 if not instance.measured_timeout else instance.measured_timeout
            if run_behavior:
                collision_occured = False
                timeout_occured = False
                start_time = time.time()
                while not collision_occured and not timeout_occured:
                    for a in carla_agents:
                        carla_actor = carla_actors[a]
                        agent = carla_agents[a]
                        carla_actor.apply_control(agent.run_step())
                        if agent.has_collided:
                            collision_occured = True
                            break
                    if time.time() - start_time > timeout:
                        timeout_occured = True
                        break
            else:
                # Run simulation for a fixed time
                time.sleep(timeout)

            # store and return simulation data
            data = {}
            data['map'] = self.carla_map
            data['junction'] = instance.specification.junction.junction_id
            data['weather'] = self.weather
            data['simulation_id'] = simulation_id
            data['num_actors'] = len(instance.actors)

            data['non_ego_maneuvers_id'] = set()
            data['non_ego_maneuver_types'] = set()

            for ac in instance.actors:
                man_uid = ac.assigned_maneuver_instance.connectingLane.uid
                man_type = utils.get_type_string(ac.assigned_maneuver_instance.type)
                if ac.isEgo:
                    data['ego_maneuver_id'] =man_uid
                    data['ego_maneuver_type'] = man_type
                else:
                    data['non_ego_maneuvers_id'].add(man_uid)
                    data['non_ego_maneuver_types'].add(man_type)
            data['collision_occured'] = 1 if collision_occured else 0
            # TODO: add more data, e.g. speeds
            return data

        finally:
            utils.destroy_all_actors(world)

    def save_and_update(self, stats_json):
        if self.save:
            # 1 save stats
            df_act = pd.json_normalize(stats_json)
            self.stats_df = self.stats_df.append(df_act)

            save_path = self.save_dir / "simulation_data.csv"
            self.stats_df.to_csv(save_path, index=False)        
            print(f"Saved simulation data at {save_path}")

            # 2 create/update figures
            plot_types = [
            ('num_actors',        None,       'scenario_size', 'Number of Actors'),
            ('ego_maneuver_type', None,       'maneuver_type' , 'Maneuver Types'),
            ('ego_maneuver_id',   None,       'maneuver_instance_all',  'Maneuver Instances'),
            ('ego_maneuver_id',   'Left Turn',     'maneuver_instance_left',  'Left Turn Instances'),
            ('ego_maneuver_id',   'Right Turn',    'maneuver_instance_right',  'Right Turn Instances'),
            ('ego_maneuver_id',   'Straight', 'maneuver_instance_straight',  'Go Straight Instances'),
            ]

            for groupby, further_group, file_name, xlabel in plot_types:
                utils.generate_and_save_figure(df=self.stats_df, groupby=groupby, further_group=further_group, file_name=file_name, xlabel=xlabel, save_dir=self.save_dir )
            print(f"Updated figures in {self.save_dir}/")


