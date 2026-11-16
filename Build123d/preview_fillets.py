import sys
from pathlib import Path
sys.path.insert(0,'Build123d')
from build123d import import_step
from mesh_preview import render
import numpy as np
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parent; a=import_step(p/'exports/adapter-body.step');v,t=a.tessellate(.08,.12);mesh=np.array([[tuple(v[i]) for i in row] for row in t]);im=Image.new('RGB',(1800,1100),'white')
for eye,pos in [((1,-1,1),(0,60)),((1,1,-1),(900,60))]:im.paste(render([(mesh,(62,156,192))],eye,(900,1000)),pos)
d=ImageDraw.Draw(im);d.text((30,20),'Implemented 1 mm fillets — adapter only / dovetail rail protected',fill='black',font=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',28));im.save(p/'exports/body-fillets-implemented.png');im.save(p/'tmp/body-fillets-implemented.png')
