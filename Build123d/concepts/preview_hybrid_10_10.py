"""Requested 10 mm wall move + 10 mm cavity-side thickening: native CAD preview.

Standalone review variant; never changes manufacturing exports or build_master.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build123d import import_step,export_step,export_stl,Face,Wire,Solid,Plane,Keep,GeomType,Compound,ShapeList
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from mesh_preview import render
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'exports/concepts/rear-cavity/hybrid-10-10'
MOVE_MM=10.0
EXTRA_WALL_MM=10.0

def combined(shape):
    if shape is None:return Compound([])
    return Compound(shape) if isinstance(shape,(ShapeList,list)) else shape

def one(shape):
    shape=Compound(shape) if isinstance(shape,(ShapeList,list)) else shape
    if not shape.is_valid or len(shape.solids())!=1:
        raise ValueError('Expected one valid native preview solid')
    return shape.solids()[0]

def mesh(shape):
    vs,ts=shape.tessellate(.035,.10)
    return np.array([[tuple(vs[i]) for i in t] for t in ts])

def build():
    original=one(import_step(ROOT/'exports/adapter-body.step'))
    latch=one(import_step(ROOT/'exports/latch.step'))
    wheel=one(import_step(ROOT/'exports/sherman-p-prepared/body-scaled.step'))
    handle=import_step(ROOT/'exports/sherman-p-prepared/rear-handle.step')
    inner=[f for f in original.faces() if 3400<f.area<3500 and 150<f.center().Y<155
           and f.normal_at().Y<-.85 and f.normal_at().Z<-.4]
    if len(inner)!=1:raise ValueError('Current rear cavity face is missing/ambiguous')
    inner=inner[0];p,n=inner.center(),inner.normal_at()
    # Imported source stores this planar drafted face as a B-spline.
    plane_error=max(abs((v.center()-p).dot(n)) for v in inner.vertices())
    if plane_error>1e-5:raise ValueError('Rear cavity face is no longer planar')
    def wall_y(z):return p.Y-n.Z/n.Y*(z-p.Z)-.01
    # Local native surgery: only the rear web and mating feature behind its
    # cavity plane, below the roof. Upper seat structure and front stay fixed.
    region=Solid.extrude(Face(Wire.make_polygon([
        (-150,wall_y(-140),-140),(-150,400,-140),
        (-150,400,60),(-150,wall_y(60),60)],close=True)),(300,0,0))
    moved=one(original.intersect(region)).translate((0,-MOVE_MM,0))
    retained=one(original.cut(region))
    extra=Solid.extrude(inner.translate((0,-MOVE_MM,0)),(0,-EXTRA_WALL_MM,0))
    adapter=one(retained.fuse(moved,extra).clean())
    # Reapply precisely the existing scaled-body cutter, no new allowance.
    adapter=one(adapter.cut(wheel).clean())
    # Extend only the adapter-facing front/top faces; retain original latch.
    mating=[f for f in latch.faces() if f.geom_type==GeomType.PLANE
            and f.normal_at().Y<-.3 and f.center().Z>0]
    if len(mating)!=4:raise ValueError(f'Unexpected latch mating planes: {len(mating)}')
    added=[Solid.extrude(f,(0,-MOVE_MM,0)) for f in mating]
    extended=one(latch.fuse(*added).clean())
    # Trim the swept top transitions against the relocated native adapter.
    # This preview uses their exact boundary; running fit clearance is undecided.
    extended=one(extended.cut(adapter).clean())
    return original,latch,adapter,extended,wheel,handle,extra,region,plane_error

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    original,latch,adapter,extended,wheel,handle,extra,region,plane_error=build()
    # Meaningful checks for a review prototype, including native round trips.
    unchanged_region=Solid.make_box(400,600,300,Plane((-200,-500,-100))) # Y <= 100
    front_old=combined(original.intersect(unchanged_region))
    front_new=combined(adapter.intersect(unchanged_region))
    front_xor=combined(front_old.cut(front_new)).volume+combined(front_new.cut(front_old)).volume
    upper_region=Solid.make_box(400,1000,200,Plane((-200,-500,60.001)))
    upper_old=combined(original.intersect(upper_region));upper_new=combined(adapter.intersect(upper_region))
    upper_xor=combined(upper_old.cut(upper_new)).volume+combined(upper_new.cut(upper_old)).volume
    assert front_xor<.001 and upper_xor<.001
    removed_latch=combined(latch.cut(extended))
    original_hook=combined(latch.split(Plane((0,0,0),z_dir=(0,0,1)),Keep.BOTTOM))
    assert combined(original_hook.cut(extended)).volume<.001
    contact=max((f for f in latch.faces() if f.geom_type==GeomType.PLANE
                 and f.normal_at().Y>.8 and f.normal_at().Z>.4),key=lambda f:f.area)
    # Native back contact plane must remain an exposed face of the new latch.
    normal=contact.normal_at();center=contact.center()
    contact_faces=[f for f in extended.faces() if f.geom_type==GeomType.PLANE
                   and f.normal_at().dot(normal)>1-1e-8
                   and abs((f.center()-center).dot(normal))<1e-6]
    assert abs(sum(f.area for f in contact_faces)-contact.area)<.001
    rows={}
    for name,s in [('adapter-preview',adapter),('latch-preview',extended)]:
        path=OUT/f'{name}.step';export_step(s,path)
        export_stl(s,OUT/f'{name}.stl',tolerance=.035,angular_tolerance=.1)
        reopened=one(import_step(path));assert abs(s.volume-reopened.volume)<.01
        rows[name]=dict(valid=s.is_valid,solids=len(s.solids()),volumeMm3=s.volume,
                       stepRoundtripVolumeDeltaMm3=reopened.volume-s.volume)
    overlap=combined(adapter.intersect(extended)).volume
    report=dict(previewOnly=True,source='current manufacturing STEP exports',
        method='native region translation, face extrusion and solid Boolean; no mesh deformation',
        wallMoveTowardWheelCenterMm=MOVE_MM,additionalCavitySideWallMm=EXTRA_WALL_MM,
        dimensionDirection='negative model Y for both dimensions; not face-normal thickness',
        innerBoundaryTotalYShiftMm=MOVE_MM+EXTRA_WALL_MM,
        movedRegion='behind original cavity rear plane, below Z=60 mm; includes local rear side-wall portions',
        rearCavityPlanarityErrorMm=plane_error,frontUnchangedXorMm3=front_xor,
        upperSeatStructureUnchangedXorMm3=upper_xor,latchContactFacePreserved=True,
        adapterLatchOverlapMm3=overlap,originalLatchMatingMaterialTrimmedMm3=removed_latch.volume,hookBelowZ0Preserved=True,parts=rows,
        originalVolumesMm3=dict(adapter=original.volume,latch=latch.volume),
        productionFilesChanged=False,
        limitations=['Review geometry only; latch transition trimmed to adapter with zero new running clearance; not a print release.',
                    'Native region relocation creates local transitions at the rear web boundary.',
                    'Full-width wheel coverage, mounting access, print planes and fit require design validation.'])
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)
    blue=(81,132,170);teal=(39,160,173);green=(63,158,110);gold=(211,171,91)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
    def half(s):
        cut=s.split(Plane((0,0,0),z_dir=(1,0,0)),Keep.BOTTOM)
        return Compound(cut) if isinstance(cut,(ShapeList,list)) else cut
    originals=[original,latch,wheel,handle]
    proposals=[adapter,extended,wheel,handle]
    full_old=[(mesh(s),c) for s,c in zip(originals,[blue,green,gold,gold])]
    full_new=[(mesh(s),c) for s,c in zip(proposals,[teal,green,gold,gold])]
    cuts_old=[(mesh(half(s)),c) for s,c in zip(originals,[blue,green,gold,gold])]
    cuts_new=[(mesh(half(s)),c) for s,c in zip(proposals,[teal,green,gold,gold])]
    views=[('01-assembled','Assembled rear underside',full_old,full_new,(1,.9,-.35)),
           ('02-cutaway','Solid 3D cutaway / cavity and latch',cuts_old,cuts_new,(1,.4,.18)),
           ('03-exploded','Rear wall and separate extended latch',
            [(full_old[0][0],blue),(full_old[1][0]+[0,45,-12],green)],
            [(full_new[0][0],teal),(full_new[1][0]+[0,45,-12],green)],(1,.6,-.1))]
    for name,title,old,new,eye in views:
        im=Image.new('RGB',(2600,1500),'#e9eef3');d=ImageDraw.Draw(im)
        d.text((35,24),'10 mm wall move + 10 mm extra wall / '+title,font=font(35),fill='#203b50')
        d.text((35,86),'CURRENT MODEL',font=font(25),fill='#203b50')
        d.text((1335,86),'REQUESTED HYBRID PREVIEW',font=font(25),fill='#203b50')
        for i,gs in enumerate([old,new]):
            im.paste(render(gs,eye,(1270,1120),focus=(0,167,23)),(15+i*1300,140))
        d=ImageDraw.Draw(im)
        d.text((35,1300),'Teal: adapter with wall moved inward 10 mm and thickened another 10 mm into the cavity.',font=font(26),fill='#203b50')
        d.text((35,1348),'Green: latch extended 10 mm toward adapter; original wheel-contact face and hook retained. Gold: fixed wheel.',font=font(25),fill='#203b50')
        d.text((35,1432),'NATIVE CAD PREVIEW • dimensions along front-to-back Y • production model unchanged • fit / closure not yet approved',font=font(22),fill='#637889')
        im.save(OUT/f'{name}.png');print(name,flush=True)
    # Single generous cutaway, avoids requiring users to inspect tiny panels.
    hero=Image.new('RGB',(1900,1550),'#e9eef3');d=ImageDraw.Draw(hero)
    d.text((35,25),'Requested hybrid / 10 mm inward + 10 mm thicker wall',font=font(36),fill='#203b50')
    d.text((35,85),'Native current-model variant • cutaway through cavity • latch remains a separate part',font=font(25),fill='#526b7d')
    hero.paste(render(cuts_new,(1,.4,.18),(1860,1190),focus=(0,158,26)),(20,140))
    d=ImageDraw.Draw(hero)
    d.text((35,1370),'TEAL: revised rear wall     GREEN: extended latch     GOLD: stationary wheel reference',font=font(26),fill='#203b50')
    d.text((35,1420),'10 mm wall movement + another 10 mm into the cavity; measurements are along Y.',font=font(25),fill='#203b50')
    d.text((35,1480),'PREVIEW ONLY • production geometry unchanged • fit, dovetail and complete closure require validation',font=font(22),fill='#637889')
    hero.save(OUT/'hybrid-hero.png')
    print(OUT)

if __name__=='__main__':run()
