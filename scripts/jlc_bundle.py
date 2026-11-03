"""Pack everything JLCPCB needs into one zip: the Gerber/drill zip, the BOM and CPL in JLC format, and an order
sheet with the board options and the parts that need attention.  Run after export_fab.py (it calls this itself).

Run:  python scripts/jlc_bundle.py
"""
import os
import zipfile

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAB = os.path.join(PRJ, 'fab')
OUT = os.path.join(FAB, 'BEACON_PhoneModule_JLCPCB.zip')
# source file in fab/ -> name inside the bundle (numbered in upload order)
FILES = {'BEACON_PhoneModule_gerbers.zip': '1_UPLOAD_AS_GERBER_BEACON_PhoneModule_gerbers.zip',
         'BEACON_PhoneModule_BOM_JLC.csv': '2_UPLOAD_AS_BOM_BEACON_PhoneModule_BOM_JLC.csv',
         'BEACON_PhoneModule_CPL_JLC.csv': '3_UPLOAD_AS_CPL_BEACON_PhoneModule_CPL_JLC.csv'}

ORDER = """BEACON Phone Module - JLCPCB order sheet
=========================================

UNZIP THIS PACKAGE FIRST. Do not upload the package zip itself to JLCPCB: the Gerbers are inside the
file numbered 1, and JLC does not look inside nested zips (it reports "0 layers detected").

Upload
------
1. "Add Gerber file":           1_UPLOAD_AS_GERBER_BEACON_PhoneModule_gerbers.zip  (upload this zip as it is)
2. PCB Assembly -> BOM:         2_UPLOAD_AS_BOM_BEACON_PhoneModule_BOM_JLC.csv
3. PCB Assembly -> CPL:         3_UPLOAD_AS_CPL_BEACON_PhoneModule_CPL_JLC.csv

PCB options
-----------
Base material ......... FR-4
Layers ................ 4
Dimensions ............ 55 x 78.45 mm (detected from the Gerbers)
Thickness ............. 1.6 mm
Impedance control ..... Yes, stackup JLC04161H-7628 (50 ohm RF CPWG is sized for it)
Via covering .......... Epoxy filled & capped (via-in-pad, POFV) - REQUIRED, the nRF52840 has vias in its pads
Min via hole / diam. .. 0.15 mm / 0.3 mm
Surface finish ........ ENIG
Outer copper .......... 1 oz
Inner copper .......... 0.5 oz
Mark on PCB ........... Remove mark (or specify a location) so it does not land on the logo
Everything else ....... default

Assembly
--------
Type .................. Standard PCBA, top side, JLC-added tooling holes
J3 .................... BOM has no LCSC number: search "U.FL-R-SMT-1(10)" (Hirose) and select it
AE1 ................... Taoglas WDP.2458.25.4 patch antenna: not stocked at LCSC. Set "do not place" and
                        solder it yourself, or supply it as a consigned part
Placement preview ..... Check pin 1 of every IC against the board marking (U4-U8, filters FL1/FL2, USB-C J1).
                        QFN/SOT rotations are often off by 90 or 180 degrees; rotate in the viewer if needed

Not on the board
----------------
Taoglas FXP70.07.0053A flex antenna (TX): order separately, plugs into J3 at final assembly.
"""

missing = [f for f in FILES if not os.path.exists(os.path.join(FAB, f))]
if missing:
    raise SystemExit('run export_fab.py first, missing: ' + ', '.join(missing))
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('0_READ_ME_FIRST_JLCPCB_ORDER.txt', ORDER.replace('\n', '\r\n'))
    for src, name in FILES.items():
        z.write(os.path.join(FAB, src), name)
print('JLCPCB bundle:', OUT)
