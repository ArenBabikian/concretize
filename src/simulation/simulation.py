
import logging
import random
from scenic.domains.driving.workspace import Workspace

from pathlib import Path

import carla

import time
# from scenario_runner.scenario_runner import ScenarioRunner
from agents.navigation.constant_velocity_agent import ConstantVelocityAgent
import src.simulation.utils as utils



class Scenario_Simulation:

    def __init__(self, instance, simulation_id, args):
        self.spec = instance
        self.workspace = Workspace(instance.roadmap.drivableRegion)
        self.simulation = None

        #TODO improve below, avoid the "hasattr"
        self.simulate = args.simulate
        if hasattr(args, "simulation_path"):
            self.save_path = args.simulation_path
        else:
            self.save_path = Path(args.output_directory) / "scenarios" / f"{simulation_id}.xml"
            raise Exception(self.save_path)
        
        self.carla_map = args.map

        self.ip = args.simulation_ip
        self.port = args.simulation_port

        self.weather = args.simulation_weather

    def save_executable(self):
        
        logging.info(f'Saved scenario executable at {self.save_path}')

    def execute_simulation(self):
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
            for i, ac in enumerate(self.spec.actors):

                # Spawn actors at initial positions
                xs.append(ac.position.x)
                ys.append(-ac.position.y) # TEMP
                carla_actor = utils.spawn_fixed_actors(world, ac)
                carla_actors[ac] = carla_actor

            print("Actors spawned")

            # set the camera to the top of the scenario
            utils.fix_spectator(world, self.spec.specification.junction, xs, ys)
            print("Camera spawned")

            # alows time for actors to spawn and drop on the road
            time.sleep(2)

            # assign behaviors
            run_behavior = False
            carla_agents = {}
            for ac in self.spec.actors:
                carla_actor = carla_actors[ac]
                if ac.assigned_maneuver_instance is not None:
                    run_behavior = True

                    # Add collision sensor
                    # given for free with the ConstantVelocityAgent

                    # define agent
                    agent = ConstantVelocityAgent(carla_actor, ac.speed_profile.speed_on_road) # TODO temporary
                    target = utils.posToCarlaLocation(ac.end_of_junction_point)
                    agent.set_destination(target)
                    carla_agents[ac] = agent

            # Run behaviors untill timeout or collision
            timeout = 10 if not self.spec.measured_timeout else self.spec.measured_timeout
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

            # log results
            # TODO HERE
            

        finally:
            utils.destroy_all_actors(world)

