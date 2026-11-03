"""Close short leftover gaps the autorouter didn't finish: for every net still split into islands, join the two closest
items (track end / via / pad) of different islands with a straight segment on a shared copper layer when the segment
clears all other-net copper; if no layer is shared, drop a via at the track end first.

Run after reroute.py, before stitch.py:  D:/KiCAD/bin/python.exe -I scripts/closegaps.py
"""
import math
import os

import pcbnew
from pcbnew import FromMM, ToMM

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
OX, OY = 100.0, 100.0
MAX_GAP = 3.0           # mm: only close short gaps
CLR = 0.15
SIGNAL_LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)

board = pcbnew.LoadBoard(PCB)


def mm(v):
    return ToMM(v.x) - OX, ToMM(v.y) - OY


def seg_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def seg_seg(a, b, c, d):
    return min(seg_dist(a, c, d), seg_dist(b, c, d), seg_dist(c, a, b), seg_dist(d, a, b)) if not _cross(a, b, c, d) else 0


def _cross(a, b, c, d):
    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return (o(a, b, c) * o(a, b, d) < 0) and (o(c, d, a) * o(c, d, b) < 0)


def rect_seg(r, a, b):
    # distance from segment to rectangle (sampled)
    best = 1e9
    for k in range(21):
        p = (a[0] + (b[0] - a[0]) * k / 20, a[1] + (b[1] - a[1]) * k / 20)
        best = min(best, math.hypot(max(r[0] - p[0], 0, p[0] - r[2]), max(r[1] - p[1], 0, p[1] - r[3])))
    return best


def obstacles():
    obs = []
    for t in board.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            obs.append((t.GetNetCode(), 'c', mm(t.GetPosition()), ToMM(t.GetWidth(pcbnew.F_Cu)) / 2, None))
        else:
            obs.append((t.GetNetCode(), 's', (mm(t.GetStart()), mm(t.GetEnd())), ToMM(t.GetWidth()) / 2, t.GetLayer()))
    for fp in board.GetFootprints():
        for pd in fp.Pads():
            bb = pd.GetBoundingBox()
            r = (ToMM(bb.GetLeft()) - OX, ToMM(bb.GetTop()) - OY, ToMM(bb.GetRight()) - OX, ToMM(bb.GetBottom()) - OY)
            obs.append((pd.GetNetCode(), 'r', r, 0, [l for l in SIGNAL_LAYERS if pd.IsOnLayer(l)]))
    return obs


def clear(a, b, w, layer, netcode, obs):
    for nc, kind, g, hw, lyr in obs:
        if nc == netcode:
            continue
        if kind == 'c':
            if seg_dist(g, a, b) < hw + w / 2 + CLR:
                return False
        elif kind == 's':
            if lyr == layer and seg_seg(a, b, g[0], g[1]) < hw + w / 2 + CLR:
                return False
        elif kind == 'r':
            if layer in lyr and rect_seg(g, a, b) < w / 2 + CLR:
                return False
    return True


def anchors(item):
    """(point, layers) where a new segment may attach to this item."""
    if item.GetClass() == 'PCB_VIA':
        return [(mm(item.GetPosition()), list(SIGNAL_LAYERS))]
    if item.GetClass() == 'PCB_TRACK':
        return [(mm(item.GetStart()), [item.GetLayer()]), (mm(item.GetEnd()), [item.GetLayer()])]
    if item.GetClass() == 'PAD':
        return [(mm(item.GetPosition()), [l for l in SIGNAL_LAYERS if item.IsOnLayer(l)])]
    return []


closed = 0
for _round in range(3):
    board.BuildConnectivity()
    conn = board.GetConnectivity()
    obs = obstacles()
    by_net = {}
    for t in board.GetTracks():
        by_net.setdefault(t.GetNetCode(), []).append(t)
    for fp in board.GetFootprints():
        for pd in fp.Pads():
            by_net.setdefault(pd.GetNetCode(), []).append(pd)
    progress = False
    for nc, items in by_net.items():
        if nc <= 0:
            continue
        name = board.FindNet(nc).GetNetname() if hasattr(board, 'FindNet') else ''
        if name.startswith('unconnected-') or name in ('GND', '3V3', '/CW_Synth/VCC_SYN') or len(items) > 60:
            continue  # plane nets connect through their pours; huge nets are too slow to pair-search
        # group items into connected islands
        islands, seen = [], set()
        for it in items:
            if id(it) in seen:
                continue
            group = [it] + [x for x in conn.GetConnectedItems(it) if x.GetNetCode() == nc]
            for g in group:
                seen.add(id(g))
            islands.append(group)
        # zones also connect (GND/3V3 planes) - count an island as anchored if it touches a zone
        if len(islands) < 2:
            continue
        best = None
        for i in range(len(islands)):
            for j in range(i + 1, len(islands)):
                for a in islands[i]:
                    for b in islands[j]:
                        for pa, la in anchors(a):
                            for pb, lb in anchors(b):
                                d = math.hypot(pa[0] - pb[0], pa[1] - pb[1])
                                if d < 0.01 or d > MAX_GAP:
                                    continue
                                for layer in set(la) & set(lb):
                                    if best is None or d < best[0]:
                                        best = (d, pa, pb, layer)
        if best is None:
            continue
        d, pa, pb, layer = best
        w = 0.15
        if clear(pa, pb, w, layer, nc, obs):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(FromMM(OX + pa[0]), FromMM(OY + pa[1])))
            t.SetEnd(pcbnew.VECTOR2I(FromMM(OX + pb[0]), FromMM(OY + pb[1])))
            t.SetWidth(FromMM(w)); t.SetLayer(layer); t.SetNetCode(nc)
            board.Add(t)
            obs.append((nc, 's', (pa, pb), w / 2, layer))
            closed += 1
            progress = True
            print('closed %s on %s: %.2f mm' % (name, board.GetLayerName(layer), d))
    if not progress:
        break
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB, board)
print('gaps closed:', closed)
