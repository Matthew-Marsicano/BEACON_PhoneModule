"""Fabrication outputs for JLCPCB: Gerbers + drill (zipped), BOM and CPL in JLC format, schematic PDF, 3D STEP.

Run:  D:/KiCAD/bin/python.exe -I scripts/export_fab.py
"""
import csv
import os
import subprocess
import zipfile

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = r'D:\KiCAD\bin\kicad-cli.exe'
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
SCH = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_sch')
OUT = os.path.join(PRJ, 'fab')
GERB = os.path.join(OUT, 'gerbers')


def run(*args):
    r = subprocess.run([CLI, *args], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stdout + r.stderr)


os.makedirs(GERB, exist_ok=True)
layers = 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts'
# Gerbers, drill and CPL all use the drill/place origin (board bottom-left, set by finish.py) so they line up
run('pcb', 'export', 'gerbers', '--layers', layers, '--subtract-soldermask', '--use-drill-file-origin',
    '-o', GERB + os.sep, PCB)
run('pcb', 'export', 'drill', '--format', 'excellon', '--drill-origin', 'plot', '--excellon-separate-th', '--generate-map',
    '--map-format', 'gerberx2', '-o', GERB + os.sep, PCB)
with zipfile.ZipFile(os.path.join(OUT, 'BEACON_PhoneModule_gerbers.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(GERB)):
        z.write(os.path.join(GERB, f), f)

# LCSC part numbers from the sourcing table (docs/bom_lcsc.csv), keyed by designator
LCSC = {}
with open(os.path.join(PRJ, 'docs', 'bom_lcsc.csv'), newline='', encoding='utf8') as f:
    for row in csv.DictReader(f):
        for ref in row['Designator'].replace(' ', '').split(','):
            if row['LCSC Part #']:
                LCSC[ref] = row['LCSC Part #']

# BOM grouped by value+footprint, JLC column names (DNP and no-BOM parts excluded)
raw = os.path.join(OUT, 'bom_raw.csv')
run('sch', 'export', 'bom', '--fields', 'Reference,Value,Footprint,MPN,Manufacturer,${DNP},${EXCLUDE_FROM_BOM}',
    '--labels', 'Ref,Value,Footprint,MPN,Mfr,DNP,NoBOM', '--group-by', 'Value,Footprint,MPN,${DNP}',
    '--ref-range-delimiter', '', '-o', raw, SCH)
with open(raw, newline='', encoding='utf8') as f, \
        open(os.path.join(OUT, 'BEACON_PhoneModule_BOM_JLC.csv'), 'w', newline='', encoding='utf8') as g:
    w = csv.writer(g)
    w.writerow(['Comment', 'Designator', 'Footprint', 'MPN', 'Manufacturer', 'LCSC Part #'])
    for row in csv.DictReader(f):
        if row.get('DNP') or row.get('NoBOM') or row['Ref'].startswith('#'):
            continue
        refs = [r for r in row['Ref'].replace(' ', '').split(',') if r]
        lc = sorted({LCSC[r] for r in refs if r in LCSC})
        w.writerow([row['Value'], row['Ref'], row['Footprint'].split(':')[-1], row.get('MPN', ''),
                    row.get('Mfr', ''), ' / '.join(lc)])
os.remove(raw)

# CPL (placement) in JLC format
pos = os.path.join(OUT, 'pos_raw.csv')
run('pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--side', 'both', '--exclude-dnp',
    '--use-drill-file-origin', '-o', pos, PCB)
with open(pos, newline='', encoding='utf8') as f, \
        open(os.path.join(OUT, 'BEACON_PhoneModule_CPL_JLC.csv'), 'w', newline='', encoding='utf8') as g:
    w = csv.writer(g)
    w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for row in csv.DictReader(f):
        if row['Ref'].startswith('TP') or row['Ref'] == 'J2':
            continue  # bare test pads / Tag-Connect footprint: nothing to place
        w.writerow([row['Ref'], row['PosX'] + 'mm', row['PosY'] + 'mm',
                    'Top' if row['Side'] == 'top' else 'Bottom', row['Rot']])
os.remove(pos)

run('sch', 'export', 'pdf', '-o', os.path.join(OUT, 'BEACON_PhoneModule_schematic.pdf'), SCH)
run('pcb', 'export', 'pdf', '--layers', 'F.Fab,F.Courtyard,Edge.Cuts', '--mode-single',
    '-o', os.path.join(OUT, 'BEACON_PhoneModule_assembly_top.pdf'), PCB)
try:
    run('pcb', 'export', 'step', '--subst-models', '-o', os.path.join(OUT, 'BEACON_PhoneModule.step'), PCB)
except SystemExit as e:
    print('STEP export skipped:', str(e)[:200])
print('fab outputs in', OUT)
