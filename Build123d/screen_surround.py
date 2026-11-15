"""Native reinforcement of screen-side walls, retaining the original front ramp."""
from build123d import GeomType,Plane,Keep,Solid,Compound,ShapeList,Face,Wire


def reinforce_screen(body):
    """Add above the existing top, parallel to the underside, without a front ledge.

    Native face datums define the start, angle, aperture and central ramp. No
    manufacturing geometry is loaded from preview meshes or exchange exports.
    """
    planes=[f for f in body.faces() if f.geom_type==GeomType.PLANE]
    rear=next(f for f in planes if f.area>2000 and -103<f.center().Y<-100
              and f.normal_at().Y<-.99)
    cliptop=next(f for f in planes if f.area>1000 and f.center().Y<-200
                 and f.normal_at().Z>.99)
    bottom=next(f for f in planes if f.area>4000 and abs(f.normal_at().X)<1e-6
                and f.normal_at().Z<-.99 and f.normal_at().Y<-.1)
    ramp=next(f for f in planes if f.area>3000 and .81<f.normal_at().Y<.83
              and .57<f.normal_at().Z<.58)
    rails=[f for f in planes if f.area>800 and -160<f.center().Y<-145
           and f.normal_at().Z>.99]
    if len(rails)!=2:
        raise ValueError('Expected both original screen-side top faces')
    y0,z0=rear.center().Y,rear.bounding_box().max.Z
    # Side wings may extend behind the central ramp join; use plane intersection,
    # not the face's bounding box, as the front limit of side reinforcement.
    def yz_line(face):
        p,n=face.center(),face.normal_at()
        m=-n.Y/n.Z
        return m,p.Z-m*p.Y
    mr,br=yz_line(ramp);mc,bc=yz_line(cliptop)
    y1=(bc-br)/(mr-mc)
    slope=-bottom.normal_at().Y/bottom.normal_at().Z
    target=Plane((0,y0,z0),x_dir=(1,0,0),z_dir=(0,-slope,1))
    slab=Solid.make_box(200,y0-y1,200,Plane((-100,y1,-50)))
    yfront=min(f.bounding_box().min.Y for f in rails)
    xmin,xmax=rear.bounding_box().min.X,rear.bounding_box().max.X
    aperture=Solid.make_box(xmax-xmin,y0-yfront,200,Plane((xmin,yfront,-50)))
    point,normal=ramp.center(),ramp.normal_at()
    def ramp_z(y):
        return point.Z-normal.Y/normal.Z*(y-point.Y)
    low,high=ramp.bounding_box().min.Y,ramp.bounding_box().max.Y
    polygon=[(xmin,low,ramp_z(low)),(xmin,high,ramp_z(high)),
             (xmin,high,150),(xmin,low,150)]
    ramp_air=Solid.extrude(Face(Wire.make_polygon(polygon,close=True)),(xmax-xmin,0,0))
    def shape(value):
        return Compound(value) if isinstance(value,(list,ShapeList)) else value
    additions=[]
    for face in planes:
        n=face.normal_at()
        if abs(n.X)>1e-6 or n.Z<.55 or face.area<500:
            continue
        if face.bounding_box().min.Y>=y0 or face.bounding_box().max.Y<=y1:
            continue
        piece=shape(Solid.extrude(face,(0,0,100)).intersect(slab))
        if not piece.solids():
            continue
        piece=piece.split(target,Keep.BOTTOM)
        if piece is None:
            continue
        # Remove the unwanted front ledge from additions only. The original
        # solid, including its continuous 55 degree ramp, is never subtracted.
        piece=shape(shape(piece).cut(aperture,ramp_air))
        if piece.volume>1e-6:
            additions.append(piece)
    if not additions:
        raise ValueError('No screen-side reinforcement was constructed')
    result=body.fuse(*additions).clean()
    if not result.is_valid or len(result.solids())!=1:
        raise ValueError('Screen reinforcement must leave one valid adapter solid')
    return result
