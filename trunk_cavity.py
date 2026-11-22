"""Approved long central pocket and symmetric rear exterior relief."""
from build123d import Face, Wire, Solid, Vector, Plane, Keep, Compound, ShapeList

# Millimeters in BodyCutSketch's (u,v) frame; one editable closed outline.
REAR_CAVITY_POINTS = ((-12,105),(12,105),(12,-65),(23,-80),(43,-96),
                      (48,-110),(48,-126),(33,-132),(33,-165),
                      (-33,-165),(-33,-132),(-48,-126),(-48,-110),
                      (-43,-96),(-23,-80),(-12,-65))
# Existing AirTag pocket is 8.5 mm deep: 18.5 leaves a 10 mm roof below it.
CAVITY_ROOF_OFFSET_MM = 18.5
REAR_WALL_THICKNESS_MM = 5.0
# Exact original broad latch-wall plane in the placed Build123d model frame.
REAR_WALL_POINT_MM = (0,165.41714823915711,1.578677917809248)
REAR_WALL_NORMAL = (0,.8597932986247546,.5106422266518543)
# Lower latch root in the placed model; mirrored wall slope across XY.
REAR_TIP_POINT_MM = (0,177.270005683283,-17.98689437242)
REAR_TIP_NORMAL = (0,REAR_WALL_NORMAL[1],-REAR_WALL_NORMAL[2])
REAR_TIP_WALL_THICKNESS_MM = 14.0
# Coordinates in the placed Build123d model frame; mirrored about X=0.
REAR_SIDE_X_MM = 55.0
REAR_SIDE_POINTS = ((78,126),(REAR_SIDE_X_MM,140),(REAR_SIDE_X_MM,300),(120,300),(120,126))


def rear_cavity_profile(sketch):
    """One sixteen-line profile; no secondary pocket or roof patch."""
    origin,x,y=map(Vector,(sketch['originMm'],sketch['xAxis'],sketch['yAxis']))
    return Face(Wire.make_polygon([origin+x*u+y*v for u,v in REAR_CAVITY_POINTS],close=True))


def rear_cavity_tool(sketch):
    """Straight cavity bounded by the original wall and local lower-tip planes."""
    direction=-Vector(sketch['normal']).normalized()
    profile=rear_cavity_profile(sketch).translate(direction*CAVITY_ROOF_OFFSET_MM)
    cutter=Solid.extrude(profile,direction*350)
    # Bound the original cut by the inward parallel plane, before subtraction.
    # This preserves a 5 mm wall; it never repairs or adds material afterward.
    from coordinates import ADAPTER_TRANSLATION_MM
    normal=Vector(REAR_WALL_NORMAL)
    point=Vector(REAR_WALL_POINT_MM)-Vector(ADAPTER_TRANSLATION_MM)-normal*REAR_WALL_THICKNESS_MM
    cutter=cutter.split(Plane(point,z_dir=normal),Keep.BOTTOM)
    # Keep the approved cavity everywhere except beside the new lower diagonal.
    tip_normal=Vector(REAR_TIP_NORMAL)
    tip_point=(Vector(REAR_TIP_POINT_MM)-Vector(ADAPTER_TRANSLATION_MM)
               -tip_normal*REAR_TIP_WALL_THICKNESS_MM)
    return cutter.split(Plane(tip_point,z_dir=tip_normal),Keep.BOTTOM)


def rear_side_tools():
    """Two simple full-height cuts, retaining the central rear bridge."""
    face=Face(Wire.make_polygon([(x,y,-150) for x,y in REAR_SIDE_POINTS],close=True))
    right=Solid.extrude(face,(0,0,350))
    return right,right.mirror(Plane.YZ)


def trim_lower_rear_tip(body):
    """Remove only the toe below the latch root; retain the upper seat support."""
    point=Vector(REAR_TIP_POINT_MM)
    outside=body.split(Plane(point,z_dir=REAR_TIP_NORMAL),Keep.TOP)
    if isinstance(outside,(list,ShapeList)):
        outside=Compound(outside)
    toe=outside.split(Plane(point,z_dir=(0,0,1)),Keep.BOTTOM)
    return body.cut(toe)
