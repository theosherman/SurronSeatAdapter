"""Verify the exported cavity roof, symmetry, and optional approved STEP parity."""
from pathlib import Path
import json
from build123d import import_step,Vector,Axis
from adapter import SKETCHES
from coordinates import ADAPTER_TRANSLATION_MM
from trunk_cavity import rear_cavity_profile,rear_side_tools,CAVITY_ROOF_OFFSET_MM

ROOT=Path(__file__).resolve().parent
body=import_step(ROOT/'exports/adapter-body.step')
sketch=SKETCHES['BodyCutSketch']
n=Vector(sketch['normal'])
x,y=map(Vector,(sketch['xAxis'],sketch['yAxis']))
origin=Vector(sketch['originMm'])+Vector(ADAPTER_TRANSLATION_MM)-n*CAVITY_ROOF_OFFSET_MM
profile=rear_cavity_profile(sketch).translate(Vector(ADAPTER_TRANSLATION_MM)-n*CAVITY_ROOF_OFFSET_MM)
samples=[]
for v in range(-164,105,2):
    for u in range(-47,48,2):
        p=origin+x*u+y*v
        if not profile.is_inside(p):continue
        # Sample interior of the newly exposed roof; points outside body or on
        # existing openings are counted separately, not assigned a thickness.
        if not body.is_inside(p+n*.05):continue
        distances=[(point-p).dot(n) for point,_ in body.find_intersection_points(Axis(p,n)) if (point-p).dot(n)>1e-3]
        if distances:samples.append(min(distances))
assert len(samples)>2000
minimum=min(samples)
assert minimum>=9.999,minimum
for tool in rear_side_tools():
    overlap=body.intersect(tool)
    assert overlap is None or sum(s.volume for s in overlap.solids())<.001
report=dict(valid=body.is_valid,solids=len(body.solids()),volumeMm3=body.volume,
            roofOffsetMm=CAVITY_ROOF_OFFSET_MM,sampledRoofLocations=len(samples),
            minimumSampledRoofMm=minimum,samplingGridMm=2,
            limitation='Interior roof-normal samples; not a continuous all-surface minimum proof.',
            approvedPreviewSymmetricDifferenceMm3=None)
approved=ROOT/'tmp/requested-cavity-preview/concept.step'
if approved.exists():
    ref=import_step(approved)
    def volume(s):return 0 if s is None else sum(p.volume for p in s.solids())
    difference=volume(body.cut(ref))+volume(ref.cut(body))
    assert difference<.001,difference
    report['approvedPreviewSymmetricDifferenceMm3']=difference
assert body.is_valid and len(body.solids())==1
(ROOT/'logs/approved-cavity-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
