"""Render two local orthographic previews from the exported STEP, using Pillow."""
from pathlib import Path
from build123d import import_step, Vector
from PIL import Image, ImageDraw, ImageFont
import numpy as np

folder = Path(__file__).resolve().parent
body = import_step(folder/'exports/adapter-body.step')
vertices, triangles = body.tessellate(0.15,0.15)
center = body.bounding_box().center()
image = Image.new('RGB',(1600,1000),(235,239,243))
pixels = np.array(image)
depth = np.full((1000,1600), -np.inf)
font = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',22)
for i,(label,eye) in enumerate([('Adapter body — upper view',Vector(1,-1,1)),('Adapter body — underside / wheel imprint',Vector(1,1,-1))]):
    eye = eye.normalized()
    right = Vector(0,0,1).cross(eye).normalized()
    up = eye.cross(right).normalized()
    projected = [((v-center).dot(right),(v-center).dot(up),(v-center).dot(eye)) for v in vertices]
    span_x = max(p[0] for p in projected)-min(p[0] for p in projected)
    span_y = max(p[1] for p in projected)-min(p[1] for p in projected)
    scale = min(710/span_x,830/span_y)
    xmid = (max(p[0] for p in projected)+min(p[0] for p in projected))/2
    ymid = (max(p[1] for p in projected)+min(p[1] for p in projected))/2
    for tri in triangles:
        a,b,c = [vertices[j] for j in tri]
        normal = (b-a).cross(c-a)
        if normal.length<1e-12: continue
        shade = 0.4+0.6*abs(normal.normalized().dot((eye+up*0.5+right*0.2).normalized()))
        color = tuple(int(v*shade) for v in (75,155,205))
        xy = [(400+i*800+(projected[j][0]-xmid)*scale,530-(projected[j][1]-ymid)*scale) for j in tri]
        (ax,ay),(bx,by),(cx,cy) = xy
        xmin,xmax = max(0,int(min(ax,bx,cx))),min(1599,int(max(ax,bx,cx))+1)
        ymin,ymax = max(0,int(min(ay,by,cy))),min(999,int(max(ay,by,cy))+1)
        if xmax<xmin or ymax<ymin: continue
        xx,yy = np.meshgrid(np.arange(xmin,xmax+1)+0.5,np.arange(ymin,ymax+1)+0.5)
        denom = (by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
        if abs(denom)<1e-10: continue
        u = ((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/denom
        v = ((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/denom
        w = 1-u-v
        z = u*projected[tri[0]][2]+v*projected[tri[1]][2]+w*projected[tri[2]][2]
        old = depth[ymin:ymax+1,xmin:xmax+1]
        mask = (u>=0)&(v>=0)&(w>=0)&(z>old)
        old[mask] = z[mask]
        pixels[ymin:ymax+1,xmin:xmax+1][mask] = color

image = Image.fromarray(pixels)
draw = ImageDraw.Draw(image)
for i,label in enumerate(['Adapter body — upper view','Adapter body — underside / wheel imprint']):
    draw.text((30+i*800,25),label,fill=(30,45,60),font=font)
image.save(folder/'exports/adapter-body-preview.png')
