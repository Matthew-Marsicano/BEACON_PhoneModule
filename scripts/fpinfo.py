"""Load every assigned footprint, check pin<->pad numbering and report courtyard sizes."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew  # noqa: E402
import design  # noqa: E402

PRJ = design.OUT
STOCK = 'D:/KiCAD/share/kicad/footprints/'


def lib_path(nick):
    return os.path.join(PRJ, 'BEACON.pretty') if nick == 'BEACON' else STOCK + nick + '.pretty'


def load(fpid):
    nick, name = fpid.split(':', 1)
    fp = pcbnew.FootprintLoad(lib_path(nick), name)
    if fp is None:
        raise RuntimeError('cannot load ' + fpid)
    return fp


if __name__ == '__main__':
    total = 0
    cache = {}
    for p in design.d.all_parts():
        if not p.fp:
            continue
        if p.fp not in cache:
            fp = load(p.fp)
            bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox() if fp.GetCourtyard(pcbnew.F_CrtYd).OutlineCount() else fp.GetBoundingBox(False)
            pads = {pd.GetNumber() for pd in fp.Pads()}
            cache[p.fp] = (pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight()), pads)
        w, h, pads = cache[p.fp]
        total += w * h
        missing = [n for n, net in p.nets.items() if net and n not in pads]
        extra = [n for n in pads if n and n not in p.nets]
        if missing or extra:
            print(f'{p.ref:6s} {p.fp}: pins w/o pad {missing}  pads w/o pin {sorted(extra)[:8]}')
    for k, (w, h, _) in sorted(cache.items(), key=lambda kv: -kv[1][0] * kv[1][1])[:12]:
        print(f'{w:6.2f} x {h:5.2f}  {k}')
    print(f'total courtyard area {total:.0f} mm^2')
