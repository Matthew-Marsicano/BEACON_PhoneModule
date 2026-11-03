"""GND stitching after routing: via fences along RF lines (1.0 mm pitch) and board-perimeter stitching
(<= 2.5 mm pitch, docs/magnetics_thermal.md rule 7) and a 3 mm field grid wherever F.Cu/B.Cu has GND pour, with exact distance checks against other-net copper.

Run after route.py:  D:/KiCAD/bin/python.exe -I scripts/stitch.py
"""
import math
import os

import pcbnew
from pcbnew import FromMM, ToMM

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
OX, OY, BW, BH = 100.0, 100.0, 55.0, 78.45
HOLES = [(3.5, 3.5), (51.5, 3.5), (3.5, 74.95), (51.5, 74.95)]   # board coords (y up)
VIA_D, VIA_H, CLR = 0.45, 0.25, 0.2
RF = {'RX_PATCH', 'SYN_OUTAP', 'CW_RF', 'PA_IN', 'PA_OUT', 'PA_MATCH', 'TX_LPF', 'TX_ANT', 'NRF_ANT', 'RX_RF',
      'RX_ATT', 'LNA_OUT', 'LNA_IN', 'RX_BPF', 'RX_ANT'}


def mm(v):
    return ToMM(v.x) - OX, ToMM(v.y) - OY


def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


board = pcbnew.LoadBoard(PCB)
gnd = board.FindNet('GND')
obst = []   # (kind, geometry, half-width) of non-GND copper
for t in board.GetTracks():
    if t.GetNetname() == 'GND':
        continue
    if t.GetClass() == 'PCB_VIA':
        obst.append(('c', mm(t.GetPosition()), ToMM(t.GetWidth()) / 2))
    else:
        obst.append(('s', (mm(t.GetStart()), mm(t.GetEnd())), ToMM(t.GetWidth()) / 2))
for fp in board.GetFootprints():
    for pd in fp.Pads():
        if pd.GetNetname() == 'GND' and pd.GetAttribute() == pcbnew.PAD_ATTRIB_SMD:
            continue
        bb = pd.GetBoundingBox()
        obst.append(('r', (ToMM(bb.GetLeft()) - OX, ToMM(bb.GetTop()) - OY, ToMM(bb.GetRight()) - OX,
                           ToMM(bb.GetBottom()) - OY), 0))
existing = [mm(t.GetPosition()) for t in board.GetTracks() if t.GetClass() == 'PCB_VIA']
# rule areas that forbid vias (standoff keepouts, footprint keepouts such as the patch feed void)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
power_fills = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname() != 'GND'
               and (z.GetLayerSet().Contains(pcbnew.F_Cu) or z.GetLayerSet().Contains(pcbnew.B_Cu))]
no_via = [z for z in list(board.Zones()) + [z for fp in board.GetFootprints() for z in fp.Zones()]
          if z.GetIsRuleArea() and z.GetDoNotAllowVias()]


def free(x, y):
    r = VIA_D / 2 + CLR
    if not (0.7 < x < BW - 0.7 and 0.7 < y < BH - 0.7):
        return False
    if any(math.hypot(x - hx, y - (BH - hy)) < 3.6 for hx, hy in HOLES):
        return False
    for cx, cy in ((3, 3), (BW - 3, 3), (3, BH - 3), (BW - 3, BH - 3)):   # r = 3 mm board corners
        if abs(x - cx) <= 3 and abs(y - cy) <= 3 and (x - cx) * (cx - BW / 2) > 0 and (y - cy) * (cy - BH / 2) > 0 \
                and math.hypot(x - cx, y - cy) > 3 - 0.7:
            return False
    if x > BW - 1.5 - 0.7 and BH - 69.55 - 0.7 < y < BH - 62.45 + 0.7:   # TX jack notch
        return False
    if math.hypot(x - BW / 2 + 0.0, 0) < 5.0 and y > BH - 8.0:          # USB-C receptacle body
        return False
    if any(math.hypot(x - ex, y - ey) < VIA_D + 0.25 for ex, ey in existing):
        return False
    pt = pcbnew.VECTOR2I(FromMM(OX + x), FromMM(OY + y))
    if any(z.Outline().Contains(pt, -1, FromMM(VIA_D / 2 + 0.05)) for z in no_via):
        return False
    # other-net fills on the outer layers (5V power fills): a via there would cut the fill
    if any(z.HitTestFilledArea(l, pt, FromMM(r)) for z in power_fills for l in (pcbnew.F_Cu, pcbnew.B_Cu)
           if z.GetLayerSet().Contains(l)):
        return False
    for kind, g, hw in obst:
        if kind == 'c' and math.hypot(x - g[0], y - g[1]) < r + hw:
            return False
        if kind == 's' and seg_dist((x, y), g[0], g[1]) < r + hw:
            return False
        if kind == 'r' and g[0] - r < x < g[2] + r and g[1] - r < y < g[3] + r:
            return False
    return True


def add(x, y):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(FromMM(OX + x), FromMM(OY + y)))
    v.SetWidth(FromMM(VIA_D)); v.SetDrill(FromMM(VIA_H))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(gnd)
    board.Add(v)
    existing.append((x, y))


n_fence = 0
for t in list(board.GetTracks()):
    if t.GetClass() != 'PCB_TRACK' or t.GetNetname().rsplit('/', 1)[-1] not in RF:
        continue
    (x1, y1), (x2, y2) = mm(t.GetStart()), mm(t.GetEnd())
    L = math.hypot(x2 - x1, y2 - y1)
    if L < 0.5:
        continue
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    off = ToMM(t.GetWidth()) / 2 + 0.2 + VIA_D / 2 + 0.15     # ~0.75 mm from the centreline
    for k in range(int(L / 1.0) + 1):
        s = min(k * 1.0, L)
        for side in (-1, 1):
            x, y = x1 + ux * s - uy * off * side, y1 + uy * s + ux * off * side
            if free(x, y):
                add(x, y)
                n_fence += 1
n_edge = 0
inset = 0.9
perim = [(inset, inset), (BW - inset, inset), (BW - inset, BH - inset), (inset, BH - inset), (inset, inset)]
for (ax, ay), (bx, by) in zip(perim, perim[1:]):
    L = math.hypot(bx - ax, by - ay)
    for k in range(int(L / 2.5) + 1):
        x, y = ax + (bx - ax) * k * 2.5 / L, ay + (by - ay) * k * 2.5 / L
        if free(x, y):
            add(x, y)
            n_edge += 1
# field stitching: tie the outer GND pours to L2 on a grid, wherever an outer layer actually has GND copper
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
outer = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND'
         and (z.GetLayerSet().Contains(pcbnew.F_Cu) or z.GetLayerSet().Contains(pcbnew.B_Cu))]
n_grid = 0
GRID = 3.0
for i in range(int(BW / GRID) + 1):
    for j in range(int(BH / GRID) + 1):
        x, y = 1.5 + i * GRID, 1.5 + j * GRID
        ring = [pcbnew.VECTOR2I(FromMM(OX + x + dx), FromMM(OY + y + dy))
                for dx, dy in ((0, 0), (0.35, 0), (-0.35, 0), (0, 0.35), (0, -0.35))]
        on = [l for z in outer for l in (pcbnew.F_Cu, pcbnew.B_Cu)
              if z.GetLayerSet().Contains(l) and all(z.HitTestFilledArea(l, q, 0) for q in ring)]
        if on and free(x, y):
            add(x, y)
            n_grid += 1
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB, board)
print('RF fence vias: %d, perimeter vias: %d, grid vias: %d' % (n_fence, n_edge, n_grid))
