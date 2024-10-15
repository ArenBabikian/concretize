
import carla
import carla.libcarla
from shapely.geometry import Polygon

from agents.tools.hints import ObstacleDetectionResult

import math

def vehicle_obstacle_detected(self, vehicle_list=None, sensor_angle= 180, sensor_distance=None):
        """
        Method to check if there is a vehicle in front of the agent blocking its path.

            :self is a Agent object

            :param vehicle_list (list of carla.Vehicle): list contatining vehicle objects.
                If None, all vehicle in the scene are used
            :param max_distance: max freespace to check for obstacles.
                If None, the base threshold value is used
        """
        def get_route_polygon():
            route_bb = []
            extent_y = self._vehicle.bounding_box.extent.y
            r_ext = extent_y + self._offset
            l_ext = -extent_y + self._offset
            r_vec = ego_transform.get_right_vector()
            p1 = ego_location + carla.Location(r_ext * r_vec.x, r_ext * r_vec.y)
            p2 = ego_location + carla.Location(l_ext * r_vec.x, l_ext * r_vec.y)
            route_bb.extend([[p1.x, p1.y, p1.z], [p2.x, p2.y, p2.z]])

            for wp, _ in self._local_planner.get_plan():
                if ego_location.distance(wp.transform.location) > max_distance:
                    break

                r_vec = wp.transform.get_right_vector()
                p1 = wp.transform.location + carla.Location(r_ext * r_vec.x, r_ext * r_vec.y)
                p2 = wp.transform.location + carla.Location(l_ext * r_vec.x, l_ext * r_vec.y)
                route_bb.extend([[p1.x, p1.y, p1.z], [p2.x, p2.y, p2.z]])

            # Two points don't create a polygon, nothing to check
            if len(route_bb) < 3:
                return None

            return Polygon(route_bb)
      
        if self._ignore_vehicles:
            return ObstacleDetectionResult(False, None, -1)

        if vehicle_list is None:
            vehicle_list = self._world.get_actors().filter("*vehicle*")
        if len(vehicle_list) == 0:
            return ObstacleDetectionResult(False, None, -1)
        
        if sensor_distance is None:
            sensor_distance = 5

        # get ego center-point
        ego_transform = self._vehicle.get_transform()
        ego_location = ego_transform.location
        ego_head = ego_transform.rotation.yaw

        # iterate over all vehicles
        for target_vehicle in vehicle_list:
            if target_vehicle.id == self._vehicle.id:
                continue

            # get target center point
            target_transform = target_vehicle.get_transform()
            target_location = target_transform.location

            # get target bounding box
            target_bb = target_vehicle.bounding_box
            corners = target_bb.get_world_vertices(target_transform)
            corners = [corner for corner in corners if corner.z < 1]
            
            min_theta_to_corner = float('inf')
            min_d_to_corner = float('inf')
            for corner in corners+[target_location]:

                # angle
                # Calculate the angle from ego to corner relative to ego's heading
                dx = corner.x - ego_location.x
                dy = corner.y - ego_location.y
                angle_to_corner = math.degrees(math.atan2(dy, dx))
                theta = angle_to_corner - ego_head
                theta = (theta + 180) % 360 - 180  # Normalize to [-180, 180]

                if abs(theta) < min_theta_to_corner:
                    min_theta_to_corner = abs(theta)
                # exit()

                # distance
                d = ego_location.distance_2d(corner)
                if d < min_d_to_corner:
                    min_d_to_corner = d

            # angle
            theta_sat = min_theta_to_corner < sensor_angle/2

            # distance
            d_sat = min_d_to_corner < sensor_distance
            
            if theta_sat and d_sat:
                self._world.debug.draw_point(ego_location+carla.Location(z=5), size=0.1, life_time=5)
                return ObstacleDetectionResult(True, target_vehicle, min_d_to_corner)

        return ObstacleDetectionResult(False, None, -1)
