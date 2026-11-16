"""Side-profile concept from existing STL geometry; no manufacturing edits."""
from pathlib import Path
Path('/tmp/surron-seat-adapter-previews/Build123d/exports').mkdir(parents=True,exist_ok=True)
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops
from preview_front_clip import DTYPE

ROOT=Path(__file__).resolve().parent
OUT=Path('/tmp/surron-seat-adapter-previews/Build123d/exports')
RISE=8.0
# Keep the approved preview reproducible after manufacturing exports change.
BASELINE='fb38b1acc4f525ca9ce3cbb3f4079566f98807d2'
def load(path):
    relative=path.relative_to(ROOT.parent)
    raw=subprocess.check_output(['git','show',f'{BASELINE}:{relative}'],cwd=ROOT.parent)
    return np.frombuffer(raw,dtype=DTYPE,offset=84)['vertices'].astype(float)
body=load(OUT/'adapter-body.stl')
wheel=[load(OUT/'sherman-p-prepared'/f'{name}.stl') for name in ('body-scaled','front-handle','rear-handle')]
FONT='/usr/share/fonts/TTF/DejaVuSans.ttf'
font=lambda n:ImageFont.truetype(FONT,n)
W,H=1800,1270
im=Image.new('RGB',(W,H),'#eef2f6');d=ImageDraw.Draw(im)
d.text((35,20),'8 mm deeper seating / placement preview',font=font(34),fill='#183044')
d.text((35,70),'EUC and front grip rise together; adapter stays fixed. Front is left; Z is up.',font=font(23),fill='#40566a')

def panel(origin,size,yrange,zrange,proposed,title):
    w,h=size
    tile=Image.new('RGB',size,'white')
    scale=min((w-40)/(yrange[1]-yrange[0]),(h-110)/(zrange[1]-zrange[0]))
    def xy(y,z):return (20+(y-yrange[0])*scale,h-35-(z-zrange[0])*scale)
    def mask(mesh,shift=0,clip=None):
        m=Image.new('L',size);p=ImageDraw.Draw(m)
        for tri in mesh:
            pts=[(v[1],v[2]+shift) for v in tri]
            if clip:
                boundary,keep_left=clip
                result=[]
                for a,b in zip(pts,pts[1:]+pts[:1]):
                    ina=a[0]<=boundary if keep_left else a[0]>=boundary
                    inb=b[0]<=boundary if keep_left else b[0]>=boundary
                    if ina:result.append(a)
                    if ina!=inb:
                        t=(boundary-a[0])/(b[0]-a[0]);result.append((boundary,a[1]+t*(b[1]-a[1])))
                pts=result
            if len(pts)>=3:p.polygon([xy(*p) for p in pts],fill=255)
        return m
    original=mask(body)
    if proposed:
        # A side silhouette illustrates seating only, not a 3-D Boolean result.
        fixed=mask(body,clip=(-192.950417,False))
        raised=mask(body,RISE,clip=(-192.950417,True))
        proposed_body=ImageChops.lighter(fixed,raised)
        wheelmask=mask(wheel[0],RISE)
        proposed_body=ImageChops.subtract(proposed_body,wheelmask)
        tile.paste('#e0e5eb',mask=original)
        tile.paste('#218caa',mask=proposed_body)
    else:tile.paste('#54849e',mask=original)
    for mesh in wheel:
        tile.paste('#d6b060',mask=mask(mesh,RISE if proposed else 0))
    td=ImageDraw.Draw(tile)
    td.text((20,12),title,font=font(24),fill='#183044')
    if proposed:
        # Existing and requested bore centers establish the exact relative move.
        y,z=-220.3743032668,32.8742416819
        x0,z0=xy(y,z);x1,z1=xy(y,z+RISE)
        td.line((x0,z0,x1,z1),fill='#b33e6d',width=3)
        for zz,sign in ((z0,-1),(z1,1)):
            td.line((x0-5,zz+sign*8,x0,zz,x0+5,zz+sign*8),fill='#b33e6d',width=3)
        td.text((x1+12,z1-6),'+8 mm',font=font(20),fill='#a12f5c')
        if yrange[1]<0:
            q=xy(-192,54)
            td.ellipse((q[0]-36,q[1]-52,q[0]+36,q[1]+65),outline='#d16735',width=3)
            td.text((260,70),'Reshape this connection',font=font(21),fill='#b4552a')
            td.line((360,101,q[0]+25,q[1]-20),fill='#d16735',width=2)
    im.paste(tile,origin)

panel((25,115),(865,440),(-270,265),(-80,115),False,'Current assembly')
panel((910,115),(865,440),(-270,265),(-80,115),True,'Proposed / wheel + grip up 8 mm')
panel((25,580),(1110,540),(-260,-125),(-30,100),True,'Front detail / same grip, raised 8 mm')
d=ImageDraw.Draw(im)
for i,line in enumerate(['Teal: proposed adapter profile','Gold: EUC body and handle references','Pale gray: current adapter position','','Underside cutout becomes 8 mm deeper.','Front grip follows the handle upward.','Orange: connection requires redesign.']):
    d.text((1170,625+i*43),line,font=font(22),fill='#40566a')
d.text((35,1155),'CONCEPT ONLY: projected silhouettes from current STL exports; the clip bridge is not redesigned here.',font=font(23),fill='#9a4b2d')
d.text((35,1200),'Manufacturing CAD and exports unchanged. Rear latch shown in a later fit review if needed.',font=font(22),fill='#40566a')
path=OUT/'deeper-seating-8mm-preview.png';im.save(path);print(path)
