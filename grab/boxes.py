import numpy as np
import itertools
from Polygon import Polygon
#from cpolygon import inside_polygon
#from polygon import inside_polygon
import matplotlib as ma
ma.use('agg')
import matplotlib.pyplot as plt
import shpUtils


def bounding(col):
    all = np.concatenate(col)
    mn, mx = np.min(all,0),np.max(all,0)
    return mn,mx

def potentials((mn,mx),n=10):
    rand = np.zeros((n,2))
    rand[:,0] = np.random.uniform(mn[0],mx[0],n)
    rand[:,1] = np.random.uniform(mn[1],mx[1],n)
    return rand

def getrects(pts, k=3):
    k = int(k)
    rectslist = []
    assert len(pts)%2==0 #we're going to pair them up
    pairlist = pts.reshape((-1,2,2)) #remaining, pairs, 2 deep
    for comb in itertools.combinations(pairlist,k):
        cntue = True
        for rect in comb: # check that it's ll, ur
            if not np.all(rect[0] < rect[1]):
                cntue = False
        if cntue: 
            rectslist.append(comb)
    return rectslist

def inside_box(rect, (x,y)):
    x_ok = False
    y_ok = False
    if x >= rect[0][0] and x <= rect[1][0]:
        x_ok = True
    if y >= rect[0][1] and y <= rect[1][1]:
        y_ok = True
    if x_ok and y_ok: return True
    else: return False
        

def overlap(test, rects, n=100):
    bbox = bounding(test)
    mc = potentials(bbox, 100)
    missed, overlaps, excess = 0,0,0   
    for pt in mc:
        in_t = False
        for t in test:
            if inside_polygon(t, pt[0], pt[1]):
                in_t = True
                continue
        in_rects = False
        for r in rects:
            if inside_box(r, pt):
                in_rects = True
                continue
        if in_t and in_rects:
            overlaps += 1
        elif in_t and not in_rects:
            missed += 1
        elif in_rects and not in_t:
            excess += 1
    return overlaps, missed, excess

def overlap(p_test, rects):
    p_rects = poligonify(rects) 
    intersections = [[(t-r) for t in p_test] for r in p_rects]
    #http://weblogs.asp.net/george_v_reilly/archive/2009/03/24/flattening-list-comprehensions-in-python.aspx
    flattened_intersections = sum(intersections, [])
    overlap_area = sum([x.area() for x in flattened_intersections])
    #TODO subtract out overlaps of rects; too much overlap now
    return overlap_area

def poligonify(l_of_arrs):
    return [Polygon(x) for x in l_of_arrs]

def cover(test, k=2, n_pts=100):
    p_test = poligonify(test)
    rectangles = getrects(potentials(bounding(test),n_pts),k)
    rectify = [[helpersquare(pts) for pts in rect] for rect in rectangles] 
    run = [overlap(p_test,rect) for rect in rectify]
    best = np.argsort(run)[0]
    return rectangles[best], run[best]
    

def helpersquare((ll,ur)):
    return [ll,(ll[0],ur[1]),ur,(ur[0],ll[1]),ll]

def draw(test, rect):
    plt.clf()
    for t in test:
        plt.plot(t[:,0],t[:,1])
    q = [np.asarray(helpersquare(x)) for x in rect]
    [plt.plot(x[:,0],x[:,1]) for x in q]
    return

def shape_to_dict(shapefile):
    name = lambda d: d['STATE']+d['COUNTY']+('%-6s'%d['TRACT']).replace(' ','0')
    shp = shpUtils.loadShapefile(shapefile)
    out = {}
    for sh in shp:
        n = name(sh['dbf_data'])
        parts = []
        for shlist in sh['shp_data']['parts']:
            points = []
            for pt in shlist['points']:
                points.append((pt['x'],pt['y']))
            parts.append(np.asarray(points))
        out[n] = parts
    return out
            

def find_rects(shapedict):
    out = {}
    for sh in shapedict:
        out[sh] = cover(shapedict[sh],n_pts=200)
    return out

if __name__=="__main__":
    pass
