"""Compare the KiCad-exported netlist (kicad-cli sch export netlist) with design.py's intended nets."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexpr import parse, find, first  # noqa: E402
import design  # noqa: E402

net_file = sys.argv[1]
tree = parse(open(net_file, encoding='utf8').read())
actual = {}
for net in find(first(tree, 'nets'), 'net'):
    name = first(net, 'name')[1].split('/')[-1]
    pins = frozenset(f"{first(n, 'ref')[1]}.{first(n, 'pin')[1]}" for n in find(net, 'node'))
    actual[pins] = name

_, _, intended = design.d.check()
intended = {k: frozenset(p for p in v if not p.startswith('#')) for k, v in intended.items()}
bad = 0
act_sets = set(actual)
for name, pins in sorted(intended.items()):
    if not pins:
        continue
    if pins not in act_sets:
        bad += 1
        near = [actual[a] + ':' + ','.join(sorted(a)) for a in act_sets if a & pins]
        print(f'MISMATCH {name}: want {sorted(pins)}\n    got {near}')
print(f'{len(intended)} intended nets, {len(actual)} exported nets, {bad} mismatches')
