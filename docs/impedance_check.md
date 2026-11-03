# 50 Ω RF line check

## JLCPCB impedance calculator (run by the user, 2026-11-02)
- **Mode:** coplanar single-ended, without solder mask, L1 referenced to L2.
- **Result: 50 Ω at 13.17 mil width with an 8.0 mil gap, i.e. 0.335 mm / 0.203 mm.**
- **Stackup the calculator used:** L1 35 µm | 7628 prepreg (RC 49 %, 8.6 mil) 0.2104 mm | L2 15.2 µm | core 0.25 mm | L3 15.2 µm | 7628 0.2104 mm | L4 35 µm.
  - That core makes it the 0.8 mm board.
  - The L1–L2 dielectric (7628, 0.2104 mm) is the same on the 1.6 mm JLC04161H-7628, so the L1/L2 CPWG result applies to our 1.6 mm board unchanged.
- **Compared with the earlier in-house 2-D solver estimate** (`stackup_and_rules.md`, 0.30/0.20 mm, about 51.7 Ω bare): JLC asks for 0.035 mm more width.
- **Adopted:** `RF_W = 0.335`, `RF_GAP = 0.203` in `scripts/build_pcb.py`; RF net class 0.335/0.203; DRC rule 0.325–0.345 mm.
- **Solder mask** over the line lowers Z by about 2 Ω, to roughly 48 Ω. Order with impedance control so JLC can trim the width.

## Wearable PCB stackup (`C:\Users\marsi\Downloads\4layer-1oz-jlc2313-1.6mm.stackup`, Altium)
| Layer | Material | Thickness | Er |
|---|---|---|---|
| Top solder | Solder resist | 0.0127 mm | 3.8 |
| Top layer | Cu | 0.035 mm | |
| Dielectric 1 | 2313 prepreg | 0.10 mm | 4.05 |
| Mid layer 1 | Cu | 0.0175 mm | |
| Core | FR-4 | 1.265 mm | 4.5 |
| Mid layer 2 | Cu | 0.0175 mm | |
| Dielectric 2 | 2313 prepreg | 0.10 mm | 4.05 |
| Bottom layer | Cu | 0.035 mm | |

- The wearable is on the **JLC04161H-2313** stackup.
- Its L1–L2 dielectric is 0.10 mm, about half that of 7628, so a 50 Ω CPWG there is roughly 0.17–0.20 mm wide. Confirm with JLC's calculator if it's ever needed.
- **The phone module stays on 7628:**
  - Its RF parts have 0402-and-larger pads (0.5–0.6 mm) and LTCC filters. A 0.335 mm line is a much better match into those pads than a 0.18 mm one.
  - It's less sensitive to etch tolerance.
  - The two boards are ordered separately, so sharing a stackup isn't required.
- **If you'd rather standardise on 2313:** re-run JLC's calculator for 2313 and set `RF_W`/`RF_GAP` (`build_pcb.py`) and the RF net class (`route.py`) to the result, then rebuild and re-route.

## L2 reference plane
- **In1.Cu (L2)** is a plane layer (`LT_POWER`), exported to Freerouting as `(type power)`, so nothing is routed on it.
- **DRC enforces it:** the rule "L2 is the solid GND reference plane: no tracks" rejects any track there.
- **The only intended L2 openings:**
  - Via anti-pads.
  - The void under the Cinch SMA launch pad. It's part of that footprint's impedance design, and L3 is solid GND underneath it.
  - Anti-pads around the patch feed pin.
