"""Merge the BEACON phone module (KiCad) and wearable (Altium) Gerbers into one JLC panel.

Layout (mm, panel origin = bottom-left): 100 x 92.45, 5 mm rails top/bottom, 4.5 mm side frames,
2 mm milled slots, mouse-bite tabs, 3 fiducials per side. Phone origin -> (6.5, 7.0),
wearable origin -> (63.5, 31.225). Run with the scratch venv python.
"""
import csv
import math
import sys
from pathlib import Path

from gerbonara import ExcellonFile, GerberFile
from gerbonara.apertures import CircleAperture, ExcellonTool
from gerbonara.graphic_objects import Flash, Line
from gerbonara.utils import MM
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

W_DIR = Path(r"D:\Backscatter Radio Capstone - Wearable\Project Outputs\JLCPCB\gerbers")
P_DIR = Path(r"C:\Users\marsi\KiCAD\BEACON_PhoneModule\fab\gerbers")
W_CPL = Path(r"C:\Users\marsi\KiCAD\BEACON_PhoneModule\fab\wearable\BEACON_Wearable_CPL_JLC.csv")
P_CPL = Path(r"C:\Users\marsi\KiCAD\BEACON_PhoneModule\fab\BEACON_PhoneModule_CPL_JLC.csv")
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
OUT.mkdir(parents=True, exist_ok=True)

PW, PH = 100.0, 92.45
P_OFF, W_OFF = (6.5, 7.0), (63.5, 31.225)
GAP, TAB_W, BITE_D, BITE_PITCH = 2.0, 3.0, 0.5, 0.8
FIDS = [(10.0, 2.5), (90.0, 2.5), (10.0, PH - 2.5)]   # asymmetric so orientation is unambiguous

P = "BEACON_PhoneModule-"
LAYERS = {  # panel ext: (wearable file, phone file)
    "GTL": ("PCB1.GTL", P + "F_Cu.gtl"), "G1": ("PCB1.G1", P + "In1_Cu.g1"),
    "G2": ("PCB1.G2", P + "In2_Cu.g2"), "GBL": ("PCB1.GBL", P + "B_Cu.gbl"),
    "GTO": ("PCB1.GTO", P + "F_Silkscreen.gto"), "GBO": ("PCB1.GBO", P + "B_Silkscreen.gbo"),
    "GTP": ("PCB1.GTP", P + "F_Paste.gtp"), "GBP": ("PCB1.GBP", P + "B_Paste.gbp"),
    "GTS": ("PCB1.GTS", P + "F_Mask.gts"), "GBS": ("PCB1.GBS", P + "B_Mask.gbs"),
}

# ---- board shapes in panel coords -------------------------------------------------------------
def rrect(x0, y0, w, h, r):
    return box(x0 + r, y0 + r, x0 + w - r, y0 + h - r).buffer(r, quad_segs=32)

px, py = P_OFF
wx, wy = W_OFF
phone = rrect(px, py, 55.0, 78.45, 3.0).difference(box(px + 53.5, py + 62.45, px + 55.1, py + 69.55))
wear = rrect(wx, wy, 30.0, 30.0, 3.0)
boards = unary_union([phone, wear])

# ---- tabs: (board, edge, position along edge in board coords) ---------------------------------
# edges: 'L','R' -> position is board y; 'B','T' -> position is board x
TAB_CANDIDATES = {
    "P": {"L": [20, 58, 12, 66], "R": [12, 60, 8, 16], "B": [14, 41, 20, 35], "T": [14, 41, 20, 35]},
    "W": {"B": [15, 10, 20], "T": [15, 10, 20], "R": [15, 10, 20]},
}
TABS_PER_EDGE = {"P": {"L": 2, "R": 2, "B": 2, "T": 2}, "W": {"B": 1, "T": 1, "R": 1}}
SIZE = {"P": (55.0, 78.45), "W": (30.0, 30.0)}
OFFS = {"P": P_OFF, "W": W_OFF}


def load_cpl(path):
    pts = []
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            pts.append((r["Designator"], float(r["Mid X"].rstrip("m")), float(r["Mid Y"].rstrip("m")), r["Layer"]))
    return pts


CPL = {"P": load_cpl(P_CPL), "W": load_cpl(W_CPL)}


def tab_geom(b, edge, pos):
    """Return (tab rectangle across the gap, edge point, unit vector along edge) in panel coords."""
    (ox, oy), (w, h) = OFFS[b], SIZE[b]
    hw = TAB_W / 2
    if edge in "LR":
        x = ox if edge == "L" else ox + w
        y = oy + pos
        xa, xb = (x - GAP - 0.05, x + 0.05) if edge == "L" else (x - 0.05, x + GAP + 0.05)
        return box(xa, y - hw, xb, y + hw), (x, y), (0.0, 1.0)
    y = oy if edge == "B" else oy + h
    x = ox + pos
    ya, yb = (y - GAP - 0.05, y + 0.05) if edge == "B" else (y - 0.05, y + GAP + 0.05)
    return box(x - hw, ya, x + hw, yb), (x, y), (1.0, 0.0)


tabs, report = [], []
for b, edges in TAB_CANDIDATES.items():
    for edge, cands in edges.items():
        chosen = 0
        for pos in cands:
            if chosen >= TABS_PER_EDGE[b][edge]:
                break
            rect, (ex, ey), _ = tab_geom(b, edge, pos)
            # local edge point for clearance test against CPL (board coords)
            lx, ly = ex - OFFS[b][0], ey - OFFS[b][1]
            near = [(d, round(math.hypot(x - lx, y - ly), 2)) for d, x, y, _ in CPL[b] if math.hypot(x - lx, y - ly) < 3.0]
            if near:
                report.append(f"skip {b}-{edge}@{pos}: parts within 3 mm {near}")
                continue
            if any(rect.distance(t[0]) < 4.0 for t in tabs):
                continue
            tabs.append((rect, (ex, ey), tab_geom(b, edge, pos)[2], f"{b}-{edge}@{pos}"))
            chosen += 1
        if chosen < TABS_PER_EDGE[b][edge]:
            report.append(f"WARN {b}-{edge}: only {chosen} tab(s) placed")

# ---- milled slots ---------------------------------------------------------------------------------
rings = unary_union([phone.buffer(GAP, quad_segs=32), wear.buffer(GAP, quad_segs=32)]).difference(boards)
slots = rings.difference(unary_union([t[0] for t in tabs]))
slot_polys = list(slots.geoms) if hasattr(slots, "geoms") else [slots]
slot_polys = [s for s in slot_polys if s.area > 0.05]
assert all(len(s.interiors) == 0 for s in slot_polys), "a slot still encircles a board (missing tab)"
panel_rect = box(0, 0, PW, PH)
assert slots.within(panel_rect.buffer(1e-6)), "slots leave the panel"

# ---- merge copper / mask / silk / paste -------------------------------------------------------
fid_cu, fid_mask = CircleAperture(1.0, unit=MM), CircleAperture(2.0, unit=MM)
for ext, (wf, pf) in LAYERS.items():
    g = GerberFile.open(P_DIR / pf)
    g.offset(px, py, MM)
    w = GerberFile.open(W_DIR / wf)
    w.offset(wx, wy, MM)
    g.merge(w)
    if ext in ("GTL", "GBL"):
        for fx, fy in FIDS:
            g.objects.append(Flash(fx, fy, fid_cu, unit=MM))
    if ext in ("GTS", "GBS"):
        for fx, fy in FIDS:
            g.objects.append(Flash(fx, fy, fid_mask, unit=MM))
    g.save(OUT / f"panel.{ext}")
    print(f"panel.{ext}: {len(g.objects)} objects")

# ---- outline (profile) -----------------------------------------------------------------------------
edge_ap = CircleAperture(0.05, unit=MM)
outline = GerberFile.open(P_DIR / (P + "Edge_Cuts.gm1"))  # reuse header/settings, replace content
outline.objects.clear()


def add_ring(coords):
    c = list(coords)
    for (x1, y1), (x2, y2) in zip(c, c[1:]):
        outline.objects.append(Line(x1, y1, x2, y2, aperture=edge_ap, unit=MM))


add_ring(panel_rect.exterior.coords)
for s in slot_polys:
    add_ring(s.exterior.coords)
outline.save(OUT / "panel.GKO")

# ---- drills -------------------------------------------------------------------------------------------
import dataclasses


def set_plating(exc, plated):
    cache = {}
    for o in exc.objects:
        ap = o.aperture
        if id(ap) not in cache:
            cache[id(ap)] = dataclasses.replace(ap, plated=plated)
        o.aperture = cache[id(ap)]


pth =ExcellonFile.open(P_DIR / (P + "PTH.drl"))
pth.offset(px, py, MM)
wp = ExcellonFile.open(W_DIR / "PCB1-Plated.TXT")
wp.offset(wx, wy, MM)
pth.merge(wp)
set_plating(pth, True)
pth.save(OUT / "panel-PTH.drl")

npth = ExcellonFile.open(P_DIR / (P + "NPTH.drl"))
npth.offset(px, py, MM)
wn = ExcellonFile.open(W_DIR / "PCB1-NonPlated.TXT")
wn.offset(wx, wy, MM)
npth.merge(wn)
bite = ExcellonTool(BITE_D, plated=False, unit=MM)
nb = 0
for rect, (ex, ey), (ux, uy), name in tabs:
    n = int(TAB_W // BITE_PITCH) + 1  # 4 holes at 0.8 mm span 2.9 mm of the 3 mm tab
    for k in range(n):
        t = (k - (n - 1) / 2) * BITE_PITCH
        npth.objects.append(Flash(ex + ux * t, ey + uy * t, bite, unit=MM))
        nb += 1
set_plating(npth, False)
npth.save(OUT / "panel-NPTH.drl")

print(f"tabs ({len(tabs)}):", ", ".join(t[3] for t in tabs))
print(f"slots: {len(slot_polys)} polygons, mouse-bite holes: {nb}")
print("\n".join(report))

# parts close to a board edge (possible overhang / break stress)
for b, shape in (("P", phone), ("W", wear)):
    ox, oy = OFFS[b]
    close = [(d, round(shape.exterior.distance(Point(x + ox, y + oy)), 2)) for d, x, y, _ in CPL[b]
             if shape.exterior.distance(Point(x + ox, y + oy)) < 1.2]
    print(f"{b} parts with centroid < 1.2 mm from edge: {close}")
