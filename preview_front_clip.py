"""Render the implemented manufacturing exports, never modify geometry."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from mesh_preview import render

ROOT=Path(__file__).resolve().parent
DTYPE=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')])
def load(path):
    data=path.read_bytes()
    count=int.from_bytes(data[80:84],'little')
    if len(data)!=84+count*50:raise ValueError('Expected binary STL')
    return np.frombuffer(data,dtype=DTYPE,offset=84)['vertices'].astype(float)

def main():
    body=load(ROOT/'exports/adapter-body.stl')
    handle=load(ROOT/'exports/sherman-p-prepared/front-handle.stl')
    front=body[:,:,1].min(axis=1)<-179.157
    normals=np.cross(body[:,1]-body[:,0],body[:,2]-body[:,0])
    normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
    cut=front & (abs(abs(normals[:,0])-.8918512712)<1e-5) & (abs(normals[:,2]-.4523287632)<1e-5)
    meshes=[(handle,(197,161,88)),(body[~front],(86,119,145)),
            (body[front & ~cut],(39,154,166)),(body[cut],(93,194,158))]
    image=Image.new('RGB',(2200,1470),'#e9eef3')
    draw=ImageDraw.Draw(image)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
    draw.text((40,25),'IMPLEMENTED / reinforced screen + continuous clip ramp',font=font(35),fill='#183044')
    draw.text((40,83),'Rendered directly from the rebuilt manufacturing STL • front dovetail removed • both printing planes restored',font=font(23),fill='#4c6074')
    image.paste(render(meshes,(1,-.55,.68),(1250,1000),focus=(0,-166,20)),(20,145))
    image.paste(render(meshes,(1,0,.02),(900,660),focus=(0,-178,25)),(1290,170))
    draw=ImageDraw.Draw(image)
    draw.text((1320,145),'Side view / actual exported geometry',font=font(24),fill='#183044')
    for i,text in enumerate(['55° screen ramp continues into the front.','Original clip bore: 30.2 mm diameter.','Clip center raised 18.053 mm.','Screen sides parallel to the underside.','Front dovetail removed; rear latch retained.','Both rear printing planes extend through front.']):
        draw.text((1320,900+i*43),text,font=font(22),fill='#405b70')
    draw.text((45,1175),'Oblique view / screen opening and front bridge',font=font(26),fill='#183044')
    draw.text((45,1230),'Teal: redesigned front   Green: trimmed contact faces   Slate: retained body   Gold: handle scan',font=font(23),fill='#405b70')
    draw.text((45,1290),'Native planar and circular geometry • no fillets • unchanged wheel imprint clearance',font=font(23),fill='#405b70')
    draw.text((45,1390),'CAD geometry verified separately; physical snap fit and printed strength require a real-world fit check.',font=font(22),fill='#405b70')
    path=ROOT/'exports/front-clip-implemented.png'
    image.save(path)
    print(path)

if __name__=='__main__':main()
