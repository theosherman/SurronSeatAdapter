"""Restore the adapter's existing rear printing planes after raising its front."""
from build123d import GeomType,Keep,Plane


def trim_to_rear_print_planes(body):
    """Retain the inward half-spaces of the two actual native rear side faces.

    Use the native rear planes in the placed model, including the approved
    outward offset already applied to the original RearSketch profile.
    Reject missing/ambiguous datums instead of silently choosing another face.
    """
    faces=[f for f in body.faces() if f.geom_type==GeomType.PLANE
           and f.area>5000 and f.center().Y>0
           and abs(f.normal_at().X)>.85 and .4<f.normal_at().Z<.5
           and abs(f.normal_at().Y)<1e-8]
    if len(faces)!=2 or faces[0].normal_at().X*faces[1].normal_at().X>=0:
        raise ValueError('Expected one left and one right original rear printing face')
    datums=[(f.center(),f.normal_at()) for f in sorted(faces,key=lambda f:f.normal_at().X)]
    for point,normal in datums:
        body=body.split(Plane(point,z_dir=normal),Keep.BOTTOM).clean()
    if not body.is_valid or len(body.solids())!=1:
        raise ValueError('Print-plane trim must leave one valid adapter solid')
    for point,normal in datums:
        if max((v.center()-point).dot(normal) for v in body.vertices())>1e-6:
            raise ValueError('Adapter still protrudes beyond a rear printing plane')
    return body
