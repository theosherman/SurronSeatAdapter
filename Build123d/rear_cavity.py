"""Approved native rear web relocation and separate latch interface adaptation."""
import math
from build123d import Compound,ShapeList,Face,Wire,Solid,GeomType

REAR_WALL_MOVE_MM=10.0
REAR_WALL_EXTRA_MM=10.0

def combined(shape):
    if shape is None:return Compound([])
    return Compound(shape) if isinstance(shape,(ShapeList,list)) else shape

def one(shape):
    shape=combined(shape)
    if not shape.is_valid or len(shape.solids())!=1:
        raise ValueError('Rear cavity operation must produce one valid solid')
    return shape.solids()[0]

def dimension(value,name):
    if not math.isfinite(value) or value<0:
        raise ValueError(f'{name} must be finite and nonnegative')

def revise_rear_wall(body,move=REAR_WALL_MOVE_MM,extra=REAR_WALL_EXTRA_MM):
    """Move the lower rear web -Y, then add extra material on its cavity side.

    Both dimensions are axial Y distances, not offsets normal to drafted faces.
    Fresh native feature geometry supplies the rear plane, roof and dovetail.
    The wheel imprint remains a subsequent independent body-only subtraction.
    """
    dimension(move,'Rear wall movement');dimension(extra,'Rear wall addition')
    if not move and not extra:return body
    faces=[f for f in body.faces() if f.area>2000 and 120<f.center().Y<180
           and f.normal_at().Y<-.85 and -.5<f.normal_at().Z<-.4]
    if len(faces)!=1:raise ValueError('Expected one original drafted rear cavity face')
    inner=faces[0];point,normal=inner.center(),inner.normal_at()
    if max(abs((v.center()-point).dot(normal)) for v in inner.vertices())>1e-5:
        raise ValueError('Rear cavity datum must be planar')
    def y_at(z):return point.Y-normal.Z/normal.Y*(z-point.Z)-.01
    # A 0.01 mm overlap at the inner datum avoids coincident-face ambiguity.
    # Roof above Z=60 and all geometry forward of the cavity rear web stay put.
    region=Solid.extrude(Face(Wire.make_polygon([
        (-150,y_at(-140),-140),(-150,400,-140),(-150,400,60),
        (-150,y_at(60),60)],close=True)),(300,0,0))
    moved=one(body.intersect(region)).translate((0,-move,0))
    retained=one(body.cut(region))
    additions=[Solid.extrude(inner.translate((0,-move,0)),(0,-extra,0))] if extra else []
    return one(retained.fuse(moved,*additions).clean())

def extend_latch(latch,adapter,move=REAR_WALL_MOVE_MM,clearance=.2):
    """Extend adapter-facing planes; retain hook/contact and clear native mates.

    The existing source latch supplies all outside faces and original clearance.
    Offset only nearby planar adapter mating faces, never the wheel cutter.
    """
    dimension(move,'Latch extension');dimension(clearance,'Latch clearance')
    if not move:return latch
    mates=[f for f in latch.faces() if f.geom_type==GeomType.PLANE
           and f.normal_at().Y<-.3 and f.center().Z>0]
    if len(mates)!=4:raise ValueError('Expected four latch front/top mating faces')
    extensions=[Solid.extrude(f,(0,-move,0)) for f in mates]
    extended=one(latch.fuse(*extensions).clean())
    cutters=[adapter]
    if clearance:
        for face in adapter.faces():
            if face.geom_type==GeomType.PLANE and face.distance_to(extended)<clearance+1e-5:
                cutters.append(Solid.extrude(face,face.normal_at()*clearance))
    return one(extended.cut(*cutters).clean())
