"""Discussion-only section overlays on real exports; never edits manufacturing CAD."""
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from preview_front_clip import load
from mesh_preview import render
Path('/tmp/surron-seat-adapter-previews/Build123d/exports').mkdir(parents=True,exist_ok=True)
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/tmp/surron-seat-adapter-previews/Build123d/exports/concepts/rear-cavity')
OUT.mkdir(parents=True,exist_ok=True)
FONT='/usr/share/fonts/TTF/DejaVuSans.ttf'
font=lambda n: ImageFont.truetype(FONT,n)
BLUE='#5794bb'; GREEN='#55ad82'; GOLD='#e6b34b'; BG='#ffffff'; INK='#203b50'; ADD='#ae77d1'

def section(mesh,x=.1):
    segments=[]
    for t in mesh:
        pts=[]
        for i,j in [(0,1),(1,2),(2,0)]:
            a,b=t[i],t[j]
            if (a[0]-x)*(b[0]-x)<0:
                pts.append((a+(b-a)*((x-a[0])/(b[0]-a[0])))[1:])
        if len(pts)==2: segments.append(pts)
    return np.array(segments)

def loops(segments):
    # Connect coincident STL section endpoints; rounding only affects this drawing.
    remaining={i:tuple(tuple(np.round(p,3)) for p in seg) for i,seg in enumerate(segments)}
    adjacency={}
    for i,(a,b) in remaining.items():
        adjacency.setdefault(a,set()).add(i);adjacency.setdefault(b,set()).add(i)
    result=[]
    while remaining:
        idx=next(iter(remaining)); a,b=remaining.pop(idx); chain=[a,b]
        while chain[-1]!=chain[0]:
            matches=[i for i in adjacency[chain[-1]] if i in remaining]
            if not matches: break
            c,d=remaining.pop(matches[0]);chain.append(d if c==chain[-1] else c)
        if len(chain)>3 and chain[-1]==chain[0]:result.append(chain)
    return sorted(result,key=lambda ps:abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ps,ps[1:]))),reverse=True)

meshes={k:load(ROOT/'exports'/p) for k,p in {
'adapter':'adapter-body.stl','latch':'latch.stl','body':'sherman-p-prepared/body-scaled.stl',
'handle':'sherman-p-prepared/rear-handle.stl'}.items()}
sections={k:section(v) for k,v in meshes.items()}

def panel(option,title,lines):
    im=Image.new('RGB',(1000,1000),BG);d=ImageDraw.Draw(im)
    d.text((28,20),title,font=font(29),fill=INK)
    d.text((28,64),'Rear side section  |  wheel center is to the left',font=font(19),fill='#607384')
    def xy(p):return (55+(p[0]-85)*4.9,665-(p[1]+48)*3.8)
    def poly(ps,col):d.polygon([xy(p) for p in ps],fill=col)
    def line(ps,col,width=3):d.line([xy(p) for p in ps],fill=col,width=width)
    for k,col in [('body',GOLD),('handle',GOLD),('adapter',BLUE),('latch',GREEN)]:
        for ps in loops(sections[k]):poly(ps,col)
        for seg in sections[k]:line(seg,col,2)
    if option==0:
        line([(151,-25),(170,-27)],'#e54e47',9)
        d.ellipse((*xy((147,-14)),*xy((177,-39))),outline='#e54e47',width=3)
        d.text((240,745),'Exposed route into the underside cavity',font=font(23),fill='#c34139')
        d.line([(450,735),xy((161,-26))],fill='#c34139',width=2)
    elif option==1:
        # Fill the rear end of the hollow pocket, retaining all exterior surfaces.
        poly([(102,57),(129,60),(171,-30),(144,-32)],ADD)
        line([(102,57),(144,-24)],'#744499',4)
        d.text((70,745),'Purple: solid material replacing rear cavity volume',font=font(22),fill='#744499')
    elif option==2:
        # Illustrative lower-web relocation, not a solved mating interface.
        poly([(129,60),(171,-27),(182,-28),(147,26)],BG)
        poly([(104,57),(130,60),(122,26),(157,-30),(146,-32)],BLUE)
        poly([(122,26),(147,26),(129,60)],BLUE)
        # Extend only the adapter-facing part of the stationary latch.
        poly([(122,26),(147,26),(173,-16),(182,-28),(157,-30)],'#267b55')
        line([(129,60),(171,-27),(182,-28)],'#b9c6cf',2)
        d.line([xy((170,0)),xy((143,0))],fill='#744499',width=4)
        poly([(143,0),(147,2),(147,-2)],'#744499')
        d.text((65,745),'Wall moves inward; dark green extends the latch',font=font(22),fill='#267b55')
    else:
        poly([(140,-25),(173,-23),(175,-29),(140,-32)],ADD)
        line([(140,-25),(173,-23)],'#744499',4)
        d.text((65,745),'Purple: thin bridge closes only the exposed strip',font=font(22),fill='#744499')
    # Wheel masks illustrative overlap: proposals must be trimmed to the accepted cutter.
    if option:
        for ps in loops(sections['body']):poly(ps,GOLD)
    d.rectangle((0,725,1000,795),fill=BG)
    captions={0:'Red: exposed route into the underside cavity',1:'Purple: solid material replacing rear cavity volume',2:'Wall moves inward; dark green extends the latch',3:'Purple: thin bridge closes only the exposed strip'}
    d.text((28,750),captions[option],font=font(22),fill=INK)
    # Mask beyond the diagram frame; sections use identical view and scale.
    d.rectangle((0,90,54,725),fill=BG)
    for i,text in enumerate(lines):d.text((28,807+34*i),text,font=font(22),fill=INK)
    d.text((28,960),'CONCEPT OVERLAY • not rebuilt CAD • dimensions not selected',font=font(18),fill='#697b89')
    return im

cards=[
('Current: rear cavity remains exposed',[
'Blue: adapter    Green: separate latch    Gold: wheel',
'The rear handle does not close the cavity opening.',
'Section from the current manufacturing STL exports.']),
('A / Smaller cavity, original outer wall',[
'Keep the latch and its mating interface unchanged.',
'Simple geometry, but adds a relatively solid wedge.',
'Retain the rest of the filament-saving cavity.']),
('B / Move wall inward, extend latch',[
'Keep the latch hook and wheel contact where they are.',
'Move its adapter interface inward with the rear wall.',
'Potential material saving; dovetail needs redesign.']),
('C / Thin closure bridge',[
'Keep wall and latch locations; close the exposed strip.',
'Potentially least added material; retain hollow space.',
'Bridge must join both side walls and clear the wheel.'])]
images=[]
for i,(title,lines) in enumerate(cards):
    im=panel(i,title,lines);im.save(OUT/f'{i}-rear-cavity-section.png');images.append(im)
board=Image.new('RGB',(2040,2180),'#e9eef3');d=ImageDraw.Draw(board)
d.text((30,22),'Rear underside cavity / three ways to close the exposed opening',font=font(35),fill=INK)
d.text((30,77),'Actual center section + illustrative proposed edits. All options keep adapter and latch as separate parts.',font=font(23),fill=INK)
for i,im in enumerate(images):board.paste(im,(10+(i%2)*1020,140+(i//2)*1020))
board.save(OUT/'rear-cavity-options.png')
# Real STL context image, independent of the conceptual overlays.
context=Image.new('RGB',(1600,1200),'#e9eef3');d=ImageDraw.Draw(context)
d.text((30,25),'Current assembly / looking up into the rear opening',font=font(32),fill=INK)
context.paste(render([(meshes['adapter'],(87,148,187)),(meshes['latch'],(85,173,130)),(meshes['body'],(230,179,75)),(meshes['handle'],(230,179,75))],(1,1,-.55),(1560,990),focus=(0,170,15)),(20,100))
d=ImageDraw.Draw(context);d.text((30,1120),'Actual exports. Blue: adapter   Green: separate latch   Gold: Sherman P reference scan',font=font(24),fill=INK)
context.save(OUT/'current-rear-underside.png')
print(OUT/'rear-cavity-options.png')
