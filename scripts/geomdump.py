"""Dump copper geometry (pads as polygons, tracks, vias, keepouts, board edge) to JSON for plotting and the pair router.

Run:  D:/KiCAD/bin/python.exe -I scripts/geomdump.py out.json
"""
import json
import sys

import pcbnew
from pcbnew import ToMM

PRJ_PCB = __file__.replace('scripts', '').rsplit('geomdump.py', 1)[0] + 'BEACON_PhoneModule.kicad_pcb'
board = pcbnew.LoadBoard(sys.argv[2] if len(sys.argv) > 2 else PRJ_PCB)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
LAYERS = {pcbnew.F_Cu: 'F', pcbnew.In1_Cu: 'In1', pcbnew.In2_Cu: 'In2', pcbnew.B_Cu: 'B'}


def poly(ps):
    out = []
    for k in range(ps.OutlineCount()):
        ch = ps.Outline(k)
        out.append([(ToMM(ch.CPoint(i).x), ToMM(ch.CPoint(i).y)) for i in range(ch.PointCount())])
    return out


pads = []
for fp in board.GetFootprints():
    for pd in fp.Pads():
        lys = [n for l, n in LAYERS.items() if pd.IsOnLayer(l)]
        for l, n in LAYERS.items():
            if pd.IsOnLayer(l):
                pads.append({'ref': fp.GetReference(), 'num': pd.GetNumber(), 'net': pd.GetNetname(), 'layer': n,
                             'pos': (ToMM(pd.GetPosition().x), ToMM(pd.GetPosition().y)),
                             'poly': poly(pd.GetEffectivePolygon(l, pcbnew.ERROR_INSIDE)),
                             'hole': ToMM(max(pd.GetDrillSize().x, pd.GetDrillSize().y)) if pd.HasHole() else 0})
tracks, vias = [], []
for t in board.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        vias.append({'net': t.GetNetname(), 'pos': (ToMM(t.GetPosition().x), ToMM(t.GetPosition().y)),
                     'd': ToMM(t.GetWidth(pcbnew.F_Cu)), 'h': ToMM(t.GetDrillValue()), 'locked': t.IsLocked()})
    elif t.GetLayer() in LAYERS:
        tracks.append({'net': t.GetNetname(), 'layer': LAYERS[t.GetLayer()], 'w': ToMM(t.GetWidth()), 'locked': t.IsLocked(),
                       'a': (ToMM(t.GetStart().x), ToMM(t.GetStart().y)), 'b': (ToMM(t.GetEnd().x), ToMM(t.GetEnd().y))})
keepouts = []
for z in [board.GetArea(i) for i in range(board.GetAreaCount())] + [z for fp in board.GetFootprints() for z in fp.Zones()]:
    if z.GetIsRuleArea():
        keepouts.append({'layers': [LAYERS[l] for l in z.GetLayerSet().CuStack() if l in LAYERS],
                         'tracks': z.GetDoNotAllowTracks(), 'vias': z.GetDoNotAllowVias(), 'poly': poly(z.Outline())})
fills = []
for z in [board.GetArea(i) for i in range(board.GetAreaCount())]:
    if z.GetIsRuleArea():
        continue
    for l, n in LAYERS.items():
        if z.GetLayerSet().Contains(l) and z.IsFilled():
            fp = z.GetFilledPolysList(l)
            fills.append({'net': z.GetNetname(), 'layer': n, 'name': z.GetZoneName(), 'poly': poly(fp),
                          'holes': [[(ToMM(fp.CHole(k, h).CPoint(i).x), ToMM(fp.CHole(k, h).CPoint(i).y))
                                     for i in range(fp.CHole(k, h).PointCount())]
                                    for k in range(fp.OutlineCount()) for h in range(fp.HoleCount(k))]})
outline = pcbnew.SHAPE_POLY_SET()
board.GetBoardPolygonOutlines(outline, True)
court = {}
for fp in board.GetFootprints():
    c = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd)
    court[fp.GetReference()] = poly(c)
json.dump({'pads': pads, 'tracks': tracks, 'vias': vias, 'keepouts': keepouts, 'edge': poly(outline), 'fills': fills,
           'courtyards': court}, open(sys.argv[1], 'w'))
print('pads', len(pads), 'tracks', len(tracks), 'vias', len(vias))
