from scenic.core.regions import EmptyRegion
from scenic.core.geometry import averageVectors

import src.visualization.colors as colors
import math

# JUNCTION
def zoom_to_junction(map_plt, junction, margin=10):

    j = junction.junction_in_network
    aabb = j.getAABB()

    # margins = [xlo, xhi, ylo, yhi]
    if isinstance(margin, int):
        margins = [margin, margin, margin, margin]
    elif isinstance(margin, tuple) and len(margin) == 2:
        margins = [margin[0], margin[0], margin[1], margin[1]]
    elif isinstance(margin, tuple) and len(margin) == 4:
        margins = margin
    else:
        exit(f'Invalid margin <{margin}>. Must be int or tuple of 2 or 4 ints')

    xlo = aabb[0][0]-margins[0]
    xhi = aabb[1][0]+margins[1]
    ylo = aabb[0][1]-margins[2]
    yhi = aabb[1][1]+margins[3]

    # TODO this is from previous version
    # fig = map_plt.gcf()
    # xrange = xhi-xlo
    # yrange = yhi-ylo
    # fig.set_size_inches(xrange/2.54, yrange/2.54)  # Convert from centimeters to inches

    map_plt.xlim(xlo, xhi)
    map_plt.ylim(ylo, yhi)

# NETWORK
def show_alt_network(plt, network):
    # network.walkableRegion.show(plt, style='-', color=colors.gray)
    network.shoulderRegion.show(plt, style='-', color=colors.gray)
    for road in network.roads:
        road.show(plt, style='-', color=colors.gray)
        for lane in road.lanes:     # will loop only over lanes of main roads
            lane.leftEdge.show(plt, style='--', color=colors.gray)
            lane.rightEdge.show(plt, style='--', color=colors.gray)

            # # Draw arrows indicating road direction
            # if lane.centerline.length >= 10:
            #     pts = lane.centerline.equallySpacedPoints(5)
            # else:
            #     pts = [lane.centerline.pointAlongBy(0.5, normalized=True)]
            # hs = [lane.centerline.orientation[pt] for pt in pts]
            # x, y = zip(*pts)
            # u = [math.cos(h + (math.pi/2)) for h in hs]
            # v = [math.sin(h + (math.pi/2)) for h in hs]
            # plt.quiver(x, y, u, v,
            #            pivot='middle', headlength=4.5,
            #            scale=0.06, units='dots', color='#A0A0A0')
    # for lane in network.lanes:     # draw centerlines of all lanes (including connecting)
    #     lane.centerline.show(plt, style=':', color='#A0A0A0')
    network.intersectionRegion.show(plt, style=colors.gray)

# REGIONS
def show_regions(plt, regions, c):
    for r in regions:
        show_region(plt, r, c)

def show_region(plt, r, c):
    r.show(plt, style='-', color='w')
    points = tuple(r.polygons.geoms[0].exterior.coords)
    x, y = zip(*points)
    plt.fill(x, y, color=c)

def showPairwiseCollidingRegions(plt, all_roads, color='r', zorder=99):
    for i, roadi in enumerate(all_roads[1:2]):
        for roadj in all_roads[:]:
            if roadi == roadj:
                continue
            try:
                collidingRegion = roadi.intersect(roadj)
            except:
                collidingRegion = EmptyRegion('')
            collidingRegion.show(plt, style='-', color='w')
            if isinstance(collidingRegion, EmptyRegion):
                continue
            points = tuple(collidingRegion.polygons.geoms[0].exterior.coords)
            x, y = zip(*points)
            plt.fill(x, y, color=color, zorder=zorder)

# CENTERLINE + ARROWS
def show_cl(plt, cl, c='w', style='--', linewidth=5):
    cl.show(plt, style=style, color=c, linewidth=linewidth)

def show_arrows(plt, cl, c, pointsDelts=-1, rmFirst=False, size=1, zorder=100):
    # Positions
    if pointsDelts == -1:
        assert cl.length >= 10
        pts = cl.equallySpacedPoints(6)
    else:
        pts = cl.pointsSeparatedBy(pointsDelts)

    # Corner cases
    pts.pop(-1)
    if rmFirst:
        pts.append(cl[-1])
        pts.pop(0)

    # Drawing
    hs = [cl.orientation[pt] for pt in pts]
    x, y = zip(*pts)
    u = [math.cos(h + (math.pi/2)) for h in hs]
    v = [math.sin(h + (math.pi/2)) for h in hs]
    ql = 10
    # scale=0.06 is half as big as scale=0.03
    scale = 0.06/size
    plt.quiver(x, y, u, v,
                headlength=ql, headaxislength=ql,
                headwidth=2*ql/3,
                scale=scale, units='dots',
                pivot='middle', color=c,
                zorder=zorder)

# OBJECTS
def show_object(plt, actor, c, size=None, zorder=101):
    plt.rcParams['hatch.linewidth'] = 10.0
    corners = actor.get_rectangular_region(size).corners
    x, y = zip(*corners)
    w = 1
    if actor.isEgo:
        # TODO make this visually more appealing

        w = 2
        rad = 0.6 * max(actor.width, actor.length)
        # circle=plt.Circle(actor.position, rad, color='k', fill=False)
        c1=plt.Circle(actor.position, rad, facecolor=c, edgecolor='w', fill=True, alpha=0.5, hatch='\\')
        c2=plt.Circle(actor.position, rad, edgecolor='k', linewidth=w, fill=False)
        plt.gca().add_artist(c1)
        plt.gca().add_artist(c2)
        # glow_x, glow_y = zip(*actor.get_rectangular_region(size, multiplier=1.5).corners)
        # plt.fill(glow_x, glow_y, color='k', zorder=zorder, alpha=0.25)
        # glow_x, glow_y = zip(*actor.get_rectangular_region(size, multiplier=1.25).corners)
        # plt.fill(glow_x, glow_y, color='k', zorder=zorder, alpha=0.25)
    plt.fill(x, y, color=c, zorder=zorder)
    plt.plot(x + (x[0],), y + (y[0],), color="k", linewidth=w, zorder=zorder)

    frontMid = averageVectors(corners[0], corners[1])
    baseTriangle = [frontMid, corners[2], corners[3]]
    triangle = [averageVectors(p, actor.position, weight=0.5) for p in baseTriangle]
    x, y = zip(*triangle)
    plt.fill(x, y, "w", zorder=zorder)
    plt.plot(x + (x[0],), y + (y[0],), color="k", linewidth=w, zorder=zorder)
