"""Top-view review of the exact selected BottomSketch; no CAD mutations."""
from pathlib import Path
import json
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from adapter import profiles
from mesh_preview import render
from preview_front_clip import load
from coordinates import ADAPTER_TRANSLATION_MM

ROOT = Path(__file__).resolve().parent


def main():
    proposal = '--proposal' in sys.argv
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
    # Merge contiguous collinear halves so each visible straight line gets one ID.
    pending = [np.round(s, 7) for s in segments]
    changed = True
    while changed:
        changed = False
        for i in range(len(pending)):
            if changed:
                break
            for j in range(i+1, len(pending)):
                for ai, bj in ((0, 0), (0, 1), (1, 0), (1, 1)):
                    a, b = pending[i], pending[j]
                    if not np.allclose(a[ai], b[bj], atol=1e-6):
                        continue
                    u, v = a[1-ai]-a[ai], b[1-bj]-b[bj]
                    if abs(u[0]*v[1]-u[1]*v[0]) < 1e-5 and u@v < 0:
                        pending[i] = np.array([a[1-ai], b[1-bj]])
                        pending.pop(j)
                        changed = True
                        break
                if changed:
                    break
    # Walk the outside first, then the screen opening, beginning at front-left.
    segments = []
    while pending:
        start = min((tuple(p) for s in pending for p in s), key=lambda p: (p[1], -p[0]))
        point = np.array(start)
        while True:
            matches = [(i, end) for i, s in enumerate(pending) for end in (0, 1)
                       if np.allclose(s[end], point, atol=1e-6)]
            if not matches:
                break
            i, end = min(matches, key=lambda pair: (pending[pair[0]][1-pair[1]][1],
                                                    pending[pair[0]][1-pair[1]][0]))
            s = pending.pop(i)
            segments.append(np.array([s[end], s[1-end]]))
            point = s[1-end]
            if np.allclose(point, start, atol=1e-6):
                break
    original = {i: s.copy() for i, s in enumerate(segments, 1)}
    proposed = {i: s.copy() for i, s in original.items()}
    if proposal:
        # Keep line 13's direction and extend to the unchanged X of line 16.
        a, b = proposed[13]
        intersection = a+(b-a)*((22-a[0])/(b[0]-a[0]))
        proposed[13][1] = intersection
        proposed[16][0] = intersection
        for i in (14, 15, 5, 6):
            del proposed[i]
        # Preview assumption: parallel frontward translation, not a new angle.
        proposed[17][:, 1] -= 10
        proposed[16][1] = proposed[17][0]
        proposed[18][0] = proposed[17][1]
        for left, right in ((13, 7), (16, 4), (17, 3), (18, 2)):
            proposed[right] = proposed[left][::-1]*[-1, 1]
        proposed[19][:, 1] -= 10
        proposed[20][0] = proposed[19][1]
        proposed[22][1] = proposed[19][0]
        outer = [proposed[i] for i in range(1, 19) if i in proposed]
        assert all(np.allclose(a[1], b[0]) for a, b in zip(outer, outer[1:]+outer[:1]))
        assert np.allclose(proposed[13][1], proposed[16][0])
        assert np.allclose(np.diff(proposed[17], axis=0), np.diff(original[17], axis=0))
        assert np.allclose(proposed[19][:, 1], original[19][:, 1]-10)
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
    def draw_outline(img, entries=original, color='#ed2266'):
        d = ImageDraw.Draw(img)
        for segment in entries.values():
            d.line([pixel(x, y) for x, y in segment], fill=color, width=5)
        for number, segment in entries.items():
            if proposal and number not in (1, 10, 11, 12, 13, 16, 17, 18, 19, 21, 22):
                continue
            a, b = np.array([pixel(x, y) for x, y in segment])
            middle = (a+b)/2
            delta = b-a
            normal = np.array([-delta[1], delta[0]])/np.linalg.norm(delta)
            center = middle+normal*23
            d.line([tuple(middle), tuple(center)], fill='#163b58', width=2)
            x, y = center
            d.rounded_rectangle((x-18, y-15, x+18, y+15), radius=8,
                                fill='white', outline='#163b58', width=2)
            d.text((x, y), str(number), font=font(18), fill='#163b58', anchor='mm')
        # The narrow portion's exact 44 mm width is shown without inferring caps.
        y = -10+ADAPTER_TRANSLATION_MM[1]
        a, b = pixel(-22, y), pixel(22, y)
        d.text((a[0]+12, a[1]+8), '44 mm', font=font(18), fill='#b91850')
    font = lambda n: ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', n)
    result = Image.new('RGB', (2040, 1510), '#e9eef3')
    d = ImageDraw.Draw(result)
    d.text((30, 20), 'PROPOSED SUSPENSION OUTLINE / preview only' if proposal else 'CURRENT BOTTOM SKETCH / Sherman P alignment review', font=font(32), fill='#183044')
    d.text((30, 70), 'Orthographic top view • front at top • identical scale in every panel • geometry unchanged', font=font(23), fill='#405b70')
    overlay = base.copy()
    if proposal:
        current = base.copy(); draw_outline(current)
        draw_outline(overlay, proposed, '#009779'); draw_outline(blank, proposed, '#009779')
        panels = [(15, 'Current outline / reference', current), (690, 'Proposed sketch / mirrored', blank), (1365, 'Proposed outline over scan', overlay)]
    else:
        draw_outline(overlay); draw_outline(blank)
        panels = [(15, 'Aligned Sherman P scan', base), (690, 'Current BottomSketch + mirror', blank), (1365, 'Current sketch over the scan', overlay)]
    for x, title, panel in panels:
        result.paste(panel, (x, 155))
        d.text((x+15, 115), title, font=font(23), fill='#183044')
        d.text((x+285, 162), 'FRONT', font=font(18), fill='#405b70')
    d.text((30, 1420), '13 extended to vertical 16; 14/15 removed. Mirrored on right. 19 moved 10 mm toward front.' if proposal else 'Pink: exact selected base profile, mirrored and placed. Later cuts, clip changes and imprint are not this sketch.', font=font(22), fill='#405b70')
    d.text((30, 1460), '17: shift 10 mm toward screen, original angle retained. Original line IDs kept; manufactured CAD unchanged.' if proposal else 'Scan: aligned, unscaled body + handles. Suspension-cover boundaries have not been inferred or marked.', font=font(22), fill='#405b70')
    path = ROOT/('exports/bottom-outline-sherman-p-proposed.png' if proposal else 'exports/bottom-outline-sherman-p-numbered.png')
    result.save(path)
    print(path)
    mapping = 'bottom-outline-proposed-lines.json' if proposal else 'bottom-outline-line-numbers.json'
    (ROOT/'exports'/mapping).write_text(json.dumps(
        {str(i): s.tolist() for i, s in (proposed if proposal else original).items()}, indent=2)+'\n')
    print(json.dumps(dict(halfProfileAreaMm2=half_area, mirroredAreaMm2=2*half_area,
                          assemblyTranslationMm=ADAPTER_TRANSLATION_MM, triangles=len(scan))))


if __name__ == '__main__':
    main()
