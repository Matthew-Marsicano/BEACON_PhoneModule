"""Make wearable-only assembly files for the panel: keep only `_W` parts from the panel BOM/CPL.

The phone module on the panel is fabricated but left unassembled. Coordinates stay in panel
coordinates, designators keep their `_W` suffix. Run from fab/panel: python -I scripts/wearable_only.py
"""
import csv
from pathlib import Path

here = Path(__file__).resolve().parent.parent
bom_in, cpl_in = here / "BEACON_Panel_BOM_JLC.csv", here / "BEACON_Panel_CPL_JLC.csv"
bom_out = here / "BEACON_Panel_BOM_JLC_wearable_only.csv"
cpl_out = here / "BEACON_Panel_CPL_JLC_wearable_only.csv"

with open(bom_in, encoding="utf-8-sig", newline="") as f:
    r = csv.DictReader(f)
    fields, rows = r.fieldnames, list(r)

out_rows, des_bom = [], []
for row in rows:
    des = [d.strip() for d in row["Designator"].split(",") if d.strip().endswith("_W")]
    if not des:
        continue
    row = dict(row)
    row["Designator"] = ",".join(des)
    row["Board"] = "W"
    for k in ("Footprint", "MPN", "Manufacturer"):  # merged rows joined both boards' values with " / "
        if " / " in (row.get(k) or ""):
            row[k] = row[k].split(" / ")[-1]
    if (row.get("Notes") or "").startswith("W:"):
        row["Notes"] = row["Notes"][2:].strip()
    out_rows.append(row)
    des_bom += des

with open(bom_out, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(out_rows)

with open(cpl_in, encoding="utf-8-sig", newline="") as f:
    r = csv.DictReader(f)
    cfields, crow = r.fieldnames, [c for c in r if c["Designator"].endswith("_W")]
with open(cpl_out, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cfields)
    w.writeheader()
    w.writerows(crow)

sides = {}
for c in crow:
    sides[c["Layer"]] = sides.get(c["Layer"], 0) + 1
des_cpl = [c["Designator"] for c in crow]
print(f"BOM rows {len(out_rows)}, designators {len(des_bom)}; CPL {len(crow)} {sides}")
print("in BOM not CPL:", sorted(set(des_bom) - set(des_cpl)), "| in CPL not BOM:", sorted(set(des_cpl) - set(des_bom)))
xs = [float(c["Mid X"].rstrip("m")) for c in crow]
ys = [float(c["Mid Y"].rstrip("m")) for c in crow]
print(f"x {min(xs):.2f}..{max(xs):.2f}  y {min(ys):.2f}..{max(ys):.2f} (wearable area x 63.5..93.5, y 31.225..61.225)")
print("unique LCSC:", len({r['LCSC Part #'] for r in out_rows if r['LCSC Part #']}),
      "| no LCSC:", [r["Designator"] for r in out_rows if not r["LCSC Part #"]])
