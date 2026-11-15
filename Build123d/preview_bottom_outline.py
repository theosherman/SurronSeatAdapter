"""Top-view review of the exact selected BottomSketch; no CAD mutations."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from adapter import profiles
from mesh_preview import render
from preview_front_clip import load
from coordinates import ADAPTER_TRANSLATION_MM

ROOT = Path(__file__).resolve().parent


def main():
    recipe = json.loads((ROOT.parent/'cad-rebuild/recipe.json').read_text())
    selected = next(p for p in recipe['selectedProfiles'] if p['sourceTimelineIndex'] == 9)
    curves = selected['profiles'][0]['loops'][0]['curves']
    assert all(c['type'] == 'Line3D' for c in curves)
    half_area = profiles(9)[0].area
    assert abs(half_area-selected['profiles'][0]['areaMm2']) < 1e-5
    # Exact line endpoints; remove the shared center seam of mirrored M02.
    segments = []
    for c in curves:
        a, b = np.array(c['startMm']), np.array(c['endMm'])
        if abs(a[0]) < 1e-8 and abs(b[0]) < 1e-8:
            continue
        for side in (-1, 1):
            segment = np.array([a, b])*[side, -1, 1]+ADAPTER_TRANSLATION_MM
            segments.append(segment[:, :2])
    scan = np.concatenate([load(ROOT/'exports/sherman-p-prepared'/f'{part}.stl')
                           for part in ('body-original', 'front-handle', 'rear-handle')])
    # Degenerate triangles set identical framing; the renderer skips their pixels.
    bounds = np.array([[[-125, -270, 0]]*3, [[125, 310, 0]]*3], dtype=float)
    size = (660, 1250)
    eye = np.array([0., 1e-9, 1.]); eye /= np.linalg.norm(eye)
    right = np.cross([0, 0, 1], eye); right /= np.linalg.norm(right)
    up = np.cross(eye, right)
    basis = np.array([right, up, eye]).T
    verts = np.concatenate([scan.reshape(-1, 3), bounds.reshape(-1, 3)])
    projected = verts@basis
    lo, hi = projected[:, :2].min(0), projected[:, :2].max(0)
    mid = (hi+lo)/2
    factor = min((size[0]-65)/(hi[0]-lo[0]), (size[1]-55)/(hi[1]-lo[1]))
    def pixel(x, y):
        p = np.array([x, y, 0])@basis
        return tuple((p[:2]-mid)*[factor, -factor]+np.array(size)/2)
    base = render([(scan, (177, 191, 202)), (bounds, (0, 0, 0))], eye, size)
    blank = Image.new('RGB', size, '#f9fbfd')
    def draw_outline(img):
        d = ImageDraw.Draw(img)
        for segment in segments:
            d.line([pixel(x, y) for x, y in segment], fill='#ed2266', width=5)
        # The narrow portion's exact 44 mm width is shown without inferring caps.
        y = -10+ADAPTER_TRANSLATION_MM[1]
        a, b = pixel(-22, y), pixel(22, y)
        d.line([a, b], fill='#ed2266', width=2)
        d.text((a[0]+12, a[1]+8), '44 mm', font=font(18), fill='#b91850')
    font = lambda n: ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', n)
    result = Image.new('RGB', (2040, 1510), '#e9eef3')
    d = ImageDraw.Draw(result)
    d.text((30, 20), 'CURRENT BOTTOM SKETCH / Sherman P alignment review', font=font(32), fill='#183044')
    d.text((30, 70), 'Orthographic top view • front at top • identical scale in every panel • geometry unchanged', font=font(23), fill='#405b70')
    overlay = base.copy(); draw_outline(overlay); draw_outline(blank)
    for x, title, panel in [(15, 'Aligned Sherman P scan', base), (690, 'Current BottomSketch + mirror', blank), (1365, 'Current sketch over the scan', overlay)]:
        result.paste(panel, (x, 155))
        d.text((x+15, 115), title, font=font(23), fill='#183044')
        d.text((x+285, 162), 'FRONT', font=font(18), fill='#405b70')
    d.text((30, 1420), 'Pink: exact selected base profile, mirrored and placed. Later cuts, clip changes and imprint are not this sketch.', font=font(22), fill='#405b70')
    d.text((30, 1460), 'Scan: aligned, unscaled body + handles. Suspension-cover boundaries have not been inferred or marked.', font=font(22), fill='#405b70')
    path = ROOT/'exports/bottom-outline-sherman-p-overlay.png'
    result.save(path)
    print(path)
    print(json.dumps(dict(halfProfileAreaMm2=half_area, mirroredAreaMm2=2*half_area,
                          assemblyTranslationMm=ADAPTER_TRANSLATION_MM, triangles=len(scan))))


if __name__ == '__main__':
    main()
