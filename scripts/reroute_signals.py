"""Finish the remaining signal connections with Freerouting without touching existing copper and without GND tracks.

* every existing track/via is locked for the run (Freerouting keeps "protect" wires fixed), then unlocked again;
  with --unlock only the priority copper (USB, RF, GND/power nets) stays locked and other signals may be re-routed
* the 5V power fills are fenced with temporary keepouts (Freerouting does not see outer-layer fills)
* the GND net is emptied in the DSN so Freerouting never routes it (GND is pours + vias only, see gnd_pour.py);
  any GND track that still comes back is deleted
* L2 (GND) and L3 (3V3 / VCC_SYN) are plane layers, as in reroute.py

Run:  D:/KiCAD/bin/python.exe -I scripts/reroute_signals.py [--passes N] [--unlock]
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew  # noqa: E402
import route  # noqa: E402

PASSES = int(sys.argv[sys.argv.index('--passes') + 1]) if '--passes' in sys.argv else 20
board = pcbnew.LoadBoard(route.PCB)
board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)
gnd = board.FindNet('GND').GetNetCode()


def key(t):
    if t.GetClass() == 'PCB_VIA':
        return ('v', t.GetNetCode(), t.GetPosition().x, t.GetPosition().y)
    return ('t', t.GetNetCode(), t.GetLayer(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y)


UNLOCK = '--unlock' in sys.argv     # let Freerouting rip up / move ordinary signal tracks too
RF = {'RX_PATCH', 'SYN_OUTAP', 'CW_RF', 'PA_IN', 'PA_OUT', 'PA_MATCH', 'TX_LPF', 'TX_ANT', 'NRF_ANT', 'RX_RF',
      'RX_ATT', 'LNA_OUT', 'LNA_IN', 'RX_BPF', 'RX_ANT'}
FIXED_NETS = {'GND', '3V3', '/CW_Synth/VCC_SYN', '5V0', '5V_BUS', 'USB_D+', 'USB_D-'}


def priority(t):
    n = t.GetNetname()
    return n in FIXED_NETS or n.rsplit('/', 1)[-1] in RF


was_locked = {key(t) for t in board.GetTracks() if t.IsLocked()}
for t in board.GetTracks():
    t.SetLocked(True if not UNLOCK else (priority(t) or t.IsLocked()))

# Freerouting does not see copper fills on the outer layers: fence the 5V power fills with temporary keepouts
temp_keepouts = []
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
for z in [board.GetArea(i) for i in range(board.GetAreaCount())]:
    if z.GetIsRuleArea() or z.GetNetname() == 'GND':
        continue
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        if not z.GetLayerSet().Contains(layer):
            continue
        polys = z.GetFilledPolysList(layer)
        for k in range(polys.OutlineCount()):
            ko = pcbnew.ZONE(board)
            ko.SetIsRuleArea(True)
            ko.SetDoNotAllowTracks(True); ko.SetDoNotAllowVias(True); ko.SetDoNotAllowPads(False)
            ko.SetDoNotAllowFootprints(False); ko.SetDoNotAllowZoneFills(False)
            ko.SetLayer(layer)
            ol = ko.Outline(); ol.NewOutline()
            ch = polys.Outline(k)
            for i in range(ch.PointCount()):
                ol.Append(ch.CPoint(i).x, ch.CPoint(i).y)
            board.Add(ko)
            temp_keepouts.append(ko)
print('temporary keepouts over power fills:', len(temp_keepouts))

os.makedirs(route.WORK, exist_ok=True)
dsn, ses = os.path.join(route.WORK, 'beacon_sig.dsn'), os.path.join(route.WORK, 'beacon_sig.ses')
if os.path.exists(ses):
    os.remove(ses)
pcbnew.ExportSpecctraDSN(board, dsn)
txt = open(dsn, encoding='utf8').read()
txt = re.sub(r'(\(via (?:"[^"]+" ?)+)', lambda m: m.group(1).replace(' "Via[0-3]_300:150_um"', ''), txt, count=1)
txt, n = re.subn(r'(\(net GND\s*\(pins)[^)]*\)', r'\1)', txt, count=1)
print('GND pins removed from DSN:', n)
open(dsn, 'w', encoding='utf8').write(txt)

cmd = [route.JAVA, '-jar', route.JAR, '-de', dsn, '-do', ses, '-mp', str(PASSES), '-mt', '8', '--gui.enabled=false']
r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
open(os.path.join(route.WORK, 'freerouting_sig.log'), 'w').write(r.stdout + r.stderr)
print('\n'.join(ln for ln in (r.stdout + r.stderr).splitlines() if 'completed' in ln.lower())[-2000:])
if not os.path.exists(ses):
    sys.exit('no session file')
pcbnew.ImportSpecctraSES(board, ses)

graveyard = []   # keep removed items referenced (SWIG wrapper lifetime, see plane_nets.py)
for t in [t for t in board.GetTracks() if t.GetClass() != 'PCB_VIA' and t.GetNetCode() == gnd]:
    board.Remove(t)
    graveyard.append(t)
print('GND tracks from the router deleted:', len(graveyard))
for t in board.GetTracks():
    t.SetLocked(key(t) in was_locked)
for ko in temp_keepouts:
    board.Remove(ko)
graveyard.extend(temp_keepouts)

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
board.BuildConnectivity()
print('unrouted connections:', board.GetConnectivity().GetUnconnectedCount(False))
pcbnew.SaveBoard(route.PCB, board)
print('saved', route.PCB)
