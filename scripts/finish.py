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
# Board title and team on the front, in the free bands between the 3 mm stitching-via rows (the back is the logo).
# Names as in the schematic title block.
label(board, 'BEACON Phone Module rev A', 19.55, 24.1, 1.2)                               # above the patch
label(board, 'HW: M. Marsicano, J. Oshinsky, N. McKillips, I. Hong', 20.75, 21.35, 0.8)
label(board, 'FW: J. Faubus, J. Hensley', 36.55, 3.0, 0.8)                                 # top edge
label(board, 'Advisor: Prof. Bahram Shafai', 39.25, 6.0, 0.8)
label(board, 'Northeastern Senior Capstone 2026', 14.7, 53.85, 0.8)                       # below the patch
label(board, 'MAGSAFE SIDE - PHONE', 40.5, 75.0, 0.8, pcbnew.B_SilkS)                     # back, clear of the logo
label(board, 'TX', 49.5, 18.5, 1.0)
label(board, 'USB-C', 31.4, 69.0, 0.8)                                                    # clear of R25/L6/C36
# drill/place origin at the board's bottom-left corner: Gerbers, drill and the JLC CPL share it (positive X/Y)
outline = pcbnew.SHAPE_POLY_SET()
board.GetBoardPolygonOutlines(outline, True)
bb = outline.BBox()
board.GetDesignSettings().SetAuxOrigin(VECTOR2I(bb.GetLeft(), bb.GetBottom()))
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB, board)
print('finished', PCB)
