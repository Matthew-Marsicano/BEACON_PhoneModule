"""Commit the priority-routed USB pair (scripts/pairroute.py output) to the board:

  U5 AD6/AD4 (D+/D-) via-in-pad 0.3/0.15 -> coupled pair on B.Cu (0.20 / 0.13 gap) -> via-in-pad 0.45/0.25 in the
  U1 (ESD) flow-through pins 6/4, joining the existing J1 -> U1 routing on F.Cu.

Every other-net track or via the new copper collides with is ripped up (the autorouter re-routes those nets), and the
USB and RF copper is locked so later passes route around it.

Run:  D:/KiCAD/bin/python.exe -I scripts/apply_usb.py routes.json
"""
import json
import math
import os
import sys

import pcbnew
from pcbnew import FromMM, ToMM

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
W, PITCH, CLR = 0.20, 0.33, 0.2
RF = {'RX_PATCH', 'SYN_OUTAP', 'CW_RF', 'PA_IN', 'PA_OUT', 'PA_MATCH', 'TX_LPF', 'TX_ANT', 'NRF_ANT', 'RX_RF',
      'RX_ATT', 'LNA_OUT', 'LNA_IN', 'RX_BPF', 'RX_ANT'}

route = json.load(open(sys.argv[1]))['usb_b']
board = pcbnew.LoadBoard(PCB)
dp, dm = board.FindNet('USB_D+'), board.FindNet('USB_D-')
graveyard = []
# re-running replaces an earlier B.Cu pair (and its vias); the J1 -> U1 F.Cu routing stays
old = [t for t in board.GetTracks() if t.GetNetCode() in (dp.GetNetCode(), dm.GetNetCode())
       and (t.GetClass() == 'PCB_VIA' or t.GetLayer() == pcbnew.B_Cu)]
for t in old:
    board.Remove(t)
    graveyard.append(t)
print('previous pair items removed:', len(old))


def pad(ref, num):
    return [p for p in board.FindFootprintByReference(ref).Pads() if p.GetNumber() == num][0]


def at(p):
    return ToMM(p.GetPosition().x), ToMM(p.GetPosition().y)


def offset(poly, off):
    res = []
    for k in range(len(poly)):
        if k in (0, len(poly) - 1):
            a, b = (poly[0], poly[1]) if k == 0 else (poly[-2], poly[-1])
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            q = poly[k]
            res.append((q[0] - dy / L * off, q[1] + dx / L * off))
        else:
            a, b, c = poly[k - 1], poly[k], poly[k + 1]
            L1 = math.hypot(b[0] - a[0], b[1] - a[1]); d1 = ((b[0] - a[0]) / L1, (b[1] - a[1]) / L1)
            L2 = math.hypot(c[0] - b[0], c[1] - b[1]); d2 = ((c[0] - b[0]) / L2, (c[1] - b[1]) / L2)
            n1, n2 = (-d1[1], d1[0]), (-d2[1], d2[0])
            m = (n1[0] + n2[0], n1[1] + n2[1]); Lm = math.hypot(*m); m = (m[0] / Lm, m[1] / Lm)
            s = off / (m[0] * n1[0] + m[1] * n1[1])
            res.append((b[0] + m[0] * s, b[1] + m[1] * s))
    return res


# centreline: start with a short straight run out of the U5 ball row, end heading straight down into U1
c = [tuple(p) for p in route['center']]
c = [(c[0][0], c[0][1] + 0.15)] + c
if math.hypot(c[-1][0] - c[-2][0], c[-1][1] - c[-2][1]) < 0.2:     # grid-snap stub: its offsets kink the pair
    c = c[:-1]
c.append((c[-1][0], c[-1][1] + 0.3))      # straight down into the U1 breakout (end_dir = down)
h = PITCH / 2
plus, minus = offset(c, -h), offset(c, h)        # pos_side -1: D+ on the left leaving U5
ad6, ad4 = at(pad('U5', 'AD6')), at(pad('U5', 'AD4'))
u16, u14 = at(pad('U1', '6')), at(pad('U1', '4'))
e = minus[-1]
plus_path = [ad6] + plus + [u16]
minus_path = [ad4] + minus + [(e[0] - 0.135, e[1] + 0.135), (e[0] - 0.135, u14[1] - 0.54), u14]
new_tracks = [(dp, plus_path), (dm, minus_path)]
new_vias = [(dp, ad6, 0.3, 0.15), (dm, ad4, 0.3, 0.15), (dp, u16, 0.45, 0.25), (dm, u14, 0.45, 0.25)]


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def segseg(a, b, c2, d):
    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    if o(a, b, c2) * o(a, b, d) < 0 and o(c2, d, a) * o(c2, d, b) < 0:
        return 0.0
    return min(seg_dist(a, c2, d), seg_dist(b, c2, d), seg_dist(c2, a, b), seg_dist(d, a, b))


new_segs = [(a, b) for _, path in new_tracks for a, b in zip(path, path[1:])]
usb = {dp.GetNetCode(), dm.GetNetCode()}
ripped, problems = set(), []
for t in list(board.GetTracks()):
    if t.GetNetCode() in usb:
        continue
    rf = t.GetNetname().rsplit('/', 1)[-1] in RF
    if t.GetClass() == 'PCB_VIA':
        p, r = at(t), ToMM(t.GetWidth(pcbnew.F_Cu)) / 2
        hit = any(seg_dist(p, a, b) < r + W / 2 + CLR for a, b in new_segs) or \
            any(math.hypot(p[0] - q[0], p[1] - q[1]) < r + d / 2 + 0.15 for _, q, d, _h in new_vias)
    else:
        a, b, hw = (ToMM(t.GetStart().x), ToMM(t.GetStart().y)), (ToMM(t.GetEnd().x), ToMM(t.GetEnd().y)), ToMM(t.GetWidth()) / 2
        hit = (t.GetLayer() == pcbnew.B_Cu and any(segseg(a, b, s0, s1) < hw + W / 2 + CLR for s0, s1 in new_segs)) or \
            any(seg_dist(q, a, b) < hw + d / 2 + 0.1 for _, q, d, _h in new_vias)
    if not hit:
        continue
    if rf or t.IsLocked():
        problems.append('%s %s at %s' % (t.GetClass(), t.GetNetname(), at(t) if t.GetClass() == 'PCB_VIA' else ''))
        continue
    ripped.add(t.GetNetname())
    board.Remove(t)
    graveyard.append(t)
if problems:
    print('WARNING - new USB copper touches protected copper:', problems)

for net, path in new_tracks:
    for a, b in zip(path, path[1:]):
        if math.hypot(b[0] - a[0], b[1] - a[1]) < 1e-4:
            continue
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(FromMM(a[0]), FromMM(a[1]))); t.SetEnd(pcbnew.VECTOR2I(FromMM(b[0]), FromMM(b[1])))
        t.SetWidth(FromMM(W)); t.SetLayer(pcbnew.B_Cu); t.SetNet(net); board.Add(t)
for net, p, d, hole in new_vias:
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(FromMM(p[0]), FromMM(p[1]))); v.SetWidth(FromMM(d)); v.SetDrill(FromMM(hole))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(net); board.Add(v)

# lock the priority copper: USB pair and every RF net
for t in board.GetTracks():
    if t.GetNetCode() in usb or t.GetNetname().rsplit('/', 1)[-1] in RF:
        t.SetLocked(True)


def length(net):
    return sum(ToMM(t.GetLength()) for t in board.GetTracks() if t.GetClass() != 'PCB_VIA' and t.GetNetCode() == net.GetNetCode())


print('ripped nets (%d): %s' % (len(ripped), ', '.join(sorted(ripped))))
print('USB_D+ %.2f mm, USB_D- %.2f mm, skew %.2f mm' % (length(dp), length(dm), length(dp) - length(dm)))
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB, board)
print('saved')
