"""Priority router for sensitive nets (USB pair): octilinear A* on a clearance map built from scripts/geomdump.py
output.  Pads, RF copper, GND vias, locked vias and the nRF via-in-pad escape are hard obstacles; every other track
and via is a soft obstacle (allowed at a cost - apply_routes.py rips whatever the new copper collides with, and the
autorouter puts those nets back afterwards).

A 'pair' route is routed as one fat centreline (both tracks + gap) and split into the two offset tracks.

Run (system Python with numpy/scipy):  python scripts/pairroute.py geom.json jobs.json out.json
"""
import heapq
import json
import math
import sys

import numpy as np
from matplotlib.path import Path
from scipy.ndimage import distance_transform_edt

RES = 0.025          # raster mm
STEP = 2             # A* grid = STEP * RES
RF = {'RX_PATCH', 'SYN_OUTAP', 'CW_RF', 'PA_IN', 'PA_OUT', 'PA_MATCH', 'TX_LPF', 'TX_ANT', 'NRF_ANT', 'RX_RF',
      'RX_ATT', 'LNA_OUT', 'LNA_IN', 'RX_BPF', 'RX_ANT'}
DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
SOFT_COST = 4.0      # extra mm-equivalent per mm of soft overlap
TURN_COST = 0.6      # mm-equivalent per 45 deg turn

geom = json.load(open(sys.argv[1]))
jobs = json.load(open(sys.argv[2]))
u5 = geom['courtyards']['U5'][0]
u5x0, u5x1 = min(p[0] for p in u5), max(p[0] for p in u5)
u5y0, u5y1 = min(p[1] for p in u5), max(p[1] for p in u5)


def rf(net):
    return net.rsplit('/', 1)[-1] in RF


class Raster:
    def __init__(self, x0, y0, x1, y1):
        self.x0, self.y0 = x0, y0
        self.nx, self.ny = int((x1 - x0) / RES) + 1, int((y1 - y0) / RES) + 1
        xs = x0 + np.arange(self.nx) * RES
        ys = y0 + np.arange(self.ny) * RES
        self.X, self.Y = np.meshgrid(xs, ys)
        self.pts = np.column_stack([self.X.ravel(), self.Y.ravel()])

    def poly(self, mask, pts):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        i0, i1 = self.idx(min(xs), min(ys)), self.idx(max(xs), max(ys))
        sl = (slice(max(i0[1] - 1, 0), min(i1[1] + 2, self.ny)), slice(max(i0[0] - 1, 0), min(i1[0] + 2, self.nx)))
        sub = np.column_stack([self.X[sl].ravel(), self.Y[sl].ravel()])
        if sub.size:
            mask[sl] |= Path(pts).contains_points(sub, radius=1e-9).reshape(self.X[sl].shape)

    def seg(self, mask, a, b, hw):
        x0, x1 = min(a[0], b[0]) - hw, max(a[0], b[0]) + hw
        y0, y1 = min(a[1], b[1]) - hw, max(a[1], b[1]) + hw
        i0, i1 = self.idx(x0, y0), self.idx(x1, y1)
        sl = (slice(max(i0[1], 0), min(i1[1] + 2, self.ny)), slice(max(i0[0], 0), min(i1[0] + 2, self.nx)))
        X, Y = self.X[sl], self.Y[sl]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dy * dy
        t = np.zeros_like(X) if L2 == 0 else np.clip(((X - a[0]) * dx + (Y - a[1]) * dy) / L2, 0, 1)
        mask[sl] |= np.hypot(X - a[0] - t * dx, Y - a[1] - t * dy) <= hw

    def circle(self, mask, c, r):
        self.seg(mask, c, c, r)

    def idx(self, x, y):
        return int(round((x - self.x0) / RES)), int(round((y - self.y0) / RES))


def build(job, ras):
    nets = set(job['nets'])
    layer = job['layer']
    hard = np.zeros((ras.ny, ras.nx), bool)
    soft = np.zeros((ras.ny, ras.nx), bool)
    soft_items = []
    for p in geom['pads']:
        if p['layer'] == layer and p['net'] not in nets:
            for q in p['poly']:
                ras.poly(hard, q)
        elif p['hole'] and p['net'] not in nets:          # holes on any layer
            ras.circle(hard, p['pos'], p['hole'] / 2)
    for v in geom['vias']:
        if v['net'] in nets:
            continue
        inside_u5 = u5x0 < v['pos'][0] < u5x1 and u5y0 < v['pos'][1] < u5y1
        # GND pad / stitching vias are re-placed afterwards (plane_nets.py, stitch.py): soft like other nets'
        tgt = hard if (inside_u5 or v['locked'] or rf(v['net'])) else soft
        ras.circle(tgt, v['pos'], v['d'] / 2)
    for t in geom['tracks']:
        if t['layer'] != layer or t['net'] in nets:
            continue
        ras.seg(hard if rf(t['net']) else soft, t['a'], t['b'], t['w'] / 2)
    for name in job.get('avoid', []):            # copper of routes placed earlier in this run
        r = results.get(name)
        if r and r.get('layer') == layer:
            for line in [r[k] for k in ('pos', 'neg') if k in r] or [r['center']]:
                for a, b in zip(line, line[1:]):
                    ras.seg(hard, a, b, 0.1)
    for x0, y0, x1, y1 in job.get('hard_rects', []):   # reserved areas (e.g. escape vias of neighbouring balls)
        ras.poly(hard, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    for z in geom['keepouts']:
        if layer in z['layers'] and z['tracks']:
            for q in z['poly']:
                ras.poly(hard, q)
    inside = np.zeros((ras.ny, ras.nx), bool)
    for q in geom['edge']:
        ras.poly(inside, q)
    dh = distance_transform_edt(~hard) * RES
    de = distance_transform_edt(inside) * RES
    ds = distance_transform_edt(~soft) * RES
    return dh, de, ds


def astar(job, ras, dh, de, ds):
    R = job['halfwidth'] + job['clearance'] + RES
    edge_r = job['halfwidth'] + 0.3 + RES
    sx, sy = ras.idx(*job['start'])
    ex, ey = ras.idx(*job['end'])
    sx, sy, ex, ey = (sx // STEP) * STEP, (sy // STEP) * STEP, (ex // STEP) * STEP, (ey // STEP) * STEP
    free_r = job.get('free_radius', 0.6)       # ignore hard obstacles this close to the ports (pad breakouts)

    def ok(i, j):
        if not (0 <= i < ras.nx and 0 <= j < ras.ny) or de[j, i] < edge_r:
            return False
        if dh[j, i] >= R:
            return True
        return min(math.hypot(i - sx, j - sy), math.hypot(i - ex, j - ey)) * RES < free_r

    sdirs = [job['start_dir']] if 'start_dir' in job else range(8)
    edir = job.get('end_dir')
    openq, best, came = [], {}, {}
    for d in sdirs:
        st = (sx, sy, d)
        best[st] = 0.0
        heapq.heappush(openq, (0.0, 0.0, st))
    goal = None
    while openq:
        f, g, st = heapq.heappop(openq)
        if g > best.get(st, 1e18) + 1e-9:
            continue
        i, j, d = st
        if (i, j) == (ex, ey) and (edir is None or d == edir):
            goal = st
            break
        for dd in (-1, 0, 1):
            nd = (d + dd) % 8
            di, dj = DIRS[nd]
            ni, nj = i + di * STEP, j + dj * STEP
            if not ok(ni, nj):
                continue
            L = math.hypot(di, dj) * STEP * RES
            cost = L + (TURN_COST if dd else 0) + (SOFT_COST * L if ds[nj, ni] < R else 0)
            ns = (ni, nj, nd)
            ng = g + cost
            if ng < best.get(ns, 1e18) - 1e-9:
                best[ns] = ng
                came[ns] = st
                ax, ay = abs(ex - ni), abs(ey - nj)
                h = (max(ax, ay) - min(ax, ay) + math.sqrt(2) * min(ax, ay)) * RES
                heapq.heappush(openq, (ng + h, ng, ns))
    if goal is None:
        return None
    path = [goal]
    while path[-1] in came:
        path.append(came[path[-1]])
    path.reverse()
    pts = [(ras.x0 + i * RES, ras.y0 + j * RES, d) for i, j, d in path]
    # collapse straight runs
    out = [pts[0][:2]]
    for k in range(1, len(pts) - 1):
        if pts[k][2] != pts[k + 1][2]:
            out.append(pts[k][:2])
    out.append(pts[-1][:2])
    return out


def offset(poly, off):
    """parallel polyline at signed distance off (left of travel direction in a y-down frame is +)"""
    res = []
    n = len(poly)
    for k in range(n):
        if k == 0:
            a, b = poly[0], poly[1]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            res.append((a[0] - dy / L * off, a[1] + dx / L * off))
        elif k == n - 1:
            a, b = poly[-2], poly[-1]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            res.append((b[0] - dy / L * off, b[1] + dx / L * off))
        else:
            a, b, c = poly[k - 1], poly[k], poly[k + 1]
            d1 = ((b[0] - a[0]), (b[1] - a[1])); L1 = math.hypot(*d1); d1 = (d1[0] / L1, d1[1] / L1)
            d2 = ((c[0] - b[0]), (c[1] - b[1])); L2 = math.hypot(*d2); d2 = (d2[0] / L2, d2[1] / L2)
            n1, n2 = (-d1[1], d1[0]), (-d2[1], d2[0])
            m = (n1[0] + n2[0], n1[1] + n2[1]); Lm = math.hypot(*m); m = (m[0] / Lm, m[1] / Lm)
            s = off / (m[0] * n1[0] + m[1] * n1[1])
            res.append((b[0] + m[0] * s, b[1] + m[1] * s))
    return res


results = {}
for job in jobs:
    xs = [job['start'][0], job['end'][0]]; ys = [job['start'][1], job['end'][1]]
    m = job.get('margin', 6.0)
    ras = Raster(min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m)
    dh, de, ds = build(job, ras)
    if job.get('debug'):
        np.savez_compressed(job['debug'], dh=dh, de=de, ds=ds, x0=ras.x0, y0=ras.y0)
    path = astar(job, ras, dh, de, ds)
    if path is None:
        print(job['name'], 'NO PATH')
        results[job['name']] = None
        continue
    L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))
    print('%s: %d vertices, %.2f mm' % (job['name'], len(path), L))
    if job['kind'] == 'pair':
        h = job['pitch'] / 2
        results[job['name']] = {'center': path, 'pos': offset(path, job['pos_side'] * h),
                                'neg': offset(path, -job['pos_side'] * h)}
    else:
        results[job['name']] = {'center': path}
    results[job['name']].update(layer=job['layer'], nets=job['nets'], width=job['halfwidth'] * 2 if job['kind'] != 'pair'
                                else job['halfwidth'] * 2 - job['pitch'])
json.dump(results, open(sys.argv[3], 'w'), indent=1)
