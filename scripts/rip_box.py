"""Clear a congested area so its connections can be re-routed together: remove every unlocked track and via of an
ordinary signal net that lies (even partly) inside the box.  Priority copper stays: locked items, GND / power /
plane nets, USB and RF.

Run:  D:/KiCAD/bin/python.exe -I scripts/rip_box.py X0 Y0 X1 Y1 [--plane-tracks]     (KiCad mm)
"""
import os
import sys

import pcbnew
from pcbnew import ToMM

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
RF = {'RX_PATCH', 'SYN_OUTAP', 'CW_RF', 'PA_IN', 'PA_OUT', 'PA_MATCH', 'TX_LPF', 'TX_ANT', 'NRF_ANT', 'RX_RF',
      'RX_ATT', 'LNA_OUT', 'LNA_IN', 'RX_BPF', 'RX_ANT'}
KEEP = {'GND', '3V3', '/CW_Synth/VCC_SYN', '5V0', '5V_BUS', 'USB_D+', 'USB_D-', '/Power/REG_INTVCC'}
x0, y0, x1, y1 = map(float, sys.argv[1:5])
PLANE_TRACKS = '--plane-tracks' in sys.argv     # also clear plane-net (3V3, VCC_SYN) links; their vias stay

board = pcbnew.LoadBoard(PCB)


def inside(v):
    return x0 <= ToMM(v.x) <= x1 and y0 <= ToMM(v.y) <= y1


graveyard, nets = [], set()
for t in board.GetTracks():
    n = t.GetNetname()
    plane_link = PLANE_TRACKS and n in ('3V3', '/CW_Synth/VCC_SYN') and t.GetClass() != 'PCB_VIA'
    if t.IsLocked() or (n in KEEP and not plane_link) or n.rsplit('/', 1)[-1] in RF:
        continue
    hit = inside(t.GetPosition()) if t.GetClass() == 'PCB_VIA' else (inside(t.GetStart()) or inside(t.GetEnd()))
    if hit:
        graveyard.append(t)
        nets.add(n)
for t in graveyard:
    board.Remove(t)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
board.BuildConnectivity()
pcbnew.SaveBoard(PCB, board)
print('removed %d items of %d nets: %s' % (len(graveyard), len(nets), ', '.join(sorted(nets))))
print('unconnected now', board.GetConnectivity().GetUnconnectedCount(False))
