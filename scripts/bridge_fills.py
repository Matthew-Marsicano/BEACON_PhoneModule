"""Join same-net fills that overlap on different layers but are not connected: for every unconnected zone-to-zone
item the DRC reports, drop a via where both fills have copper all around it (so it clears every other net by the
fills' own clearance).

Run after the zones are filled:  D:/KiCAD/bin/python.exe -I scripts/bridge_fills.py drc.json
(drc.json from `kicad-cli pcb drc --format json`)
"""
import json
import math
import os
import sys

import pcbnew
from pcbnew import FromMM

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
VIA_D, VIA_H, HOLE2HOLE = 0.45, 0.25, 0.25

board = pcbnew.LoadBoard(PCB)
drc = json.load(open(sys.argv[1], encoding='utf8'))
zones = [board.GetArea(i) for i in range(board.GetAreaCount())]
no_via = [z for z in zones + [z for fp in board.GetFootprints() for z in fp.Zones()]
          if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
holes = [(v.GetPosition(), v.GetDrillValue()) for v in board.GetTracks() if v.GetClass() == 'PCB_VIA']
holes += [(p.GetPosition(), max(p.GetDrillSize().x, p.GetDrillSize().y)) for fp in board.GetFootprints()
          for p in fp.Pads() if p.HasHole()]
LAYER = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu, 'In1.Cu': pcbnew.In1_Cu, 'In2.Cu': pcbnew.In2_Cu}


def covered(net, layer, x, y):
    ring = [pcbnew.VECTOR2I(int(x + FromMM(dx)), int(y + FromMM(dy)))
            for dx, dy in ((0, 0), (0.35, 0), (-0.35, 0), (0, 0.35), (0, -0.35), (0.25, 0.25), (-0.25, 0.25),
                           (0.25, -0.25), (-0.25, -0.25))]
    return any(not z.GetIsRuleArea() and z.GetNetname() == net and z.GetLayerSet().Contains(layer)
               and all(z.HitTestFilledArea(layer, q, 0) for q in ring) for z in zones)


added = 0
for u in drc['unconnected_items']:
    items = u['items']
    if not all(i['description'].startswith('Zone') for i in items):
        continue
    net = items[0]['description'].split('[')[1].split(']')[0]
    l1, l2 = (LAYER[i['description'].split(' on ')[1].split(',')[0]] for i in items)
    if l1 == l2:
        continue
    best = None
    for z in zones:
        if z.GetIsRuleArea() or z.GetNetname() != net or not z.GetLayerSet().Contains(l1):
            continue
        bb = z.GetBoundingBox()
        step = FromMM(0.5)
        for x in range(bb.GetLeft(), bb.GetRight(), step):
            for y in range(bb.GetTop(), bb.GetBottom(), step):
                if not (covered(net, l1, x, y) and covered(net, l2, x, y)):
                    continue
                pt = pcbnew.VECTOR2I(x, y)
                if any(r.Outline().Contains(pt, -1, FromMM(VIA_D / 2)) for r in no_via):
                    continue
                if any(math.hypot(x - p.x, y - p.y) < FromMM(VIA_H / 2 + HOLE2HOLE) + d / 2 for p, d in holes):
                    continue
                best = (x, y)
                break
            if best:
                break
        if best:
            break
    if best is None:
        print('no spot for', net, items[0]['description'], '|', items[1]['description'])
        continue
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(*best)); v.SetWidth(FromMM(VIA_D)); v.SetDrill(FromMM(VIA_H))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(board.FindNet(net)); board.Add(v)
    holes.append((v.GetPosition(), FromMM(VIA_H)))
    added += 1
    print('bridged %s at (%.2f, %.2f)' % (net, best[0] / 1e6, best[1] / 1e6))
# outer GND islands with no via or plated hole in them: stitch each one to L2
gnd_vias = [v.GetPosition() for v in board.GetTracks() if v.GetClass() == 'PCB_VIA' and v.GetNetname() == 'GND']
gnd_vias += [p.GetPosition() for fp in board.GetFootprints() for p in fp.Pads() if p.HasHole() and p.GetNetname() == 'GND']
for z in zones:
    if z.GetIsRuleArea() or z.GetNetname() != 'GND':
        continue
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        if not z.GetLayerSet().Contains(layer):
            continue
        polys = z.GetFilledPolysList(layer)
        for k in range(polys.OutlineCount()):
            isl = pcbnew.SHAPE_POLY_SET(polys.Outline(k))
            if any(isl.Contains(p) for p in gnd_vias):
                continue
            bb = isl.BBox()
            spot = None
            for x in range(bb.GetLeft(), bb.GetRight(), FromMM(0.25)):
                for y in range(bb.GetTop(), bb.GetBottom(), FromMM(0.25)):
                    if isl.Contains(pcbnew.VECTOR2I(x, y)) and covered('GND', layer, x, y) and \
                            not any(r.Outline().Contains(pcbnew.VECTOR2I(x, y), -1, FromMM(VIA_D / 2)) for r in no_via) and \
                            not any(math.hypot(x - p.x, y - p.y) < FromMM(VIA_H / 2 + HOLE2HOLE) + d / 2 for p, d in holes):
                        spot = (x, y)
                        break
                if spot:
                    break
            if spot:
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(pcbnew.VECTOR2I(*spot)); v.SetWidth(FromMM(VIA_D)); v.SetDrill(FromMM(VIA_H))
                v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(board.FindNet('GND')); board.Add(v)
                holes.append((v.GetPosition(), FromMM(VIA_H))); gnd_vias.append(v.GetPosition())
                added += 1
                print('stitched GND island on %s at (%.2f, %.2f)' % (board.GetLayerName(layer), spot[0] / 1e6, spot[1] / 1e6))
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB, board)
print('vias added:', added)
