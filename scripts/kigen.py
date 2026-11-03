"""Generate KiCad 10 hierarchical schematics from a Python netlist description.

Each component is placed with rotation 0; every connected pin gets a short wire
stub ending in a net label (global label when the net spans sheets).  Unused
pins get a no-connect flag.  UUIDs are derived from names so regenerating keeps
symbol identities stable for the PCB.
"""
import math
import uuid
from sexpr import Sym, parse, dump, find, first

KICAD_SYM_DIR = 'D:/KiCAD/share/kicad/symbols/'
PROJECT = 'BEACON_PhoneModule'
NS = uuid.UUID('6f2b1c0e-6a55-4d3c-9d7e-0b5eac0b2026')
GRID = 1.27


def uid(*parts):
    return str(uuid.uuid5(NS, '/'.join(parts)))


def snap(v, g=GRID):
    return round(round(v / g) * g, 4)


# --------------------------------------------------------------------------
# Symbol libraries
# --------------------------------------------------------------------------
class SymbolLib:
    def __init__(self):
        self._files = {}
        self.custom = {}  # name -> sexpr (unprefixed name)

    def _lib(self, lib):
        if lib not in self._files:
            self._files[lib] = parse(open(KICAD_SYM_DIR + lib + '.kicad_sym', encoding='utf8').read())
        return self._files[lib]

    def get(self, lib_id):
        """Return a deep-copied symbol sexpr named lib_id, with extends resolved."""
        lib, name = lib_id.split(':', 1)
        if lib == 'BEACON':
            sym = _copy(self.custom[name])
        else:
            tree = self._lib(lib)
            syms = {s[1]: s for s in find(tree, 'symbol')}
            sym = _copy(syms[name])
            ext = first(sym, 'extends')
            if ext:
                parent = _copy(syms[ext[1]])
                # child properties override parent ones
                child_props = {p[1]: p for p in find(sym, 'property')}
                body = [e for e in parent[2:] if not (isinstance(e, list) and e[0] == 'property' and e[1] in child_props)]
                body = list(child_props.values()) + body
                for e in body:
                    if isinstance(e, list) and e[0] == 'symbol':
                        e[1] = e[1].replace(ext[1], name, 1)
                sym = [Sym('symbol'), name] + body
        # rename top-level and units
        old = sym[1]
        sym[1] = lib_id
        for e in sym:
            if isinstance(e, list) and e[0] == 'symbol':
                e[1] = name + e[1][len(old):] if e[1].startswith(old) else e[1]
        return sym

    def pins(self, lib_id):
        sym = self.get(lib_id)
        out = []
        for u in find(sym, 'symbol'):
            for p in find(u, 'pin'):
                at = first(p, 'at')
                out.append(dict(num=str(first(p, 'number')[1]), name=first(p, 'name')[1], type=str(p[1]),
                                x=float(at[1]), y=float(at[2]), a=int(float(at[3])) if len(at) > 3 else 0,
                                length=float(first(p, 'length')[1])))
        return out

    def bbox(self, lib_id):
        """Bounding box (symbol coords, y up) of pins and graphics."""
        sym = self.get(lib_id)
        xs, ys = [], []
        for p in self.pins(lib_id):
            xs.append(p['x']); ys.append(p['y'])
        for u in find(sym, 'symbol'):
            for g in u:
                if isinstance(g, list) and g[0] == 'rectangle':
                    for k in ('start', 'end'):
                        pt = first(g, k); xs.append(float(pt[1])); ys.append(float(pt[2]))
                if isinstance(g, list) and g[0] == 'polyline':
                    for pt in find(first(g, 'pts'), 'xy'):
                        xs.append(float(pt[1])); ys.append(float(pt[2]))
                if isinstance(g, list) and g[0] == 'circle':
                    c = first(g, 'center'); r = float(first(g, 'radius')[1])
                    xs += [float(c[1]) - r, float(c[1]) + r]; ys += [float(c[2]) - r, float(c[2]) + r]
        if not xs:
            return (-2.54, -2.54, 2.54, 2.54)
        return (min(xs), min(ys), max(xs), max(ys))


def _copy(x):
    if isinstance(x, list):
        return [_copy(e) for e in x]
    return x


def _font(size=1.27, hide=False, justify=None):
    eff = [Sym('effects'), [Sym('font'), [Sym('size'), size, size]]]
    if justify:
        eff.append([Sym('justify')] + [Sym(j) for j in justify.split()])
    if hide:
        eff.append([Sym('hide'), Sym('yes')])
    return eff


def box_symbol(name, left=(), right=(), top=(), bottom=(), width=None, ref='U', desc='', fp='', value=None,
               pitch=2.54):
    """Build a rectangular symbol.  Each side is a list of (number, name, type) or None for a gap."""
    def longest(side):
        return max([len(p[1]) for p in side if p] + [1])
    n_v = max(len(left), len(right), 1)
    n_h = max(len(top), len(bottom), 0)
    if width is None:
        width = max(snap((longest(left) + longest(right)) * 1.0 + 6, 2.54), snap(n_h * pitch + 5.08, 2.54), 10.16)
    height = snap(max(n_v * pitch + 2.54, (longest(top) + longest(bottom)) * 1.0 + 6 if n_h else 0, 7.62), 2.54)
    w2, h2 = snap(width / 2, 2.54), snap(height / 2, 2.54)
    L = 2.54
    pins = []

    def side(lst, x0, y0, dx, dy, ang):
        for i, p in enumerate(lst):
            if p is None:
                continue
            num, pname, ptype = p
            x, y = x0 + dx * i, y0 + dy * i
            pins.append([Sym('pin'), Sym(ptype), Sym('line'), [Sym('at'), round(x, 4), round(y, 4), ang],
                         [Sym('length'), L],
                         [Sym('name'), pname, _font()], [Sym('number'), str(num), _font()]])
    top_y = snap((len(left) - 1) * pitch / 2, 1.27)
    side(left, -w2 - L, top_y, 0, -pitch, 0)
    top_y = snap((len(right) - 1) * pitch / 2, 1.27)
    side(right, w2 + L, top_y, 0, -pitch, 180)
    x0 = -snap((len(top) - 1) * pitch / 2, 1.27)
    side(top, x0, h2 + L, pitch, 0, 270)
    x0 = -snap((len(bottom) - 1) * pitch / 2, 1.27)
    side(bottom, x0, -h2 - L, pitch, 0, 90)
    props = [
        [Sym('property'), 'Reference', ref, [Sym('at'), -w2, h2 + 1.27, 0], _font(justify='left bottom')],
        [Sym('property'), 'Value', value or name, [Sym('at'), -w2, -h2 - 1.27, 0], _font(justify='left top')],
        [Sym('property'), 'Footprint', fp, [Sym('at'), 0, 0, 0], _font(hide=True)],
        [Sym('property'), 'Datasheet', '', [Sym('at'), 0, 0, 0], _font(hide=True)],
        [Sym('property'), 'Description', desc, [Sym('at'), 0, 0, 0], _font(hide=True)],
    ]
    body = [Sym('symbol'), name + '_0_1',
            [Sym('rectangle'), [Sym('start'), -w2, h2], [Sym('end'), w2, -h2],
             [Sym('stroke'), [Sym('width'), 0.254], [Sym('type'), Sym('default')]],
             [Sym('fill'), [Sym('type'), Sym('background')]]]]
    unit = [Sym('symbol'), name + '_1_1'] + pins
    return [Sym('symbol'), name, [Sym('exclude_from_sim'), Sym('no')], [Sym('in_bom'), Sym('yes')],
            [Sym('on_board'), Sym('yes')]] + props + [body, unit]


# --------------------------------------------------------------------------
# Schematic model
# --------------------------------------------------------------------------
class Part:
    def __init__(self, lib_id, ref, value, fp, nets, props=None, dnp=False):
        self.lib_id, self.ref, self.value, self.fp = lib_id, ref, value, fp
        self.nets = {str(k): v for k, v in nets.items()}
        self.props = props or {}
        self.dnp = dnp
        self.in_bom = True
        self.at = None
        self.sheet = None


class Sheet:
    def __init__(self, name, filename, title, paper='A3'):
        self.name, self.filename, self.title, self.paper = name, filename, title, paper
        self.parts, self.notes, self.groups = [], [], []
        self.uuid = uid('sheet', name)

    def add(self, *a, **k):
        p = Part(*a, **k)
        p.sheet = self
        self.parts.append(p)
        return p

    def note(self, text):
        self.notes.append(text)

    def group(self, title):
        """Start a new layout row group with a caption."""
        self.groups.append((len(self.parts), title))


class Design:
    def __init__(self, lib):
        self.lib = lib
        self.sheets = []
        self.root_uuid = uid('root')

    def sheet(self, *a, **k):
        s = Sheet(*a, **k)
        self.sheets.append(s)
        return s

    def all_parts(self):
        for s in self.sheets:
            yield from s.parts

    def check(self):
        """Validate pin numbers and report single-pin nets."""
        errors = []
        net_pins = {}
        refs = set()
        for p in self.all_parts():
            if p.ref in refs:
                errors.append('duplicate ref ' + p.ref)
            refs.add(p.ref)
            pins = {q['num'] for q in self.lib.pins(p.lib_id)}
            for n, net in p.nets.items():
                if n not in pins:
                    errors.append(f'{p.ref}: no pin {n} on {p.lib_id}')
                if net:
                    net_pins.setdefault(net, []).append(f'{p.ref}.{n}')
        singles = {n: v for n, v in net_pins.items() if len(v) < 2}
        return errors, singles, net_pins

    # ---------------------------------------------------------------- layout
    def layout(self, sheet):
        W, H = {'A4': (297, 210), 'A3': (420, 297), 'A2': (594, 420), 'A1': (841, 594)}[sheet.paper]
        x, y, row_h = 20.32, 30.48, 0
        group_at = dict(sheet.groups)
        self.captions = getattr(self, 'captions', {})
        for i, p in enumerate(sheet.parts):
            x0, y0, x1, y1 = self.lib.bbox(p.lib_id)
            pins = self.lib.pins(p.lib_id)
            used = [q for q in pins if p.nets.get(q['num']) is not None]
            maxlab = max([len(p.nets[q['num']]) for q in used] + [4])
            lab = 6 + maxlab * 1.05
            padl = lab if any(q['a'] == 0 for q in used) else 3
            padr = lab if any(q['a'] == 180 for q in used) else 3
            padt = lab if any(q['a'] == 270 for q in used) else 5
            padb = lab if any(q['a'] == 90 for q in used) else 5
            if (x1 - x0) < 6:
                padr = max(padr, 3) + 2 + max(len(p.ref), len(p.value)) * 1.0
            w = (x1 - x0) + padl + padr
            h = (y1 - y0) + padt + padb
            if i in group_at:
                if x > 20.32:
                    y += row_h + 7.62
                x, row_h = 20.32, 0
                self.captions.setdefault(sheet.name, []).append((group_at[i], x, y))
                y += 5.08
            if x + w > W - 15 and x > 20.32:
                x, y, row_h = 20.32, y + row_h + 5.08, 0
            # origin so that bbox top-left lands at (x+padl, y+padt); symbol y is up
            p.at = (snap(x + padl - x0, 2.54), snap(y + padt + y1, 2.54))
            x += w + 2.54
            row_h = max(row_h, h)
        if y + row_h > H - 10:
            print(f'WARNING: sheet {sheet.name} content overflows {sheet.paper} ({y + row_h:.0f}mm > {H}mm)')

    # ---------------------------------------------------------------- output
    def global_nets(self):
        where = {}
        for s in self.sheets:
            for p in s.parts:
                for net in p.nets.values():
                    if net:
                        where.setdefault(net, set()).add(s.name)
        return {n for n, ss in where.items() if len(ss) > 1}

    def lib_symbols(self, sheet):
        ids = []
        for p in sheet.parts:
            if p.lib_id not in ids:
                ids.append(p.lib_id)
        return [Sym('lib_symbols')] + [self.lib.get(i) for i in ids]

    def sheet_path(self, sheet):
        return '/' + self.root_uuid + ('' if sheet is None else '/' + sheet.uuid)

    def write_sheet(self, sheet, path):
        self.layout(sheet)
        glob = self.global_nets()
        items = [Sym('kicad_sch'), [Sym('version'), 20250114], [Sym('generator'), 'eeschema'],
                 [Sym('generator_version'), '10.0'], [Sym('uuid'), sheet.uuid], [Sym('paper'), sheet.paper],
                 [Sym('title_block'), [Sym('title'), sheet.title], [Sym('date'), '2026-11-02'],
                  [Sym('rev'), 'A'], [Sym('company'), 'BEACON - Northeastern University Senior Capstone'],
                  [Sym('comment'), 1, 'Translated from Altium BeaconPhoneModule.pdf and completed'],
                  [Sym('comment'), 2, 'HW: M. Marsicano, J. Oshinsky, N. McKillips, I. Hong'],
                  [Sym('comment'), 3, 'Advisor: Prof. Bahram Shafai']],
                 self.lib_symbols(sheet)]
        for (title, x, y) in self.captions.get(sheet.name, []):
            items.append([Sym('text'), title, [Sym('exclude_from_sim'), Sym('no')], [Sym('at'), x, y, 0],
                          _font(2.0, justify='left bottom'), [Sym('uuid'), uid(sheet.name, 'cap', title)]])
        ny = 20.0
        for i, t in enumerate(sheet.notes):
            items.append([Sym('text'), t, [Sym('exclude_from_sim'), Sym('no')],
                          [Sym('at'), {'A3': 300, 'A2': 440, 'A4': 200, 'A1': 650}[sheet.paper], ny, 0],
                          _font(1.27, justify='left top'), [Sym('uuid'), uid(sheet.name, 'note', str(i))]])
            ny += 2.2 * (t.count('\n') + 1) + 3
        for p in sheet.parts:
            items += self._symbol_items(sheet, p, glob)
        items.append([Sym('sheet_instances'), [Sym('path'), '/', [Sym('page'), '1']]])
        with open(path, 'w', encoding='utf8', newline='\n') as f:
            f.write(dump(items) + '\n')

    def _symbol_items(self, sheet, p, glob):
        X, Y = p.at
        su = uid('sym', p.ref)
        x0, y0, x1, y1 = self.lib.bbox(p.lib_id)
        out = []
        if (x1 - x0) < 6:
            ref_at = [Sym('at'), snap(X + x1 + 1.27), snap(Y - 1.27), 0]
            val_at = [Sym('at'), snap(X + x1 + 1.27), snap(Y + 1.27), 0]
            rj, vj = 'left bottom', 'left top'
        else:
            ref_at = [Sym('at'), snap(X + x0), snap(Y - y1 - 1.27), 0]
            val_at = [Sym('at'), snap(X + x0), snap(Y - y0 + 2.54), 0]
            rj, vj = 'left bottom', 'left top'
        sym = [Sym('symbol'), [Sym('lib_id'), p.lib_id], [Sym('at'), X, Y, 0], [Sym('unit'), 1],
               [Sym('exclude_from_sim'), Sym('no')], [Sym('in_bom'), Sym('yes') if p.in_bom else Sym('no')],
               [Sym('on_board'), Sym('yes')],
               [Sym('dnp'), Sym('yes') if p.dnp else Sym('no')], [Sym('uuid'), su],
               [Sym('property'), 'Reference', p.ref, ref_at, _font(justify=rj)],
               [Sym('property'), 'Value', p.value, val_at, _font(justify=vj)],
               [Sym('property'), 'Footprint', p.fp, [Sym('at'), X, Y, 0], _font(hide=True)]]
        for k, v in p.props.items():
            sym.append([Sym('property'), k, v, [Sym('at'), X, Y, 0], _font(hide=True)])
        for q in self.lib.pins(p.lib_id):
            sym.append([Sym('pin'), q['num'], [Sym('uuid'), uid('pin', p.ref, q['num'])]])
        sym.append([Sym('instances'), [Sym('project'), PROJECT,
                                       [Sym('path'), self.sheet_path(sheet), [Sym('reference'), p.ref],
                                        [Sym('unit'), 1]]]])
        out.append(sym)
        # stubs + labels
        for q in self.lib.pins(p.lib_id):
            net = p.nets.get(q['num'], None)
            px, py = snap(X + q['x']), snap(Y - q['y'])
            if net is None:
                if q['num'] in p.nets or q['type'] not in ('no_connect',):
                    out.append([Sym('no_connect'), [Sym('at'), px, py], [Sym('uuid'), uid('nc', p.ref, q['num'])]])
                continue
            dx, dy = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[q['a'] % 360]
            ex, ey = snap(px + dx * 2.54), snap(py + dy * 2.54)
            out.append([Sym('wire'), [Sym('pts'), [Sym('xy'), px, py], [Sym('xy'), ex, ey]],
                        [Sym('stroke'), [Sym('width'), 0], [Sym('type'), Sym('default')]],
                        [Sym('uuid'), uid('w', p.ref, q['num'])]])
            ang, just = {(-1, 0): (180, 'right'), (1, 0): (0, 'left'), (0, -1): (90, 'left'),
                         (0, 1): (270, 'right')}[(dx, dy)]
            lu = uid('lbl', p.ref, q['num'])
            if net in glob:
                out.append([Sym('global_label'), net, [Sym('shape'), Sym('bidirectional')],
                            [Sym('at'), ex, ey, ang], [Sym('fields_autoplaced'), Sym('yes')],
                            _font(justify=just), [Sym('uuid'), lu],
                            [Sym('property'), 'Intersheetrefs', '${INTERSHEET_REFS}', [Sym('at'), ex, ey, 0],
                             _font(hide=True)]])
            else:
                out.append([Sym('label'), net, [Sym('at'), ex, ey, ang], [Sym('fields_autoplaced'), Sym('yes')],
                            _font(justify=just + ' bottom'), [Sym('uuid'), lu]])
        return out

    def write_root(self, path, title):
        items = [Sym('kicad_sch'), [Sym('version'), 20250114], [Sym('generator'), 'eeschema'],
                 [Sym('generator_version'), '10.0'], [Sym('uuid'), self.root_uuid], [Sym('paper'), 'A3'],
                 [Sym('title_block'), [Sym('title'), title], [Sym('date'), '2026-11-02'], [Sym('rev'), 'A'],
                  [Sym('company'), 'BEACON - Northeastern University Senior Capstone'],
                  [Sym('comment'), 1, 'Never charge. Never miss a beat. - World\'s first backscatter wearable'],
                  [Sym('comment'), 2, 'HW: M. Marsicano, J. Oshinsky, N. McKillips, I. Hong | FW: J. Faubus, J. Hensley'],
                  [Sym('comment'), 3, 'Advisor: Prof. Bahram Shafai']],
                 [Sym('lib_symbols')]]
        for i, s in enumerate(self.sheets):
            col, row = i % 3, i // 3
            x, y = 30 + col * 120, 40 + row * 80
            items.append([Sym('sheet'), [Sym('at'), x, y], [Sym('size'), 90, 50],
                          [Sym('exclude_from_sim'), Sym('no')], [Sym('in_bom'), Sym('yes')],
                          [Sym('on_board'), Sym('yes')], [Sym('dnp'), Sym('no')],
                          [Sym('fields_autoplaced'), Sym('yes')],
                          [Sym('stroke'), [Sym('width'), 0.1524], [Sym('type'), Sym('solid')]],
                          [Sym('fill'), [Sym('color'), 0, 0, 0, 0.0]], [Sym('uuid'), s.uuid],
                          [Sym('property'), 'Sheetname', s.name, [Sym('at'), x, y - 0.7, 0],
                           _font(justify='left bottom')],
                          [Sym('property'), 'Sheetfile', s.filename, [Sym('at'), x, y + 50.6, 0],
                           _font(justify='left top')],
                          [Sym('instances'), [Sym('project'), PROJECT,
                                              [Sym('path'), '/' + self.root_uuid, [Sym('page'), str(i + 2)]]]]])
        for i, t in enumerate(getattr(self, 'root_notes', [])):
            items.append([Sym('text'), t, [Sym('exclude_from_sim'), Sym('no')], [Sym('at'), 30, 205 + i * 0, 0],
                          _font(1.5, justify='left top'), [Sym('uuid'), uid('root', 'note', str(i))]])
        items.append([Sym('sheet_instances'), [Sym('path'), '/', [Sym('page'), '1']]])
        with open(path, 'w', encoding='utf8', newline='\n') as f:
            f.write(dump(items) + '\n')

    def write_custom_lib(self, path):
        items = [Sym('kicad_symbol_lib'), [Sym('version'), 20241209], [Sym('generator'), 'kigen'],
                 [Sym('generator_version'), '10.0']] + [self.lib.custom[k] for k in sorted(self.lib.custom)]
        with open(path, 'w', encoding='utf8', newline='\n') as f:
            f.write(dump(items) + '\n')
