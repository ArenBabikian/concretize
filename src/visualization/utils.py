from scenic.core.regions import EmptyRegion

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

# TODO import the rest from Scenic.core.visuals.utils
def show_regions(plt, regions, c):
    for r in regions:
        show_region(plt, r, c)

def show_region(plt, r, c):
    r.show(plt, style='-', color='w')
    points = tuple(r.polygons[0].exterior.coords)
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
            points = tuple(collidingRegion.polygons[0].exterior.coords)
            x, y = zip(*points)
            plt.fill(x, y, color=color, zorder=zorder)


