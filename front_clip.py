"""Approved native front reconstruction in the permanently placed model frame.

Raise the analytic clip and join the screen opening and underside to its
curves with tangent ramps. Trim the main underside to retain the imprint depth.
"""
from math import acos, atan2, cos, hypot, sin, sqrt

from build123d import Edge, Face, Wire, Solid, Plane, Keep, GeomType, Compound, ShapeList, Vector

from reference.wheel import SEATING_DEPTH_MM, SEAT_LOWERING_MM

ORIGINAL_CLIP_RISE_MM = 18.052632063736358
CLIP_RISE_MM = ORIGINAL_CLIP_RISE_MM + SEATING_DEPTH_MM
HANDLE_CENTER_Z_MM = 32.87424168191536 + SEATING_DEPTH_MM
CLIP_BORE_RADIUS_MM = 29.7 / 2


def fitted_clip_curves(curves):
    """Redraw the bore and its two tangent jaws in HandleMountSketch."""
    if not any(abs(curve.get("radiusMm", 0) - 15.1) < 1e-6 for curve in curves):
        return curves
    rear_jaw, bore, front_jaw, *outer = curves
    center = Vector(bore['centerMm'])
    bore_points = {
        key: tuple(center + (Vector(bore[key]) - center).normalized() * CLIP_BORE_RADIUS_MM)
        for key in ('startMm', 'midMm', 'endMm')
    }
    jaws = []
    for jaw, inner_key in ((rear_jaw, 'endMm'), (front_jaw, 'startMm')):
        outer_key = 'startMm' if inner_key == 'endMm' else 'endMm'
        inner_point = Vector(bore_points[inner_key])
        outer_point = Vector(jaw[outer_key])
        # Each jaw is a semicircle between the concentric bore and outer crown.
        jaw_center = (inner_point + outer_point) / 2
        jaw_radius = (outer_point - inner_point).length / 2
        mid_direction = (Vector(jaw['midMm']) - Vector(jaw['centerMm'])).normalized()
        jaws.append(dict(jaw, **{inner_key: tuple(inner_point)},
                         midMm=tuple(jaw_center + mid_direction * jaw_radius),
                         centerMm=tuple(jaw_center), radiusMm=jaw_radius))
    return [jaws[0], dict(bore, **bore_points, radiusMm=CLIP_BORE_RADIUS_MM), jaws[1], *outer]


def prism_yz(points, width=200):
    face=Face(Wire.make_polygon([(-width/2,y,z) for y,z in points],close=True))
    return Solid.extrude(face,(width,0,0))


def main_underside(body):
    return next(f for f in body.faces() if f.geom_type == GeomType.PLANE
                and f.area > 10000 and f.normal_at().Z < -.99
                and abs(f.normal_at().Y + .118) < .002)


def trim_main_underside(body):
    underside = main_underside(body)
    front_y = underside.bounding_box().min.Y
    rear_y = body.bounding_box().max.Y + 1
    datum, normal = underside.center(), underside.normal_at()
    slope = -normal.Y / normal.Z
    front_z = datum.Z + slope * (front_y - datum.Y) + SEAT_LOWERING_MM
    rear_z = front_z + slope * (rear_y - front_y)
    floor = body.bounding_box().min.Z - 1
    return body.cut(prism_yz([(front_y, front_z), (rear_y, rear_z),
                             (rear_y, floor), (front_y, floor)]))


def redesign_front(body):
    planes=[f for f in body.faces() if f.geom_type==GeomType.PLANE]
    from bottom_outline import SCREEN_EXTENSION_MM
    ramp=next(f for f in planes if f.area>1500 and -176-SCREEN_EXTENSION_MM<f.center().Y<-170-SCREEN_EXTENSION_MM
              and .81<f.normal_at().Y<.83 and .57<f.normal_at().Z<.58)
    top=next(f for f in planes if f.area>4000 and -200<f.center().Y<-175
             and f.normal_at().Z>.99)
    bottom=main_underside(body)
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
    # Draw the lower ramp tangent to the rear jaw from the raised underside
    # at the lift boundary. The gusset and bridge share this lower line.
    jaw = next(edge for edge in clip.intersect(Plane.YZ).edges()
               if edge.geom_type == GeomType.CIRCLE and 5 < edge.radius < 6
               and -210 < edge.arc_center.Y < -195)
    jaw_center = jaw.arc_center
    root_z = sb*lift_join+bb+SEAT_LOWERING_MM
    dy, dz = lift_join-jaw_center.Y, root_z-jaw_center.Z
    jaw_angle = atan2(dz, dy) - acos(jaw.radius / hypot(dy, dz))
    contact_y = jaw_center.Y + jaw.radius*cos(jaw_angle)
    contact_z = jaw_center.Z + jaw.radius*sin(jaw_angle)
    lower_slope = (root_z-contact_z) / (lift_join-contact_y)
    gusset=prism_yz([(lift_join,root_z),(contact_y,contact_z),
                     (contact_y,st*contact_y+bt+CLIP_RISE_MM),
                     (lift_join,st*lift_join+bt+CLIP_RISE_MM)]).intersect(footprint)
    # Derive the new ramp from its original lower edge and the outer clip circle.
    # The original crown and the new tangent point lie on the same circle.
    outer = max((edge for edge in clip.edges()
                 if edge.geom_type == GeomType.CIRCLE and edge.arc_center.Y < -210),
                key=lambda edge: edge.radius)
    center, radius = outer.arc_center, outer.radius
    start_z = sr*start+br+SEAT_LOWERING_MM
    dy, dz = start-center.Y, start_z-center.Z
    angle = atan2(dz, dy) + acos(radius / hypot(dy, dz))

    def circle_point(theta):
        return (-100, center.Y+radius*cos(theta), center.Z+radius*sin(theta))

    arc_start_angle = acos((contact_y-center.Y) / radius)
    arc_start = circle_point(arc_start_angle)
    tangent = circle_point(angle)
    ramp_start = (-100, start, start_z)
    floor_at_screen = (-100, start, root_z+lower_slope*(start-lift_join))
    floor_at_jaw = (-100, contact_y, contact_z)
    contour = Edge.make_three_point_arc(arc_start, circle_point((angle+arc_start_angle)/2), tangent)
    profile = Face(Wire([contour, Edge.make_line(tangent, ramp_start),
                         Edge.make_line(ramp_start, floor_at_screen),
                         Edge.make_line(floor_at_screen, floor_at_jaw),
                         Edge.make_line(floor_at_jaw, arc_start)]))
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
                     and abs(edge.radius-CLIP_BORE_RADIUS_MM) < 1e-6)
    bore_center = bore_edge.arc_center
    bore = Solid.make_cylinder(bore_edge.radius,200,
        Plane((-100,bore_center.Y,bore_center.Z),z_dir=(1,0,0)))
    bridge = Compound(bridge) if isinstance(bridge,ShapeList) else bridge
    gusset = Compound(gusset) if isinstance(gusset,ShapeList) else gusset
    bridge = bridge.cut(bore)
    gusset = gusset.cut(bore)
    bridge = Compound(bridge) if isinstance(bridge,ShapeList) else bridge
    result = rear.fuse(clip,bridge,gusset).clean()
    if len(result.solids())!=1 or not result.is_valid:
        raise ValueError('Raised front reconstruction is not one valid solid')
    return result
