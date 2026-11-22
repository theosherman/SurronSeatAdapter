"""Native screen walls joining the existing body-top and front-ramp planes."""
from build123d import GeomType,Plane,Keep,Solid,Compound,ShapeList,Face,Wire
from reference.wheel import SEAT_LOWERING_MM

SCREEN_REAR_JOIN_Y_MM = -87.0


def reinforce_screen(body):
    """Carry the raised sides into the front ramp and the original body top.

    Native face datums define the start, angle, aperture and central ramp. No
    manufacturing geometry is loaded from preview meshes or exchange exports.
    """
    planes=[f for f in body.faces() if f.geom_type==GeomType.PLANE]
    rear=next(f for f in planes if f.area>2000 and -103<f.center().Y<-100
              and f.normal_at().Y<-.99)
    bottom=next(f for f in planes if f.area>4000 and abs(f.normal_at().X)<1e-6
                and f.normal_at().Z<-.99 and f.normal_at().Y<-.1)
    ramp=next(f for f in planes if f.area>3000 and .84<f.normal_at().Y<.86
              and .52<f.normal_at().Z<.54)
    bodytop=next(f for f in planes if f.area>2000
                 and -.27<f.normal_at().Y<-.26 and .96<f.normal_at().Z<.97
                 and f.bounding_box().max.Y>rear.center().Y)
    rails=[f for f in planes if f.area>800 and -160<f.center().Y<-145
           and f.normal_at().Z>.99]
    if len(rails)!=2:
        raise ValueError('Expected both original screen-side top faces')
    y0,z0=rear.center().Y,rear.bounding_box().max.Z
    y1=ramp.bounding_box().min.Y
    slope=-bottom.normal_at().Y/bottom.normal_at().Z
    rail_z = z0 - 8.0 + SEAT_LOWERING_MM
    target=Plane((0,y0,rail_z),x_dir=(1,0,0),z_dir=(0,-slope,1))
    slab=Solid.make_box(200,SCREEN_REAR_JOIN_Y_MM-y1,200,Plane((-100,y1,-50)))
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
    # The wall-top envelope follows the rail plane up to the rear of the
    # aperture, then slopes back to the body top ahead of the bolt seats.
    above_top=shape(slab.split(target,Keep.TOP))
    above_bodytop=shape(slab.split(
        Plane(bodytop.center(),z_dir=bodytop.normal_at()),Keep.TOP))
    top_point, top_normal = bodytop.center(), bodytop.normal_at()
    join_z = top_point.Z - top_normal.Y / top_normal.Z * (SCREEN_REAR_JOIN_Y_MM - top_point.Y)
    blend = Plane((0,y0,rail_z), z_dir=(0,(rail_z-join_z)/(SCREEN_REAR_JOIN_Y_MM-y0),1))
    aft = shape(slab.split(Plane((0,y0,0), z_dir=(0,1,0)), Keep.TOP))
    above_blend = shape(aft.split(blend, Keep.TOP))
    above_sides=shape(above_top.fuse(above_blend).intersect(above_bodytop))
    additions=[]
    for face in planes:
        n=face.normal_at()
        if abs(n.X)>1e-6 or n.Z<.52 or face.area<500:
            continue
        if face.bounding_box().min.Y>=SCREEN_REAR_JOIN_Y_MM or face.bounding_box().max.Y<=y1:
            continue
        piece=shape(Solid.extrude(face,(0,0,100)).intersect(slab))
        if not piece.solids():
            continue
        piece=shape(piece.cut(above_sides))
        # Keep additions out of the aperture and air above the central incline.
        piece=shape(shape(piece).cut(aperture,ramp_air))
        if piece.volume>1e-6:
            additions.append(piece)
    result=body.fuse(*additions).clean()
    # Lower both original rail material and reinforcement. Retain the higher
    # uphill ramp so the rails flow into it instead of ending at a vertical step.
    above_ramp=shape(slab.split(Plane(point,z_dir=normal),Keep.TOP))
    cap=shape(above_sides.intersect(above_ramp))
    result=result.cut(cap).clean()
    if not result.is_valid or len(result.solids())!=1:
        raise ValueError('Screen reinforcement must leave one valid adapter solid')
    return result
