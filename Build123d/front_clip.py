"""Approved native front reconstruction in the permanently placed model frame.

Keep the screen and rearward underside, extend the screen-front plane upwards,
and relocate the existing analytic clip. The source recipe is never edited.
"""
from build123d import Face, Wire, Solid, Plane, Keep, GeomType, Compound, ShapeList

CLIP_RISE_MM = 18.052632063736358
HANDLE_CENTER_Z_MM = 32.87424168191536


def prism_yz(points, width=200):
    face=Face(Wire.make_polygon([(-width/2,y,z) for y,z in points],close=True))
    return Solid.extrude(face,(width,0,0))


def redesign_front(body):
    planes=[f for f in body.faces() if f.geom_type==GeomType.PLANE]
    from bottom_outline import SCREEN_EXTENSION_MM
    ramp=next(f for f in planes if f.area>1500 and -176-SCREEN_EXTENSION_MM<f.center().Y<-170-SCREEN_EXTENSION_MM
              and .81<f.normal_at().Y<.83 and .57<f.normal_at().Z<.58)
    top=next(f for f in planes if f.area>4000 and -200<f.center().Y<-175
             and f.normal_at().Z>.99)
    bottom=next(f for f in planes if f.area>10000
                and f.normal_at().Z<-.99 and abs(f.normal_at().Y+.118)<.002)
    def line(face):
        p,n=face.center(),face.normal_at()
        slope=-n.Y/n.Z
        return slope,p.Z-slope*p.Y
    sr,br=line(ramp);st,bt=line(top);sb,bb=line(bottom)
    start=ramp.bounding_box().min.Y
    join=(bt+CLIP_RISE_MM-br)/(sr-st)
    # Lift the complete original jaw. The screen-ramp join can move independently;
    # using it as the lift boundary strands part of the jaw at its old height.
    lift_join=join+SCREEN_EXTENSION_MM
    split=Plane((0,lift_join,0),z_dir=(0,1,0))
    rear=body.split(split,Keep.TOP)
    clip=body.split(split,Keep.BOTTOM).translate((0,0,CLIP_RISE_MM))
    # The actual upper face supplies the footprint, including its screen boundary
    # and side chamfers. Vertical prisms add thickness, never scale the section.
    footprint=Solid.extrude(top.translate((0,0,-80)),(0,0,160))
    wedge=prism_yz([(start,st*start+bt),(join,st*join+bt),
                    (join,sr*join+br)]).intersect(footprint)
    # Small local root gusset joins the retained lower line to the raised jaw.
    # Its front end is safely forward of the bridge but behind the bore's rear
    # tangent (Y=-205.2743), so it cannot close or resize the circular bore.
    # The root datum follows the original lift boundary, independently of screen.
    bore_rear=-205.27430326680117
    root_end=-199.0
    if not bore_rear < root_end < lift_join:
        raise ValueError('Screen extension leaves no room for the clip root gusset')
    clip_section=clip.intersect(Plane((0,root_end,0),z_dir=(0,1,0)))
    lower=min(v.center().Z for v in clip_section.vertices())
    gusset=prism_yz([(lift_join,sb*lift_join+bb),(root_end,lower),
                     (root_end,st*root_end+bt+CLIP_RISE_MM),
                     (lift_join,st*lift_join+bt+CLIP_RISE_MM)]).intersect(footprint)
    # Plane/solid intersections return ShapeList in build123d 0.13.
    wedge=Compound(wedge) if isinstance(wedge,ShapeList) else wedge
    gusset=Compound(gusset) if isinstance(gusset,ShapeList) else gusset
    result=rear.fuse(clip,wedge,gusset).clean()
    # Remove only the upper central connector above the moved screen ramp;
    # leave the original complete clip and its lower support envelope intact.
    ramp_air=prism_yz([(join,sr*join+br),(start,sr*start+br),
                      (start,200),(join,200)],width=86)
    result=result.cut(ramp_air).clean()
    if len(result.solids())!=1 or not result.is_valid:
        raise ValueError('Raised front reconstruction is not one valid solid')
    return result
