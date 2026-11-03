"""Power nets without a plane (5V0, 5V_BUS) as copper fills: on each outer layer the net's routed tracks and pads are
grown into a pour (track edge + MARGIN each side, clipped by the normal clearances), priority above the GND pour.
The tracks are then removed if the net stays fully connected through the fill alone; otherwise they are kept as the
pour's backbone (they merge into the same copper).

Run after the signal routing is complete:  D:/KiCAD/bin/python.exe -I scripts/power_fills.py [NET,NET,...]
"""
import math
import os
import sys

import pcbnew
from pcbnew import FromMM, ToMM

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
NETS = sys.argv[1].split(',') if len(sys.argv) > 1 else ['5V0', '5V_BUS']
MARGIN = 0.5          # mm of extra copper beside each track edge
CLEARANCE = 0.15      # Power class clearance
PRIORITY = 3          # above the outer GND pours (1) and the inner GND islands (2)
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)

board = pcbnew.LoadBoard(PCB)
graveyard = []        # removed items must stay referenced (SWIG wrapper lifetime)


def stadium(a, b, r, n=16):
    """polygon of a track of half-width r from a to b (rounded ends)"""
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    pts = []
    for c, base in ((b, ang - math.pi / 2), (a, ang + math.pi / 2)):
        for k in range(n + 1):
            t = base + math.pi * k / n
            pts.append((c[0] + r * math.cos(t), c[1] + r * math.sin(t)))
    ps = pcbnew.SHAPE_POLY_SET()
    ps.NewOutline()
    for x, y in pts:
        ps.Append(int(x), int(y))
    return ps


def unconnected():
    board.BuildConnectivity()
    return board.GetConnectivity().GetUnconnectedCount(False)


old = [z for z in [board.GetArea(i) for i in range(board.GetAreaCount())]
       if not z.GetIsRuleArea() and z.GetNetname() in NETS and z.GetZoneName().startswith('PWR_FILL')]
for z in old:                                  # re-running replaces the previous fills
    board.Remove(z); graveyard.append(z)

made = []
for name in NETS:
    net = board.FindNet(name)
    for layer in LAYERS:
        shape = pcbnew.SHAPE_POLY_SET()
        tr = [t for t in board.GetTracks() if t.GetClass() != 'PCB_VIA' and t.GetNetCode() == net.GetNetCode()
              and t.GetLayer() == layer]
        for t in tr:
            r = t.GetWidth() / 2 + FromMM(MARGIN)
            shape.BooleanAdd(stadium((t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y), r))
        for fp in board.GetFootprints():
            for pd in fp.Pads():
                if pd.GetNetCode() == net.GetNetCode() and pd.IsOnLayer(layer) and tr:
                    p = pd.GetEffectivePolygon(layer, pcbnew.ERROR_OUTSIDE)
                    shape.BooleanAdd(p)
        if shape.OutlineCount() == 0:
            continue
        shape.Simplify()
        for k in range(shape.OutlineCount()):
            z = pcbnew.ZONE(board)
            z.SetLayer(layer)
            z.SetNet(net)
            z.SetZoneName('PWR_FILL_%s' % name.replace('/', '_'))
            z.SetAssignedPriority(PRIORITY)
            z.SetLocalClearance(FromMM(CLEARANCE))
            z.SetMinThickness(FromMM(0.15))
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
            ol = z.Outline()
            ol.NewOutline()
            ch = shape.Outline(k)
            for i in range(ch.PointCount()):
                ol.Append(ch.CPoint(i).x, ch.CPoint(i).y)
            board.Add(z)
            made.append(z)
print('fill zones created:', len(made))
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
base = unconnected()

for name in NETS:
    net = board.FindNet(name)
    tr = [t for t in board.GetTracks() if t.GetClass() != 'PCB_VIA' and t.GetNetCode() == net.GetNetCode()
          and not t.IsLocked()]
    saved = [(t.GetStart(), t.GetEnd(), t.GetWidth(), t.GetLayer()) for t in tr]
    for t in tr:
        board.Remove(t); graveyard.append(t)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    now = unconnected()
    if now > base:
        for a, b, w, l in saved:
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(a); t.SetEnd(b); t.SetWidth(w); t.SetLayer(l); t.SetNet(net); board.Add(t)
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        print('%s: fill alone leaves %d gap(s) -> kept its %d tracks inside the fill' % (name, now - base, len(saved)))
    else:
        print('%s: %d tracks replaced by the fill' % (name, len(saved)))
pcbnew.SaveBoard(PCB, board)
print('unconnected items:', unconnected(), '| saved', PCB)
