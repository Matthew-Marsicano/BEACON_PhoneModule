"""Silkscreen clean-up and labels, zone refill.  Run after route.py.

Reference designators move to F.Fab/B.Fab (the board is too dense for legible silk refs; the assembly drawing
and the position file carry them).  A few functional labels are added on F.Silkscreen.
"""
import os

import pcbnew
from pcbnew import FromMM, VECTOR2I

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
OX, OY = 100.0, 100.0


def label(board, text, x, y, size=1.0, layer=pcbnew.F_SilkS, rot=0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(VECTOR2I(FromMM(OX + x), FromMM(OY + y)))
    t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
    t.SetTextThickness(FromMM(0.15))
    t.SetTextAngleDegrees(rot)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    board.Add(t)


board = pcbnew.LoadBoard(PCB)
for fp in board.GetFootprints():
    r = fp.Reference()
    r.SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
    r.SetTextSize(VECTOR2I(FromMM(0.5), FromMM(0.5)))
    r.SetTextThickness(FromMM(0.08))
    v = fp.Value()
    v.SetVisible(False)
    # drop footprint silk text items that are not graphics (e.g. 'PCB EDGE' notes stay on Dwgs.User)
old_text = [item for item in board.GetDrawings()
            if item.GetClass() == 'PCB_TEXT' and item.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)]
for item in old_text:   # keep the list alive: freeing removed SWIG wrappers corrupts later lookups
    board.Remove(item)
label(board, 'BEACON Phone Module rev A', 27.5, 9.0, 1.2, pcbnew.B_SilkS)
label(board, 'Northeastern Senior Capstone 2026', 27.5, 11.5, 0.9, pcbnew.B_SilkS)
label(board, 'MAGSAFE SIDE - PHONE', 27.5, 14.0, 0.9, pcbnew.B_SilkS)
label(board, 'TX', 49.5, 18.5, 1.0)
label(board, 'USB-C', 27.5, 66.6, 0.8)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB, board)
print('finished', PCB)
