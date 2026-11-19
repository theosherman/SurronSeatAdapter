"""Approved native front reconstruction in the permanently placed model frame.

Keep the screen and rearward underside, raise the analytic clip, and join
its outer circle to the screen opening with a tangent ramp.
"""
from math import acos, atan2, cos, hypot, pi, sin, sqrt

from build123d import Edge, Face, Wire, Solid, Plane, Keep, GeomType, Compound, ShapeList

from prepare_sherman_p import SEATING_DEPTH_MM

ORIGINAL_CLIP_RISE_MM = 18.052632063736358
CLIP_RISE_MM = ORIGINAL_CLIP_RISE_MM + SEATING_DEPTH_MM
HANDLE_CENTER_Z_MM = 32.87424168191536 + SEATING_DEPTH_MM


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
    start=ramp.bounding_box().max.Y
    # Lift the complete original jaw. The screen-ramp join can move independently;
    # using it as the lift boundary strands part of the jaw at its old height.
    lift_join=(bt+ORIGINAL_CLIP_RISE_MM-br)/(sr-st)+SCREEN_EXTENSION_MM
    split=Plane((0,lift_join,0),z_dir=(0,1,0))
    rear=body.split(split,Keep.TOP)
    clip=body.split(split,Keep.BOTTOM).translate((0,0,CLIP_RISE_MM))
    # The actual upper face supplies the footprint, including its screen boundary
    # and side chamfers. Vertical prisms add thickness, never scale the section.
    footprint=Solid.extrude(top.translate((0,0,-80)),(0,0,160))
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
    # Derive the new ramp from its original lower edge and the outer clip circle.
    # The original crown and the new tangent point lie on the same circle.
    outer = max((edge for edge in clip.edges()
                 if edge.geom_type == GeomType.CIRCLE and edge.arc_center.Y < -210),
                key=lambda edge: edge.radius)
    center, radius = outer.arc_center, outer.radius
    start_z = sr*start+br
    dy, dz = start-center.Y, start_z-center.Z
    angle = atan2(dz, dy) + acos(radius / hypot(dy, dz))

    def circle_point(theta):
        return (-100, center.Y+radius*cos(theta), center.Z+radius*sin(theta))

    crown_angle = pi / 2
    crown = circle_point(crown_angle)
    tangent = circle_point(angle)
    ramp_start = (-100, start, start_z)
    floor_front = (-100, start, 0)
    floor_back = (-100, crown[1], 0)
    contour = Edge.make_three_point_arc(crown, circle_point((angle+crown_angle)/2), tangent)
    profile = Face(Wire([contour, Edge.make_line(tangent, ramp_start),
                         Edge.make_line(ramp_start, floor_front),
                         Edge.make_line(floor_front, floor_back),
                         Edge.make_line(floor_back, crown)]))
    envelope = Solid.extrude(profile, (200,0,0))
    gusset = Compound(gusset) if isinstance(gusset,ShapeList) else gusset
    gusset = gusset.intersect(envelope)
    bridge_footprint = Solid.extrude(top, (0,0,100)).fuse(Solid.extrude(ramp, (0,0,100))).clean()
    bridge = envelope.intersect(bridge_footprint)
    # Start the trim 0.05 mm into the original flat to avoid a vanishing
    # Boolean intersection at the old circle-to-flat tangency.
    join = max((outer @ 0, outer @ 1), key=lambda point: point.Y)
    join_y = join.Y + 0.05
    join_z = sqrt(radius**2-(join_y-center.Y)**2)
    join_angle = atan2(join_z, join_y-center.Y)
    arc_join = circle_point(join_angle)
    arc_trim = Edge.make_three_point_arc(arc_join, circle_point((join_angle+angle)/2), tangent)
    tangent_top = (-100,tangent[1],100)
    join_top = (-100,join_y,100)
    arc_air = Solid.extrude(Face(Wire([arc_trim, Edge.make_line(tangent,tangent_top),
        Edge.make_line(tangent_top,join_top), Edge.make_line(join_top,arc_join)])), (200,0,0))
    ramp_air = prism_yz([(tangent[1],tangent[2]),(start,start_z),(start,100),(tangent[1],100)])
    clip = clip.cut(ramp_air).cut(arc_air)
    bore_edge = next(edge for edge in clip.edges() if edge.geom_type == GeomType.CIRCLE
                     and abs(edge.radius-15.1) < 1e-6)
    bore_center = bore_edge.arc_center
    bore = Solid.make_cylinder(bore_edge.radius,200,
        Plane((-100,bore_center.Y,bore_center.Z),z_dir=(1,0,0)))
    bridge = Compound(bridge) if isinstance(bridge,ShapeList) else bridge
    gusset = Compound(gusset) if isinstance(gusset,ShapeList) else gusset
    bridge = bridge.cut(bore)
    bridge = Compound(bridge) if isinstance(bridge,ShapeList) else bridge
    result = rear.fuse(clip,bridge,gusset).clean()
    if len(result.solids())!=1 or not result.is_valid:
        raise ValueError('Raised front reconstruction is not one valid solid')
    return result
