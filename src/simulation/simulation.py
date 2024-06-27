
import logging
from scenic.domains.driving.workspace import Workspace

from pathlib import Path

import carla
import time
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
        
        self.carla_map = 'T'+args.map[6:11]

        self.ip = args.simulation_ip
        self.port = args.simulation_port

        self.weather = args.simulation_weather

    def save_executable(self):
        
        logging.info(f'Saved scenario executable at {self.save_path}')

    def execute_simulation(self):
        logging.info(f'Executing scenario in simulation')

        # ####### see PythonAPI\custom\dynamic\sample1.py
        # Connect to CARLA
        client = carla.Client(self.ip, self.port)
        client.set_timeout(10.0)
        world = client.get_world()
        
        try:
            # Set configuration
            utils.fix_map(client, self.carla_map, self.ip, self.port )
            world.set_weather(getattr(carla.WeatherParameters, self.weather))

            # Spawn actors in inital positions
            xs, ys = [], []
            for i, ac in enumerate(self.spec.actors):
                xs.append(ac.position.x)
                ys.append(-ac.position.y)
                utils.spawn_fixed_actors(world, ac)
            print("Actors spawned")


            # set the camera to the top of the scenario
            utils.fix_spectator(world, xs, ys)
            print("Camera spawned")

            # START THE BEHAVIORS

            # WAIT UNTIL TERMINATION

            # LOG THAT SIMULATION FINISHED

            # Wait for 10 seconds
            input("Press Enter to continue...")
            

        finally:
            vehicles = world.get_actors().filter('vehicle.*')
            pedestrians = world.get_actors().filter('walker.*')
            for actor in vehicles:
                actor.destroy()
            for actor in pedestrians:
                actor.destroy()
            logging.info('Actors Destroyed')

