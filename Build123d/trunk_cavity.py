"""Keep the filament-saving underside pocket inside the revised outer walls."""
from build123d import Face, Wire, Solid, Plane, Kind, Compound, ShapeList, Vector

MIN_SIDE_WALL_MM = 8.0


def bound_trunk_cavity(cutter, bottom_half):
    """Retain the existing roof/draft where they fit, with an 8 mm XY wall guard.

    The old tapered tool can grow beyond the newly narrowed footprint. Its
    intersection with the inset envelope keeps that tool from cutting out the
    side walls. This is a local cavity constraint, not scan fit clearance.
    """
    # Unite thin solids first so the mirror seam is removed from the top face.
    blank=Solid.extrude(bottom_half,(0,0,1))
    footprint=blank.fuse(blank.mirror(Plane.YZ)).clean()
    faces=[f for f in footprint.faces() if f.normal_at().Z>.99]
    if len(faces)!=1:
        raise ValueError('Expected one mirrored bottom footprint')
    wire=faces[0].outer_wire().offset_2d(-MIN_SIDE_WALL_MM,kind=Kind.INTERSECTION)
    inset=Face(wire).translate((0,0,-1))
    if not inset.is_valid or inset.area>=faces[0].area:
        raise ValueError('Trunk wall guard must be a valid inward footprint offset')
    envelope=Solid.extrude(inset.translate((0,0,-1000)),(0,0,2000))
    result=cutter.intersect(envelope)
    result=Compound(result) if isinstance(result,ShapeList) else result
    if result is None or not result.is_valid or not result.solids():
        raise ValueError('Trunk wall guard removed the entire cavity')
    return result


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
