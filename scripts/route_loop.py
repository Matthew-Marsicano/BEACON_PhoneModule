"""Negotiated routing loop: alternate a parallel hard pass and a rip-up (soft) pass of scripts/netroute.py until
nothing is unconnected, keeping the best board seen (fewest unconnected + DRC errors) in route/best_loop.kicad_pcb.

Run (system Python):  python scripts/route_loop.py WORKDIR [ROUNDS] [--inner]
"""
import json
import os
import shutil
import subprocess
import sys

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
BEST = os.path.join(PRJ, 'route', 'best_loop.kicad_pcb')
KPY, KCLI = r'D:\KiCAD\bin\python.exe', r'D:\KiCAD\bin\kicad-cli.exe'
WORK = sys.argv[1]
ROUNDS = int(sys.argv[2]) if len(sys.argv) > 2 else 4
HIST = os.path.join(WORK, 'rip_history.json')
json.dump({}, open(HIST, 'w'))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return '\n'.join(ln for ln in (r.stdout + r.stderr).splitlines()
                     if not any(k in ln for k in ('image handler', 'memory leak', 'assert')))


def drc(tag):
    out = os.path.join(WORK, 'loop_%s.json' % tag)
    run([KCLI, 'pcb', 'drc', '--refill-zones', '--format', 'json', '--severity-error', '-o', out, PCB])
    d = json.load(open(out, encoding='utf8'))
    errs = [v for v in d['violations'] if v['type'] != 'unconnected_items']
    return out, len(d['unconnected_items']), len(errs)


def step(tag, soft):
    rep, n, e = drc(tag + '_in')
    geom = os.path.join(WORK, 'loop_%s_geom.json' % tag)
    run([KPY, '-I', os.path.join(PRJ, 'scripts', 'geomdump.py'), geom])
    res = os.path.join(WORK, 'loop_%s_routes.json' % tag)
    args = [sys.executable, '-u', os.path.join(PRJ, 'scripts', 'netroute.py'), geom, rep, res]
    args += (['--soft'] if soft else []) + ['--jobs', str(os.cpu_count()), '--history', HIST] + sys.argv[3:]
    print(run(args).splitlines()[-1], flush=True)
    if soft:                                   # remember whose copper was ripped (anti-oscillation)
        h = json.load(open(HIST))
        for r in json.load(open(res))['routed']:
            for k in r.get('rip', []):
                h[k[1]] = h.get(k[1], 0) + 1
        json.dump(h, open(HIST, 'w'))
    print(run([KPY, '-I', os.path.join(PRJ, 'scripts', 'apply_routes.py'), res]).strip().splitlines()[-1], flush=True)


_, n0, e0 = drc('start')
best = n0 + 5 * e0
shutil.copy(PCB, BEST)
print('start: %d unconnected, %d errors' % (n0, e0), flush=True)
for k in range(ROUNDS):
    for soft in (False, True):
        tag = '%d%s' % (k, 's' if soft else 'h')
        step(tag, soft)
        _, n, e = drc(tag + '_out')
        score = n + 5 * e
        print('round %s: %d unconnected, %d errors%s' % (tag, n, e, '  <- best' if score < best else ''), flush=True)
        if score < best:
            best = score
            shutil.copy(PCB, BEST)
        if n == 0:
            break
    if n == 0:
        break
shutil.copy(BEST, PCB)
print('board restored to the best state, score', best)
