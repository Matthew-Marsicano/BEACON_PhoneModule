#!/usr/bin/env python
"""Render a Gerber/Excellon set to PNGs for visual fab checks.

usage: render_panel.py <gerber_dir> <out_prefix> [--ppmm 20] [--margin 2]

Outputs <out_prefix>_top.png, <out_prefix>_bottom.png (mirrored in X, viewed
from below) and <out_prefix>_outline_drill.png, and prints a layer summary.
Read-only on the input directory.
"""
import argparse
import math
import re
import sys
import time
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import shapely
from shapely.geometry import LineString, Polygon, MultiPolygon, Point
from shapely.ops import unary_union, polygonize, polygonize_full

from gerbonara import GerberFile, ExcellonFile
from gerbonara import graphic_primitives as gp
from gerbonara.utils import MM, approximate_arc

warnings.filterwarnings('ignore')

# ----------------------------------------------------------------------------
# Layer detection
# ----------------------------------------------------------------------------
DRILL_EXT = {'.drl', '.txt', '.xln', '.exc', '.drd', '.nc', '.tap', '.xnc'}
IGNORE_RE = re.compile(r'(drl_map|drill_map|\.gbrjob$|-job\.|\.zip$|\.pdf$|\.csv$|\.pos$|\.rpt$|\.drr$|'
                       r'\.extrep$|\.rul$|\.ldp$|\.apr$|\.reptxt$|\.html?$|\.png$|\.svg$|\.ipc$|\.d356$|\.json$)',
                       re.I)

KICAD_NAMES = [  # (regex on stem, key)
    (r'[-_.]F[._]Cu$', 'top_cu'), (r'[-_.]B[._]Cu$', 'bot_cu'),
    (r'[-_.]In(\d+)[._]Cu$', 'in'),
    (r'[-_.]F[._]Mask$', 'top_mask'), (r'[-_.]B[._]Mask$', 'bot_mask'),
    (r'[-_.]F[._]Silk(screen|S)$', 'top_silk'), (r'[-_.]B[._]Silk(screen|S)$', 'bot_silk'),
    (r'[-_.]F[._]Paste$', 'top_paste'), (r'[-_.]B[._]Paste$', 'bot_paste'),
    (r'[-_.]Edge[._]Cuts$', 'outline'),
]
EXT_NAMES = {'.gtl': 'top_cu', '.gbl': 'bot_cu', '.gts': 'top_mask', '.gbs': 'bot_mask',
             '.gto': 'top_silk', '.gbo': 'bot_silk', '.gtp': 'top_paste', '.gbp': 'bot_paste',
             '.gko': 'outline'}

# priority of candidate outline files (lower wins)
OUTLINE_PRIO = {'kicad': 0, '.gko': 1, '.gm1': 2, '.gm': 3}


def sniff(path, n=8192):
    try:
        with open(path, 'rb') as f:
            return f.read(n).decode('latin-1')
    except OSError:
        return ''


def classify(path):
    """Return (key, extra) for a file, or (None, reason)."""
    name, stem, ext = path.name, path.stem, path.suffix.lower()
    if IGNORE_RE.search(name):
        return None, 'ignored'
    head = sniff(path)
    is_excellon = ext in DRILL_EXT and ('M48' in head[:2000] or re.search(r'^T\d+C', head, re.M))
    if is_excellon:
        if re.search(r'npth|non[-_ ]?plated', name, re.I):
            return 'npth', None
        if re.search(r'pth|plated', name, re.I):
            return 'pth', None
        if re.search(r'TYPE=NON_PLATED|FileFunction,NonPlated', head):
            return 'npth', None
        if re.search(r'TYPE=PLATED|FileFunction,Plated', head):
            return 'pth', None
        return 'drill_mixed', None
    if ext in DRILL_EXT:
        return None, 'not excellon'
    for rx, key in KICAD_NAMES:
        m = re.search(rx, stem, re.I)
        if m:
            if key == 'in':
                return f'in{int(m.group(1))}_cu', None
            if key == 'outline':
                return 'outline', 'kicad'
            return key, None
    if ext in EXT_NAMES:
        k = EXT_NAMES[ext]
        return k, (ext if k == 'outline' else None)
    m = re.fullmatch(r'\.g(\d+)', ext)
    if m:
        return f'in{int(m.group(1))}_cu', None
    m = re.fullmatch(r'\.gp(\d+)', ext)  # Altium internal plane (negative image)
    if m:
        return f'plane{int(m.group(1))}', 'negative'
    m = re.fullmatch(r'\.gm(\d*)', ext)
    if m:
        return 'outline', ext
    # X2 attribute sniffing as a fallback
    m = re.search(r'%TF\.FileFunction,([^*]+)\*%', head)
    if m:
        ff = m.group(1).split(',')
        side = ff[-1] if len(ff) > 1 else ''
        if ff[0] == 'Copper':
            ln = int(ff[1][1:]) if ff[1][1:].isdigit() else 0
            return {'Top': 'top_cu', 'Bot': 'bot_cu'}.get(side, f'in{max(ln - 1, 1)}_cu'), None
        if ff[0] in ('Soldermask', 'Legend', 'Paste'):
            kind = {'Soldermask': 'mask', 'Legend': 'silk', 'Paste': 'paste'}[ff[0]]
            return ('top_' if side == 'Top' else 'bot_') + kind, None
        if ff[0] == 'Profile':
            return 'outline', 'x2'
    return None, 'unrecognized'


def detect_layers(d):
    layers, unused = {}, []
    outline_cands = []
    for p in sorted(Path(d).iterdir()):
        if not p.is_file():
            continue
        key, extra = classify(p)
        if key is None:
            unused.append((p.name, extra))
            continue
        if key == 'outline':
            outline_cands.append((OUTLINE_PRIO.get(extra, 5), p))
            continue
        if key in layers:
            if key in ('pth', 'npth', 'drill_mixed'):
                layers.setdefault(key + '_extra', []).append(p)
            else:
                unused.append((p.name, f'duplicate {key}'))
            continue
        layers[key] = p
    if outline_cands:
        outline_cands.sort(key=lambda t: (t[0], t[1].name))
        layers['outline'] = outline_cands[0][1]
        unused += [(p.name, 'other mechanical') for _, p in outline_cands[1:]]
    return layers, unused


# ----------------------------------------------------------------------------
# Rasterizer
# ----------------------------------------------------------------------------
class Raster:
    def __init__(self, bbox, ppmm, margin):
        (x0, y0), (x1, y1) = bbox
        self.s = ppmm
        self.x0 = x0 - margin
        self.y1 = y1 + margin
        self.W = int(math.ceil((x1 - x0 + 2 * margin) * ppmm))
        self.H = int(math.ceil((y1 - y0 + 2 * margin) * ppmm))
        self.err = 0.25 / ppmm  # arc chord error, quarter pixel

    def px(self, x, y):
        return ((x - self.x0) * self.s, (self.y1 - y) * self.s)

    def new(self):
        return Image.new('L', (self.W, self.H), 0)

    # --- primitive drawing ---
    def _round_cap(self, dr, x, y, r, fill):
        cx, cy = self.px(x, y)
        r = max(r * self.s, 0.5)
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)

    def _thick_poly(self, dr, pts, width, fill):
        """Polyline with round caps/joins, width in mm."""
        w = width * self.s
        ppts = [self.px(x, y) for x, y in pts]
        if w < 1.5:
            dr.line(ppts, fill=fill, width=1)
            return
        if len(ppts) == 2:
            (ax, ay), (bx, by) = ppts
            dx, dy = bx - ax, by - ay
            L = math.hypot(dx, dy)
            if L > 1e-9:
                nx, ny = -dy / L * w / 2, dx / L * w / 2
                dr.polygon([(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)],
                           fill=fill)
        else:
            dr.line(ppts, fill=fill, width=int(round(w)), joint='curve')
        r = w / 2
        for cx, cy in (ppts[0], ppts[-1]):
            dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)

    def draw_prim(self, dr, p, fill, min_width=0.0):
        t = type(p)
        if t is gp.Circle:
            self._round_cap(dr, p.x, p.y, p.r, fill)
        elif t is gp.Line:
            self._thick_poly(dr, [(p.x1, p.y1), (p.x2, p.y2)], max(p.width, min_width), fill)
        elif t is gp.Arc:
            r = math.dist((p.x1, p.y1), (p.cx, p.cy))
            if r < 1e-6:
                self._round_cap(dr, p.x1, p.y1, max(p.width, min_width) / 2, fill)
                return
            pts = [(p.x1, p.y1)] + list(approximate_arc(p.cx, p.cy, p.x1, p.y1, p.x2, p.y2, p.clockwise,
                                                         max_error=self.err))
            self._thick_poly(dr, pts, max(p.width, min_width), fill)
        elif t is gp.Rectangle:
            c, s = math.cos(p.rotation), math.sin(p.rotation)
            pts = []
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                lx, ly = dx * p.w / 2, dy * p.h / 2
                pts.append(self.px(p.x + lx * c - ly * s, p.y + lx * s + ly * c))
            dr.polygon(pts, fill=fill)
        elif t is gp.ArcPoly:
            if not p.outline:
                return
            if p.arc_centers and any(p.arc_centers):
                p = p.approximate_arcs(max_error=self.err)
            pts = [self.px(x, y) for x, y in p.outline]
            if len(pts) >= 3:
                dr.polygon(pts, fill=fill)
            elif pts:
                dr.point(pts, fill=fill)
        else:
            raise TypeError(t)

    def render_objects(self, objects, min_width=0.0):
        img = self.new()
        dr = ImageDraw.Draw(img)
        for obj in objects:
            prims = list(obj.to_primitives(MM))
            if not prims:
                continue
            pol = obj.polarity_dark
            if all(pp.polarity_dark == pol for pp in prims):
                fill = 255 if pol else 0
                for pp in prims:
                    self.draw_prim(dr, pp, fill, min_width)
            else:
                # macro with internal exposure-off parts: compose locally, then apply object polarity
                tmp = self.new()
                tdr = ImageDraw.Draw(tmp)
                for pp in prims:
                    self.draw_prim(tdr, pp, 255 if pp.polarity_dark == pol else 0, min_width)
                img.paste(255 if pol else 0, mask=tmp)
        return np.asarray(img) > 127

    def render_geom(self, geom):
        img = self.new()
        dr = ImageDraw.Draw(img)
        polys = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
        for poly in polys:
            if poly.is_empty or not isinstance(poly, Polygon):
                continue
            dr.polygon([self.px(x, y) for x, y in poly.exterior.coords], fill=255)
        for poly in polys:
            if poly.is_empty or not isinstance(poly, Polygon):
                continue
            for ring in poly.interiors:
                dr.polygon([self.px(x, y) for x, y in ring.coords], fill=0)
        return np.asarray(img) > 127


# ----------------------------------------------------------------------------
# Outline -> board material polygon
# ----------------------------------------------------------------------------
def outline_lines(gfile, err=0.005):
    lines = []
    for obj in gfile.objects:
        for p in obj.to_primitives(MM):
            if type(p) is gp.Line:
                if math.dist((p.x1, p.y1), (p.x2, p.y2)) > 1e-6:
                    lines.append([(p.x1, p.y1), (p.x2, p.y2)])
            elif type(p) is gp.Arc:
                pts = [(p.x1, p.y1)] + list(approximate_arc(p.cx, p.cy, p.x1, p.y1, p.x2, p.y2, p.clockwise,
                                                             max_error=err))
                lines.append(pts)
            elif type(p) is gp.ArcPoly and len(p.outline) >= 3:
                q = p.approximate_arcs(max_error=err) if p.arc_centers else p
                pts = list(q.outline) + [q.outline[0]]
                lines.append(pts)
            elif type(p) is gp.Rectangle:
                lines.append([(p.x - p.w / 2, p.y - p.h / 2), (p.x + p.w / 2, p.y - p.h / 2),
                              (p.x + p.w / 2, p.y + p.h / 2), (p.x - p.w / 2, p.y + p.h / 2),
                              (p.x - p.w / 2, p.y - p.h / 2)])
    return [LineString([(round(x, 4), round(y, 4)) for x, y in l]) for l in lines]


def board_from_outline(gfile, gap_tol=0.02):
    """Even-odd fill of the profile linework. Returns (material geometry, info dict)."""
    lines = outline_lines(gfile)
    info = {'segments': len(lines)}
    if not lines:
        return None, info
    noded = unary_union(lines)
    polys, cuts, dangles, invalid = polygonize_full(noded)
    info['dangles'] = len(getattr(dangles, 'geoms', []))
    info['open_ends'] = sum(1 for _ in getattr(cuts, 'geoms', []))
    # close small gaps: work on the boundary of the buffered linework
    band = noded.buffer(gap_tol, quad_segs=4)
    faces = list(polygonize(band.boundary))
    xmax = noded.bounds[2] + 10.0
    material, nfaces = [], 0
    for f in faces:
        if f.area < 1e-6:
            continue
        inner = f.buffer(-gap_tol / 4)
        if inner.is_empty:
            continue
        if band.contains(inner.representative_point()):
            continue  # this face is the buffered linework itself
        nfaces += 1
        cands = [inner.representative_point()]
        rng = np.random.default_rng(len(material))
        minx, miny, maxx, maxy = inner.bounds
        for _ in range(12):
            cands.append(Point(rng.uniform(minx, maxx), rng.uniform(miny, maxy)))
        parity = None
        for c in cands:
            if not inner.contains(c) or band.contains(c):
                continue
            ray = LineString([(c.x, c.y + 1.234e-5), (xmax, c.y + 1.234e-5)])
            hit = ray.intersection(noded)
            if hit.is_empty:
                parity = 0
                break
            geoms = getattr(hit, 'geoms', [hit])
            if any(g.geom_type != 'Point' for g in geoms):
                continue
            parity = len(geoms) % 2
            break
        if parity:
            material.append(f)
    info['faces'] = nfaces
    info['material_faces'] = len(material)
    if not material:
        return None, info
    board = unary_union(material).buffer(gap_tol * 1.01, quad_segs=4).buffer(0)
    info['closed'] = info['dangles'] == 0 and info['open_ends'] == 0
    return board, info


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
LABELS = {'top_cu': 'Top copper', 'bot_cu': 'Bottom copper', 'top_mask': 'Top mask', 'bot_mask': 'Bottom mask',
          'top_silk': 'Top silk', 'bot_silk': 'Bottom silk', 'top_paste': 'Top paste', 'bot_paste': 'Bottom paste',
          'outline': 'Outline/profile', 'pth': 'Plated drill', 'npth': 'Non-plated drill',
          'drill_mixed': 'Drill (mixed/unknown)'}

C = dict(bg=(38, 38, 42), fr4=(194, 170, 112), mask_fr4=(22, 84, 40), mask_cu=(58, 132, 62),
         gold=(214, 176, 66), silk=(245, 245, 245), hole=(0, 0, 0), outline=(235, 30, 30))


def font(sz):
    try:
        return ImageFont.load_default(size=sz)
    except Exception:
        return ImageFont.load_default()


def annotate(img, title, ppmm, legend=None):
    """Add a header with title, wrapped legend and a 10 mm scale bar."""
    W = max(img.width, 420)
    ft, fl = font(15), font(13)
    meas = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    # wrap title on ', ' boundaries
    rows, cur = [], ''
    for part in re.split(r'(?<=,) |   ', title):
        trial = (cur + ' ' + part).strip() if cur else part
        if meas.textlength(trial, font=ft) > W - 16 and cur:
            rows.append(cur); cur = part
        else:
            cur = trial
    rows.append(cur)
    # legend layout
    items, x, y = [], 8, 0
    for name, col in (legend or []):
        w = 22 + int(meas.textlength(name, font=fl))
        if x + w > W - 8 and x > 8:
            x, y = 8, y + 18
        items.append((x, y, name, col))
        x += w + 10
    th = 6 + 19 * len(rows)
    lh = (y + 20) if legend else 0
    hh = th + lh + 26
    out = Image.new('RGB', (W, img.height + hh), (20, 20, 20))
    out.paste(img, (0, hh))
    d = ImageDraw.Draw(out)
    for i, r in enumerate(rows):
        d.text((8, 4 + 19 * i), r, fill=(255, 255, 255), font=ft)
    for x, y, name, col in items:
        d.rectangle([x, th + y + 2, x + 13, th + y + 15], fill=col, outline=(200, 200, 200))
        d.text((x + 18, th + y + 1), name, fill=(230, 230, 230), font=fl)
    L = 10 if img.width > 12 * ppmm else 5
    yb = th + lh + 8
    d.rectangle([8, yb, 8 + L * ppmm, yb + 5], fill=(255, 255, 255))
    for k in range(L + 1):
        xx = 8 + k * ppmm
        d.line([xx, yb - (4 if k % 5 == 0 else 2), xx, yb], fill=(255, 255, 255))
    d.text((16 + L * ppmm, yb - 6), f'{L} mm  ({ppmm:g} px/mm)', fill=(255, 255, 255), font=fl)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('gerber_dir')
    ap.add_argument('out_prefix')
    ap.add_argument('--ppmm', type=float, default=20.0, help='pixels per mm (default 20)')
    ap.add_argument('--margin', type=float, default=2.0, help='margin around board in mm')
    a = ap.parse_args()
    T0 = time.time()

    paths, unused = detect_layers(a.gerber_dir)
    if not paths:
        sys.exit(f'no gerber/drill files recognised in {a.gerber_dir}')

    files, load_t = {}, {}
    for key, p in paths.items():
        if key.endswith('_extra'):
            continue
        t = time.time()
        if key in ('pth', 'npth', 'drill_mixed'):
            ef = ExcellonFile.open(p, plated={'pth': True, 'npth': False}.get(key))
            for extra in paths.get(key + '_extra', []):
                ef.merge(ExcellonFile.open(extra, plated={'pth': True, 'npth': False}.get(key)))
            files[key] = ef
        else:
            files[key] = GerberFile.open(p)
        load_t[key] = time.time() - t

    # split mixed drill by per-tool plating
    drill_pth, drill_npth = [], []
    for key in ('pth', 'npth', 'drill_mixed'):
        if key not in files:
            continue
        for o in files[key].objects:
            plated = o.aperture.plated if key == 'drill_mixed' else key == 'pth'
            (drill_npth if plated is False else drill_pth).append(o)

    # ---- summary ----
    print(f'== {a.gerber_dir}')
    print('Layer map:')
    order = ['top_silk', 'top_paste', 'top_mask', 'top_cu'] + \
            sorted([k for k in files if re.fullmatch(r'(in|plane)\d+_?c?u?', k)], key=lambda k: int(re.sub(r'\D', '', k))) + \
            ['bot_cu', 'bot_mask', 'bot_paste', 'bot_silk', 'outline', 'pth', 'npth', 'drill_mixed']
    bboxes = {}
    for key in order:
        if key not in files:
            if key in ('top_cu', 'bot_cu', 'top_mask', 'bot_mask', 'top_silk', 'bot_silk', 'outline'):
                print(f'  {key:12s} <missing>')
            continue
        f = files[key]
        try:
            bb = f.bounding_box(MM)
        except Exception:
            bb = None
        bboxes[key] = bb
        bbs = (f'({bb[0][0]:8.3f},{bb[0][1]:8.3f}) - ({bb[1][0]:8.3f},{bb[1][1]:8.3f})  '
               f'{bb[1][0]-bb[0][0]:7.3f} x {bb[1][1]-bb[0][1]:7.3f} mm') if bb and bb[0][0] is not None else 'empty'
        extra = ''.join(f' +{e.name}' for e in paths.get(key + '_extra', []))
        print(f'  {key:12s} {paths[key].name + extra:42s} {len(f.objects):6d} obj  {bbs}')
    for name, why in unused:
        print(f'  (unused)     {name}  [{why}]')

    print('Drill tools:')
    for label, objs in (('PTH', drill_pth), ('NPTH', drill_npth)):
        cnt = Counter()
        for o in objs:
            cnt[(round(o.aperture.diameter, 4), 'slot' if type(o).__name__ == 'Line' else 'hit')] += 1
        tot_h = sum(v for (d, k), v in cnt.items() if k == 'hit')
        tot_s = sum(v for (d, k), v in cnt.items() if k == 'slot')
        print(f'  {label}: {tot_h} hits, {tot_s} slots')
        for (d, k), v in sorted(cnt.items()):
            print(f'     {d:7.4f} mm  {v:5d} {k}{"s" if v != 1 else ""}')

    # ---- board outline ----
    t = time.time()
    board, binfo = (None, {})
    if 'outline' in files:
        board, binfo = board_from_outline(files['outline'])
    if board is None:
        cu = [bboxes[k] for k in ('top_cu', 'bot_cu') if bboxes.get(k)]
        if cu:
            (x0, y0), (x1, y1) = cu[0]
            board = shapely.box(x0, y0, x1, y1)
            print('  WARNING: no usable outline; using copper bbox as board area')
    if board is not None:
        bx0, by0, bx1, by1 = board.bounds
        nparts = len(getattr(board, 'geoms', [board]))
        nholes = sum(len(p.interiors) for p in getattr(board, 'geoms', [board]))
        print(f'Board: {bx1-bx0:.3f} x {by1-by0:.3f} mm, bounds ({bx0:.3f},{by0:.3f})-({bx1:.3f},{by1:.3f}), '
              f'{nparts} piece(s), {nholes} internal cutout(s), area {board.area:.1f} mm^2')
    if binfo:
        closed = binfo.get('dangles', 0) == 0 and binfo.get('open_ends', 0) == 0
        print(f'Outline: {binfo.get("segments")} segments, {binfo.get("faces", 0)} faces ({binfo.get("material_faces", 0)} material), '
              f'{"closed" if closed else "NOT CLEANLY CLOSED"} '
              f'(dangles={binfo.get("dangles")}, cut edges={binfo.get("open_ends")})')

    # ---- frame bbox: outline if present, else everything ----
    allbb = [bb for k, bb in bboxes.items() if bb and bb[0][0] is not None and k not in ('outline',)]
    if board is not None:
        x0, y0, x1, y1 = board.bounds
        if 'outline' in bboxes and bboxes['outline']:
            (ox0, oy0), (ox1, oy1) = bboxes['outline']
            x0, y0, x1, y1 = min(x0, ox0), min(y0, oy0), max(x1, ox1), max(y1, oy1)
    else:
        x0 = min(b[0][0] for b in allbb); y0 = min(b[0][1] for b in allbb)
        x1 = max(b[1][0] for b in allbb); y1 = max(b[1][1] for b in allbb)
    R = Raster(((x0, y0), (x1, y1)), a.ppmm, a.margin)
    print(f'Image: {R.W} x {R.H} px at {a.ppmm:g} px/mm')

    # ---- rasterize ----
    masks, rt = {}, {}
    for key in files:
        if key in ('pth', 'npth', 'drill_mixed'):
            continue
        tt = time.time()
        masks[key] = R.render_objects(files[key].objects, min_width=(2.0 / a.ppmm if key == 'outline' else 0.0))
        rt[key] = time.time() - tt
    tt = time.time()
    masks['pth'] = R.render_objects(drill_pth)
    masks['npth'] = R.render_objects(drill_npth)
    rt['drills'] = time.time() - tt
    board_m = R.render_geom(board) if board is not None else np.ones((R.H, R.W), bool)
    holes = masks['pth'] | masks['npth']
    zero = np.zeros_like(board_m)

    def side(prefix):
        cu = masks.get(f'{prefix}_cu', zero)
        if f'{prefix}_mask' in masks:
            opening = masks[f'{prefix}_mask']
        else:
            opening = zero
        silk = masks.get(f'{prefix}_silk', zero)
        img = np.empty((R.H, R.W, 3), np.uint8)
        img[:] = C['bg']
        img[board_m] = C['mask_fr4']
        img[cu & ~opening] = C['mask_cu']
        img[board_m & opening & ~cu] = C['fr4']
        img[cu & opening] = C['gold']
        img[silk] = C['silk']
        img[holes] = C['hole']
        if 'outline' in masks:
            img[masks['outline']] = C['outline']
        return img

    outs = []
    for prefix, label in (('top', 'TOP (viewed from top)'), ('bot', 'BOTTOM (viewed from bottom, X mirrored)')):
        img = side(prefix)
        if prefix == 'bot':
            img = img[:, ::-1]
        names = ', '.join(paths[k].name for k in (f'{prefix}_cu', f'{prefix}_mask', f'{prefix}_silk') if k in paths)
        missing = [k for k in (f'{prefix}_cu', f'{prefix}_mask', f'{prefix}_silk') if k not in paths]
        title = f'{label}   {names}' + (f'   missing: {", ".join(missing)}' if missing else '')
        legend = [('mask over FR4', C['mask_fr4']), ('copper under mask', C['mask_cu']),
                  ('exposed copper', C['gold']), ('bare FR4', C['fr4']), ('silk', C['silk']),
                  ('hole', C['hole']), ('outline', C['outline'])]
        out = annotate(Image.fromarray(img), title, a.ppmm, legend)
        fn = f'{a.out_prefix}_{"top" if prefix == "top" else "bottom"}.png'
        out.save(fn, optimize=False, compress_level=3)
        outs.append(fn)

    # ---- outline + drill view ----
    img = np.empty((R.H, R.W, 3), np.float32)
    img[:] = (255, 255, 255)
    img[board_m] = (232, 232, 232)
    inner_cols = [(60, 110, 230), (240, 140, 30), (40, 170, 170), (170, 60, 200), (120, 120, 40), (200, 60, 90)]
    legend = [('board area', (232, 232, 232))]
    inner_keys = sorted([k for k in masks if re.fullmatch(r'(in|plane)\d+(_cu)?', k)],
                        key=lambda k: (k.startswith('plane'), int(re.sub(r'\D', '', k))))
    for i, k in enumerate(inner_keys):
        m = masks[k]
        if k.startswith('plane'):  # Altium plane layers are negative
            m = board_m & ~m
        col = np.array(inner_cols[i % len(inner_cols)], np.float32)
        edge = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
        img[m] = img[m] * 0.85 + col * 0.15
        img[edge] = img[edge] * 0.45 + col * 0.55
        lc = tuple(int(v) for v in (np.array((255, 255, 255)) * 0.6 + col * 0.4))
        legend.append((f'{k} (faint)', lc))
    img = img.astype(np.uint8)
    if 'outline' in masks:
        img[masks['outline']] = C['outline']
    img[masks['pth']] = (0, 140, 0)
    img[masks['npth']] = (30, 40, 220)
    legend += [('outline', C['outline']), (f'PTH ({len(drill_pth)})', (0, 140, 0)),
               (f'NPTH ({len(drill_npth)})', (30, 40, 220))]
    title = 'OUTLINE + DRILLS (top view)   ' + ', '.join(paths[k].name for k in ('outline', 'pth', 'npth', 'drill_mixed') if k in paths)
    out = annotate(Image.fromarray(img), title, a.ppmm, legend)
    fn = f'{a.out_prefix}_outline_drill.png'
    out.save(fn, compress_level=3)
    outs.append(fn)

    print('Raster time per layer (s): ' + ', '.join(f'{k}={v:.2f}' for k, v in rt.items()))
    print('Load time per layer (s):   ' + ', '.join(f'{k}={v:.2f}' for k, v in load_t.items()))
    print('Wrote: ' + ', '.join(outs))
    print(f'Total {time.time() - T0:.1f} s')


if __name__ == '__main__':
    main()
