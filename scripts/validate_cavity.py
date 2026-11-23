"""Verify the exported cavity roof, symmetry, and optional approved STEP parity."""
from pathlib import Path
import json
import argparse
from build123d import import_step,Vector,GeomType
from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector
from OCP.IntCurveSurface import IntCurveSurface_In, IntCurveSurface_Out
from OCP.gp import gp_Dir, gp_Lin, gp_Pnt

from adapter import SKETCHES
from coordinates import ADAPTER_TRANSLATION_MM
from trunk_cavity import rear_cavity_profile,rear_side_tools,CAVITY_ROOF_OFFSET_MM,REAR_WALL_POINT_MM,REAR_WALL_NORMAL,REAR_WALL_THICKNESS_MM,REAR_TIP_POINT_MM,REAR_TIP_NORMAL,REAR_TIP_WALL_THICKNESS_MM,rear_cavity_tool

parser=argparse.ArgumentParser()
parser.add_argument('--approved-step',type=Path)
args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[1]
body=import_step(ROOT/'exports/adapter-body.step')
sketch=SKETCHES['BodyCutSketch']
n=Vector(sketch['normal'])
x,y=map(Vector,(sketch['xAxis'],sketch['yAxis']))
origin=Vector(sketch['originMm'])+Vector(ADAPTER_TRANSLATION_MM)-n*CAVITY_ROOF_OFFSET_MM
profile=rear_cavity_profile(sketch).translate(Vector(ADAPTER_TRANSLATION_MM)-n*CAVITY_ROOF_OFFSET_MM)
samples=[]
intersector=IntCurvesFace_ShapeIntersector()
intersector.Load(body.wrapped,1e-6)
direction=gp_Dir(*n)
grid_mm=1
for v in range(-164,105,grid_mm):
    for u in range(-47,48,grid_mm):
        p=origin+x*u+y*v
        if not profile.is_inside(p):continue
        # Start at the original cavity roof and measure only where the ray
        # still enters material there after the underside and wheel cuts.
        intersector.Perform(gp_Lin(gp_Pnt(*p),direction),-.05,200)
        hits=[(intersector.WParameter(i),intersector.Transition(i))
              for i in range(1,intersector.NbPnt()+1)]
        if not any(abs(t)<.001 and transition==IntCurveSurface_In for t,transition in hits):
            continue
        thickness=[t for t,transition in hits if t>.001 and transition==IntCurveSurface_Out]
        if thickness:samples.append(min(thickness))
assert len(samples)>=1800,len(samples)
minimum=min(samples)
assert minimum>=9.999,minimum
for tool in rear_side_tools():
    overlap=body.intersect(tool)
    assert overlap is None or sum(s.volume for s in overlap.solids())<.001
wall_normal=Vector(REAR_WALL_NORMAL)
wall_point=Vector(REAR_WALL_POINT_MM)
wall_checks=[]
for x_pos in (-25,-15,0,15,25):
    # Sample the surviving wall above the raised underside plane.
    for z_pos in (5,10,15,20):
        y_pos=wall_point.Y-(z_pos-wall_point.Z)*wall_normal.Z/wall_normal.Y
        outer=Vector(x_pos,y_pos,z_pos)
        for depth in (.1,REAR_WALL_THICKNESS_MM/2,REAR_WALL_THICKNESS_MM-.1):
            assert body.is_inside(outer-wall_normal*depth),(x_pos,z_pos,depth)
            wall_checks.append(dict(x=x_pos,z=z_pos,inwardNormalDepthMm=depth))
        assert not body.is_inside(outer-wall_normal*(REAR_WALL_THICKNESS_MM+.1)),(x_pos,z_pos)
report=dict(rearWallNormalThicknessMm=REAR_WALL_THICKNESS_MM,rearWallMaterialChecks=len(wall_checks),valid=body.is_valid,solids=len(body.solids()),volumeMm3=body.volume,
            roofOffsetMm=CAVITY_ROOF_OFFSET_MM,sampledRoofLocations=len(samples),
            minimumSampledRoofMm=minimum,samplingGridMm=grid_mm,
            limitation='Interior roof-normal samples; not a continuous all-surface minimum proof.',
            approvedPreviewSymmetricDifferenceMm3=None)
tip_normal=Vector(REAR_TIP_NORMAL)
cavity=rear_cavity_tool(sketch).translate(ADAPTER_TRANSLATION_MM)
cut_faces=[f for f in body.faces() if f.geom_type==GeomType.PLANE
           and f.normal_at().dot(tip_normal)>.999999]
distances=[f.distance_to(cavity) for f in cut_faces]
# The raised underside cut can remove the outer tip face. Check the original
# cavity limit even where its matching exterior face has been trimmed away.
maximum=max((v.center()-Vector(REAR_TIP_POINT_MM)).dot(tip_normal) for v in cavity.vertices())
assert maximum<=-REAR_TIP_WALL_THICKNESS_MM+1e-5,maximum
assert not distances or min(distances)>=REAR_TIP_WALL_THICKNESS_MM-1e-5,distances
report['lowerTipWallMinimumDistanceMm']=min(distances,default=None)
report['lowerTipPointMm']=REAR_TIP_POINT_MM
report['lowerTipNormal']=REAR_TIP_NORMAL
approved=args.approved_step
if approved is not None:
    ref=import_step(approved)
    def volume(s):return 0 if s is None else sum(p.volume for p in s.solids())
    difference=volume(body.cut(ref))+volume(ref.cut(body))
    assert difference<.001,difference
    report['approvedPreviewSymmetricDifferenceMm3']=difference
assert body.is_valid and len(body.solids())==1
report_path = ROOT/'logs/approved-cavity-validation.json'
report_path.parent.mkdir(exist_ok=True)
report_path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
