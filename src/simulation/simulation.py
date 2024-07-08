
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
        if hasattr(args, 'simulation_initial_file') and args.simulation_initial_file:
            self.stats_df = pd.read_csv(args.simulation_initial_file)
        else:
            self.stats_df = pd.DataFrame()
        if args is None:
            return

        #TODO improve below, avoid the "hasattr"
        self.simulate = args.simulate
        self.carla_map = args.map
        self.weather = args.simulation_weather

        self.ip = args.simulation_ip
        self.port = args.simulation_port

        # stats        
        self.save = args.save_simulation_stats
        if self.save:
            if hasattr(args, "save_path_sim"):
                self.save_dir = args.save_path_sim
            else:
                self.save_dir = Path(args.output_directory) / "simulation"


    # TODO Refactort this
    def update_args(self, args):

        self.simulate = args.simulate
        self.carla_map = args.map
        self.weather = args.simulation_weather
        self.ip = args.simulation_ip
        self.port = args.simulation_port

        # stats        
        self.save = args.save_simulation_stats
        if self.save:
            if hasattr(args, "save_path_sim"):
                self.save_dir = Path(args.save_path_sim)
            else:
                self.save_dir = Path(args.output_directory) / "simulation"


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
                if ac.controller:
                    run_behavior = True

                    id2options = {
                        'SimpleAgent': {'ignore_traffic_light': True, 'ignore_stop_signs': True},
                        'DummyAgent': {'ignore_traffic_light': True, 'ignore_stop_signs': True, 'ignore_vehicles': True}
                    }

                    if ac.controller not in id2options:
                        raise Exception(f"Unknown controller {str(ac.controller)}. Please assign one of the following controllers: {str(id2options.keys())}.")
                    
                    # TODO add a warning if ego is assigned a DummyAgent
                    
                    opt_dict = id2options[ac.controller]
                    agent = ConstantVelocityAgent(carla_actor, target_speed=ac.speed_profile.speed_on_road, opt_dict=opt_dict)

                    if ac.assigned_maneuver_instance is not None:
                        target = utils.posToCarlaLocation(ac.end_of_junction_point)
                        agent.set_destination(target)
                    
                    carla_agents[ac] = agent

                elif ac.assigned_maneuver_instance is not None:
                    raise Exception(f"Actor {str(ac)} is assigned a maneuver but no controller. Please assign a controller.")

            # Run behaviors untill timeout or collision
            timeout = 7
            if run_behavior:
                timeout = 12
            if instance.measured_timeout:
                timeout = instance.measured_timeout
            collision_occured = False
            if run_behavior:
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
            jun = instance.specification.junction
            data['junction'] = jun.junction_id if jun else None
            data['weather'] = self.weather
            data['simulation_id'] = simulation_id
            data['num_actors'] = len(instance.actors)

            data['non_ego_maneuvers_id'] = set()
            data['non_ego_maneuver_types'] = set()

            for ac in instance.actors:
                assigned_man_instance = ac.assigned_maneuver_instance
                if assigned_man_instance is None:
                    man_uid = 'None'
                    man_type = 'None'
                else:
                    man_uid = assigned_man_instance.connectingLane.uid
                    man_type = utils.get_type_string(assigned_man_instance.type)
                if ac.isEgo:
                    data['ego_maneuver_id'] = man_uid
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


