"""Preview only: infer rear grip circle from the scan; never change CAD solids."""
from pathlib import Path
Path('/tmp/surron-seat-adapter-previews/Build123d/logs').mkdir(parents=True,exist_ok=True)
Path('/tmp/surron-seat-adapter-previews/Build123d/exports').mkdir(parents=True,exist_ok=True)
import json
import numpy as np
from scipy.optimize import least_squares
from PIL import Image, ImageDraw, ImageFont
from build123d import import_step, GeomType, Vector

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'exports'
DTYPE = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)), ('attribute', '<u2')])


def triangles(name):
    raw = (OUT/name).read_bytes()
    count = int.from_bytes(raw[80:84], 'little')
    if len(raw) != 84+50*count:
        raise ValueError('Expected binary STL')
    return np.frombuffer(raw, dtype=DTYPE, offset=84)['vertices'].astype(float)


def section(mesh, x=0):
    segments = []
    for triangle in mesh:
        points = []
        for i, j in ((0, 1), (1, 2), (2, 0)):
            a, b = triangle[i], triangle[j]
            if (a[0]-x)*(b[0]-x) < 0:
                points.append((a+(b-a)*((x-a[0])/(b[0]-a[0])))[1:])
        if len(points) == 2:
            segments.append(points)
    return np.array(segments)


scan = triangles('sherman-p-prepared/rear-handle.stl')
latch = triangles('latch.stl')
adapter = triangles('adapter-body.stl')
master = import_step(OUT/'adapter-body.step')
clip_arcs = [e for e in master.edges() if e.geom_type == GeomType.CIRCLE
             and e.arc_center.Y < -200 and 10 < e.radius < 20]
if not clip_arcs or max(e.radius for e in clip_arcs)-min(e.radius for e in clip_arcs)>1e-6:
    raise ValueError('Cannot identify a unique front clip inner radius')
radius = float(clip_arcs[0].radius)
sections = {}
for x in (-40, -20, 0, 20, 40):
    segments = section(scan, x)
    points = np.unique(segments.reshape(-1, 2), axis=0)
    # User: both handles match the clip bore. Only the crown of the scan is reliable.
    top_z = points[:, 1].max()
    upper = points[(points[:, 0] > 210) & (points[:, 1] >= top_z-3.0)]
    fit = least_squares(lambda c: np.linalg.norm(upper-c, axis=1)-radius,
                        [231, top_z-radius], loss='soft_l1', f_scale=0.1)
    sections[x] = dict(centerYZmm=fit.x.tolist(), radiusMm=radius,
                       trustedTopBandMm=3.0, topZmm=float(top_z),
                       rmsResidualMm=float(np.sqrt(np.mean(fit.fun**2))), points=len(upper))
center = np.array(sections[0]['centerYZmm'])
# Analytic outward-facing back plane of the existing latch, toward the grip.
solid = import_step(OUT/'latch.step')
face = max((f for f in solid.faces() if f.geom_type == GeomType.PLANE
            and f.normal_at().Y > 0.8 and f.normal_at().Z > 0.4), key=lambda f: f.area)
normal = np.array([face.normal_at().Y, face.normal_at().Z])
plane_point = np.array([face.center().Y, face.center().Z])
distance = float((center-plane_point) @ normal)
overlap = radius-distance
contact = center-normal*distance
contact_on_face = face.distance_to(Vector(0, *contact)) < 1e-5
if not contact_on_face:
    raise ValueError('Inferred tangency is outside the actual latch face')
surface = center-normal*radius
target = surface+normal  # 1 mm inward from the inferred circle, along face normal.
report = dict(previewOnly=True, frame='Build123d; Y rearward, Z up',
              source='exports/sherman-p-prepared/rear-handle.stl',
              sectionFits={str(k): v for k,v in sections.items()},
              selectedSectionXmm=0, fixedDiameterFromClipMm=2*radius,
              diameterSource='Front clip analytic inner arcs from adapter-body.step; same front/rear handle size per user',
              existingLatchPlaneNormalYZ=normal.tolist(),
              existingPlaneDistanceToCircleCenterMm=distance,
              existingNormalInterferenceMm=overlap, contactOnActualFace=contact_on_face,
              requestedNormalInterferenceMm=1.0,
              requiredPlaneOffsetMm=1.0-overlap,
              caveat='Fixed clip diameter positioned using only the uppermost 3 mm of the rear scan; sides/underside excluded. Plane interference assumes contact is within the face.',
              cadGeometryChanged=False)
Path('/tmp/surron-seat-adapter-previews/Build123d/logs/rear-handle-circle-preview.json').write_text(json.dumps(report, indent=2)+'\n')

W,H=1600,1000
image=Image.new('RGB',(W,H),'#f6f8fb')
draw=ImageDraw.Draw(image)
font_path='/usr/share/fonts/TTF/DejaVuSans.ttf'
font=lambda n:ImageFont.truetype(font_path,n)
draw.text((32,23),'Rear handle circle estimate / latch contact',font=font(30),fill='#193047')
draw.text((32,70),'PREVIEW ONLY — exact clip diameter; trusted scan crown fitted; sides / underside ignored; no CAD changes',font=font(20),fill='#46576b')
for panel in (0,1):
    tile=Image.new('RGB',(780,690),'#ffffff'); d=ImageDraw.Draw(tile)
    scale=7.0 if panel==0 else 11.0
    ymid,zmid=(215,-3) if panel==0 else (228,-22)
    def xy(point):
        y,z=point
        return (390+(y-ymid)*scale,345-(z-zmid)*scale)
    if panel==0:
        for mesh,color in ((scan,'#c5a04b'),(adapter,'#428cba'),(latch,'#40a875')):
            for triangle in mesh[np.argsort(mesh[:,:,0].mean(axis=1))]:
                if triangle[:,1].max()<150:continue
                d.polygon([xy(p[1:]) for p in triangle],fill=color)
    else:
        for mesh,color in ((scan,'#c5a04b'),(latch,'#309267')):
            for segment in section(mesh):d.line([xy(p) for p in segment],fill=color,width=4)
    # Ideal circle is purely an annotation, not an exported CAD object.
    pts=[xy(center+radius*np.array([np.cos(t),np.sin(t)])) for t in np.linspace(0,2*np.pi,241)]
    d.line(pts,fill='#a53567',width=3)
    cx,cz=xy(center)
    d.line((cx-11,cz,cx+11,cz),fill='#a53567',width=2)
    d.line((cx,cz-11,cx,cz+11),fill='#a53567',width=2)
    if panel==1:
        crown = np.unique(section(scan).reshape(-1,2),axis=0)
        crown = crown[crown[:,1] >= crown[:,1].max()-3.0]
        for p in crown:
            px,py = xy(p)
            d.ellipse((px-3,py-3,px+3,py+3),fill='#138d9d')
        # Show existing and target parallel planes near the contact region.
        tangent=np.array([-normal[1],normal[0]])
        for t in np.arange(-14,14,1.5):
            d.line([xy(target+t*tangent),xy(target+(t+.8)*tangent)],fill='#df5d34',width=3)
        d.line([xy(surface),xy(target)],fill='#df5d34',width=5)
        d.line([xy(contact),xy(contact+normal*5)],fill='#238355',width=2)
        q=xy(contact+normal*6)
        d.text(q,f'Current: ~{overlap:.1f} mm',font=font(18),fill='#237451')
        d.rectangle((0,0,780,58),fill='white')
        d.rectangle((0,580,780,690),fill='white')
        d.text((28,24),'X = 0 section; cyan points = trusted crown',font=font(21),fill='#193047')
        d.text((28,590),'Green: existing latch section',font=font(19),fill='#237451')
        d.text((28,620),'Orange dashed: plane for 1 mm interference',font=font(19),fill='#c7512c')
        d.text((28,650),'Gold: scanned surface; magenta: inferred circle',font=font(19),fill='#46576b')
    else:
        d.rectangle((0,0,780,58),fill='white')
        d.rectangle((0,615,780,690),fill='white')
        d.text((24,22),'Side view: existing assembly',font=font(21),fill='#193047')
        d.text((24,625),'Blue: adapter    Green: separate latch',font=font(19),fill='#193047')
        d.text((24,653),'Gold: rear handle scan    Magenta: ideal circle',font=font(19),fill='#193047')
    image.paste(tile,(20+panel*800,120))
draw=ImageDraw.Draw(image)
draw.text((35,836),f'Rear grip: fixed diameter {2*radius:.1f} mm from clip; estimated center Y {center[0]:.2f}, Z {center[1]:.2f} mm',font=font(22),fill='#193047')
draw.text((35,878),f'This estimate already intersects the existing latch by ~{overlap:.1f} mm, measured normal to its back face.',font=font(21),fill='#193047')
draw.text((35,920),'Confirm the inferred circle before deciding how to reach the requested 1 mm interference.',font=font(21),fill='#a53567')
image.save(Path('/tmp/surron-seat-adapter-previews/Build123d/exports')/'rear-handle-circle-preview.png')
print(json.dumps(report,indent=2))
