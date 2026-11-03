"""Pre-route (fanout, planes, net classes), autoroute with Freerouting, post-route (stitching, pours, fill).

Run:  D:/KiCAD/bin/python.exe -I scripts/route.py [--passes N]
"""
import json
import re
import math
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew  # noqa: E402
from pcbnew import FromMM, ToMM, VECTOR2I  # noqa: E402

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
PRO = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pro')
WORK = os.path.join(PRJ, 'route')
JAVA = r'C:\Program Files\Eclipse Adoptium\jre-25.0.5.8-hotspot\bin\java.exe'
JAR = os.path.join(os.environ.get('USERPROFILE', r'C:\Users\marsi'), '.kicad-mcp', 'freerouting.jar')
OX, OY, BW, BH = 100.0, 100.0, 55.0, 78.45
PASSES = int(sys.argv[sys.argv.index('--passes') + 1]) if '--passes' in sys.argv else 40

RF_NETS = ['RX_PATCH', 'SYN_OUTAP', 'CW_RF', 'PA_IN', 'PA_OUT', 'PA_MATCH', 'TX_LPF', 'TX_ANT', 'NRF_ANT', 'RX_RF',
           'RX_ATT', 'LNA_OUT', 'LNA_IN', 'RX_BPF', 'RX_ANT', 'SYN_OUTAM']
POWER_NETS = ['5V_BUS', 'VBUS_C', '5V0', '3V3_OUT', '3V3', 'VDD_PA', 'VCC_SYN', 'LNA_VCC', 'PA_AVDD1', 'REG_SW',
              ]


def P(x, y):
    return VECTOR2I(FromMM(OX + x), FromMM(OY + y))


def netclasses():
    """Net classes in the project file (KiCad reads them when the board is loaded)."""
    pro = json.load(open(PRO)) if os.path.exists(PRO) else {}

    def cls(name, track, clr, via_d=0.45, via_h=0.2, prio=0):
        return {'name': name, 'clearance': clr, 'track_width': track, 'via_diameter': via_d, 'via_drill': via_h,
                'microvia_diameter': 0.3, 'microvia_drill': 0.1, 'diff_pair_width': 0.2, 'diff_pair_gap': 0.2,
                'diff_pair_via_gap': 0.25, 'wire_width': 6, 'bus_width': 12, 'line_style': 0,
                'schematic_color': 'rgba(0, 0, 0, 0.000)', 'pcb_color': 'rgba(0, 0, 0, 0.000)', 'priority': prio}
    pro['net_settings'] = {
        'classes': [cls('Default', 0.15, 0.15, 0.45, 0.25, prio=2147483647), cls('Power', 0.4, 0.15, 0.6, 0.3, 1),
                    cls('RF', 0.335, 0.203, 0.45, 0.25, 0), cls('USB', 0.2, 0.2, prio=2)],
        'meta': {'version': 4},
        'netclass_patterns': ([{'netclass': 'RF', 'pattern': p} for n in RF_NETS for p in (n, '*/' + n)] +
                              [{'netclass': 'Power', 'pattern': p} for n in POWER_NETS for p in (n, '*/' + n)] +
                              [{'netclass': 'USB', 'pattern': n} for n in ('USB_D+', 'USB_D-')]),
        'net_colors': None, 'netclass_assignments': None,
    }
    b = pro.setdefault('board', {}).setdefault('design_settings', {})
    b.setdefault('rules', {}).update({
        'min_clearance': 0.127, 'min_track_width': 0.1, 'min_via_diameter': 0.3, 'min_through_hole_diameter': 0.15,
        'min_via_annular_width': 0.075, 'min_hole_to_hole': 0.25, 'min_copper_edge_clearance': 0.25,
        'min_hole_clearance': 0.2, 'min_microvia_diameter': 0.2, 'min_microvia_drill': 0.1,
        'min_silk_clearance': 0.0, 'min_text_height': 0.6, 'min_text_thickness': 0.08})
    json.dump(pro, open(PRO, 'w'), indent=2)


def add_via(board, x, y, net, d=0.45, h=0.2, locked=True):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(P(x, y))
    v.SetWidth(FromMM(d))
    v.SetDrill(FromMM(h))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetNet(net)
    v.SetLocked(locked)
    board.Add(v)
    return v


def add_zone(board, layer, net, pts, clearance=0.2, min_w=0.15, prio=0, thermal=True):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(FromMM(OX + x), FromMM(OY + y))
    z.SetLocalClearance(FromMM(clearance))
    z.SetMinThickness(FromMM(min_w))
    z.SetAssignedPriority(prio)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if thermal else pcbnew.ZONE_CONNECTION_FULL)
    z.SetThermalReliefGap(FromMM(0.2))
    z.SetThermalReliefSpokeWidth(FromMM(0.25))
    board.Add(z)
    return z


def prerouting(board):
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)   # exported to the DSN as a plane: no routing on L2
    board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)   # L3 = 3V3 plane (+GND/VCC_SYN islands): pads drop a via, nothing routes through it
    nrf = next(f for f in board.GetFootprints() if f.GetValue() == 'nRF52840-QIAA')
    c = nrf.GetPosition()
    gnd = board.FindNet('GND')
    n_vip = 0
    for pad in nrf.Pads():
        num, net = pad.GetNumber(), pad.GetNetname()
        if not net or net.startswith('unconnected-') or num in ('EP', 'H23'):
            continue
        dx, dy = ToMM(pad.GetPosition().x - c.x), ToMM(pad.GetPosition().y - c.y)
        if max(abs(dx), abs(dy)) < 3.0:   # inner ring: no escape between 0.5 mm outer balls -> via-in-pad
            x, y = ToMM(pad.GetPosition().x) - OX, ToMM(pad.GetPosition().y) - OY
            add_via(board, x, y, pad.GetNet(), 0.3, 0.15)
            n_vip += 1
    cx, cy = ToMM(c.x) - OX, ToMM(c.y) - OY
    for i in range(-2, 3):
        for j in range(-2, 3):
            add_via(board, cx + i * 0.95, cy + j * 0.95, gnd, 0.45, 0.2)
    # planes: L2 solid GND, L3 3V3 (5V0/5V_BUS stay as tracks)
    outline = [(0.25, 0.25), (BW - 0.25, 0.25), (BW - 0.25, BH - 0.25), (0.25, BH - 0.25)]
    add_zone(board, pcbnew.In1_Cu, gnd, outline, 0.2, prio=0, thermal=False)
    add_zone(board, pcbnew.In2_Cu, board.FindNet('3V3'), outline, 0.2, prio=0)
    # VCC_SYN plane on L3 under the LMX2582 block (16 decoupling pins connect by a via each)
    vp = [pd for fp in board.GetFootprints() for pd in fp.Pads() if pd.GetNetname().endswith('VCC_SYN')]
    vx = [ToMM(pd.GetPosition().x) - OX for pd in vp]
    vy = [ToMM(pd.GetPosition().y) - OY for pd in vp]
    add_zone(board, pcbnew.In2_Cu, board.FindNet('/CW_Synth/VCC_SYN'),
             [(min(vx) - 1, min(vy) - 1), (max(vx) + 1, min(vy) - 1), (max(vx) + 1, max(vy) + 1), (min(vx) - 1, max(vy) + 1)],
             0.2, prio=1)
    # L3 is the reference plane for the patch feed on B.Cu: make it GND under that run
    feed = [t for t in board.GetTracks() if t.GetNetname().endswith('RX_PATCH') and t.GetLayer() == pcbnew.B_Cu]
    # the Cinch SMA launch voids L2 under its centre pad: L3 must be GND there
    sma = next(f for f in board.GetFootprints() if f.GetValue() == 'TX antenna U.FL')
    bb = sma.GetBoundingBox(False)
    sx0, sy0 = ToMM(bb.GetLeft()) - OX, ToMM(bb.GetTop()) - OY
    sx1, sy1 = min(ToMM(bb.GetRight()) - OX, BW - 0.3), ToMM(bb.GetBottom()) - OY
    add_zone(board, pcbnew.In2_Cu, gnd, [(sx0 - 1, sy0), (sx1, sy0), (sx1, sy1), (sx0 - 1, sy1)], 0.2, prio=2,
             thermal=False)
    for t in feed:
        x1, y1 = ToMM(t.GetStart().x) - OX, ToMM(t.GetStart().y) - OY
        x2, y2 = ToMM(t.GetEnd().x) - OX, ToMM(t.GetEnd().y) - OY
        add_zone(board, pcbnew.In2_Cu, gnd, [(min(x1, x2) - 2.5, min(y1, y2) - 2.0), (max(x1, x2) + 2.5, min(y1, y2) - 2.0),
                                             (max(x1, x2) + 2.5, max(y1, y2) + 2.0), (min(x1, x2) - 2.5, max(y1, y2) + 2.0)],
                 0.2, prio=2, thermal=False)
    print('nRF via-in-pad:', n_vip, '+ 25 EP vias')


def freeroute(board):
    os.makedirs(WORK, exist_ok=True)
    dsn, ses = os.path.join(WORK, 'beacon.dsn'), os.path.join(WORK, 'beacon.ses')
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.ExportSpecctraDSN(board, dsn)
    # the 0.3/0.15 padstack exists only for the fixed nRF52840 via-in-pad vias: don't let the router use it
    txt = open(dsn, encoding='utf8').read()
    txt = re.sub(r'(\(via (?:"[^"]+" ?)+)', lambda m: m.group(1).replace(' "Via[0-3]_300:150_um"', ''), txt, count=1)
    open(dsn, 'w', encoding='utf8').write(txt)
    cmd = [JAVA, '-jar', JAR, '-de', dsn, '-do', ses, '-mp', str(PASSES), '-mt', '8', '--gui.enabled=false']
    print('running', ' '.join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    open(os.path.join(WORK, 'freerouting.log'), 'w').write(r.stdout + r.stderr)
    tail = [ln for ln in (r.stdout + r.stderr).splitlines() if 'unrouted' in ln.lower() or 'completed' in ln.lower()]
    print('\n'.join(tail[-6:]))
    if not os.path.exists(ses):
        sys.exit('Freerouting produced no session file; see route/freerouting.log')
    pcbnew.ImportSpecctraSES(board, ses)


def stitching(board):
    """GND via fence along every RF track, both sides, ~1.4 mm pitch, skipping spots that collide."""
    gnd = board.FindNet('GND')
    rf = {n for n in RF_NETS}
    tracks = [t for t in board.GetTracks() if t.GetClass() == 'PCB_TRACK' and t.GetNetname().rsplit('/', 1)[-1] in rf]
    obst = []
    for fp in board.GetFootprints():
        for pd in fp.Pads():
            bb = pd.GetBoundingBox()
            obst.append((ToMM(bb.GetLeft()) - OX, ToMM(bb.GetTop()) - OY, ToMM(bb.GetRight()) - OX,
                         ToMM(bb.GetBottom()) - OY, pd.GetNetname()))
    for t in board.GetTracks():
        if t.GetNetname() != 'GND':
            bb = t.GetBoundingBox()
            obst.append((ToMM(bb.GetLeft()) - OX, ToMM(bb.GetTop()) - OY, ToMM(bb.GetRight()) - OX,
                         ToMM(bb.GetBottom()) - OY, t.GetNetname()))
    placed = []
    for t in tracks:
        x1, y1 = ToMM(t.GetStart().x) - OX, ToMM(t.GetStart().y) - OY
        x2, y2 = ToMM(t.GetEnd().x) - OX, ToMM(t.GetEnd().y) - OY
        L = math.hypot(x2 - x1, y2 - y1)
        if L < 0.8:
            continue
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        off = ToMM(t.GetWidth()) / 2 + 0.2 + 0.35
        n = max(1, int(L / 1.4))
        for k in range(n + 1):
            s = k * L / n
            for side in (-1, 1):
                x, y = x1 + ux * s - uy * off * side, y1 + uy * s + ux * off * side
                if not (0.6 < x < BW - 0.6 and 0.6 < y < BH - 0.6):
                    continue
                r = 0.225 + 0.15
                if any(o[0] - r < x < o[2] + r and o[1] - r < y < o[3] + r and o[4] != 'GND' for o in obst):
                    continue
                if any(math.hypot(x - px, y - py) < 0.7 for px, py in placed):
                    continue
                add_via(board, x, y, gnd, 0.45, 0.2, locked=False)
                placed.append((x, y))
    print('stitching vias:', len(placed))


def pours(board):
    gnd = board.FindNet('GND')
    outline = [(0.3, 0.3), (BW - 0.3, 0.3), (BW - 0.3, BH - 0.3), (0.3, BH - 0.3)]
    add_zone(board, pcbnew.F_Cu, gnd, outline, 0.2, prio=1)
    add_zone(board, pcbnew.B_Cu, gnd, outline, 0.2, prio=1)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


def install_rules():
    src = os.path.join(PRJ, 'docs', 'BEACON_PhoneModule.kicad_dru.proposed')
    s = open(src, encoding='utf8').read()
    s += ('\n# --- project overrides (route.py) ---\n'
          '(rule "nRF52840 inner-ring via-in-pad (JLC POFV, filled and capped)"\n'
          '\t(condition "A.Type == \'Via\' && A.insideCourtyard(\'U5\')")\n'
          '\t(constraint via_diameter (min 0.3mm))\n'
          '\t(constraint hole_size (min 0.15mm))\n'
          '\t(constraint hole_to_hole (min 0.2mm)))\n'
          '(rule "nRF ANT escape between balls"\n'
          '\t(condition "A.NetName == \'/MCU/NRF_ANT\' && A.intersectsCourtyard(\'U5\')")\n'
          '\t(constraint clearance (min 0.12mm)))\n'
          '(rule "Patch feed: B.Cu run and one RF via to L1"\n'
          '\t(condition "A.NetName == \'/RX_Frontend/RX_PATCH\'")\n'
          '\t(constraint track_width (min 0.325mm) (opt 0.335mm) (max 0.345mm)))\n'
          '(rule "GCT USB4105 stock footprint: shell holes to its own GND pads"\n'
          '\t(condition "A.memberOfFootprint(\'J1\') && B.memberOfFootprint(\'J1\')")\n'
          '\t(constraint hole_clearance (min 0.15mm)))\n'
          '(rule "L2 is the solid GND reference plane: no tracks"\n'
          '\t(layer "In1.Cu")\n'
          '\t(constraint disallow track))\n'
          '(rule "Pad-to-pad inside fine-pitch parts"\n'
          '\t(condition "A.Type == \'Pad\' && B.Type == \'Pad\' && A.Parent == B.Parent")\n'
          '\t(constraint clearance (min 0.1mm)))\n'
          '(rule "RF into LTCC filter pads"\n'
          '\t(condition "A.hasNetclass(\'RF\') && A.intersectsCourtyard(\'FL*\')")\n'
          '\t(constraint clearance (min 0.12mm)))\n')
    open(os.path.join(PRJ, 'BEACON_PhoneModule.kicad_dru'), 'w', encoding='utf8', newline='\n').write(s)


if __name__ == '__main__':
    install_rules()
    netclasses()
    board = pcbnew.LoadBoard(PCB)
    prerouting(board)
    freeroute(board)
    # GND stitching is done afterwards by scripts/stitch.py (exact clearances, keepout-aware)
    pours(board)
    pcbnew.SaveBoard(PCB, board)
    print('saved', PCB)
