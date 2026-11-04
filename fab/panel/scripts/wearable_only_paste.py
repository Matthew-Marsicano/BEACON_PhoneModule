"""Gerber set for 'fabricate the whole panel, assemble only the wearable': identical to gerbers/
except the paste layers, which keep only the wearable's pads so the JLC stencil prints no paste on
the phone module. Run with a python that has gerbonara:  python scripts/wearable_only_paste.py
"""
import shutil
import zipfile
from pathlib import Path

from gerbonara import GerberFile
from gerbonara.utils import MM

here = Path(__file__).resolve().parent.parent
src, out = here / "gerbers", here / "gerbers_wearable_assembly"
W_DIR = Path(r"C:\Users\marsi\KiCAD\BEACON_PhoneModule\fab\wearable\gerbers")
W_OFF = (63.5, 31.225)

out.mkdir(exist_ok=True)
for f in src.iterdir():
    shutil.copy2(f, out / f.name)
for ext in ("GTP", "GBP"):
    g = GerberFile.open(W_DIR / f"PCB1.{ext}")
    g.offset(*W_OFF, MM)
    g.save(out / f"panel.{ext}")
    print(f"panel.{ext}: {len(g.objects)} wearable paste objects, bbox {g.bounding_box(MM)}")

zp = here / "BEACON_Panel_gerbers_wearable_assembly.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(out.iterdir()):
        z.write(f, f.name)
print("wrote", zp)
