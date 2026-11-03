"""Incremental completion pass after route.py: drop route.py's first-pass stitching vias, add an L3 VCC_SYN pour under
the synthesizer, then let Freerouting finish the remaining connections on top of the existing wiring.

Run:  D:/KiCAD/bin/python.exe -I scripts/reroute.py [--passes N]
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew  # noqa: E402
from pcbnew import FromMM, ToMM  # noqa: E402
import route  # noqa: E402

PASSES = int(sys.argv[sys.argv.index('--passes') + 1]) if '--passes' in sys.argv else 25
board = pcbnew.LoadBoard(route.PCB)
board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)

# 1) first-pass stitching vias from route.stitching(): unlocked GND vias with a 0.2 mm drill
gone = 0
for t in list(board.GetTracks()):
    if t.GetClass() == 'PCB_VIA' and t.GetNetname() == 'GND' and not t.IsLocked() and abs(ToMM(t.GetDrillValue()) - 0.2) < 1e-3:
        board.Remove(t)
        gone += 1
print('removed first-pass stitching vias:', gone)

# 2) planes: L2 GND and L3 (3V3 + islands) are plane layers - nothing routes on them
board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())

# 3) Freerouting on top of the existing wiring
os.makedirs(route.WORK, exist_ok=True)
dsn, ses = os.path.join(route.WORK, 'beacon_inc.dsn'), os.path.join(route.WORK, 'beacon_inc.ses')
pcbnew.ExportSpecctraDSN(board, dsn)
txt = open(dsn, encoding='utf8').read()
txt = re.sub(r'(\(via (?:"[^"]+" ?)+)', lambda m: m.group(1).replace(' "Via[0-3]_300:150_um"', ''), txt, count=1)
open(dsn, 'w', encoding='utf8').write(txt)
cmd = [route.JAVA, '-jar', route.JAR, '-de', dsn, '-do', ses, '-mp', str(PASSES), '-mt', '8', '--gui.enabled=false']
r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
open(os.path.join(route.WORK, 'freerouting_inc.log'), 'w').write(r.stdout + r.stderr)
print('\n'.join(ln for ln in (r.stdout + r.stderr).splitlines() if 'Auto-routing stage completed' in ln))
if not os.path.exists(ses):
    sys.exit('no session file')
pcbnew.ImportSpecctraSES(board, ses)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(route.PCB, board)
print('saved', route.PCB)
