"""Two-layer (F.Cu / B.Cu) A* router for the connections KiCad still reports as unconnected.

Inputs: geometry from scripts/geomdump.py and a kicad-cli DRC report (its unconnected_items give the ratsnest
anchors).  Every other-net pad, track, via, hole, keepout and non-GND fill is an obstacle (GND pours re-fill around
new copper); USB and RF copper keep their 0.2 mm clearance and via holes keep 0.2 mm to other copper.  Inside the
nRF (U5) courtyard the aQFN escape rules apply (0.09 mm track, 0.08 mm clearance, 0.3/0.15 via).  Plane nets (3V3,
VCC_SYN) may instead end on a via into their L3 area; a connection to a fill may start/end anywhere in that fill.

--soft: unlocked tracks/vias of ordinary nets become passable at a cost; whatever the new route collides with is
listed under 'rip' so apply_routes.py removes it (those nets are routed again in the next pass).

Run (system Python, numpy/scipy/matplotlib):  python scripts/netroute.py geom.json drc.json routes.json [--soft]
"""
import heapq
import json
import math
import re
import sys

import numpy as np
from matplotlib.path import Path
from scipy.ndimage import distance_transform_edt, label

RES, STEP = 0.025, 2
MARGIN = 4.0
VIA_COST, TURN_COST, SOFT_COST = 1.2, 0.05, 15.0
RF = {'RX_PATCH', 'SYN_OUTAP', 'CW_RF', 'PA_IN', 'PA_OUT', 'PA_MATCH', 'TX_LPF', 'TX_ANT', 'NRF_ANT', 'RX_RF',
      'RX_ATT', 'LNA_OUT', 'LNA_IN', 'RX_BPF', 'RX_ANT'}
POWER = {'3V3', '5V0', '5V_BUS', '/Power/REG_INTVCC'}
PLANE = {'3V3': 'In2', '/CW_Synth/VCC_SYN': 'In2'}
DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
VIA, VIA_U5 = (0.45, 0.25), (0.3, 0.15)
SOFT = '--soft' in sys.argv
INNER = '--inner' in sys.argv          # also route on L3 (In2, the 3V3 plane layer), at a cost; never under USB
LAY = ['F', 'B'] + (['In2'] if INNER else [])
INNER_COST = 0.6                       # extra cost factor per mm on In2

geom = json.load(open(sys.argv[1]))
drc = json.load(open(sys.argv[2], encoding='utf8'))
u5 = geom['courtyards']['U5'][0]
U5BOX = (min(p[0] for p in u5), min(p[1] for p in u5), max(p[0] for p in u5), max(p[1] for p in u5))
routed = []      # results, also fed back as obstacles
ripped = []      # items removed by soft routes (no longer obstacles)


def area(q):
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(q, q[1:] + q[:1]))) / 2


def special(net):
    return net.rsplit('/', 1)[-1] in RF or net in ('USB_D+', 'USB_D-')


def in_u5(x, y):
    return U5BOX[0] < x < U5BOX[2] and U5BOX[1] < y < U5BOX[3]


class Raster:
    def __init__(self, x0, y0, x1, y1):
        x0, y0 = math.floor(x0 / (RES * STEP)) * RES * STEP, math.floor(y0 / (RES * STEP)) * RES * STEP
        self.x0, self.y0 = x0, y0
        self.nx, self.ny = int((x1 - x0) / RES) + 1, int((y1 - y0) / RES) + 1
        self.X, self.Y = np.meshgrid(self.x0 + np.arange(self.nx) * RES, self.y0 + np.arange(self.ny) * RES)

    def mask(self):
        return np.zeros((self.ny, self.nx), bool)

    def idx(self, x, y):
        return int(round((x - self.x0) / RES)), int(round((y - self.y0) / RES))

    def window(self, x0, y0, x1, y1):
        i0, j0 = self.idx(x0, y0)
        i1, j1 = self.idx(x1, y1)
        if i1 < 0 or j1 < 0 or i0 >= self.nx or j0 >= self.ny:
            return None
        return slice(max(j0 - 1, 0), min(j1 + 2, self.ny)), slice(max(i0 - 1, 0), min(i1 + 2, self.nx))

    def poly(self, mask, pts):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        sl = self.window(min(xs), min(ys), max(xs), max(ys))
        if sl is None:
            return
        sub = np.column_stack([self.X[sl].ravel(), self.Y[sl].ravel()])
        mask[sl] |= Path(pts).contains_points(sub, radius=1e-9).reshape(self.X[sl].shape)

    def seg(self, mask, a, b, hw):
        sl = self.window(min(a[0], b[0]) - hw, min(a[1], b[1]) - hw, max(a[0], b[0]) + hw, max(a[1], b[1]) + hw)
        if sl is None:
            return
        X, Y = self.X[sl], self.Y[sl]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dy * dy
        t = np.zeros_like(X) if L2 == 0 else np.clip(((X - a[0]) * dx + (Y - a[1]) * dy) / L2, 0, 1)
        mask[sl] |= np.hypot(X - a[0] - t * dx, Y - a[1] - t * dy) <= hw


def parse_item(it):
    d = it['description']
    net = re.search(r'\[([^\]]*)\]', d).group(1)
    on = d.split(' on ', 1)[1].split(',')[0]
    layers = ['F', 'B'] if ' - ' in on else [{'F.Cu': 'F', 'B.Cu': 'B', 'In1.Cu': 'In1', 'In2.Cu': 'In2'}[on.strip()]]
    return net, (it['pos']['x'], it['pos']['y']), layers, d.split(' ')[0]


def key_t(t):
    return ('t', t['net'], t['layer'], round(t['a'][0], 4), round(t['a'][1], 4), round(t['b'][0], 4), round(t['b'][1], 4))


def key_v(v):
    return ('v', v['net'], round(v['pos'][0], 4), round(v['pos'][1], 4))


def all_tracks():
    gone = set(ripped)
    for t in geom['tracks']:
        if key_t(t) not in gone:
            yield t
    for r in routed:
        for s in r['segs']:
            yield {'net': r['net'], 'layer': s['layer'], 'w': s['w'], 'a': s['a'], 'b': s['b'], 'locked': True}


def all_vias():
    gone = set(ripped)
    for v in geom['vias']:
        if key_v(v) not in gone:
            yield v
    for r in routed:
        for v in r['vias']:
            yield {'net': r['net'], 'pos': v['pos'], 'd': v['d'], 'h': v['h'], 'locked': True}


HISTORY = json.load(open(sys.argv[sys.argv.index('--history') + 1])) if '--history' in sys.argv else {}


def rippable(item):
    return SOFT and not item.get('locked') and not special(item['net']) and HISTORY.get(item['net'], 0) < 2


def build(net, ras, power_w):
    extra = 0.05              # USB / RF want 0.2 mm, the default threshold below is 0.15
    hard = {L: ras.mask() for L in LAY}
    soft = {L: ras.mask() for L in LAY}
    holes, holes_other, novia = ras.mask(), ras.mask(), ras.mask()
    for p in geom['pads']:
        if p['hole']:
            ras.seg(holes, p['pos'], p['pos'], p['hole'] / 2)
            if p['net'] != net:
                ras.seg(holes_other, p['pos'], p['pos'], p['hole'] / 2 + 0.08)   # PTH: 0.28 mm hole clearance
        if p['net'] == net or p['layer'] not in LAY:
            continue
        for q in p['poly']:
            ras.poly(hard[p['layer']], q)
            if special(p['net']):
                for a, b in zip(q, q[1:] + q[:1]):
                    ras.seg(hard[p['layer']], a, b, extra)
    for t in all_tracks():
        if t['net'] == net or t['layer'] not in LAY:
            continue
        ras.seg((soft if rippable(t) else hard)[t['layer']], t['a'], t['b'],
                t['w'] / 2 + (extra if special(t['net']) else 0))
    if INNER:
        for t in all_tracks():
            if t['net'] in ('USB_D+', 'USB_D-') and t['layer'] == 'B':
                ras.seg(hard['In2'], t['a'], t['b'], t['w'] / 2 + 0.6)
    for v in all_vias():
        ras.seg(holes, v['pos'], v['pos'], v['h'] / 2)
        if v['net'] == net:
            continue
        tgt = soft if rippable(v) else hard
        if tgt is hard:
            ras.seg(holes_other, v['pos'], v['pos'], v['h'] / 2)
        for L in LAY:
            ras.seg(tgt[L], v['pos'], v['pos'], v['d'] / 2 + (extra if special(v['net']) else 0))
    own = {L: ras.mask() for L in LAY}
    for f in geom['fills']:
        if f['layer'] not in LAY:
            continue
        if f['net'] == net:
            for q in f['poly']:
                ras.poly(own[f['layer']], q)
            continue
        if (f['net'] == 'GND' and f['layer'] != 'In2') or (f['layer'] == 'In2' and f['net'] == '3V3'):
            continue
        for q in f['poly']:
            ras.poly(hard[f['layer']], q)
    for z in geom['keepouts']:
        for q in z['poly']:
            if z['tracks']:
                for L in LAY:
                    if L in z['layers']:
                        ras.poly(hard[L], q)
            if z['vias']:
                ras.poly(novia, q)
    inside = ras.mask()
    for q in geom['edge']:
        ras.poly(inside, q)
    plane = None
    if net in PLANE:
        plane, hole_m = ras.mask(), ras.mask()
        isl = [q for f in geom['fills'] if f['net'] == net and f['layer'] == PLANE[net] for q in f['poly']]
        if isl:
            ras.poly(plane, max(isl, key=area))           # main plane only, not cut-off islands
        for f in geom['fills']:
            if f['net'] == net and f['layer'] == PLANE[net]:
                for q in f['holes']:
                    ras.poly(hole_m, q)
        plane = distance_transform_edt(plane & ~hole_m) * RES >= 0.35
    u5m = (ras.X > U5BOX[0]) & (ras.X < U5BOX[2]) & (ras.Y > U5BOX[1]) & (ras.Y < U5BOX[3])
    dh = {L: distance_transform_edt(~hard[L]) * RES for L in LAY}
    ds = {L: distance_transform_edt(~soft[L]) * RES for L in LAY}
    dhole = distance_transform_edt(~holes) * RES
    dho = distance_transform_edt(~holes_other) * RES
    dedge = distance_transform_edt(inside) * RES
    hw = np.where(u5m, 0.045, power_w / 2)
    clr = np.where(u5m, 0.08, 0.15)
    track_ok = {L: (dh[L] >= hw + clr + RES / 2) & (dedge >= hw + 0.3) & (dho >= hw + 0.2 + RES / 2) for L in LAY}
    track_soft = {L: ds[L] < hw + clr + RES / 2 for L in LAY}
    vr = np.where(u5m, VIA_U5[0] / 2, VIA[0] / 2)
    vh = np.where(u5m, VIA_U5[1] / 2, VIA[1] / 2)
    vreach = np.maximum(vr + clr, vh + 0.2)     # copper clearance, and 0.2 mm from the drill to other copper
    via_ok = (dh['F'] >= vreach + RES / 2) & (dh['B'] >= vreach + RES / 2) & (dhole >= vh + 0.2 + RES / 2) & \
        (dho >= vr + 0.2 + RES / 2) & ~novia & (dedge >= vr + 0.35)
    via_soft = (ds['F'] < vreach + RES / 2) | (ds['B'] < vreach + RES / 2)
    return track_ok, track_soft, via_ok, via_soft, plane, u5m, own


def route(conn, power_w):
    net = conn['net']
    (sx, sy), slay, (gx, gy), glay = conn['a'], conn['alay'], conn['b'], conn['blay']
    use_plane = net in PLANE
    m = MARGIN
    ras = Raster(min(sx, gx) - m, min(sy, gy) - m, max(sx, gx) + m, max(sy, gy) + m)
    track_ok, track_soft, via_ok, via_soft, plane, u5m, own = build(net, ras, power_w)

    def snap(x, y):
        i, j = ras.idx(x, y)
        return int(round(i / STEP)) * STEP, int(round(j / STEP)) * STEP

    labels = {L: label(own[L])[0] for L in LAY}

    def island(L, i, j):
        """label of the own-net fill island at / nearest to a cell"""
        lab = labels[L]
        r = int(0.4 / RES)
        win = lab[max(j - r, 0):j + r + 1, max(i - r, 0):i + r + 1]
        vals = win[win > 0]
        return int(np.bincount(vals).argmax()) if vals.size else 0

    def region(x, y, layers, kind, avoid=()):
        """grid cells an end may use: the anchor cell, or any free cell of the anchor's own fill island"""
        ci, cj = snap(x, y)
        cells = {(ci, cj, L) for L in layers if L in LAY}
        isl = {}
        if kind == 'Zone':
            r = int(1.5 / RES)
            for L in layers:
                if L not in LAY:
                    continue
                k = island(L, ci, cj)
                isl[L] = k
                if not k or (L, k) in avoid:
                    continue
                for i in range(max(ci - r, 0) // STEP * STEP, min(ci + r, ras.nx - 1), STEP):
                    for j in range(max(cj - r, 0) // STEP * STEP, min(cj + r, ras.ny - 1), STEP):
                        if labels[L][j, i] == k and track_ok[L][j, i]:
                            cells.add((i, j, L))
        return cells, isl

    starts, s_isl = region(sx, sy, slay, conn['akind'])
    goals, _ = region(gx, gy, glay, conn['bkind'], avoid={(L, k) for L, k in s_isl.items()})
    end_cells = {(i, j) for i, j, _ in starts | goals}
    gi, gj = snap(gx, gy)

    def tok(L, i, j):
        """extra cost factor of a track cell: None = blocked, SOFT_COST = crosses rippable copper"""
        if not (0 <= i < ras.nx and 0 <= j < ras.ny):
            return None
        if (i, j) in end_cells:
            return 0.0
        if not track_ok[L][j, i]:
            return None
        return SOFT_COST if track_soft[L][j, i] else 0.0

    def h(i, j):
        if use_plane:
            return 0.0
        ax, ay = abs(gi - i), abs(gj - j)
        return (max(ax, ay) - min(ax, ay) + math.sqrt(2) * min(ax, ay)) * RES

    # search state in flat numpy arrays (dicts of tuples cost hundreds of MB per worker)
    GX, GY, NL = ras.nx // STEP + 1, ras.ny // STEP + 1, len(LAY)
    LI = {L: k for k, L in enumerate(LAY)}

    def sid(i, j, L, d):
        return (((LI[L] * 9) + d + 1) * GY + j // STEP) * GX + i // STEP

    def unsid(k):
        gi_, k = k % GX, k // GX
        gj_, k = k % GY, k // GY
        d, li = k % 9 - 1, k // 9
        return gi_ * STEP, gj_ * STEP, LAY[li], d

    best = np.full(GX * GY * NL * 9, np.inf, np.float32)
    came = np.full(GX * GY * NL * 9, -1, np.int64)
    openq = []
    for i, j, L in starts:
        k = sid(i, j, L, -1)
        best[k] = 0.0
        heapq.heappush(openq, (h(i, j), 0.0, k))
    goal, pops, end_plane = None, 0, False
    while openq and pops < 1500000:
        f, g, k = heapq.heappop(openq)
        pops += 1
        if g > best[k] + 1e-6:
            continue
        i, j, L, d = unsid(k)
        if (i, j, L) in goals:
            goal = k
            break
        if use_plane and g > 0 and plane[j, i] and via_ok[j, i] and not via_soft[j, i]:
            goal, end_plane = k, True
            break
        nbrs = range(8) if d < 0 else ((d - 1) % 8, d, (d + 1) % 8)
        for nd in nbrs:
            di, dj = DIRS[nd]
            ni, nj = i + di * STEP, j + dj * STEP
            c = tok(L, ni, nj)
            if c is None:
                continue
            step = math.hypot(di, dj) * STEP * RES
            ng = g + step * (1 + c + (INNER_COST if L == 'In2' else 0)) + (TURN_COST if d >= 0 and nd != d else 0)
            ns = sid(ni, nj, L, nd)
            if ng < best[ns] - 1e-6:
                best[ns] = ng
                came[ns] = k
                heapq.heappush(openq, (ng + h(ni, nj), ng, ns))
        if via_ok[j, i]:
            for OL in LAY:
                if OL == L:
                    continue
                c = tok(OL, i, j)
                ns = sid(i, j, OL, -1)
                ng = g + VIA_COST + (SOFT_COST if via_soft[j, i] else 0)
                if c is not None and ng < best[ns] - 1e-6:
                    best[ns] = ng
                    came[ns] = k
                    heapq.heappush(openq, (ng + h(i, j), ng, ns))
    if goal is None:
        return None
    path = [unsid(goal)]
    k = goal
    while came[k] >= 0:
        k = int(came[k])
        path.append(unsid(k))
    path.reverse()
    pts = [(ras.x0 + i * RES, ras.y0 + j * RES, L) for i, j, L, _ in path]
    segs, vias = [], []
    first = (sx, sy) if conn['akind'] != 'Zone' else pts[0][:2]
    cur, curL = [first], pts[0][2]
    for k in range(1, len(pts)):
        x, y, L = pts[k]
        if L != curL:
            px, py = pts[k - 1][0], pts[k - 1][1]
            cur.append((px, py))
            segs.append((curL, cur))
            d, hh = VIA_U5 if in_u5(px, py) else VIA
            vias.append({'pos': (px, py), 'd': d, 'h': hh})
            cur, curL = [(px, py)], L
        else:
            cur.append((x, y))
    if end_plane:
        x, y, _ = pts[-1]
        d, hh = VIA_U5 if in_u5(x, y) else VIA
        vias.append({'pos': (x, y), 'd': d, 'h': hh})
    elif conn['bkind'] != 'Zone':
        cur.append((gx, gy))
    segs.append((curL, cur))
    out = []
    for L, line in segs:
        simp = [line[0]]
        for k in range(1, len(line) - 1):
            a, b, c = simp[-1], line[k], line[k + 1]
            if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) > 1e-9:
                simp.append(b)
        simp.append(line[-1])
        for a, b in zip(simp, simp[1:]):
            if math.hypot(b[0] - a[0], b[1] - a[1]) < 1e-6:
                continue
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            out.append({'layer': L, 'a': a, 'b': b, 'w': 0.09 if in_u5(*mid) else power_w})
    return {'net': net, 'segs': out, 'vias': vias, 'plane_end': end_plane}


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def segseg(a, b, c, d):
    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    if o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0:
        return 0.0
    return min(seg_dist(a, c, d), seg_dist(b, c, d), seg_dist(c, a, b), seg_dist(d, a, b))


def collisions(res):
    """unlocked other-net items within clearance of a soft route"""
    hits = []
    for t in all_tracks():
        if t['net'] == res['net'] or not rippable(t):
            continue
        for s in res['segs']:
            if s['layer'] == t['layer'] and segseg(s['a'], s['b'], t['a'], t['b']) < (s['w'] + t['w']) / 2 + 0.15:
                hits.append(key_t(t)); break
        else:
            for v in res['vias']:
                if seg_dist(v['pos'], t['a'], t['b']) < v['d'] / 2 + t['w'] / 2 + 0.2:
                    hits.append(key_t(t)); break
    for v in all_vias():
        if v['net'] == res['net'] or not rippable(v):
            continue
        hit = any(seg_dist(v['pos'], s['a'], s['b']) < v['d'] / 2 + s['w'] / 2 + 0.2 for s in res['segs']) or \
            any(math.hypot(v['pos'][0] - w['pos'][0], v['pos'][1] - w['pos'][1]) < (v['d'] + w['d']) / 2 + 0.2
                for w in res['vias'])
        if hit:
            hits.append(key_v(v))
    return hits


def route_conn(c):
    widths = (0.3, 0.2, 0.1) if c['net'] in POWER else (0.1,)
    for w in widths:
        res = route(c, w)
        if res:
            res['w'] = w
            return res
    return None


def route_order(args):
    """route every connection in the given order, each result an obstacle for the next (one worker)"""
    conns, seed = args
    import random
    order = list(conns)
    if seed:
        random.Random(seed).shuffle(order)
    routed.clear()
    done, fails = [], []
    for c in order:
        res = route_conn(c)
        if res:
            routed.append(res)
            done.append(res)
        else:
            fails.append(c)
    return seed, done, fails


def clash(r1, r2):
    """two new routes of different nets violate clearance"""
    if r1['net'] == r2['net']:
        return False
    for a in r1['segs']:
        for b in r2['segs']:
            if a['layer'] == b['layer'] and segseg(a['a'], a['b'], b['a'], b['b']) < (a['w'] + b['w']) / 2 + 0.16:
                return True
    for v in r1['vias']:
        for b in r2['segs']:
            if seg_dist(v['pos'], b['a'], b['b']) < v['d'] / 2 + b['w'] / 2 + 0.21:
                return True
        for w in r2['vias']:
            if math.hypot(v['pos'][0] - w['pos'][0], v['pos'][1] - w['pos'][1]) < (v['d'] + w['d']) / 2 + 0.21:
                return True
    for v in r2['vias']:
        for a in r1['segs']:
            if seg_dist(v['pos'], a['a'], a['b']) < v['d'] / 2 + a['w'] / 2 + 0.21:
                return True
    return False


def report(c, res):
    L = math.hypot(c['a'][0] - c['b'][0], c['a'][1] - c['b'][1])
    if res:
        print('OK   %-22s %5.1f mm  %d segs %d vias%s w=%.2f rip %d' % (
            c['net'], L, len(res['segs']), len(res['vias']), ' (plane via)' if res['plane_end'] else '', res['w'],
            len(res.get('rip', []))), flush=True)
    else:
        print('FAIL %-22s %5.1f mm  %s -> %s' % (c['net'], L, c['a'], c['b']), flush=True)


if __name__ == '__main__':
    conns = []
    for u in drc['unconnected_items']:
        (na, pa, la, ka), (nb, pb, lb, kb) = (parse_item(i) for i in u['items'])
        if na == 'GND':
            print('skip', na, ka, kb)
            continue
        conns.append({'net': na, 'a': pa, 'alay': la, 'akind': ka, 'b': pb, 'blay': lb, 'bkind': kb})
    conns.sort(key=lambda c: math.hypot(c['a'][0] - c['b'][0], c['a'][1] - c['b'][1]))
    failed, todo = [], conns
    if '--orders' in sys.argv:
        todo = []
    jobs = int(sys.argv[sys.argv.index('--jobs') + 1]) if '--jobs' in sys.argv else 1
    try:                                   # ~0.35 GB per worker; leave 1 GB free
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [('l', ctypes.c_ulong), ('load', ctypes.c_ulong), ('total', ctypes.c_ulonglong),
                        ('avail', ctypes.c_ulonglong), ('a', ctypes.c_ulonglong), ('b', ctypes.c_ulonglong),
                        ('c', ctypes.c_ulonglong), ('d', ctypes.c_ulonglong), ('e', ctypes.c_ulonglong)]
        ms = MS(); ms.l = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
        jobs = max(1, min(jobs, int((ms.avail / 2**30 - 1.0) / 0.35)))
    except Exception:
        pass
    print('workers:', jobs, flush=True)
    if jobs > 1 and '--orders' not in sys.argv:
        # route everything in parallel against the same board, keep the results that do not clash, redo the rest
        from multiprocessing import Pool
        with Pool(jobs) as pool:
            first = pool.map(route_conn, conns, chunksize=1)
        todo = []
        for c, res in zip(conns, first):
            if res is None:
                todo.append(c)
                continue
            if SOFT:
                res['rip'] = [k for k in collisions(res) if k not in set(ripped)]
            if any(clash(res, r) for r in routed):
                todo.append(c)
            else:
                ripped.extend(res.get('rip', []))
                routed.append(res)
                report(c, res)
        print('parallel pass: %d kept, %d to redo sequentially' % (len(routed), len(todo)), flush=True)
    if '--orders' in sys.argv:
        # try many routing orders in parallel, keep the order that leaves the fewest connections unrouted
        from multiprocessing import Pool
        n_orders = int(sys.argv[sys.argv.index('--orders') + 1])
        with Pool(jobs) as pool:
            best_run = None
            for seed, done, fails in pool.imap_unordered(route_order, [(conns, k) for k in range(n_orders)]):
                print('order %2d: %d routed, %d failed' % (seed, len(done), len(fails)), flush=True)
                if best_run is None or len(fails) < len(best_run[2]):
                    best_run = (seed, done, fails)
        routed[:] = best_run[1]
        failed = best_run[2]
        todo = []
        for c in failed:
            report(c, None)
        print('best order:', best_run[0])
    for c in todo:
        res = route_conn(c)
        if res:
            res['rip'] = collisions(res) if SOFT else []
            ripped.extend(res['rip'])
            routed.append(res)
        else:
            failed.append(c)
        report(c, res)
    json.dump({'routed': routed, 'failed': failed}, open(sys.argv[3], 'w'), indent=1)
    print('routed %d, failed %d' % (len(routed), len(failed)))
