


from scenic.core.regions import EmptyRegion, PolygonalRegion, RectangularRegion, SectorRegion, toPolygon
from scenic.simulators.carla.utils.utils import carlaToScenicHeading, carlaToScenicPosition
from scenic.core.geometry import cos, sin
import math

import matplotlib.pyplot as plt
import numpy as np

CAR_WIDTH = 2
CAR_LENGTH = 4.5

LIDAR_SQUARE_SIZE = 32
VISIBILITY_SECTOR_ANGLE = 132
VISIBILITY_DISTANCE = 50

def radialToCartesian(point, radius, heading):
	angle = heading + (math.pi / 2.0)
	rx, ry = radius * cos(angle), radius * sin(angle)
	return (point[0] + rx, point[1] + ry)


def closestDistanceBetweenRectangles(rectReg1, rectReg2):

    # The shortest distance must necessarily involve at least 1 corner
    # unless the rectangles are intersecting, which shouldnt happen in our case
    o1_polygon = rectReg1.polygon
    o2_polygon = rectReg2.polygon

    da = o1_polygon.distance(o2_polygon)
    db = o2_polygon.distance(o1_polygon)
    assert da == db
    return da


def getCarRegion(actor_transform):
    actor_vec = carlaToScenicPosition(actor_transform.location)
    actor_head = carlaToScenicHeading(actor_transform.rotation)
    return RectangularRegion(actor_vec, actor_head, CAR_WIDTH, CAR_LENGTH)


def findVisibilitySector(transform):
    pos = carlaToScenicPosition(transform.location)
    head = carlaToScenicHeading(transform.rotation)
    r = SectorRegion(pos, VISIBILITY_DISTANCE, head, math.radians(VISIBILITY_SECTOR_ANGLE))
    return r


def findLidarSquare(transform):
    
    pos = carlaToScenicPosition(transform.location)
    head = carlaToScenicHeading(transform.rotation)

    lidar_center = radialToCartesian(pos, (CAR_LENGTH + LIDAR_SQUARE_SIZE) / 2, head)

    r = RectangularRegion(lidar_center, head, LIDAR_SQUARE_SIZE, LIDAR_SQUARE_SIZE)
    return r

    # DEBUGGING  visualise the lidar square

    # import random
    # import carla
    # import matplotlib.pyplot as plt
    # import numpy as np

    # # Randomize location and rotation
    # x = random.uniform(-10, 10)
    # y = random.uniform(-10, 10)
    # yaw = random.uniform(-180, 180)
    # location = carla.Location(x=x, y=y, z=0)
    # rotation = carla.Rotation(pitch=0, yaw=yaw, roll=0)
    # transform = carla.Transform(location, rotation)
    # pos = carlaToScenicPosition(transform.location)
    # head = carlaToScenicHeading(transform.rotation)

    # LIDAR_SQUARE_SIZE = 32
    # # print(pos)
    # lidar_center = radialToCartesian(pos, (CAR_LENGTH + LIDAR_SQUARE_SIZE) / 2, head)
    # # print(lidar_center)
    # # lidar_center = pos + head.toVector() * (2 + LIDAR_SQUARE_SIZE) / 2 # TODO check this
    # a = RectangularRegion(pos, head, CAR_WIDTH, CAR_LENGTH)

    # r = RectangularRegion(lidar_center, head, LIDAR_SQUARE_SIZE, LIDAR_SQUARE_SIZE)
    visualiseRegions([a, r])


def findIntersectionDetails(actor_region, region, doCorners=False, doArea=False, doPerimeter=False):

        num_corners_inside_region = None
        if doCorners:
            actor_corners = actor_region.corners
            num_corners_inside_region = 0
            for corner in actor_corners:
                if region.containsPoint(corner):
                    num_corners_inside_region += 1

        perc_of_car_in_region = None
        if doArea:
            actor_pr = PolygonalRegion(polygon=toPolygon(actor_region))
            other_pr = PolygonalRegion(polygon=toPolygon(region))
            part_of_car_in_region = actor_pr.intersect(other_pr)

            if not isinstance(part_of_car_in_region, EmptyRegion):
                area_of_car_in_region = sum(part_of_car_in_region.cumulativeTriangleAreas)
                perc_of_car_in_region = area_of_car_in_region / (CAR_WIDTH*CAR_LENGTH)

        # TODO : In reality, we are not really interested in the area of the vehicle that is within the region.
        # We are interested in the size of the perimeter (Or, more specifically, the size of the orthogonal projection of the perimeter)
        # From the point of view of the actor.

        return num_corners_inside_region, perc_of_car_in_region


def visualiseRegions(regions, colors=None, display=False):

    def getRegionCorners(region):
        if isinstance(region, RectangularRegion):
            return np.array(region.corners)
        elif isinstance(region, SectorRegion):
            # c = region.center
            # half_angle = math.radians(region.angle / 2)
            # num_points, points = 20, []
            # for i in range(num_points):
            #     angle = region.heading - half_angle + (i / (num_points - 1)) * math.radians(region.angle)
            #     point = tuple(radialToCartesian(c, region.radius, angle))
            #     points.append(point)
            # return np.array([c] + points)
            return np.array(region.polygon.exterior.coords)
        else:
            exit("Unknown region type")

    if colors is None:
        colors = ['b'] * len(regions)

    for i, region in enumerate(regions):
        corners = getRegionCorners(region)
        plt.scatter(corners[:, 0], corners[:, 1], c=colors[i])
        for j in range(len(corners)):
            plt.plot([corners[j, 0], corners[(j+1)%len(corners), 0]], [corners[j, 1], corners[(j+1)%len(corners), 1]], c=colors[i])
    plt.gca().set_aspect('equal', adjustable='box')
    
    x_min_list = [np.min(getRegionCorners(region)[:, 0]) for region in regions]
    y_min_list = [np.min(getRegionCorners(region)[:, 1]) for region in regions]
    x_max_list = [np.max(getRegionCorners(region)[:, 0]) for region in regions]
    y_max_list = [np.max(getRegionCorners(region)[:, 1]) for region in regions]
    plt.xlim(np.min(x_min_list) - 1, np.max(x_max_list) + 1)
    plt.ylim(np.min(y_min_list) - 1, np.max(y_max_list) + 1)
    if display:
        plt.show()


def visualiseReset():
    plt.clf()

