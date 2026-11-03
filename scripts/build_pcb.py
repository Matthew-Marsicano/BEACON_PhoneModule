"""Build BEACON_PhoneModule.kicad_pcb for the MagSafe enclosure (beacon_phone_magsafe_2p5mm_Latest.scad):
outline + TX-jack notch, M2 holes and keepouts, footprints with nets, RF chains, greedy placement, RF traces.

Board coordinates in the enclosure file have the origin at the lower-left corner with the USB-C edge at the
bottom (y up).  KiCad uses y down, so here X = x_board and Y = BH - y_board (origin at the top-left corner).

Run:  D:/KiCAD/bin/python.exe -I scripts/build_pcb.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew  # noqa: E402
from pcbnew import FromMM, ToMM, VECTOR2I  # noqa: E402
import design  # noqa: E402
import fpinfo  # noqa: E402
import kigen  # noqa: E402

PRJ = design.OUT
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
OX, OY = 100.0, 100.0          # board top-left corner on the KiCad sheet (mm)
BW, BH = 55.0, 78.45           # board size from the enclosure (pcb_W x pcb_L)
CORNER_R = 3.0
HOLES_B = [(3.5, 3.5), (51.5, 3.5), (3.5, 74.95), (51.5, 74.95)]   # board coords (y up)
STANDOFF_KEEPOUT = 6.2         # 6 mm standoff/screw-head pad, both sides
TX_Y_B = 66.0                  # SMA jack centre along the right edge (board y)
TX_NOTCH, TX_NW = 1.5, 3.55    # notch depth into the right edge and half-width
RING_C_B = (27.5, 50.95)       # MagSafe ring centre (board coords)
PATCH_C_B = (27.5, 39.225)     # RX patch centre (board centre)
RF_W = 0.335                   # 50 ohm CPWG L1/L2, JLC calculator: 13.17 mil width / 8.0 mil gap (no mask), 7628 prepreg
RF_GAP = 0.203
EDGE = 0.4

D = design.d
PARTS = {p.ref: p for p in D.all_parts() if not p.ref.startswith('#')}


def K(xb, yb):
    """Board coords (y up) -> KiCad-relative coords (y down)."""
    return xb, BH - yb


def P(x, y):
    return VECTOR2I(FromMM(OX + x), FromMM(OY + y))


def xy(v):
    return ToMM(v.x) - OX, ToMM(v.y) - OY


def find(lib_id=None, value=None, nets=None, sheet=None):
    out = []
    for p in PARTS.values():
        if lib_id and p.lib_id != lib_id:
            continue
        if value and p.value != value:
            continue
        if sheet and p.sheet.name != sheet:
            continue
        if nets and set(nets) != {n for n in p.nets.values() if n}:
            continue
        out.append(p)
    return out


def one(**k):
    r = find(**k)
    assert len(r) == 1, (k, [p.ref for p in r])
    return r[0]


# ------------------------------------------------------------------ board setup
board = pcbnew.NewBoard(PCB)
board.SetCopperLayerCount(4)
board.GetDesignSettings().SetBoardThickness(FromMM(1.6))
board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)       # L2 = solid GND reference plane, never routed
board.SetLayerName(pcbnew.In1_Cu, 'In1.Cu')
nets = {}
GLOBAL = D.global_nets()
FULL = {}
for _p in PARTS.values():
    for _n in _p.nets.values():
        if _n:
            FULL.setdefault(_n, set()).add(_n if _n in GLOBAL else '/%s/%s' % (_p.sheet.name, _n))
assert all(len(v) == 1 for v in FULL.values()), [k for k, v in FULL.items() if len(v) > 1]
FULL = {k: next(iter(v)) for k, v in FULL.items()}


def base(n):
    return n.rsplit('/', 1)[-1]


def net(name):
    name = FULL.get(name, name)
    if name not in nets:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        nets[name] = ni
    return nets[name]


for p in PARTS.values():
    for n in p.nets.values():
        if n:
            net(n)


# ------------------------------------------------------------------ outline: rounded rectangle + TX notch
def seg(x1, y1, x2, y2, layer=pcbnew.Edge_Cuts, w=0.1):
    s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2)); s.SetLayer(layer); s.SetWidth(FromMM(w))
    board.Add(s)


def arc(cx, cy, r, a0):
    """Quarter arc centred (cx, cy) starting at angle a0 (deg, y down) sweeping +90."""
    s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)
    pt = lambda a: P(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    s.SetArcGeometry(pt(a0), pt(a0 + 45), pt(a0 + 90))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.1))
    board.Add(s)


R = CORNER_R
ny0, ny1 = BH - (TX_Y_B + TX_NW), BH - (TX_Y_B - TX_NW)   # notch span in KiCad Y
seg(R, 0, BW - R, 0)
arc(BW - R, R, R, 270)
seg(BW, R, BW, ny0)
seg(BW, ny0, BW - TX_NOTCH, ny0)
seg(BW - TX_NOTCH, ny0, BW - TX_NOTCH, ny1)
seg(BW - TX_NOTCH, ny1, BW, ny1)
seg(BW, ny1, BW, BH - R)
arc(BW - R, BH - R, R, 0)
seg(BW - R, BH, R, BH)
arc(R, BH - R, R, 90)
seg(0, BH - R, 0, R)
arc(R, R, R, 180)

# ------------------------------------------------------------------ footprints
FPS = {}


def make_fp(p):
    nick, name = p.fp.split(':', 1)
    fp = fpinfo.load(p.fp)
    fp.SetFPID(pcbnew.LIB_ID(nick, name))
    fp.SetReference(p.ref)
    fp.SetValue(p.value)
    fp.SetPath(pcbnew.KIID_PATH('/' + p.sheet.uuid + '/' + kigen.uid('sym', p.ref)))
    fp.SetSheetname(p.sheet.name)
    fp.SetSheetfile(p.sheet.filename)
    if p.dnp:
        fp.SetDNP(True)
    fp.SetExcludedFromBOM(not p.in_bom)
    for k, v in p.props.items():
        fp.SetField(k, v)
    pin_names = {q['num']: q['name'] for q in D.lib.pins(p.lib_id)}
    for pad in fp.Pads():
        num = pad.GetNumber()
        n = p.nets.get(num)
        if n:
            pad.SetNet(net(n))
        elif num in pin_names:
            pad.SetNet(net('unconnected-(%s-%s-Pad%s)' % (p.ref, pin_names[num].replace('/', '{slash}'), num)))
    board.Add(fp)
    FPS[p.ref] = fp
    return fp


for p in PARTS.values():
    if p.fp:
        make_fp(p)

_nrf = FPS[one(lib_id='MCU_Nordic:nRF52840').ref]
for g in list(_nrf.GraphicalItems()):
    if g.GetLayer() == pcbnew.F_CrtYd:
        _nrf.Remove(g)
_cy = pcbnew.PCB_SHAPE(_nrf, pcbnew.SHAPE_T_RECT)
_cy.SetStart(P(-OX - 3.75, -OY - 3.75)); _cy.SetEnd(P(-OX + 3.75, -OY + 3.75))
_cy.SetLayer(pcbnew.F_CrtYd); _cy.SetWidth(FromMM(0.05)); _nrf.Add(_cy)

PLACED = set()


def pad_of(ref, num):
    return next(pd for pd in FPS[ref].Pads() if pd.GetNumber() == str(num))


def pad_on_net(ref, netname):
    return [pd for pd in FPS[ref].Pads() if base(pd.GetNetname()) == base(netname)]


def place(ref, x, y, rot=0, bottom=False):
    fp = FPS[ref]
    fp.SetOrientationDegrees(rot)
    fp.SetPosition(P(x, y))
    if bottom and not fp.IsFlipped():
        fp.Flip(P(x, y), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    PLACED.add(ref)


def place_pad_at(ref, padnum, x, y, rot=0):
    fp = FPS[ref]
    fp.SetOrientationDegrees(rot)
    fp.SetPosition(P(0, 0))
    px, py = xy(pad_of(ref, padnum).GetPosition())
    fp.SetPosition(P(x - px, y - py))
    PLACED.add(ref)


# ------------------------------------------------------------------ anchors
U_NRF = one(lib_id='MCU_Nordic:nRF52840').ref
U_LMX = one(lib_id='BEACON:LMX2582').ref
U_PA = one(lib_id='BEACON:CC2595').ref
U_LNA = one(lib_id='BEACON:QPL9547').ref
U_REG = one(lib_id='BEACON:LT80602').ref
INA5, INA3 = [p.ref for p in find(lib_id='Sensor_Energy:INA219AxDCN')]
U_ESD = one(lib_id='Power_Protection:USBLC6-2SC6').ref
J_USB = one(lib_id='Connector:USB_C_Receptacle_USB2.0_16P').ref
L_BUCK = one(value='5.6uH').ref
FL_BPF = one(lib_id='BEACON:DEA202450BT-1294D1-H').ref
FL_LPF = one(lib_id='BEACON:2450LP07C0100001T').ref
J_TX = one(value='TX antenna U.FL').ref
AE_RX = one(lib_id='BEACON:Taoglas_WDP2458').ref
J_SWD = one(lib_id='Connector:Conn_ARM_SWD_TagConnect_TC2030-NL').ref
HOLES = [p.ref for p in find(lib_id='Mechanical:MountingHole')]

for ref, (xb, yb) in zip(HOLES, HOLES_B):
    place(ref, *K(xb, yb))
place(AE_RX, *K(*PATCH_C_B), 0)
place(J_USB, BW / 2, BH - 3.675, 0)                       # receptacle front face flush with the bottom edge
place_pad_at(J_TX, '1', 49.0, BH - TX_Y_B, 0)            # U.FL signal pad at the TX line, body inside the notch edge
place(U_LMX, 22.6, BH - TX_Y_B - 1.25, 0)                # OUTAP (pin 23) on the TX line
place(U_REG, 10.0, 62.0, 0)
place(L_BUCK, 10.0, 69.5, 0)
place(INA5, 17.0, 72.5, 0)
place(INA3, 8.5, 52.0, 0)
place(U_ESD, 35.0, 72.5, 0)
place(J_SWD, 46.0, 50.0, 0, bottom=True)

# ------------------------------------------------------------------ RF chains (any direction)
RF_SEGMENTS = []   # (x1, y1, x2, y2, net[, width[, layer]])
CHAIN_REFS = set()
CHAIN_NETS = {'RX_ATT', 'SYN_OUTAP', 'CW_RF', 'PA_IN', 'PA_OUT', 'PA_MATCH', 'TX_LPF', 'TX_ANT', 'NRF_ANT',
              'RX_RF', 'LNA_OUT', 'LNA_IN', 'RX_BPF', 'RX_ANT', 'RX_PATCH'}


def extent(pad, d):
    bb = pad.GetBoundingBox()
    return (ToMM(bb.GetWidth()) * abs(d[0]) + ToMM(bb.GetHeight()) * abs(d[1])) / 2


def best_rot(ref, pa, pb, want):
    """Rotation putting the vector pad pa -> pad pb as close as possible to direction `want`."""
    fp = FPS[ref]
    best = None
    for r in (0, 90, 180, 270):
        fp.SetOrientationDegrees(r)
        fp.SetPosition(P(0, 0))
        ax, ay = xy(pad_of(ref, pa).GetPosition())
        bx, by = xy(pad_of(ref, pb).GetPosition())
        score = (bx - ax) * want[0] + (by - ay) * want[1]
        if best is None or score > best[0]:
            best = (score, r)
    return best[1]


def chain(x, y, d, steps, net0):
    """Straight RF chain from (x, y) heading unit direction d (KiCad coords).
    ('s', ref, pad_in, pad_out[, rot]) series part (rot auto for 2-pad parts),
    ('n', [(ref, side)], gap) node gap with shunts (side +1/-1 = right/left of travel),
    ('g', gap) plain line.  Returns end point and the net there."""
    cur, cur_net = (x, y), net0
    perp = (-d[1], d[0])
    for st in steps:
        if st[0] == 'g':
            nxt = (cur[0] + d[0] * st[1], cur[1] + d[1] * st[1])
            RF_SEGMENTS.append((cur[0], cur[1], nxt[0], nxt[1], cur_net))
            cur = nxt
        elif st[0] == 'n':
            shunts, gap = st[1], st[2]
            nxt = (cur[0] + d[0] * gap, cur[1] + d[1] * gap)
            mid = ((cur[0] + nxt[0]) / 2, (cur[1] + nxt[1]) / 2)
            for i, (ref, side) in enumerate(shunts):
                node = next(pd.GetNumber() for pd in FPS[ref].Pads() if base(pd.GetNetname()) in CHAIN_NETS)
                other = next(pd.GetNumber() for pd in FPS[ref].Pads() if pd.GetNumber() != node)
                want = (perp[0] * side, perp[1] * side)
                rot = best_rot(ref, node, other, want)
                o = (i - (len(shunts) - 1) / 2) * 1.1
                place_pad_at(ref, node, mid[0] + d[0] * o, mid[1] + d[1] * o, rot)
                CHAIN_REFS.add(ref)
            RF_SEGMENTS.append((cur[0], cur[1], nxt[0], nxt[1], cur_net))
            cur = nxt
        else:
            ref, pin, pout = st[1], st[2], st[3]
            rot = st[4] if len(st) > 4 else best_rot(ref, pin, pout, d)
            fp = FPS[ref]
            fp.SetOrientationDegrees(rot)
            fp.SetPosition(P(0, 0))
            ix, iy = xy(pad_of(ref, pin).GetPosition())
            h = extent(pad_of(ref, pin), d)
            fp.SetPosition(P(cur[0] + d[0] * h - ix, cur[1] + d[1] * h - iy))
            PLACED.add(ref)
            CHAIN_REFS.add(ref)
            ix, iy = xy(pad_of(ref, pin).GetPosition())
            ox, oy = xy(pad_of(ref, pout).GetPosition())
            RF_SEGMENTS.append((cur[0], cur[1], ix, iy, base(pad_of(ref, pin).GetNetname())))
            cur_net = base(pad_of(ref, pout).GetNetname())
            ho = extent(pad_of(ref, pout), d)
            cur = (ox + d[0] * ho, oy + d[1] * ho)
    return cur, cur_net


def S(nin, nout):
    ref = one(nets={nin, nout}).ref
    pads = {pd.GetNumber(): base(pd.GetNetname()) for pd in FPS[ref].Pads()}
    pin = next(k for k, v in pads.items() if v == nin)
    pout = next(k for k in pads if k != pin)
    return ('s', ref, pin, pout)


def shunt(nets_, **k):
    return one(nets=set(nets_), **k).ref


RIGHT, LEFT, DOWN, UP = (1, 0), (-1, 0), (0, 1), (0, -1)

# --- TX (heading +x along board y = 66): LMX OUTAP -> 100p -> pi pad -> CC2595 -> 1.2n -> 22p -> LPF -> SMA
ox_, oy_ = xy(pad_of(U_LMX, 23).GetPosition())
ox_ += extent(pad_of(U_LMX, 23), RIGHT)
end, _ = chain(ox_, oy_, RIGHT, [
    ('n', [(shunt({'VCC_SYN', 'SYN_OUTAP'}), -1)], 1.7),
    S('SYN_OUTAP', 'CW_RF'),
    ('n', [(shunt({'CW_RF', 'GND'}), 1)], 1.4),
    S('CW_RF', 'PA_IN'),
    ('n', [(shunt({'PA_IN', 'GND'}), 1)], 1.7),
    ('s', U_PA, '2', '10', 0),
    ('n', [(shunt({'VDD_PA', 'PA_OUT'}), -1)], 2.0),
    S('PA_OUT', 'PA_MATCH'),
    ('n', [(shunt({'PA_MATCH', 'GND'}), 1)], 1.4),
    S('PA_MATCH', 'TX_LPF'),
    ('g', 0.5),
    ('s', FL_LPF, '2', '4', 180),
    ('n', [(shunt({'TX_ANT', 'GND'}, lib_id='Device:L'), 1)], 1.6),
], 'SYN_OUTAP')
jx, jy = xy(pad_of(J_TX, 1).GetPosition())
RF_SEGMENTS.append((end[0], end[1], jx, jy, 'TX_ANT'))
print('TX chain reaches x=%.2f, SMA centre pin at x=%.2f' % (end[0], jx))
p10, p12 = xy(pad_of(U_PA, 10).GetPosition()), xy(pad_of(U_PA, 12).GetPosition())
jog = p10[0] + extent(pad_of(U_PA, 10), RIGHT) + 0.36
RF_SEGMENTS.append((p12[0], p12[1], jog, p12[1], 'PA_OUT', 0.2))
RF_SEGMENTS.append((jog, p12[1], jog, p10[1], 'PA_OUT', 0.3))

# --- RX part 1 (heading down from the patch feed): B.Cu feed -> RF via -> pi match -> ESD -> BPF -> LNA
fx, fy = xy(pad_of(AE_RX, 1).GetPosition())
patch_bottom = BH - PATCH_C_B[1] + 12.7 + 1.3
RF_SEGMENTS.append((fx, fy, fx, patch_bottom, 'RX_PATCH', RF_W, pcbnew.B_Cu))
RF_VIA = (fx, patch_bottom)
end_a, net_a = chain(fx, patch_bottom, DOWN, [
    ('n', [(shunt({'RX_PATCH', 'GND'}, lib_id='Device:C'), -1)], 1.4),
    S('RX_PATCH', 'RX_ANT'),
    ('n', [(shunt({'RX_ANT', 'GND'}, lib_id='Device:L'), 1)], 2.1),
    ('s', FL_BPF, '1', '4'),
    ('g', 0.9),
    S('RX_BPF', 'LNA_IN'),
    ('g', 0.5),
    ('s', U_LNA, '2', '7', 270),
    ('n', [(shunt({'LNA_VCC', 'LNA_OUT'}), 1)], 1.9),
], 'RX_PATCH')
# --- RX part 2 (heading -x from the nRF ANT ball toward the corner below the LNA)
# place the nRF (rot 180: ANT ball faces -x) so its escape channel lines up just below the LNA chain end
place(U_NRF, 46.0, end_a[1] + 0.4 - 1.25, 180)
ax, ay = xy(pad_of(U_NRF, 'H23').GetPosition())
neck_y = ay + 0.25                                    # rot 180: the E24/J24 channel sits below H23
start_x = ax - 0.85
RF_SEGMENTS.append((ax, ay, ax - 0.30, neck_y, 'NRF_ANT', 0.2))
RF_SEGMENTS.append((ax - 0.30, neck_y, start_x, neck_y, 'NRF_ANT', 0.2))
end_b, net_b = chain(start_x, neck_y, LEFT, [
    ('n', [(shunt({'NRF_ANT', 'GND'}), 1)], 1.4),
    S('NRF_ANT', 'RX_RF'),
    ('n', [(shunt({'RX_RF', 'GND'}, value='0.5pF'), 1)], 1.4),
    ('g', 1.9),
    ('n', [(shunt({'RX_RF', 'GND'}, value='DNP'), 1)], 1.4),
    S('RX_RF', 'RX_ATT'),
    ('n', [(shunt({'RX_ATT', 'GND'}), 1)], 1.4),
    S('RX_ATT', 'LNA_OUT'),
], 'NRF_ANT')
assert net_a == net_b == 'LNA_OUT', (net_a, net_b)
# join the two halves with an L on LNA_OUT
if end_b[0] > end_a[0] + 0.01:
    RF_SEGMENTS.append((end_b[0], end_b[1], end_a[0], end_b[1], 'LNA_OUT'))
RF_SEGMENTS.append((end_a[0], end_b[1], end_a[0], end_a[1], 'LNA_OUT'))
print('RX: LNA chain ends y=%.2f, nRF chain ends x=%.2f y=%.2f (corner at x=%.2f)' %
      (end_a[1], end_b[0], end_b[1], end_a[0]))

# ------------------------------------------------------------------ reviewed placement overrides
import json  # noqa: E402
_ov = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'placement_overrides.json')))['moves']
_n_ov = 0
for ref, (ox, oy, orot) in _ov.items():
    if ref in FPS and ref not in CHAIN_REFS:
        FPS[ref].SetOrientationDegrees(orot)
        FPS[ref].SetPosition(P(ox, oy))
        PLACED.add(ref)
        _n_ov += 1
print('placement overrides applied: %d (chain parts skipped: %s)' % (_n_ov, sorted(set(_ov) & CHAIN_REFS)))

# ------------------------------------------------------------------ greedy placement of everything else
REGIONS = {  # x0, y0, x1, y1 allowed per sheet (top side, KiCad coords)
    'USB': (14.0, 58.0, 41.0, 78.0), 'Power': (0.5, 44.0, 24.0, 78.0), 'MCU': (32.0, 44.0, 54.5, 78.0),
    'CW_Synth': (2.0, 0.5, 40.0, 25.5), 'TX_PA': (30.0, 0.5, 54.5, 25.5), 'RX_Frontend': (14.0, 50.0, 42.0, 72.0),
}
BOTTOM_REFS = {p.ref for p in PARTS.values() if p.lib_id == 'Connector:TestPoint'} | {J_SWD}


def bbox_mm(fp, margin=0.12):
    lay = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    cy = fp.GetCourtyard(lay)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
    return (ToMM(bb.GetLeft()) - OX - margin, ToMM(bb.GetTop()) - OY - margin,
            ToMM(bb.GetRight()) - OX + margin, ToMM(bb.GetBottom()) - OY + margin)


OCC = {'top': [], 'bot': []}
for ref in PLACED:
    fp = FPS[ref]
    b = bbox_mm(fp)
    side = 'bot' if fp.IsFlipped() else 'top'
    OCC[side].append(b)
    if any(pd.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) for pd in fp.Pads()):
        OCC['bot' if side == 'top' else 'top'].append(b)
for (hx, hy) in [K(*h) for h in HOLES_B]:
    r = STANDOFF_KEEPOUT / 2
    for side in ('top', 'bot'):
        OCC[side].append((hx - r, hy - r, hx + r, hy + r))
# nRF52840 via-in-pad exits on B.Cu: no bottom-side parts under it
_u5 = bbox_mm(FPS[U_NRF], 0.8)
OCC['bot'].append(_u5)
# the patch pin protrudes below the board: keep bottom parts off it
OCC['bot'].append((fx - 2, fy - 2, fx + 2, fy + 2))
for (x1, y1, x2, y2, _n, *rest) in RF_SEGMENTS:
    w = RF_W / 2 + RF_GAP + 0.25
    side = 'bot' if rest and len(rest) > 1 and rest[1] == pcbnew.B_Cu else 'top'
    OCC[side].append((min(x1, x2) - w, min(y1, y2) - w, max(x1, x2) + w, max(y1, y2) + w))
OCC['top'].append((RF_VIA[0] - 1.0, RF_VIA[1] - 1.0, RF_VIA[0] + 1.0, RF_VIA[1] + 1.0))


def overlaps(b, side):
    return any(b[0] < o[2] and b[2] > o[0] and b[1] < o[3] and b[3] > o[1] for o in OCC[side])


# clocking-bar field zone (docs/magnetics_thermal.md rule 1): board x 13.7-41.3, y 0-30.5
MAG_ZONE = (13.7, BH - 30.5, 41.3, BH)
MAG_SENSITIVE = {p.ref for p in PARTS.values() if p.value in ('5.6uH', '10uH', '32MHz', '26MHz')}


def inside(b, region):
    ok = (b[0] >= max(region[0], EDGE) and b[1] >= max(region[1], EDGE) and
          b[2] <= min(region[2], BW - EDGE) and b[3] <= min(region[3], BH - EDGE))
    if ok and b[2] > BW - TX_NOTCH - EDGE and b[3] > ny0 and b[1] < ny1:
        ok = False                                         # stay out of the TX notch
    return ok


def target_for(p):
    note = p.props.get('Note', '')
    if 'Kelvin' in note:
        for sh in [q.ref for q in PARTS.values() if q.value == '50m']:
            for pd in FPS[sh].Pads():
                if base(pd.GetNetname()) in p.nets.values():
                    return (0, xy(pd.GetPosition()), base(pd.GetNetname()))
    best = None
    for n in sorted({v for v in p.nets.values() if v and v != 'GND'}):
        cands = [(ref, pd) for ref in PLACED if ref != p.ref for pd in pad_on_net(ref, n)]
        if not cands:
            continue
        named = [c for c in cands if c[1].GetNumber() in note.replace(',', ' ').split()]
        pick = named or cands
        pick.sort(key=lambda c: -len(FPS[c[0]].Pads()))
        weight = len(pick)
        if best is None or weight < best[0] or named:
            best = (weight, xy(pick[0][1].GetPosition()), n)
            if named:
                break
    return best


_grow = {}


def try_place(p, bottom=False):
    fp = FPS[p.ref]
    side = 'bot' if bottom else 'top'
    t = target_for(p)
    region = (0, 0, BW, BH) if bottom else REGIONS.get(p.sheet.name, (0, 0, BW, BH))
    if p.ref in _grow:
        region = _grow[p.ref]
    if t is None:
        tx, ty, tnet = (region[0] + region[2]) / 2, (region[1] + region[3]) / 2, None
    else:
        _, (tx, ty), tnet = t
    best = None
    for radius in [r * 0.35 for r in range(0, 90)]:
        n_ang = max(1, int(2 * math.pi * radius / 0.35))
        for k in range(n_ang):
            a = 2 * math.pi * k / n_ang
            cx, cy = tx + radius * math.cos(a), ty + radius * math.sin(a)
            for rot in (0, 90, 180, 270):
                fp.SetOrientationDegrees(rot)
                fp.SetPosition(P(0, 0))
                if bottom and not fp.IsFlipped():
                    fp.Flip(P(0, 0), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
                off = (0, 0)
                if tnet:
                    pds = pad_on_net(p.ref, tnet)
                    if pds:
                        off = xy(pds[0].GetPosition())
                fp.SetPosition(P(cx - off[0], cy - off[1]))
                b = bbox_mm(fp)
                in_mag = (p.ref in MAG_SENSITIVE and b[0] < MAG_ZONE[2] and b[2] > MAG_ZONE[0]
                          and b[1] < MAG_ZONE[3] and b[3] > MAG_ZONE[1])
                if inside(b, region) and not overlaps(b, side) and not in_mag:
                    d = math.hypot(cx - tx, cy - ty) + (0.01 if rot else 0)
                    if best is None or d < best[0]:
                        best = (d, rot, xy(fp.GetPosition()))
            if best:
                break
        if best:
            break
    if best is None:
        if p.ref not in _grow or _grow[p.ref] != (0, 0, BW, BH):
            r0 = region
            _grow[p.ref] = (0, 0, BW, BH) if p.ref in _grow else (r0[0] - 6, r0[1] - 6, r0[2] + 6, r0[3] + 6)
            return try_place(p, bottom)
        print('!! could not place', p.ref, p.value, 'in', p.sheet.name)
        return False
    _, rot, (x, y) = best
    fp.SetOrientationDegrees(rot)
    fp.SetPosition(P(x, y))
    OCC[side].append(bbox_mm(fp))
    PLACED.add(p.ref)
    return True


def prio(p):
    order = {'Power': 0, 'USB': 1, 'CW_Synth': 2, 'TX_PA': 3, 'RX_Frontend': 4, 'MCU': 5}
    small = 0 if p.value.endswith('pF') else 1 if p.value.endswith('nF') else 2
    return (order.get(p.sheet.name, 9), small)


todo = sorted([p for p in PARTS.values() if p.fp and p.ref not in PLACED], key=prio)
for p in todo:
    try_place(p, bottom=p.ref in BOTTOM_REFS)

# ------------------------------------------------------------------ RF tracks and the patch-feed via
for (x1, y1, x2, y2, n, *rest) in RF_SEGMENTS:
    if abs(x1 - x2) < 1e-3 and abs(y1 - y2) < 1e-3:
        continue
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2))
    t.SetWidth(FromMM(rest[0] if rest else RF_W))
    t.SetLayer(rest[1] if len(rest) > 1 else pcbnew.F_Cu)
    t.SetNet(net(n))
    t.SetLocked(True)
    board.Add(t)


def via(x, y, n, d=0.45, h=0.2):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(P(x, y)); v.SetWidth(FromMM(d)); v.SetDrill(FromMM(h))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(net(n)); v.SetLocked(True)
    board.Add(v)


via(RF_VIA[0], RF_VIA[1], 'RX_PATCH', 0.5, 0.25)

# INA219 Kelvin sense: a short fixed track from the shunt pad to the adjacent sense resistor (only if it is
# short and crosses no other copper; otherwise the router connects it and the review note applies)
def _clear_path(a, b, netname):
    ax, ay = xy(a); bx, by = xy(b)
    for fp in board.GetFootprints():
        for pd in fp.Pads():
            if pd.GetNetname() == netname:
                continue
            px, py = xy(pd.GetPosition())
            L2 = (bx - ax) ** 2 + (by - ay) ** 2 or 1e-9
            t = max(0, min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / L2))
            r = max(ToMM(pd.GetBoundingBox().GetWidth()), ToMM(pd.GetBoundingBox().GetHeight())) / 2 + 0.3
            if math.hypot(px - ax - t * (bx - ax), py - ay - t * (by - ay)) < r:
                return False
    return True


for shunt_ref in [p.ref for p in PARTS.values() if p.value == '50m']:
    for spad in FPS[shunt_ref].Pads():
        n = base(spad.GetNetname())
        for sref in [p.ref for p in PARTS.values() if 'Kelvin' in p.props.get('Note', '') and n in p.nets.values()]:
            sp = next(pd for pd in FPS[sref].Pads() if base(pd.GetNetname()) == n)
            L = ToMM((spad.GetPosition() - sp.GetPosition()).EuclideanNorm())
            if L < 3.0 and _clear_path(spad.GetPosition(), sp.GetPosition(), spad.GetNetname()):
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(spad.GetPosition()); t.SetEnd(sp.GetPosition()); t.SetWidth(FromMM(0.2))
                t.SetLayer(pcbnew.F_Cu); t.SetNet(spad.GetNet()); t.SetLocked(True); board.Add(t)
                print('Kelvin sense track %s.%s -> %s (%.1f mm)' % (shunt_ref, spad.GetNumber(), sref, L))
            else:
                print('Kelvin sense %s.%s -> %s left to the router (%.1f mm)' % (shunt_ref, spad.GetNumber(), sref, L))

# GND vias at the LTCC filter ground lands (docs/layout_review.md, verified clear)
for (vx, vy) in ((28.65, 57.95), (28.65, 59.62), (29.95, 57.95), (29.95, 59.62), (45.385, 12.05), (45.385, 13.85)):
    via(vx, vy, 'GND')

# standoff keepouts (no copper / parts within the M2 screw head and standoff on either side)
for (hx, hy) in [K(*h) for h in HOLES_B]:
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False); z.SetDoNotAllowZoneFills(True)
    z.SetLayerSet(pcbnew.LSET.AllCuMask())
    ol = z.Outline(); ol.NewOutline()
    for k in range(24):
        a = 2 * math.pi * k / 24
        ol.Append(FromMM(OX + hx + 3.1 * math.cos(a)), FromMM(OY + hy + 3.1 * math.sin(a)))
    board.Add(z)

# enclosure reference drawing: ring + clocking magnet on User.1, patch radome on User.2
for rr in (23.0, 27.2):
    c = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_CIRCLE)
    c.SetCenter(P(*K(*RING_C_B))); c.SetEnd(P(K(*RING_C_B)[0] + rr, K(*RING_C_B)[1]))
    c.SetLayer(pcbnew.User_1); c.SetWidth(FromMM(0.1)); board.Add(c)
cx0, cx1 = RING_C_B[0] - 3.15, RING_C_B[0] + 3.15
cy0, cy1 = K(0, RING_C_B[1] - 31.05)[1], K(0, RING_C_B[1] - 50.65)[1]
for a in ((cx0, cy0, cx1, cy0), (cx1, cy0, cx1, cy1), (cx1, cy1, cx0, cy1), (cx0, cy1, cx0, cy0)):
    seg(*a, layer=pcbnew.User_1)

pcbnew.SaveBoard(PCB, board)
print('placed %d/%d footprints, %d RF segments -> %s' % (len(PLACED), len(FPS), len(RF_SEGMENTS), PCB))
