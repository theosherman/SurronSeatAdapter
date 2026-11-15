"""Render implemented manufacturing solids against the saved pre-change model."""
from pathlib import Path
import subprocess,tempfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build123d import import_step,Plane,Keep,Compound,ShapeList
from mesh_preview import render

ROOT=Path(__file__).resolve().parent
BASELINE='8746492'
FONT='/usr/share/fonts/TTF/DejaVuSans.ttf'

def mesh(shape):
    vs,ts=shape.tessellate(.035,.1)
    return np.array([[tuple(vs[i]) for i in t] for t in ts])

def half(shape):
    s=shape.split(Plane((0,0,0),z_dir=(1,0,0)),Keep.BOTTOM)
    return Compound(s) if isinstance(s,(list,ShapeList)) else s

def main():
    out=ROOT/'exports'
    with tempfile.TemporaryDirectory() as tmp:
        old=[]
        for name in ['adapter-body.step','latch.step']:
            raw=subprocess.run(['git','show',f'{BASELINE}:Build123d/exports/{name}'],
                               cwd=ROOT.parent,check=True,stdout=subprocess.PIPE).stdout
            path=Path(tmp)/name;path.write_bytes(raw);old.append(import_step(path))
        new=[import_step(out/'adapter-body.step'),import_step(out/'latch.step')]
        wheel=[import_step(out/'sherman-p-prepared'/p) for p in ['body-scaled.step','rear-handle.step']]
        blue=(83,135,170);teal=(35,156,169);green=(66,161,113);gold=(216,175,91)
        f=lambda n:ImageFont.truetype(FONT,n)
        variants={}
        for name,parts,color in [('before',old,blue),('after',new,teal)]:
            variants[name]=dict(full=[(mesh(s),c) for s,c in zip(parts+wheel,[color,green,gold,gold])],
                                cut=[(mesh(half(s)),c) for s,c in zip(parts+wheel,[color,green,gold,gold])])
        for mode,eye,title in [('full',(1,.9,-.35),'Assembled rear underside'),
                               ('cut',(1,.4,.18),'Native 3D cutaway through cavity')]:
            im=Image.new('RGB',(2600,1480),'#e9eef3');d=ImageDraw.Draw(im)
            d.text((35,23),'IMPLEMENTED / rear wall 10 mm inward + 10 mm thicker',font=f(36),fill='#203b50')
            d.text((35,82),'BEFORE',font=f(27),fill='#203b50');d.text((1335,82),'REBUILT MANUFACTURING MODEL',font=f(27),fill='#203b50')
            for i,name in enumerate(['before','after']):
                im.paste(render(variants[name][mode],eye,(1270,1110),focus=(0,167,23)),(15+1300*i,135))
            d=ImageDraw.Draw(im)
            d.text((35,1270),title+' / matching cameras and scale',font=f(27),fill='#203b50')
            d.text((35,1320),'Teal: revised adapter    Green: extended separate latch    Gold: unchanged wheel references',font=f(25),fill='#203b50')
            d.text((35,1370),'Latch contact end fixed; 0.2 mm planar mating clearance restored. Both wall dimensions run along front-to-back Y.',font=f(24),fill='#203b50')
            d.text((35,1430),'Rendered from actual exported STEP solids. Physical fit, installation and complete cavity sealing require a fit check.',font=f(22),fill='#627789')
            im.save(out/f'rear-cavity-implemented-{mode}.png')
        im=Image.new('RGB',(1900,1530),'#e9eef3');d=ImageDraw.Draw(im)
        d.text((35,25),'Implemented hybrid / actual adapter and separate latch',font=f(36),fill='#203b50')
        d.text((35,82),'Rear wall moved 10 mm inward; cavity-side material increased another 10 mm along Y.',font=f(25),fill='#526b7d')
        im.paste(render(variants['after']['cut'],(1,.4,.18),(1860,1190),focus=(0,158,26)),(20,130))
        d=ImageDraw.Draw(im)
        d.text((35,1360),'TEAL: revised adapter    GREEN: extended latch    GOLD: fixed Sherman P reference',font=f(26),fill='#203b50')
        d.text((35,1410),'Original latch wheel-contact face and hook remain fixed; adapter and latch are separate solids.',font=f(25),fill='#203b50')
        d.text((35,1470),'Native solid and mounting checks recorded separately; physical fit and full cavity sealing unverified.',font=f(23),fill='#627789')
        im.save(out/'rear-cavity-implemented.png')
    print(out/'rear-cavity-implemented.png')

if __name__=='__main__':main()
