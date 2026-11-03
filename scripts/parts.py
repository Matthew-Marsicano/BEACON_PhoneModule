"""Project-specific symbols (BEACON.kicad_sym) and footprints (BEACON.pretty).

Pinouts are from the manufacturer datasheets:
  LMX2582  - TI SNAS680E, VQFN-40 (RHA)
  CC2595   - TI SWRS090A, VQFN-16 (RGT)
  QPL9547  - Qorvo datasheet Rev D, DFN-8 2x2
  2450BP08C0100001T / 2450LP07C0100001T - Johanson datasheets
  UP20-C-F-G-FL-P12-TR - Same Sky drawing (USB-C plug, board edge)
  LT80602  - ADI LT80602/LT80603; see LT80602_PINS note below
"""
import os
from kigen import box_symbol
from sexpr import Sym, dump

P, PI, PO, PW, IN, OUT, BI, NC = ('passive', 'power_in', 'power_out', 'power_in', 'input', 'output',
                                  'bidirectional', 'no_connect')

# LT80602 17L FC2QFN 3x3 - ADI datasheet Rev 2, Table 3 / Figure 3.  EP is internally tied to VIN (not GND).
LT80602_PINS = {
    'GND': 1, 'BST': 2, 'VIN1': 3, 'GND1a': 4, 'GND1b': 5, 'SW': 6, 'GND2a': 7, 'GND2b': 8, 'VIN2': 9,
    'EN/UV': 10, 'BIAS/VOUT': 11, 'FB/VOS': 12, 'RT': 13, 'TR/SS': 14, 'SYNC/MODE': 15, 'PG/TJ': 16,
    'INTVCC': 17, 'EP': 'EP',
}
# Recommended land pattern (ADI 90-100271 rev B, Fig. 94), top view, mm, KiCad y-down.
# Rects measured from the drawing: (pad, x0, y0, x1, y1).  Corner pins 12 and 17 are L-shaped (two rects).
LT80602_LAND = [
    (17, -1.800, -1.300, -1.060, -0.840), (17, -1.330, -1.800, -1.060, -1.300),
    (16, -0.900, -1.800, -0.600, -0.990), (15, -0.400, -1.800, -0.100, -0.990),
    (14, 0.100, -1.800, 0.400, -0.990), (13, 0.600, -1.800, 0.900, -0.990),
    (12, 1.090, -1.300, 1.800, -0.840), (12, 1.090, -1.800, 1.360, -1.300),
    (1, -1.800, -0.650, -0.910, -0.285), (2, -1.800, -0.115, -0.960, 0.205), (3, -1.800, 0.385, -0.935, 0.690),
    (11, 0.920, -0.650, 1.800, -0.285), (10, 0.965, -0.115, 1.800, 0.205), (9, 0.935, 0.385, 1.800, 0.690),
    (4, -1.400, 0.975, -0.860, 1.800), (5, -0.700, 1.025, -0.435, 1.800), (6, -0.150, 0.610, 0.150, 1.800),
    (7, 0.435, 1.025, 0.700, 1.800), (8, 0.860, 0.975, 1.400, 1.800),
    ('EP', -0.385, -0.260, 0.385, 0.195),
]


def register(lib):
    c = lib.custom
    c['LMX2582'] = box_symbol(
        'LMX2582', ref='U', fp='Package_DFN_QFN:Texas_RHA_VQFN-40-1EP_6x6mm_P0.5mm_EP4.6x4.6mm_ThermalVias',
        desc='TI LMX2582 20 MHz-5.5 GHz wideband PLL+VCO synthesizer',
        left=[(1, 'CE', IN), (24, 'CSB', IN), (16, 'SCK', IN), (17, 'SDI', IN), None,
              (8, 'OSCinP', IN), (9, 'OSCinM', IN), None,
              (7, 'VccDIG', PI), (11, 'VccCP', PI), (15, 'VccMASH', PI), (21, 'VccBUF', PI),
              (26, 'VccVCO2', PI), (37, 'VccVCO', PI)],
        right=[(20, 'MUXout', OUT), None, (23, 'RFoutAP', P), (22, 'RFoutAM', P), (19, 'RFoutBP', P),
               (18, 'RFoutBM', P), None, (12, 'CPout', P), (35, 'Vtune', P), None,
               (3, 'VbiasVCO', P), (10, 'VregIN', P), (27, 'VbiasVCO2', P), (29, 'VrefVCO2', P),
               (33, 'VbiasVARAC', P), (36, 'VrefVCO', P), (38, 'VregVCO', P)],
        bottom=[(2, 'GND', PW), (4, 'GND', PW), (6, 'GND', PW), (13, 'GND', PW), (14, 'GND', PW),
                (25, 'GND', PW), (31, 'GND', PW), (34, 'GND', PW), (39, 'GND', PW), (40, 'GND', PW),
                (41, 'PAD', PW)],
        top=[(5, 'NC', NC), (28, 'NC', NC), (30, 'NC', NC), (32, 'NC', NC)])
    c['CC2595'] = box_symbol(
        'CC2595', ref='U', fp='Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias',
        desc='TI CC2595 2.4 GHz range-extender PA, +20 dBm',
        left=[(2, 'RF_IN', P), None, (8, 'PAEN', IN), None, (6, 'RBIAS1', P), (7, 'RBIAS2', P), None,
              (5, 'AVDD_BIAS', PI), (15, 'AVDD_PA1', PI)],
        right=[(10, 'RF_OUT', P), (12, 'RF_OUT', P)],
        bottom=[(1, 'GND', PW), (3, 'GND', PW), (4, 'GND', PW), (9, 'GND', PW), (11, 'GND', PW),
                (13, 'GND', PW), (14, 'GND', PW), (16, 'GND', PW), (17, 'EP', PW)])
    c['QPL9547'] = box_symbol(
        'QPL9547', ref='U', fp='BEACON:Qorvo_QPL9547_DFN-8-1EP_2x2mm_P0.5mm',
        desc='Qorvo QPL9547 0.6-4.2 GHz ultra-low-noise LNA (Shut_Down active high)',
        left=[(2, 'RF_IN', P), None, (1, 'VBIAS', P), (6, 'SHUT_DOWN', IN)],
        right=[(7, 'RF_OUT', P)],
        bottom=[(9, 'EP', PW)],
        top=[(3, 'NC', NC), (4, 'NC', NC), (5, 'NC', NC), (8, 'NC', NC)])
    c['2450BP08C0100001T'] = box_symbol(
        '2450BP08C0100001T', ref='FL', fp='BEACON:Johanson_2450BP08_1.1x0.9mm',
        desc='Johanson 2.45 GHz LTCC band-pass filter',
        left=[(1, 'IN', P)], right=[(4, 'OUT', P)], bottom=[(2, 'GND', P), (3, 'GND', P), (5, 'GND', P)])
    c['DEA202450BT-1294D1-H'] = box_symbol(
        'DEA202450BT-1294D1-H', ref='FL', fp='BEACON:TDK_DEA202450BT-1294D1-H_2012',
        desc='TDK 2.45 GHz LTCC band-pass filter, 2012, 1 W (pads: 1=IN, 4=OUT, 2/3=GND; TDK terminals 1/3/2,4)',
        left=[(1, 'IN', P)], right=[(4, 'OUT', P)], bottom=[(2, 'GND', P), (3, 'GND', P)])
    c['2450LP07C0100001T'] = box_symbol(
        '2450LP07C0100001T', ref='FL', fp='BEACON:Johanson_2450LP07_0402_4T',
        desc='Johanson 2.45 GHz LTCC low-pass filter',
        left=[(2, 'IN/OUT', P)], right=[(4, 'IN/OUT', P)], bottom=[(1, 'GND', P), (3, 'GND', P)])
    lt = LT80602_PINS
    c['LT80602'] = box_symbol(
        'LT80602', ref='U', fp='BEACON:ADI_FC2QFN-17-1EP_3x3mm_LT80602',
        desc='ADI LT80602 3-65V 2.5A synchronous Silent Switcher buck, 17L FC2QFN 3x3 (EP = VIN)',
        left=[(lt['VIN1'], 'VIN1', PI), (lt['VIN2'], 'VIN2', PI), (lt['EP'], 'EP(VIN)', PI), None,
              (lt['EN/UV'], 'EN/UV', IN), (lt['SYNC/MODE'], 'SYNC/MODE', IN), (lt['TR/SS'], 'TR/SS', P),
              (lt['RT'], 'RT', P), (lt['INTVCC'], 'INTVCC', PO)],
        right=[(lt['BST'], 'BST', P), (lt['SW'], 'SW', PO), None, (lt['BIAS/VOUT'], 'BIAS/VOUT', PI),
               (lt['FB/VOS'], 'FB/VOS', IN), (lt['PG/TJ'], 'PG/TJ', 'open_collector')],
        bottom=[(lt['GND'], 'GND', PW), (lt['GND1a'], 'GND1', PW), (lt['GND1b'], 'GND1', PW),
                (lt['GND2a'], 'GND2', PW), (lt['GND2b'], 'GND2', PW)])
    c['Taoglas_WDP2458'] = box_symbol(
        'Taoglas_WDP2458', ref='AE', fp='BEACON:Taoglas_WDP.2458.25.4_Patch',
        desc='Taoglas WDP.2458.25.4.B.02 2.4 GHz 25x25x4 mm pin-fed ceramic patch',
        left=[(1, 'FEED', P)], bottom=[(2, 'GND', P)])
    c['USB_C_Plug_UP20'] = box_symbol(
        'USB_C_Plug_UP20', ref='J', fp='BEACON:USB_C_Plug_SameSky_UP20-C-F-G-FL-P12',
        desc='Same Sky UP20-C-F-G-FL-P12-TR USB-C plug, USB 2.0, board edge (single CC)',
        left=[('A4', 'VBUS', P), ('B9', 'VBUS', P), None, ('A5', 'CC', BI), None,
              ('A6', 'D+', BI), ('A7', 'D-', BI), None, ('A2', 'SSTXp1', P), ('A3', 'SSTXn1', P),
              ('B11', 'SSRXp1', P), ('B10', 'SSRXn1', P)],
        bottom=[('A1', 'GND', P), ('A12', 'GND', P), ('B12', 'GND', P), ('SH', 'SHIELD', P)])


# --------------------------------------------------------------------------
# Footprints
# --------------------------------------------------------------------------
def _pad(num, kind, shape, x, y, w, h, layers, drill=None, extra=()):
    p = [Sym('pad'), str(num), Sym(kind), Sym(shape), [Sym('at'), x, y], [Sym('size'), w, h]]
    if drill:
        p.append(drill)
    p.append([Sym('layers')] + list(layers))
    p += list(extra)
    return p


SMD = ('F.Cu', 'F.Paste', 'F.Mask')
# Taoglas patch feed geometry - PROVISIONAL until checked against the WDP.2458.25.4 drawing
PATCH_SIZE = 25.4          # 25.1 +/-0.3
PATCH_FEED = (0.0, 4.5)    # feed pin offset from the patch centre (mm, footprint coords)
PATCH_PIN_DRILL = 1.0
PATCH_PIN_PAD = 1.8
PTH = ('*.Cu', '*.Mask')


def _line(layer, x1, y1, x2, y2, w=0.12):
    return [Sym('fp_line'), [Sym('start'), x1, y1], [Sym('end'), x2, y2],
            [Sym('stroke'), [Sym('width'), w], [Sym('type'), Sym('solid')]], [Sym('layer'), layer]]


def _rect(layer, x1, y1, x2, y2, w=0.05):
    return [Sym('fp_rect'), [Sym('start'), x1, y1], [Sym('end'), x2, y2],
            [Sym('stroke'), [Sym('width'), w], [Sym('type'), Sym('solid')]], [Sym('fill'), Sym('no')],
            [Sym('layer'), layer]]


def _text(kind, txt, y, layer, hide=False):
    t = [Sym('property'), kind, txt, [Sym('at'), 0, y, 0], [Sym('layer'), layer]]
    if hide:
        t.append([Sym('hide'), Sym('yes')])
    t.append([Sym('effects'), [Sym('font'), [Sym('size'), 0.5, 0.5], [Sym('thickness'), 0.08]]])
    return t


def _fp(name, descr, body, ref_y, val_y, crt, attr='smd'):
    return [Sym('footprint'), name, [Sym('version'), 20241229], [Sym('generator'), 'kigen'],
            [Sym('layer'), 'F.Cu'], [Sym('descr'), descr],
            _text('Reference', 'REF**', ref_y, 'F.SilkS'), _text('Value', name, val_y, 'F.Fab'),
            [Sym('attr'), Sym(attr)], _rect('F.CrtYd', *crt)] + body


def footprints():
    fps = {}
    # Johanson 2450BP08: 1.10 x 0.90 LGA, top view: 1 IN left-centre, 5 GND top-mid, 4 OUT top-right,
    # 2 GND bottom-mid, 3 GND bottom-right.  Terminal 0.18 x 0.25, column gap 0.205, row gap 0.25.
    w, h = 0.22, 0.29
    xc = [-0.385, 0.0, 0.385]
    yr = 0.25
    body = [_pad(1, 'smd', 'rect', xc[0], 0, w, h, SMD), _pad(5, 'smd', 'rect', xc[1], -yr, w, h, SMD),
            _pad(4, 'smd', 'rect', xc[2], -yr, w, h, SMD), _pad(2, 'smd', 'rect', xc[1], yr, w, h, SMD),
            _pad(3, 'smd', 'rect', xc[2], yr, w, h, SMD),
            _rect('F.Fab', -0.55, -0.45, 0.55, 0.45, 0.05), _line('F.SilkS', -0.75, -0.2, -0.75, 0.2, 0.1)]
    fps['Johanson_2450BP08_1.1x0.9mm'] = _fp(
        'Johanson_2450BP08_1.1x0.9mm', 'Johanson 2450BP08C0100001T band-pass filter, 1.10x0.90mm LGA-5 '
        '(land from datasheet terminal sizes; verify against Johanson recommended layout)',
        body, -0.9, 0.9, (-0.85, -0.7, 0.8, 0.7))
    # Johanson 2450LP07: EIA0402 4-terminal; 1 GND top long side, 2 I/O right end, 3 GND bottom, 4 I/O left
    body = [_pad(4, 'smd', 'rect', -0.575, 0, 0.45, 0.30, SMD), _pad(2, 'smd', 'rect', 0.575, 0, 0.45, 0.30, SMD),
            _pad(1, 'smd', 'rect', 0, -0.325, 0.30, 0.45, SMD), _pad(3, 'smd', 'rect', 0, 0.325, 0.30, 0.45, SMD),
            _rect('F.Fab', -0.5, -0.25, 0.5, 0.25, 0.05)]
    fps['Johanson_2450LP07_0402_4T'] = _fp(
        'Johanson_2450LP07_0402_4T', 'Johanson 2450LP07C0100001T low-pass filter, EIA0402 4-terminal',
        body, -0.8, 0.8, (-0.85, -0.6, 0.85, 0.6))
    # Same Sky UP20-C-F-G-FL-P12: 12 pads 0.30 x 1.00 at 0.50 pitch.  The datasheet top view has the board
    # above the pads and reads A12..A1 left->right; here the board is at +y (plug body overhangs y<0), i.e.
    # that view rotated 180 deg, so left->right is A1 A2 A3 A4 B12 B11 B10 B9 A5 A6 A7 A12.
    order = ['A1', 'A2', 'A3', 'A4', 'B12', 'B11', 'B10', 'B9', 'A5', 'A6', 'A7', 'A12']
    body = []
    for i, n in enumerate(order):
        body.append(_pad(n, 'smd', 'rect', round(-2.75 + 0.5 * i, 3), 1.56, 0.30, 1.00, SMD))
    for sx in (-1, 1):
        body.append(_pad('SH', 'thru_hole', 'oval', sx * 4.30, 1.40, 0.85, 2.20, PTH,
                         drill=[Sym('drill'), Sym('oval'), 0.45, 1.80]))
        body.append(_pad('SH', 'smd', 'rect', sx * 4.01, 0.75, 1.42, 1.00, SMD))
    body += [_line('Dwgs.User', -4.6, 0, 4.6, 0, 0.1),
             _rect('F.Fab', -4.3, -11.25, 4.3, 0.0, 0.1),
             [Sym('fp_text'), Sym('user'), 'PCB EDGE', [Sym('at'), 0, -0.6, 0], [Sym('layer'), 'Dwgs.User'],
              [Sym('effects'), [Sym('font'), [Sym('size'), 0.5, 0.5], [Sym('thickness'), 0.08]]]]]
    lt_body = []
    for num, x0, y0, x1, y1 in LT80602_LAND:
        paste = SMD if num != 'EP' else ('F.Cu', 'F.Mask')
        lt_body.append(_pad(num, 'smd', 'rect', round((x0 + x1) / 2, 4), round((y0 + y1) / 2, 4),
                         round(x1 - x0, 4), round(y1 - y0, 4), paste))
    lt_body.append(_pad('EP', 'smd', 'rect', 0, -0.0325, 0.6, 0.3, ('F.Paste',)))
    lt_body += [_rect('F.Fab', -1.5, -1.5, 1.5, 1.5, 0.1), _line('F.SilkS', -1.95, -0.47, -1.95, 0.0, 0.12)]
    fps['ADI_FC2QFN-17-1EP_3x3mm_LT80602'] = _fp(
        'ADI_FC2QFN-17-1EP_3x3mm_LT80602',
        'ADI 17L FC2QFN 3x3x0.75 (21-100774), land pattern 90-100271 rev B; pads measured from datasheet Fig.94',
        lt_body, -2.4, 2.4, (-2.05, -2.05, 2.05, 2.05))
    fps['USB_C_Plug_SameSky_UP20-C-F-G-FL-P12'] = _fp(
        'USB_C_Plug_SameSky_UP20-C-F-G-FL-P12',
        'Same Sky UP20-C-F-G-FL-P12-TR USB-C plug, board-edge, per datasheet Recommended PCB Layout '
        '(top view, rotated 180 deg so the board is at +y)',
        body, 3.2, 4.0, (-5.1, -11.5, 5.1, 2.8))
    # Qorvo QPL9547 DFN-8 2x2: Qorvo land pattern (datasheet p.8): pads 0.43 x 0.25 at x=+-0.915,
    # pitch 0.5, pin 1 top-left, counter-clockwise; EP 0.80 x 1.60 with 0.25 mm vias.
    body = []
    for i in range(4):
        body.append(_pad(i + 1, 'smd', 'rect', -0.915, -0.75 + 0.5 * i, 0.43, 0.25, SMD))
        body.append(_pad(8 - i, 'smd', 'rect', 0.915, -0.75 + 0.5 * i, 0.43, 0.25, SMD))
    body.append(_pad(9, 'smd', 'rect', 0, 0, 0.80, 1.60, ('F.Cu', 'F.Mask')))
    body.append(_pad(9, 'smd', 'rect', 0, -0.42, 0.6, 0.55, ('F.Paste',)))
    body.append(_pad(9, 'smd', 'rect', 0, 0.42, 0.6, 0.55, ('F.Paste',)))
    for vy in (-0.45, 0.45):
        body.append(_pad(9, 'thru_hole', 'circle', 0, vy, 0.45, 0.45, PTH, drill=[Sym('drill'), 0.25]))
    body += [_rect('F.Fab', -1.0, -1.0, 1.0, 1.0, 0.1), _line('F.SilkS', -1.35, -1.05, -1.35, -0.6, 0.12)]
    # Taoglas WDP.2458.25.4 pin-fed patch.  PATCH_FEED is the feed pin offset from the patch centre.
    pb = [_pad(1, 'thru_hole', 'circle', PATCH_FEED[0], PATCH_FEED[1], PATCH_PIN_PAD, PATCH_PIN_PAD,
                 ('*.Cu', 'B.Mask'), drill=[Sym('drill'), PATCH_PIN_DRILL])]
    h = PATCH_SIZE / 2
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        pb.append(_pad(2, 'smd', 'rect', sx * (h - 1.2), sy * (h - 1.2), 1.5, 1.5, ('F.Cu',)))
    k = h + 0.5
    pb.append([Sym('zone'), [Sym('net'), 0], [Sym('net_name'), ''], [Sym('layers'), 'F.Cu'],
                 [Sym('hatch'), Sym('edge'), 0.5], [Sym('connect_pads'), [Sym('clearance'), 0]],
                 [Sym('min_thickness'), 0.25], [Sym('filled_areas_thickness'), Sym('no')],
                 [Sym('keepout'), [Sym('tracks'), Sym('not_allowed')], [Sym('vias'), Sym('allowed')],
                  [Sym('pads'), Sym('allowed')], [Sym('copperpour'), Sym('allowed')],
                  [Sym('footprints'), Sym('not_allowed')]],
                 [Sym('fill'), [Sym('thermal_gap'), 0.5], [Sym('thermal_bridge_width'), 0.5]],
                 [Sym('polygon'), [Sym('pts'), [Sym('xy'), -k, -k], [Sym('xy'), k, -k], [Sym('xy'), k, k],
                                   [Sym('xy'), -k, k]]]])
    pb += [_rect('F.SilkS', -h - 0.3, -h - 0.3, h + 0.3, h + 0.3, 0.12), _rect('F.Fab', -h, -h, h, h, 0.1)]
    fps['Taoglas_WDP.2458.25.4_Patch'] = _fp(
        'Taoglas_WDP.2458.25.4_Patch', 'Taoglas WDP.2458.25.4.B.02 25x25x4 mm pin-fed ceramic patch; top copper '
        'under the patch must be solid GND (keepout: no tracks, no other parts)', pb, -h - 1.2, h + 1.2,
        (-h - 0.6, -h - 0.6, h + 0.6, h + 0.6))
    fps['Qorvo_QPL9547_DFN-8-1EP_2x2mm_P0.5mm'] = _fp(
        'Qorvo_QPL9547_DFN-8-1EP_2x2mm_P0.5mm', 'Qorvo QPL9547 2x2 DFN-8, land per datasheet Rev D p.8',
        body, -1.6, 1.6, (-1.4, -1.25, 1.4, 1.25))
    return fps


def write_footprints(dirpath):
    os.makedirs(dirpath, exist_ok=True)
    for name, fp in footprints().items():
        with open(os.path.join(dirpath, name + '.kicad_mod'), 'w', encoding='utf8', newline='\n') as f:
            f.write(dump(fp) + '\n')
    # datasheet-derived footprints reviewed in docs/antenna_connectors.md override the generated ones
    import shutil
    src = os.path.join(os.path.dirname(dirpath), 'docs', 'proposed_footprints')
    for fn in sorted(os.listdir(src)) if os.path.isdir(src) else []:
        if fn.endswith('.kicad_mod'):
            shutil.copyfile(os.path.join(src, fn), os.path.join(dirpath, fn))
