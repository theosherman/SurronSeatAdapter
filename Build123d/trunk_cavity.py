"""One rear-only octagonal sketch and its original-direction drafted cavity cut."""
from build123d import Face,Wire,Solid,Vector

# Millimeters in the existing BodyCutSketch's own (u,v) plane.
# One convex octagon: no narrow stem and no secondary wall additions.
REAR_CAVITY_POINTS = ((-14,-100),(14,-100),(28,-110),(28,-117),
                      (14,-127),(-14,-127),(-28,-117),(-28,-110))

def rear_cavity_profile(sketch):
    """The controlling eight-line sketch for the rear-only cavity."""
    origin,x,y=map(Vector,(sketch['originMm'],sketch['xAxis'],sketch['yAxis']))
    return Face(Wire.make_polygon([origin+x*u+y*v for u,v in REAR_CAVITY_POINTS],close=True))

def rear_cavity_tool(sketch):
    """Use the existing 12 mm roof offset and 15 degree downward draft."""
    direction=-Vector(sketch['normal']).normalized()
    profile=rear_cavity_profile(sketch).translate(direction*12)
    return Solid.extrude_taper(profile,direction*500,-15)
