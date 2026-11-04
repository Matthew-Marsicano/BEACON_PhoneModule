import csv, re, os
from collections import OrderedDict, Counter

FAB = r"C:\Users\marsi\KiCAD\BEACON_PhoneModule\fab"
OUT = os.path.dirname(os.path.abspath(__file__))
P_BOM = os.path.join(FAB, "BEACON_PhoneModule_BOM_JLC.csv")
P_CPL = os.path.join(FAB, "BEACON_PhoneModule_CPL_JLC.csv")
W_BOM = os.path.join(FAB, "wearable", "BEACON_Wearable_BOM_JLC.csv")
W_CPL = os.path.join(FAB, "wearable", "BEACON_Wearable_CPL_JLC.csv")
OFF = {"P": (6.5, 7.0), "W": (63.5, 31.225)}
BOUNDS = {"P": (6.5, 61.5, 7.0, 85.45), "W": (63.5, 93.5, 31.225, 61.225)}


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def split_des(s):
    return [d.strip() for d in s.split(",") if d.strip()]


def mm(v):
    return float(v.strip().lower().replace("mm", ""))


# ---------- per-board groups: key -> dict ----------
def phone_groups():
    groups = OrderedDict()
    for r in read(P_BOM):
        d = r["Designator"].strip()
        fp = r["Footprint"].strip()
        if fp.startswith(d + "_"):
            fp = fp[len(d) + 1:]
        lcsc = r["LCSC Part #"].strip()
        key = lcsc if lcsc else "NOLCSC:" + d
        g = groups.setdefault(key, dict(Comment=r["Comment"].strip(), Footprint=fp, LCSC=lcsc,
                                        MPN=r["MPN"].strip(), Manufacturer=r["Manufacturer"].strip(),
                                        des=[], notes=[], comments=[], fps=[], mpns=[], mfrs=[]))
        g["des"].append(d)
        g["comments"].append(r["Comment"].strip())
        g["fps"].append(fp)
        g["mpns"].append(r["MPN"].strip())
        g["mfrs"].append(r["Manufacturer"].strip())
    for k, g in groups.items():
        if not g["LCSC"]:
            g["notes"].append("No LCSC part. Consign it or hand-solder it.")
    return groups


SWAPS = {
    "B1": dict(Comment="SN74AUP2G04DCKR", MPN="SN74AUP2G04DCKR", Manufacturer="Texas Instruments", LCSC="C2865392",
               note="SWAP: was Nexperia 74AUP2G04GW-Q100H (JLC stock 0). Same AUP family, SC-70-6 land, same pinout."),
    "L3": dict(Comment="22uH", MPN="WPN4012H220MT", Manufacturer="Sunlord", LCSC="C370621",
               note="SWAP: was Coilcraft LPS4012-223MRC (not in JLC library). Same 4012 size, check land/Isat/DCR."),
}


def wearable_groups():
    groups = OrderedDict()
    for r in read(W_BOM):
        des = split_des(r["Designator"])
        row = dict(Comment=r["Comment"].strip(), Footprint=r["Footprint"].strip(), LCSC=r["LCSC Part #"].strip(),
                   MPN=r["MPN"].strip(), Manufacturer=r["Manufacturer"].strip())
        note = r.get("Notes", "").strip()
        if len(des) == 1 and des[0] in SWAPS:
            s = SWAPS[des[0]]
            row.update({k: s[k] for k in ("Comment", "MPN", "Manufacturer", "LCSC")})
            note = s["note"]
        qty = r.get("Quantity", "").strip()
        if qty and int(qty) != len(des):
            print(f"WARN wearable qty mismatch {des}: Quantity={qty}")
        key = row["LCSC"] if row["LCSC"] else "NOLCSC:" + des[0]
        if key in groups:  # same LCSC on two wearable rows: fold together
            g = groups[key]
        else:
            g = groups[key] = dict(row, des=[], notes=[], comments=[], fps=[], mpns=[], mfrs=[])
        g["des"] += des
        g["comments"].append(row["Comment"]); g["fps"].append(row["Footprint"])
        g["mpns"].append(row["MPN"]); g["mfrs"].append(row["Manufacturer"])
        if note:
            g["notes"].append(note)
    return groups


def uniq(xs):
    out = []
    for x in xs:
        if x and x not in out:
            out.append(x)
    return out


def natkey(d):
    m = re.match(r"([A-Za-z]+)(\d+)", d)
    return (m.group(1), int(m.group(2))) if m else (d, 0)


pg, wg = phone_groups(), wearable_groups()
p_lcsc = {k for k in pg if not k.startswith("NOLCSC")}
w_lcsc = {k for k in wg if not k.startswith("NOLCSC")}
shared = sorted(p_lcsc & w_lcsc, key=lambda s: int(s[1:]))

rows = []
for key in list(pg) + [k for k in wg if k not in pg]:
    parts = [(b, src[key]) for b, src in (("P", pg), ("W", wg)) if key in src]
    des, comments, fps, mpns, mfrs, notes = [], [], [], [], [], []
    for b, g in parts:
        des += [f"{d}_{b}" for d in sorted(g["des"], key=natkey)]
        comments += g["comments"]; fps += g["fps"]; mpns += g["mpns"]; mfrs += g["mfrs"]
        if len(parts) > 1:
            notes += [f"{b}: {n}" for n in g["notes"]]
        else:
            notes += g["notes"]
    board = "+".join(b for b, _ in parts)
    rows.append(dict(Comment=" / ".join(uniq(comments)), Designator=",".join(des),
                     Footprint=" / ".join(uniq(fps)), LCSC=parts[0][1]["LCSC"],
                     MPN=" / ".join(uniq(mpns)), Manufacturer=" / ".join(uniq(mfrs)),
                     Board=board, Notes=" ".join(notes)))

with open(os.path.join(OUT, "BEACON_Panel_BOM_JLC.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "MPN", "Manufacturer", "Board", "Notes"])
    for r in rows:
        w.writerow([r["Comment"], r["Designator"], r["Footprint"], r["LCSC"], r["MPN"], r["Manufacturer"], r["Board"], r["Notes"]])

# ---------- CPL ----------
cpl = []
side_count = Counter()
oob = []
for b, path in (("P", P_CPL), ("W", W_CPL)):
    ox, oy = OFF[b]
    x0, x1, y0, y1 = BOUNDS[b]
    for r in read(path):
        layer = r["Layer"].strip().capitalize()
        assert layer in ("Top", "Bottom"), (b, r)
        x, y = mm(r["Mid X"]) + ox, mm(r["Mid Y"]) + oy
        d = f'{r["Designator"].strip()}_{b}'
        side_count[(b, layer)] += 1
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            oob.append((d, round(x, 4), round(y, 4)))
        cpl.append([d, f"{x:.4f}mm", f"{y:.4f}mm", layer, r["Rotation"].strip()])

with open(os.path.join(OUT, "BEACON_Panel_CPL_JLC.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    w.writerows(cpl)

# ---------- checks ----------
print("CPL placements per board/side:", dict(side_count))
bom_des = Counter(d for r in rows for d in r["Designator"].split(","))
for b in "PW":
    print(f"BOM designators board {b}: {sum(v for d, v in bom_des.items() if d.endswith('_' + b))}")
dups = [d for d, c in bom_des.items() if c > 1]
cpl_des = Counter(c[0] for c in cpl)
cpl_dups = [d for d, c in cpl_des.items() if c > 1]
print("BOM designators in >1 row:", dups or "none")
print("CPL duplicate designators:", cpl_dups or "none")
print("In CPL, not in BOM:", sorted(set(cpl_des) - set(bom_des)) or "none")
print("In BOM, not in CPL:", sorted(set(bom_des) - set(cpl_des)) or "none")
print("Out of bounds:", oob or "none")
print(f"BOM rows: {len(rows)} (P only {sum(r['Board']=='P' for r in rows)}, W only {sum(r['Board']=='W' for r in rows)}, P+W {sum(r['Board']=='P+W' for r in rows)})")
print("Empty-LCSC rows:", [(r["Designator"], r["Comment"]) for r in rows if not r["LCSC"]])
print(f"Unique LCSC: phone {len(p_lcsc)}, wearable {len(w_lcsc)}, sum before merge {len(p_lcsc)+len(w_lcsc)}, after merge {len(p_lcsc|w_lcsc)}")
print(f"Shared LCSC ({len(shared)}):")
for s in shared:
    r = next(r for r in rows if r["LCSC"] == s)
    print(f"  {s}  {r['Comment']}  {r['Designator']}")
x = [mm(c[1]) for c in cpl]; y = [mm(c[2]) for c in cpl]
print(f"Panel centroid extent x {min(x):.3f}..{max(x):.3f}, y {min(y):.3f}..{max(y):.3f}")
