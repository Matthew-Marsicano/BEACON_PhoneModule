"""Add the tracks and vias from scripts/netroute.py to the board, refill the zones and save.

Run:  D:/KiCAD/bin/python.exe -I scripts/apply_routes.py routes.json
"""
import json
import os
import sys

import pcbnew
from pcbnew import FromMM

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
LAYER = {'F': pcbnew.F_Cu, 'B': pcbnew.B_Cu, 'In2': pcbnew.In2_Cu}

board = pcbnew.LoadBoard(PCB)
data = json.load(open(sys.argv[1]))
NAME = {pcbnew.F_Cu: 'F', pcbnew.B_Cu: 'B', pcbnew.In2_Cu: 'In2'}

# copper the soft routes collided with (keys as written by netroute.py)
rip = {tuple(k) for r in data['routed'] for k in r.get('rip', [])}
graveyard = []   # keep removed items referenced (SWIG wrapper lifetime)
for t in list(board.GetTracks()):
    mm = lambda v: round(v / 1e6, 4)  # noqa: E731
    if t.GetClass() == 'PCB_VIA':
        k = ('v', t.GetNetname(), mm(t.GetPosition().x), mm(t.GetPosition().y))
    elif t.GetLayer() in NAME:
        k = ('t', t.GetNetname(), NAME[t.GetLayer()], mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetEnd().x),
             mm(t.GetEnd().y))
    else:
        continue
    if k in rip:
        board.Remove(t)
        graveyard.append(t)
print('ripped %d of %d listed items' % (len(graveyard), len(rip)))
nt = nv = 0
for r in data['routed']:
    net = board.FindNet(r['net'])
    for s in r['segs']:
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(FromMM(s['a'][0]), FromMM(s['a'][1])))
        t.SetEnd(pcbnew.VECTOR2I(FromMM(s['b'][0]), FromMM(s['b'][1])))
        t.SetWidth(FromMM(s['w'])); t.SetLayer(LAYER[s['layer']]); t.SetNet(net)
        board.Add(t); nt += 1
    for v in r['vias']:
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pcbnew.VECTOR2I(FromMM(v['pos'][0]), FromMM(v['pos'][1])))
        via.SetWidth(FromMM(v['d'])); via.SetDrill(FromMM(v['h'])); via.SetViaType(pcbnew.VIATYPE_THROUGH)
        via.SetNet(net); board.Add(via); nv += 1
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
board.BuildConnectivity()
pcbnew.SaveBoard(PCB, board)
print('added %d tracks, %d vias; unconnected now %d' % (nt, nv, board.GetConnectivity().GetUnconnectedCount(False)))
