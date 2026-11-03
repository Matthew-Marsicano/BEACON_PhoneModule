# BEACON_PhoneModule: stackup, RF line geometry and design rules

Board: about 45 x 25 mm, 4 layers, 1.6 mm, JLCPCB fab and assembly, KiCad 10.
Companion file: `docs/BEACON_PhoneModule.kicad_dru.proposed`. Copy it to `BEACON_PhoneModule.kicad_dru` next to the `.kicad_pro`, or paste it into Board Setup > Custom Rules.

Date: 2026-11-02. JLCPCB data was read from jlcpcb.com/impedance and jlcpcb.com/capabilities/pcb-capabilities on that date.

---

## 1. Stackup: JLC04161H-7628 (impedance-controlled, 4 layers, 1.6 mm)

| # | Layer (KiCad) | Material | Thickness | Er | Use |
|---|---|---|---|---|---|
| L1 | F.Cu | Copper, 1 oz finished | 0.035 mm | n/a | Parts, all RF CPWG, USB pair, short signals, GND pour |
| | Prepreg | 7628 x1 | 0.2104 mm | 4.4 | L1-L2 dielectric (sets RF impedance) |
| L2 | In1.Cu | Copper, 0.5 oz | 0.0152 mm | n/a | Solid GND. No splits, no tracks. |
| | Core | FR-4 core | 1.065 mm | 4.6 | |
| L3 | In2.Cu | Copper, 0.5 oz | 0.0152 mm | n/a | Power pours and tracks, slow signals |
| | Prepreg | 7628 x1 | 0.2104 mm | 4.4 | |
| L4 | B.Cu | Copper, 1 oz finished | 0.035 mm | n/a | Signals and GND pour |

- The copper and dielectric layers sum to about 1.586 mm. Mask and finish bring it to the nominal 1.6 mm.
- Solder-mask parameters from JLC's impedance page, used in the calculations below: CEr 3.8, C2 0.6 mil (15.2 um) over traces, C3 1.2 mil (30.5 um) between traces, C1 1.2 mil over bare substrate.
- In KiCad, set Board Setup > Physical Stackup to 4 layers with exactly these thicknesses and Er values, and set the board thickness to 1.6 mm. When ordering, select "Impedance control: yes, JLC04161H-7628" and give the target: 50 ohm coplanar with ground on L1 referenced to L2, W 0.30 / gap 0.20 mm.
- Surface finish: ENIG. JLC requires ENIG for 0.20-0.25 mm BGA-type pads. The nRF52840 aQFN-73 pads are 0.25 mm round. ENIG also gives flat 0.5 mm-pitch QFN lands.

**Why 7628 rather than 3313.** JLC04161H-3313 has a 0.0994 mm prepreg (Er 4.1). On that stackup a 50 ohm CPWG is only 0.13-0.17 mm wide. That is narrower than every RF land on the board: 0402 pads are 0.5-0.6 mm, the U.FL centre pad is 1.0 mm, and the LTCC/IC pins are 0.22-0.36 mm. The result would be larger pad discontinuities, higher loss, and a line close to the 0.09 mm fab minimum, where +-0.02 mm etch is a large fraction of the width. On 7628 the 50 ohm line is 0.30 mm, which is about the width of the RF IC pins and filter lands.

---

## 2. RF line geometry (50 ohm, 2.45 GHz, L1 over L2)

### Method
Calculated with a plain-Python CPWG/microstrip script (not in this repository), cross-checked against the JLCPCB impedance calculator.

1. **Closed form, CPWG.** Wadell, *Transmission Line Design Handbook* section 3.4.3, conductor-backed CPW with infinite side grounds:
   - k = W/(W+2G)
   - k3 = tanh(pi W/4h) / tanh(pi (W+2G)/4h)
   - eeff = (1 + Er q)/(1 + q), with q = K(k')/K(k) * K(k3)/K(k3')
   - Z0 = 60 pi / sqrt(eeff) / (K(k)/K(k') + K(k3)/K(k3'))
   - The strip-thickness correction is Gupta/Bahl: Delta = 1.25t/pi [1 + ln(4 pi W/t)], W -> W+Delta, G -> G-Delta, plus an eeff correction.
   - K() is evaluated by AGM.
2. **Closed form, microstrip.** Hammerstad-Jensen, with thickness correction.
3. **Quasi-static 2-D field solver.** Finite-volume Laplace solver on a graded grid, 2 um cells at copper edges. It models the real 35 um copper and the JLC solder-mask profile above. Cross-checks:
   - Microstrip agrees with Hammerstad-Jensen within 0.5 %.
   - As t -> 0 it converges to the exact zero-thickness Wadell CPWG value: 54.2 ohm against 54.8 ohm at t = 0.5 um.
   - The closed-form thickness correction over-corrects for 35 um copper on 0.21 mm dielectric. **Treat the solver columns as the design values.**

Dispersion at 2.45 GHz on a 0.21 mm substrate is negligible (< 0.3 %), so these quasi-static values apply at 2.45 GHz.

### Results: JLC04161H-7628 (h = 0.2104 mm, Er 4.4, t = 35 um)

| Gap G (mm) | W, closed form + t-corr | W, solver, bare copper | eeff (bare) | **W, solver, with JLC mask** | eeff (masked) |
|---|---|---|---|---|---|
| 0.100 | n/a (t-corr invalid) | 0.241 | 2.61 | 0.194 | 3.03 |
| 0.127 | 0.243 | 0.274 | 2.72 | 0.234 | 3.06 |
| 0.150 | 0.269 | 0.293 | 2.79 | 0.258 | 3.10 |
| **0.200** | 0.303 | 0.321 | 2.90 | **0.292** | 3.16 |
| 0.250 | 0.321 | 0.337 | 2.98 | 0.311 | 3.21 |
| Plain microstrip (no coplanar GND) | 0.372 (H-J) | 0.370 | 3.19 | 0.348 | 3.39 |

Spot checks with the solver:

| Geometry W / G (mm) | Z bare (ohm) | Z masked (ohm) |
|---|---|---|
| **0.30 / 0.20 (recommended)** | 51.7 | 49.3 |
| 0.29 / 0.20 | 52.6 | 50.1 |
| 0.26 / 0.15 (compact alternative) | 52.8 | 49.8 |
| 0.28 / 0.18 | 52.7 | 50.0 |

Etch sensitivity, masked, at W +-0.025 mm with G changing by the opposite amount:

| Geometry | W - 0.025 | W + 0.025 |
|---|---|---|
| 0.29 / 0.20 | 53.1 ohm | 47.2 ohm |
| 0.26 / 0.15 | 53.6 ohm | 46.0 ohm |

Both stay inside JLC's +-10 % impedance tolerance.

For comparison, JLC04161H-3313 (h = 0.0994 mm, Er 4.1), masked: W = 0.138 / 0.146 / 0.150 mm at G = 0.15 / 0.20 / 0.25 mm. Microstrip W = 0.155 mm masked, 0.174 mm bare.

### Recommendation

| Parameter | Value |
|---|---|
| **CPWG track width W** | **0.30 mm** |
| **CPWG gap G (track edge to L1 GND copper)** | **0.20 mm** |
| Reference | L2 solid GND, 0.2104 mm below |
| Expected Z0 | 49.3 ohm masked, 51.7 ohm bare. This brackets 50 ohm, so the line is insensitive to the unknown mask profile. |
| eeff / lambda_g at 2.45 GHz | about 3.16 / 68.9 mm |
| Compact alternative where space is tight | W 0.26 / G 0.15 mm (49.8 ohm masked) |

**Via fence and stitching**
- Fence vias: 0.3 mm drill / 0.5 mm pad, GND.
- Pitch: **1.0 mm, never more than 1.2 mm.**
  - At 2.45 GHz, lambda_g/20 = 3.4 mm.
  - The fence is sized for the PA harmonics instead. At the 3rd harmonic (7.35 GHz), lambda_g/20 = 1.15 mm. That matters for the LPF's stop band and for the PA->LPF->U.FL path.
- Row placement: one row on each side. Via centres sit 0.75 mm from the track centreline, which puts the via annulus edge 0.15 mm outside the slot edge.
- Additional vias:
  - At every bend.
  - At both ends of every series 0402.
  - Next to every GND land of FL1/FL2, U6, U7 and U8.
  - Two or more per U.FL ground tab.
  - Around the L1 pour perimeter, at <= 2 mm pitch elsewhere.

**Layout notes**
- Keep the CPWG at constant W through series 0402 parts and taper only into smaller lands.
  - Land sizes: nRF ANT 0.25 mm round; LTCC 0.22-0.36 mm; QFN/DFN pins 0.25 mm.
  - The DRC allows down to 0.20 mm inside those parts' courtyards.
- Bends: 45-degree chamfered or arc. No right angles.
- Keep L2 solid under the entire RF chain and its fences. No L2 tracks anywhere.
- U.FL centre pad: 1.0 x 1.05 mm over 0.21 mm of dielectric is roughly 0.25 pF. That gives about -20 dB return loss at 2.45 GHz, which is acceptable as drawn.
  - Option, only if a VNA shows it is needed: a 1.2 mm L2 void under the pad with L3 GND as the reference.
- The L1 GND pour sets the CPWG gap. Its zone clearance must be **<= 0.20 mm**; use 0.15 mm.
  - KiCad fills at max(zone clearance, rule clearance). The RF rule then forces exactly 0.20 mm.
  - Verified: a test fill came out at 0.200 mm.
- Use solid zone connections on RF GND lands. A DRC rule already does this for J3, J4, FL*, U6, U7 and U8.

---

## 3. JLCPCB 4-layer capabilities (from jlcpcb.com, 2026-11-02)

| Item | JLC limit | Used here |
|---|---|---|
| Min track / space, 1 oz outer | 0.09 / 0.09 mm (3.5 mil). 3 mil accepted in BGA fan-outs. | 0.127 general; 0.09 / 0.08 inside the U5 aQFN only |
| Inner layers | 0.5 oz finished by default; no separate inner width figure published | Same rules |
| Via hole / pad | 0.15 / 0.25 mm min. Pad should be hole +0.1 mm (+0.15 preferred). | Default 0.25 / 0.45 |
| Price breaks | 0.10/0.15 mm holes, and 0.20/0.25 mm holes with pad < 0.45 mm, cost extra | Pad >= 0.45 mm everywhere (DRC enforces this) |
| PTH annular ring | >= 0.20 recommended, 0.15 absolute (1 oz) | Footprints only |
| Via-in-pad (epoxy or Cu-paste filled and capped) | Available, 0.15-0.55 mm vias; default only for 6+ layers, so a paid option on 4 layers | **Not used** (see aQFN below) |
| Hole to hole | Vias 0.20 mm; pads 0.45 mm | Same |
| Via hole to track | 0.20 mm | hole_clearance 0.20 |
| PTH hole to track | 0.28 mm min (0.35 recommended) | 0.28 |
| Pad to track | 0.10 mm (0.09 at BGA pads) | 0.127 / 0.08 in U5 |
| SMD pad to pad, different nets | 0.15 mm | FL1 lands are 0.165 mm apart: OK |
| Copper to routed edge | >= 0.20 mm (0.4 for V-cut) | **0.30 mm** (J1 excepted) |
| Plated slot min width | 0.35 mm (length >= 2x width) | J1 shell slots are 0.45 x 1.8: OK |
| NPTH min | 0.50 mm | Rule |
| Solder-mask web | 0.10 mm (green, 1 oz); 0.13 mm for black/white | Board Setup |
| Silkscreen | Line >= 0.15 mm, text >= 1.0 mm, 0.15 mm to pads | Rules (text = warning) |
| Impedance tolerance | +-10 % standard (+-5 % on request) | |

### nRF52840 aQFN-73 (U5) fan-out
The lands are 0.25 mm round on a 0.5 mm pitch in two staggered perimeter rows, which leaves 0.25 mm between lands.

- **Outer row:** escape directly on L1.
- **Inner row:** route a single 0.09 mm track between two outer lands, which leaves 0.08 mm per side. This is inside JLC's "3 mil in BGA fan-out" allowance. The DRC allows 0.09 / 0.08 only inside U5's courtyard, and not against zones.
- **Inner-row GND pins:** tie them straight to the 4.85 mm centre pad.
- **Vias:** there is no room for a via between the rows. Putting a 0.15/0.25 via inside a 0.25 mm land is a paid via-in-pad and leaves no annular margin, so it is not recommended. Put fan-out vias (0.25/0.45) outside the package outline.
- Only the pins this design actually uses need to escape.

### Thermal vias already in library footprints
- U8 (LMX2582 RHA-40) and U7 (CC2595 VQFN-16) have 0.2 mm drill / 0.5 mm vias in the EP.
- They pass all rules at standard price.
- They are unfilled, so expect some solder wicking. JLC's standard process accepts this.
- The LT80602 EP is VIN (5V0), not GND. See the Power sheet.

---

## 4. Net classes

### Board Setup > Constraints (required)
KiCad's new-board defaults would otherwise override the custom rules:

| Setting | Value |
|---|---|
| Min clearance | 0.08 |
| Min track width | 0.09 |
| Min connection width | 0.15 |
| Min annular width | 0.075 |
| Min via diameter | 0.45 |
| Copper to edge clearance | 0.30 |
| Min through hole | 0.20 |
| Hole to hole | 0.20 |
| Hole clearance | 0.20 |
| Min uVia | n/a |
| Silk clearance | 0 (rule handles pads) |
| Min text height / thickness | 1.0 / 0.15 |
| Solder mask min web | 0.10 |

### Net class table

| Class | Track (opt) | Clearance | Via pad / drill | Diff pair W / gap | Nets (patterns) |
|---|---|---|---|---|---|
| **Default** | 0.15 (DRC min 0.127) | 0.15 (DRC min 0.127) | 0.45 / 0.25 | n/a | everything else, including GND (pours) |
| **Power** | 0.40 on L1/L4 (min 0.30; 0.20 neck-down inside courtyards); **0.60 on L3** (min 0.50) | 0.20 | 0.60 / 0.30 (min 0.50 / 0.30) | n/a | `3V3`, `5V0`, `5V_BUS`, `VDD_PA`, `VCC_SYN`, `*/VBUS_C`, `*/3V3_OUT`, `*/LNA_VCC`, `*/PA_AVDD1`, `*/REG_SW`, `*/5V_SNS_?`, `*/3V3_SNS_?` |
| **RF** | **0.30** (min 0.29, max 0.31; 0.20 taper inside RF-part courtyards) | **0.20** (= CPWG gap; 0.15 inside RF-part courtyards) | 0.50 / 0.30 (no RF vias allowed; size used for GND fences) | n/a | `CW_RF`, `RX_RF`, `*/SYN_OUTAP`, `*/SYN_OUTAM`, `*/SYN_OUTAM_T`, `*/PA_IN`, `*/PA_OUT`, `*/PA_MATCH`, `*/TX_LPF`, `*/TX_ANT`, `*/RX_ANT`, `*/RX_BPF`, `*/LNA_IN`, `*/LNA_OUT`, `*/NRF_ANT` |
| **USB** | 0.20 | 0.20 to other nets | 0.45 / 0.25 | **0.20 / 0.13** (L1, gap range 0.12-0.18) | `USB_D+`, `USB_D-` (after rename, see below) |

**Power sizing (0.6 A).**
- IPC-2221 with a 10 C rise gives 0.15 mm on 1 oz outer copper and 0.89 mm on 0.5 oz inner copper. At a 20 C rise the inner figure is 0.58 mm.
- IPC-2221 is very conservative for inner layers. Use 0.40 mm on L1/L4. On L3, use 0.60 mm tracks or, better, pours.
- Drop at 0.6 A over 20 mm: 15 mV with 0.4 mm on L1, 27 mV with 0.5 mm on L3. That stays well inside the LMX2582 headroom note on the Power sheet.
- Use two vias per layer change on power nets.
- The `*_SNS_*` shunt nets carry the full current. Their INA219 Kelvin taps may neck to 0.20 mm inside the INA219 courtyard.

**USB 90 ohm (L1 over L2, edge-coupled, JLC mask)**

| Geometry W / S | Coplanar GND | Zdiff masked | Zdiff bare |
|---|---|---|---|
| **0.20 / 0.13 (recommended)** | none | 91.7 ohm | 99.1 ohm |
| 0.20 / 0.13 | at 0.30 mm | 90.8 ohm | 98.2 ohm |
| 0.20 / 0.13 | at 0.20 mm | 89.3 ohm | 96.8 ohm |
| 0.20 / 0.15 | none / 0.2 mm | 95.5 / 92.8 ohm | n/a |

- Other options: W 0.15 / S 0.094 and W 0.25 / S 0.163 also give 90 ohm masked.
- USB 2.0 Full Speed (12 Mb/s) tolerates 90 ohm +-15 % easily. The real requirements are short length, D+/D- matched within 1 mm (DRC skew rule), and an unbroken L2 underneath.
- **Rename needed:** KiCad only pairs nets whose names end in `+`/`-` or `P`/`N`. `USB_DP`/`USB_DM` are **not** recognised. Rename the global labels to `USB_D+`/`USB_D-` (or `USB_DP`/`USB_DN`), otherwise the diff-pair router and the gap/skew rules do nothing.
- Verified: KiCad 10 treated `USB_D+`/`USB_D-` at a 0.13 mm gap as a coupled pair.

Net-name note: local labels become `/<sheet name>/<label>` in the PCB. That is why the patterns use a `*/` prefix. Check the actual names once the board is created.

---

## 5. Custom rules file (`BEACON_PhoneModule.kicad_dru.proposed`)

Syntax: KiCad rules version 1, per KiCad 10's built-in rule-syntax help and docs.kicad.org (pcbnew > Custom design rules). For each constraint, the last matching rule in the file wins.

| Rule group | What it enforces |
|---|---|
| JLC fab limits | Track and clearance >= 0.127; edge 0.30; via pad >= 0.45 (standard-price band); annulus >= 0.075; hole 0.2-6.3; plated slot >= 0.35; NPTH >= 0.5; hole-to-hole 0.2 (vias) / 0.45 (pads, different nets); via hole clearance 0.20; PTH hole clearance 0.28; courtyard overlap; silk to pad 0.15; silk text 1.0 / 0.15 (warning) |
| J1 USB-C plug | `edge_clearance` ignored for J1 items, because the plug pads sit at the edge |
| Power | 0.30 min / 0.40 opt outer; 0.50 / 0.60 inner; 0.20 inside courtyards; clearance 0.20; vias 0.5-0.6 / 0.3; spoke 0.3 |
| USB | L1 width 0.20 (0.19-0.21); diff gap 0.13 (0.12-0.18); uncoupled <= 3 mm; skew <= 1 mm within the pair; 0.20 to other nets |
| RF | Width 0.30 (0.29-0.31); clearance 0.20 (sets the pour gap); **RF only on F.Cu and no RF vias**; taper down to 0.20 and clearance 0.15 inside U5/U6/U7/U8/FL*/J3/J4 courtyards; solid zone connection for RF GND lands |
| U5 aQFN-73 | Track min 0.09 and clearance 0.08 inside U5's courtyard (non-RF, non-zone items only) |

**Verification (KiCad 10.0.7 `kicad-cli pcb drc`).**
- Every rule was first loaded alone to check that it parses. One syntax error was found and fixed: `skew ... (within_diff_pairs)` needs the parentheses.
- The final file was then run against a scratch test board in `scratchpad\drctest\`, built with the real J1 and aQFN-73 footprints. Exactly the intended violations appeared: RF gap 0.17 < 0.20, RF track on In1, RF via, 0.15 mm RF track, 0.20 mm Power track, 0.10 mm Default track, 0.35 mm via, and copper 0.075 mm from the edge.
- These passed as intended: the J1 edge pads, the 0.09 mm aQFN escape, the coupled USB pair at 0.13 mm, the 0.50 mm L3 power track, and the 0.25/0.45 via.
- A GND pour refilled at exactly 0.200 mm from the RF track and 0.30 mm from the edge.

The rules refer to reference designators (J1, J3, J4, U5-U8, FL*). If the annotation changes, update the rules, or switch them to library IDs such as `A.intersectsCourtyard('Package_DFN_QFN:Nordic_AQFN-73*')`.

---

## 6. Unverified assumptions / open items

1. **JLC Er values and frequency.** The Er values (7628 = 4.4, core = 4.6) are JLC's nominal figures. JLC does not state the frequency they apply at. At 2.45 GHz, 7628 FR-4 is typically 4.2-4.3, which would raise Z0 by about 1 ohm. That is inside the bracket the recommended geometry already covers.
2. **Outer copper thickness.** The 35 um outer copper is taken as the finished thickness. JLC's page does not say whether this includes plating. At 45-50 um, Z0 drops by about 1 ohm.
3. **Mask model.** The solder-mask model (C2 15 um over copper, C3 30 um in gaps, Er 3.8) is a solver idealisation of JLC's published parameters. The bare-copper and masked results bracket the real value: 51.7 and 49.3 ohm for 0.30/0.20.
4. **No JLC calculator cross-check.** JLC's online impedance calculator could not be driven from here; it returned "No data". Before ordering, enter W 0.30 / G 0.20, "coplanar single-ended with ground", L1 referenced to L2, in JLC's calculator. Let JLC adjust the width if you select impedance control.
5. **Third-party comparison point.** A third-party Saturn PCB Toolkit value (LibreCAL PR #8) quotes 0.34 / 0.20 mm for the same stackup. Saturn's inputs are unknown, probably no mask and a different copper thickness. With the solver here, 0.34 / 0.20 gives 48.6 ohm bare and 46.5 ohm masked.
6. **Plated slot minimum.** JLC's capabilities page now says 0.35 mm; older JLC guidance said 0.5 mm. The J1 slots are 0.45 mm. **Confirm with JLC, or widen them to 0.5 mm.** The J1 footprint itself notes that its shell slot geometry is approximated and must be checked against the Same Sky drawing.
7. **J1 silkscreen text.** J1's reference text is 0.5 mm high with 0.08 mm lines, which gives a JLC silk warning. Fix it in the footprint if silk is wanted.
8. **Net names.** RF/Power netclass patterns are inferred from schematic label names. The PCB net names (sheet paths) did not exist yet; no `.kicad_pcb` was in the project.
9. **aQFN-73 escape.** The 0.09 / 0.08 mm escape relies on JLC's "3 mil in BGA fan-out" allowance. JLC's DFM may flag it; it is still above their 3 mil (0.076 mm) floor. To avoid it entirely, leave inner-row pins unused, or tie them to the EP, wherever the pin assignment allows.
10. **Via pricing interpretation.** Standard-price vias are taken as 0.25/0.45 and up, per JLC's wording "0.2/0.25 mm hole with via diameter < 0.45 mm costs more". Check the quote.
11. **Current capacity.** Power-width figures use IPC-2221. Thermal behaviour of the LT80602, CC2595 and LMX2582 EPs was not simulated.

## Sources
- JLCPCB impedance stackups: https://jlcpcb.com/impedance
- JLCPCB PCB capabilities: https://jlcpcb.com/capabilities/pcb-capabilities
- JLCPCB impedance calculator (inputs only): https://jlcpcb.com/pcb-impedance-calculator
- KiCad custom design rules: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html (Custom design rules). Constraint list and syntax were cross-checked against the rule-syntax help embedded in the installed KiCad 10.0.7 (`_pcbnew.dll`) and by running `kicad-cli`.
- LibreCAL PR #8 (Saturn CPWG figure for JLC04161H-7628): https://github.com/jankae/LibreCAL/pull/8
- B. C. Wadell, *Transmission Line Design Handbook*, Artech House, 1991, section 3.4.3 (CPWG); E. Hammerstad & O. Jensen, "Accurate models for microstrip computer-aided design", IEEE MTT-S 1980; K. C. Gupta et al., *Microstrip Lines and Slotlines*, thickness corrections.
