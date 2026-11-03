# BEACON_PhoneModule: placement review against datasheet and EVM layouts

- **Date:** 2026-11-02.
- **Board reviewed:** `route/placed.kicad_pcb`, the placed, unrouted snapshot (161 footprints, 43 locked RF tracks and vias). I worked on a scratch copy; no project file was opened for writing.
- **Coordinates:** footprint origin `(x, y, rot)` in mm, **board-relative** (board top-left = 0,0; +y down), the same convention as `scripts/build_pcb.py`. To get absolute KiCad coordinates, add 100 to both x and y. Rotations are KiCad degrees, where +90 is counter-clockwise on screen. For a vertical 0402/0603, rot 90 puts pad 1 at the bottom and rot 270 puts pad 1 at the top.
- **"Gap"** is pad edge to pad edge.
- **Verification:** every move proposed below was applied to a scratch copy. The checker then confirmed **0 courtyard overlaps** (U5 counted with the shrunk courtyard from N-1) and **0 mounting-hole keep-out hits**. It also read back the new gaps. Before/after renders (F.Cu + F.Fab + F.Courtyard) are in `docs/layout_review/*_before.png` and `*_after.png`.

**References used:**
- **ADI LT80602/LT80603 Rev 2**, p.27 "Low EMI PCB Layout" and Figure 73 (`layout_review/ref_lt80602_fig73.png`).
- **Nordic nRF52840 PS v1.11:**
  - §7.3.1, the QIAA config 1 reference circuit.
  - §7.3.15/16, layout guidance and the aQFN LDO reference layout (Fig. 232/233).
  - I did not download the Nordic Altium reference-layout zip.
- **TI LMX2582 SNAS680E** §8.4, "Layout Guidelines" and Fig. 8-13 (EVM layout).
- **TI CC2595EM** schematic and the CC2595 datasheet land pattern.
- **Qorvo QPL9547 Rev D**, EVB and PCB pattern (local copy).
- **TDK DEA202450BT-1294D1-H** and **Johanson 2450LP07** land patterns, as already analysed in `bpf_alternative.md` and `footprint_review.md`.

---

## 0. Two root causes behind most deviations
1. **The stock `Nordic_AQFN-73-1EP_7x7mm_P0.5mm` courtyard is 9.05 × 9.05 mm, 1.0 mm beyond the 7 mm body.**
   - The greedy placer in `build_pcb.py` keeps parts outside courtyards plus 0.12 mm. So no nRF decoupling cap could get closer than about 1.6 mm to its ball, and most ended up 1.7 to 3.8 mm away.
   - The Nordic reference layout puts them right at the package edge.
   - **Fix (N-1):** use a project copy of the footprint with the F.CrtYd rectangle at ±3.75 mm (body + 0.25).
2. **The greedy placer targets the first pad it finds on a shared rail net, not the pin named in the Note.**
   - The `Note` only helps when it contains the pad *number* string. Notes like "VIN2-GND2" or "TCXO VCC" do not match, so on VCC_SYN, 3V3 and 5V0 caps land at a random pin of the right net.
   - Examples:
     - **C8**, the "VIN2-GND2" hot-loop cap, sits on the VIN1 side.
     - **C47**, "TCXO VCC", sits at LMX pin 11, 7 mm from the TCXO.
     - **C3/C5**, the INA219 VS caps, sit next to the nRF.
     - **C70**, the "pull-up common node", sits on the opposite side of the LMX from R41/R42.
   - **Fix:** add an explicit `PLACEMENT_OVERRIDES = {ref: (x, y, rot)}` table in `build_pcb.py`, applied after the RF chains and before the greedy loop (so the greedy parts flow around them). Fill it from the move table in §10.

---

## 1. LT80602 buck (U4 at 10.00, 62.00, rot 0)

Pin map from the footprint:
- **Left side:** 1 GND, 2 BST, 3 VIN1.
- **Bottom:** 4/5 GND1, 6 SW, 7/8 GND2.
- **Right side:** 9 VIN2, 10 EN/UV (5V0), 11 BIAS/VOUT, 12 FB.
- **Top:** 13 RT, 14 SS, 15 SYNC, 16 PG, 17 INTVCC.
- **EP** is 5V0.

**What matches**
- The EP is on 5V0, as the datasheet requires (EP = VIN).
- The bulk input cap C6 (4.7 µF) is near the VIN2/EN side.
- The SS cap C9 is 0.92 mm from pin 14 and the RT resistor R9 is 1.62 mm from pin 13. Both are on the quiet top side, away from SW.
- The INTVCC cap C10 is on the INTVCC corner.
- The FB divider R10/R11 is on the top side, away from SW.
- All power parts are on F.Cu, as ADI asks ("same side, connections on that layer").

| # | Deviation (measured) | Sev | Fix (verified) |
|---|---|---|---|
| 1.1 | **C8, the VIN2-GND2 hot-loop cap, is on the wrong side.** It sits at (7.12, 60.60), next to pins 1 and 17, so pin 9/8 has no local 0.1 µF. | **must** | Move C8 to **(12.60, 63.55, 270)**. Pad 1 (5V0) then faces pin 9 with a 0.50 mm gap, and pad 2 (GND) faces pin 8 with 0.89 mm. This mirrors CIN2 in ADI Fig. 73. |
| 1.2 | **C7, the VIN1-GND1 cap, is rotated so its 5V0 pad faces GND1 (pin 4) and its GND pad faces BST/VIN1.** The loop crosses itself. | **must** | Move C7 to **(7.40, 63.55, 270)**. 5V0 faces pin 3 with a 0.50 mm gap and GND faces pin 4 with 0.89 mm. |
| 1.3 | **The output cap C13 (22 µF) sits between the SW pin and L1** at (10.50, 65.38). SW pin to L1 pad is about 6.5 mm with a detour. L1 is rotated so that its SW pad is 1.5 mm off-axis. | **must** | Move **L1 to (10.00, 67.30, 270)**, which puts the SW pad directly under pin 6 with a 1.45 mm straight run. Move **C13 to (6.60, 67.30, 90)** and **C14 to (13.40, 67.70, 90)**, flanking L1, with 3V3_OUT pads 0.97 mm from the L1 output pad. Their GND pads then sit 2-3 mm from the CIN GND pads, so the output return shares the input GND island (ADI). |
| 1.4 | **The BST cap C11 is 6.5 mm from pin 2,** at (6.35, 70.02). | **must** | Move C11 to **(6.94, 61.95, 180)**. The BST pad is then 0.50 mm from pin 2, as in ADI Fig. 73 (CBST left of pin 2). ADI routes the C11 SW pad to the SW node on layer 2. Here L2 is the solid GND plane, so route it on In2.Cu (L3) with 2 vias, or on F.Cu below C7, keeping it short. |
| 1.5 | The INTVCC cap C10 has a 1.21 mm gap (OK) but blocks the corner. | ok → should | Move to **(7.12, 59.90, 90)**: gap to pin 17 is 0.61 mm. |
| 1.6 | **The feed-forward cap C12 is 1.0 mm from pin 11, and the FB node runs about 5 mm** (C12 at x 14.07, R10/R11 at y 56-57.8, routed between the RT/SS parts). | should | Move C12 to **(12.62, 61.30, 90)**, straddling pins 11 and 12 (gaps 0.51 and 0.95). Keep R10/R11 where they are. |
| 1.7 | The 3V3 shunt R6 at (13.62, 64.09) blocks the new C8. | – | Move R6 to **(14.10, 64.15, 270)**. |
| 1.8 | The bulk cap C6 must move to make room for C12. | ok | Move C6 to **(14.75, 59.60, 0)**. Its 5V0 pad is 2.5 mm from pin 10, which is still "near VIN2" in ADI's sense. Connect it with a wide 5V0 pour that also carries the EP. |

**Routing notes:**
- Put a row of GND vias at y ≈ 64.4 on each side of the SW trace, under pins 4/5 and 7/8, as in Fig. 73.
- Keep the 5V0 EP pour on L3 (`magnetics_thermal.md` already says this).

Before/after: `layout_review/u4_before.png` / `u4_after.png`, and `power_*.png`.

---

## 2. nRF52840-QIAA (U5 at 46.00, 65.515, rot 180)

The rotation puts the ANT, XC and DEC3/4/6 balls on the left (x 42.75-43.25) and DEC1/VDD/DCC on the right. The Nordic reference circuit is config 1: LDO, VBUS in.

**What matches**
- The ANT match topology is Nordic v1.1: C29 0.8 pF shunt, L4 4.7 nH series, C30 0.5 pF shunt.
- The ANT match is placed in line on a straight 50 Ω CPWG, with the crystal on the opposite side of the package from the radio chain's input from the LNA.
- The DC/DC inductors L2 and L3 are DNP (LDO mode), which is fine: no DCC routing is needed.
- The SWD and UART pins go to bottom-side test points.

| # | Deviation | Sev | Fix (verified) |
|---|---|---|---|
| 2.1 | **Every decoupling cap is 1.65-3.8 mm from its ball. The Nordic reference has them at the package edge (≤ 0.6 mm).** This is caused by the 9.05 mm courtyard (§0). | **must** | Apply **N-1**: courtyard ±3.75. Then place: **C23 DEC1 (50.72, 67.77, 0)**, gap to C1 0.59 mm; **C15 VDD-W1 (51.30, 63.765, 0)**, 0.70; **C18 VDD-AD14 (45.75, 60.78, 90)**, 0.60; **C19 VDD-AD23 (43.25, 60.78, 90)**, 0.60; **C21 VBUS-AD2 (49.32, 60.22, 90)**, 0.69; **C22 DECUSB-AC5 (47.70, 60.22, 90)**, 1.19; **C25 1 µF DEC4-B5 (48.00, 70.26, 270)**, 1.11; **C16 VDD-B1 (49.25, 70.26, 270)**, 1.11; **C17 VDD-A22 (45.75, 69.79, 0)**, 1.26 (was 3.37). Also make room: **R13 (47.69, 57.60, 270)** and **R35 (47.85, 72.45, 0)**. |
| 2.2 | **DEC3 C24 (100 pF) is 2.98 mm from D23 and DEC6 (E24) has no local cap** (the 47 nF C26 sits at B5's corner, 2.6 mm away). | **must** | **C26 47 nF → (41.28, 67.80, 180)**, 0.59 mm from E24, just below the ANT line. **C24 100 pF → (41.28, 68.82, 180)**, 1.39 mm from D23. Route DEC3 out between E24 and B24. |
| 2.3 | **The 32 MHz crystal Y1 is 5.2 mm from XC1/XC2, with 12 pF caps 2.4-2.6 mm off the balls and on one side.** Nordic has X1 at the XC corner, with C1/C2 on either side of it. | **must** | **Y1 → (43.40, 70.88, 270)**: XC1 pad 1.34 mm below B24 and XC2 pad 2.25 mm from A23. **C27 → (41.10, 70.18, 180)**, 0.59 mm from Y1 pin 1. **C28 → (45.75, 71.58, 0)**, 0.64 mm from Y1 pin 3. Route XC1/XC2 as a short, roughly symmetric pair on F.Cu with a GND pour and vias around Y1, nothing under it on L1, and solid L2 under it. Y1 stays 3.5 mm below the ANT line, as Nordic requires. |
| 2.4 | **The first ANT shunt C29 is 2.0 mm from H23,** with 2.45 mm of 0.2 mm neck before the node. Nordic has C3 right at the pin. | should | In `build_pcb.py` RX part 2, change `start_x = ax - 1.75` to `ax - 0.85`, and the `('g', 1.0)` step after the 0.5 pF shunt to `('g', 1.9)`. This moves C29, L4 and C30 by +0.9 mm in x (C29 → (41.70, 66.285, 90), L4 → (40.22, 66.765, 180), C30 → (38.74, 66.285, 90)) and leaves the rest of the RX chain unchanged. The gap C29 → H23 becomes 1.12 mm. This needs N-1. |
| 2.5 | C29's GND does not return through VSS_PA (F23), which Nordic specifies. | ok | Nordic does this for TX-harmonic filtering. **This nRF never transmits** (`design.py` RX note), so it is not worth a net-tie. Give C29's GND pad its own via next to the pad. |
| 2.6 | **The SPI series resistors R16/R17/R18 (33 Ω, "series termination") are at the far end or mid-board:** R16 is at (41.96, 39.26), mid-board; R17/R18 are next to the LMX. A source termination belongs at the driver. | should | **R16 → (43.85, 58.60, 90), R17 → (44.95, 58.60, 90), R18 → (46.05, 58.60, 90)**. That is 2.9-3.5 mm from AC15/AC17/AD18, the closest positions outside the U5 cap ring. Also **R14 → (41.60, 57.75, 0)**. |
| 2.7 | C20 (VDDH Y2, 4.7 µF) is 2.4 mm away. | ok | VDDH is tied to VDD (normal-voltage mode), so the VDD caps cover it. |
| 2.8 | C1 (1 µF on 5V_BUS) is 8.6 mm from AD2. | ok | It is the TVS/USB bulk cap, not the nRF VBUS cap. C21 is the VBUS cap. |
| 2.9 | **R26 (LNA_PD 0 Ω)** is in the way of the new C24/C26. | – | Move R26 to **(38.90, 69.70, 180)**. |

Before/after: `layout_review/u5_before.png` / `u5_after.png`. The after render still draws the old 9.05 mm courtyard, because N-1 has not been applied.

---

## 3. LMX2582 (U8 at 22.60, 11.20, rot 0)

Pin map:
- **Left side:** pins 1-10 top to bottom: CE, GND, VbiasVCO, GND, NC, GND, VccDIG, OSCinP, OSCinM, VregIN.
- **Bottom:** pins 11-20 left to right: VccCP, CPout, GND, GND, VccMASH, SCK, SDI, NC, NC, MUXout.
- **Right side:** pins 21-30 bottom to top: VccBUF, OUTAM, OUTAP, CSB, GND, VccVCO2, VbiasVCO2, NC, VrefVCO2, NC.
- **Top:** pins 31-40 right to left: GND, NC, VbiasVARAC, GND, Vtune, VrefVCO, VccVCO, VregVCO, GND, GND.

**What matches**
- There is a 0.1 µF at every Vcc pin, at 0.9-2.3 mm.
- The loop-filter C1 (C66, 820 pF) is 0.90 mm from CPout, and C4 (C69, 3.3 nF) is 0.92 mm from Vtune. This matches the EVM, which keeps C4_LF at the chip.
- The OUTAP pull-up R41 is 0.53 mm from pin 23, and the DC block C71 is in line.
- The EP has a 3 × 3 via array. MUXout (pin 20) and the SPI pins are on the bottom edge, opposite Vtune (pin 35, top).
- The TCXO is outside the MagSafe clocking-bar zone.

| # | Deviation | Sev | Fix (verified) |
|---|---|---|---|
| 3.1 | **The TCXO Y2 is top-right at (28.09, 6.93), while OSCinP/M (pins 8/9) and its AC-coupling cap C48 are on the left.** The 26 MHz trace crosses the whole VCO-bypass/Vtune edge, about 13 mm, against TI's guidance to keep the input trace short and away from the CP/VCO nodes. | **must** | **Y2 → (13.60, 11.40, 0)**: OUT pad faces right, 0.50 mm from C48. **C48 → (16.06, 12.45, 0)**, on the OSCinP line. **C49 (OSCinM AC-ground) → (16.06, 13.47, 180)**. **R37 (DNP 49.9 Ω) → (14.30, 14.17, 270)**, under the OUT pad. Run OSCinP/OSCinM as a short parallel pair, 2.4 mm from the caps to pins 8/9. |
| 3.2 | **C47 "TCXO VCC" sits at LMX pin 11, 7 mm from the TCXO.** | **must** | **C47 → (14.30, 8.70, 90)**: gap to Y2 VCC pad (pin 4) 0.49 mm. |
| 3.3 | **C70 "pull-up common node" 100 pF is on the left side (18.13, 12.32), 7 mm from R41/R42.** The OUTA pull-up node has no RF bypass. | **must** | **C70 → (28.30, 11.20, 0)**: gap to R41 pad 1 is 0.40 mm. |
| 3.4 | **The OUTAM pull-up R42 is 3.7 mm from pin 22** at (29.75, 15.18). TI says "place output pull-up components close to the pin". | **must** | **R42 → (26.82, 13.89, 90)**: 0.53 mm from pin 22. **C72 → (28.30, 13.97, 0)**, 0.40 mm from R42. **C53 → (27.585, 15.45, 0)**, a 0.1 mm nudge. |
| 3.5 | **The VbiasVCO (C59, 3.9 mm), VregIN (C60, 3.3 mm) and VccDIG (C50, 2.3 mm) caps are far from pins 3/10/7.** | should | **C59 → (17.40, 10.18, 180)**, 0.60 mm. **C60 → (17.97, 14.00, 180)**, 0.51 mm. **C50 → (17.97, 11.70, 180)**, 0.49 mm. Free the space by moving **C46 → (18.10, 8.10, 90)**. |
| 3.6 | **The top-edge VCO bypass caps are 2-4.7 mm from their pins:** C65 VregVCO 2.1, C61 VbiasVCO2 4.7, C62 VrefVCO2 4.3, C63 VbiasVARAC 3.8, C64 VrefVCO 4.6. These set VCO phase noise. | should | No verified coordinates: six caps on a 0.5 mm-pitch edge need a radial fan-out like the TI EVM (chip at 45°). Two options: (a) change the 10 µF parts (C62, C63, C64) from 0603 to 0402 (e.g. GRM155R60J106ME44, 6.3 V X5R) and place them radially, pad 1 ≤ 1.0 mm from the pin, in priority order VrefVCO (36) > VbiasVARAC (33) > VrefVCO2 (29) > VregVCO (38) > VbiasVCO2 (27); or (b) rotate U8 by 45°, as the EVM does. Keep Vtune (35) with C69 as the only trace between pins 33 and 36. |
| 3.7 | **The loop filter crosses the SPI exit.** R38/C67 (R2/C2) and R39/C68/R40 sit at y 17-20, directly below SCK and SDI (pins 16/17, x 22.85/23.35), and C66's GND pad is under pin 16. So SCK/SDI must thread through the CP node, against TI's rule "no switching signals near the charge-pump traces". The Vtune return (R40 → pin 35) also runs about 14 mm around the chip. | should | Move the filter left of x 21.5: C66 directly under pin 12; R38, C67, R39, C68 and R40 in a block at x 15-21, y 15.5-19. Route SCK/SDI straight down from pins 16/17 (x ≥ 22.6), with the series resistors at the nRF (2.6). Route CP→Vtune as one guarded F.Cu trace of ≤ 10 mm around the pin-1 side, with GND pour and vias on both sides, never parallel to OSCin. Also move **C52 (VccMASH, pin 15)** to the left of the SPI pins, at about (21.95, 15.82, 270), or its trace must cross SCK/SDI. This cluster is not overlap-checked, so place it interactively after 3.1-3.5. |
| 3.8 | C45/C46 (VCC_SYN input 10 µF/100 nF) are at the chip, but the supply link R36 is 16 mm away at (38.83, 23.85). | ok | VCC_SYN is a pour on L3. If the optional LC filter is ever fitted, move R36 next to C45. |

Before/after: `layout_review/u8_before.png` / `u8_after.png`.

---

## 4. CC2595 PA (U7 at 35.73, 12.70, rot 0)

**What matches**
- The topology is the CC2595EM one: a 12 nH feed L7 at RF_OUT, 0.68 mm from pin 10, then a series 1.2 nH (L8) / shunt 1.5 pF (C43), a 22 pF DC block (C44) and the LPF.
- RF_OUT1/2 (pins 10/12) are merged with a short jog.
- The AVDD_BIAS cap C40 is 0.97 mm from pin 5, and the AVDD_PA1 cap C41 is 0.92 mm from pin 15 behind R32 (4.7 Ω), as on the EM.
- The 3 dB input pad is in line at pin 2.
- The EP has 4 × 0.2 mm vias at ±0.58-0.59, matching the TI land pattern.
- The 2.0 mm line from pin 10 to L8 mirrors the EM, which taps L1 off a transmission-line section ahead of L2. It is also forced by the pin 10/12 jog: a shorter node would put L7's VDD pad on the jog. Mark it **ok**, and re-tune L8/C43 on the bench.

| # | Deviation | Sev | Fix (verified) |
|---|---|---|---|
| 4.1 | **C42 "choke decoupling" is 5.5 mm from the cold end of L7 (VDD_PA pad at 38.60, 11.98).** The EM places C3 (0.1 µF) directly at L1. Without it the 12 nH feed is AC-floating and the output match moves. | **must** | **C42 → (40.08, 11.55, 0)**: pad 1 is 0.39 mm from L7 pad 1. Give pad 2 a GND via to L2. Optionally add a 10-22 pF RF bypass in parallel. |
| 4.2 | **The RBIAS resistors R33/R34 are 3.5/3.7 mm from pins 6/7.** | should | **R33 → (35.25, 15.86, 270)** and **R34 → (36.32, 15.86, 270)**: 0.50 mm from each pin. Make room with **C40 → (33.76, 15.385, 180)** (still 0.60 mm from pin 5), **C39 → (33.76, 16.405, 180)** and **R28 → (33.978, 17.76, 0)**. |
| 4.3 | C38 (10 µF) is 3.6 mm from pin 5. | ok | It is bulk; C39/C40 do the HF work. |
| 4.4 | The PA_EN pull-down R35 is at the nRF end. | ok | It is static. |

Before/after: `layout_review/u7_before.png` / `u7_after.png`.

---

## 5. QPL9547 LNA (U6 at 29.05, 63.335, rot -90)

**What matches**
- The 18 nH RF choke L6 is 0.63 mm from RF_OUT (pin 7).
- The VBIAS resistor R24 (3.32 kΩ) is 0.95 mm from pin 1.
- The input DC block C32 is 0.50 mm from pin 2, the BPF is directly above it, and the output DC block C33 is in line.
- LNA_VCC is decoupled at the L6 cold end: 100 pF C36 at 0.8 mm and C37 at 1.6 mm; 1 µF C35 and 10 µF C34 are behind the 10 Ω RC.
- The EP is the corrected 0.8 × 1.6 mm with 2 vias, and the input and output are on opposite sides.

| # | Deviation | Sev | Fix |
|---|---|---|---|
| 5.1 | There are 2 EP vias; Qorvo asks for "vias required" under the paddle (`footprint_review.md` suggests 3). | should | Add a third 0.25/0.45 via at the EP centre, or keep 2 and add 2 GND vias just outside the EP ends. Footprint edit only; no placement change. |
| 5.2 | C36, the first 100 pF at the choke, has a 0.8 mm gap. | ok | It could abut the L6 pad, but that would overlap courtyards. Leave it. |
| 5.3 | The SD pull-up R27 is 3.5 mm away, and the 0 Ω R26 is at the nRF. | ok | Both are static. |

---

## 6. Filters FL1 (TDK DEA202450BT-1294D1-H) and FL2 (Johanson 2450LP07)

**What matches**
- **FL1** is at rot 0: IN (pad 1) faces up to the antenna/ESD node and OUT (pad 4) faces down to C32. This is TDK's EVB orientation (`bpf_alternative.md` §4).
- **FL1** GND lands are 0.45 × 1.0 at ±0.65, with a solid zone connection.
- **FL2** is in line: 22 pF block → pad 2 → pad 4 → DNP ESD shunt L9 → SMA.
- **FL2** has the corrected lands (GND 0.30 × 0.45, I/O 0.45 × 0.30).

| # | Deviation | Sev | Fix |
|---|---|---|---|
| 6.1 | **There are no GND vias at the filter GND lands.** Only the patch-feed via has locked GND vias, and the TDK/Johanson recommended patterns both show vias at the GND lands. A zone-fill or stitching pass may or may not put a via within 0.5 mm. | **must** (RF rejection) | Add locked GND vias (0.25/0.45) in `build_pcb.py` next to the RF chain. For FL1, put two per GND land just outside the land ends: (28.65, 57.95), (28.65, 59.62), (29.95, 57.95), (29.95, 59.62). For FL2, put one per GND land outward of the land: (45.385, 12.05) and (45.385, 13.85). |
| 6.2 | The 50 Ω CPWG (0.30-0.335 / 0.20) runs into the 0.35 mm FL1 RF lands and the 0.30 mm FL2 I/O lands. | ok | The widths match within 0.05 mm, so no taper is needed. |

---

## 7. INA219 × 2 (U2 at 17.00, 72.50 = 5V monitor; U3 at 8.50, 52.00 = 3V3 monitor)

**What matches**
- Each INA219's RC input filter (10 Ω + 100 nF) is right at IN+/IN-: R4/R5/C2 are about 1.7 mm from U2 pins 1/2, and R7/R8/C4 are about 1.7 mm from U3, as TI recommends.
- The 50 mΩ 0805 shunts are on the power path.

| # | Deviation | Sev | Fix |
|---|---|---|---|
| 7.1 | **The Kelvin sense is not enforced.** R4/R5 (and R7/R8) have their force-side pads on the *same nets* as the power path (5V_BUS/5V0, 3V3_OUT/3V3). Freerouting and zone fills will join them to the nearest copper of that net, not to the shunt pad's inner edge. At 50 mΩ, 1 mm of 0.3 mm 1 oz trace (about 1.6 mΩ) in the sense path is a 3 % error. **This matters now, because the board is being autorouted.** | **must** | Make the sense nets separate. Use a 4-terminal shunt footprint (`BEACON:R_0805_Kelvin`, with pads 1/2 force and 3/4 small sense pads at the inner pad edges, and `net_tie_pad_groups "1,3" "2,4"`). Alternatively, place a NetTie_2 at each shunt pad. Then rename the nets of R4.1, R5.1, R7.1 and R8.1 to e.g. `5V_KS_P/N` and `3V3_KS_P/N` in `design.py`, and route the pairs together. |
| 7.2 | **The VS decoupling caps are far from both INAs:** C3 for U2 is 7.4 mm from pin 4, and C5 for U3 is about 20 mm away, next to the nRF (§0 cause 2). | **must** | **C3 → (15.70, 74.75, 0)**: 0.72 mm from U2 pin 4. **C5 → U3 pin 4**: see 7.3. If U3 stays where it is, use (7.20, 54.25, 0), which is 0.72 mm from pin 4. |
| 7.3 | **The U3 cluster is 12-14 mm from its shunt R6 (next to the buck).** The Kelvin pair would cross the buck's FB/RT/SS area. | should | Move the whole cluster by (+10.5, +4.8): **U3 → (19.00, 56.80, 0), R7 → (15.683, 55.301, 0), C4 → (15.641, 56.652, 0), R8 → (15.652, 58.239, 0), C5 → (17.70, 59.05, 0)**. The sense run from R6 is then 6-7 mm, runs along the right of the buck, and stays clear of the patch (which ends at about y 52). |

---

## 8. USB-C / USBLC6 (J1 at 27.50, 74.775; U1 at 35.00, 72.50)

**What matches**
- The ESD part U1 is first in line between J1 and the nRF, in flow-through orientation (pins 1/6 D+, 3/4 D-).
- It is placed against J1's courtyard, as close as the footprint allows: about 6 mm of trace.
- The CC resistors R1/R2 (5.1 kΩ) are 1.9 mm from CC1/CC2.
- The order is fuse then TVS (F1 → 5V_BUS → D1), with the TVS cathode on the rail.

| # | Deviation | Sev | Fix (verified) |
|---|---|---|---|
| 8.1 | **The fuse F1 and TVS D1 are about 10 mm from the J1 VBUS pins,** at (38.4, 63.8) and (38.3, 61.0). The unprotected VBUS_C runs across the USB-pair escape area. | should | **F1 → (23.00, 66.90, 90)**: VBUS_C pad 1.84 mm from A4/B9. **D1 → (20.30, 66.90, 90)**: 2.1 mm from F1's 5V_BUS pad. Free the space with **R12 (PG pull-up) → (17.50, 64.40, 0)**. 5V_BUS then reaches the shunt R3 in about 7 mm. Join J1's two VBUS pairs (x 25.1 and 29.9) on L3/B.Cu so they do not cross D+/D- on F.Cu. |
| 8.2 | R2 (CC2) at (28.30, 68.71) sits above the D+/D- pads. | should | Leave room for the D+/D- pair to leave J1: shift R2 to about x 29.6 (in line with B5), or route the pair down to B.Cu at the connector. |
| 8.3 | U1's VBUS pin 5 has no local cap; C1 is 13 mm away. | ok | ST shows an optional 100 nF. Only add one if the 10 µF VBUS budget allows. |

Before/after: `layout_review/usb_*.png`.

---

## 9. Decoupling caps > 2 mm from their pin (before → after the proposed moves)

| IC | Cap | Pin | Before | After |
|---|---|---|---|---|
| U4 | C11 BST | 2 | 6.52 | 0.50 |
| U4 | C8 hot loop | 9 (VIN2) | about 3.3 (wrong side) | 0.50 |
| U4 | C13 / C14 22 µF | L1 out | blocks SW / 4.5 | 0.97 / 0.97 |
| U5 | C17 VDD | A22 | 3.37 | 1.26 |
| U5 | C22 DECUSB | AC5 | 3.78 | 1.19 |
| U5 | C24 DEC3 | D23 | 2.98 | 1.39 |
| U5 | C25 DEC4 | B5 | 3.41 | 1.11 |
| U5 | C26 DEC6 | E24 | > 5 | 0.59 |
| U5 | C27 / C28 12 pF | Y1 | 2.4 / 2.6 (Y1 5.2 from the balls) | 0.59 / 0.64 (Y1 1.3 / 2.25) |
| U5 | C20 VDDH | Y2 | 2.44 | 2.44 (ok, VDDH = VDD) |
| U8 | C59 VbiasVCO | 3 | 3.91 | 0.60 |
| U8 | C60 VregIN | 10 | 3.30 | 0.51 |
| U8 | C50 VccDIG | 7 | 2.34 | 0.49 |
| U8 | C47 TCXO VCC | Y2.4 | about 11 | 0.49 |
| U8 | C70 pull-up node | R41 | about 9 | 0.40 |
| U8 | C61 / C62 / C63 / C64 / C65 | 27 / 29 / 33 / 36 / 38 | 4.7 / 4.3 / 3.8 / 4.6 / 2.1 | open (3.6) |
| U8 | C45 / C56 / C57 / C58 10 µF | Vcc | 3.5 / 3.3 / 3.2 / 2.2 | unchanged (bulk, ok) |
| U7 | C42 choke | L7 cold end | 5.5 | 0.39 |
| U7 | C38 10 µF | 5 | 3.59 | unchanged (bulk, ok) |
| U2 | C3 VS | 4 | 7.35 | 0.72 |
| U3 | C5 VS | 4 | about 20 | 0.72 |

---

## 10. Implementation notes
- **Where to make the changes:** the project rule is regenerate, don't hand-edit. So put the moves in `build_pcb.py` as `PLACEMENT_OVERRIDES` (applied after the chains, before the greedy loop, and added to `OCC`). Apply N-1 (the nRF courtyard copy) and the ANT `start_x` change (2.4) there too.
- **Re-routing:** the autorouted board will need re-routing after these changes. The locked RF segments for the nRF ANT chain are regenerated by the 2.4 change.
- **Move table:** the machine-readable move table, its overlap checker and the "after" test board were working files and are not in this repository.
- **Not verified:**
  - LMX items 3.6 and 3.7 are guidance, not overlap-checked coordinates.
  - The nRF placement was compared with the PS v1.11 reference-layout figure, not the Nordic Altium files.
  - Escape routing between the aQFN balls (no via-in-pad, per `stackup_and_rules.md`) still has to be proven by the router with the caps at the edge.

## 11. Ten highest-value fixes (absolute KiCad coordinates = board + 100)
1. **U4 C8** (VIN2 hot-loop) → **(112.60, 163.55) rot 270**, at pins 9/8. **C7** → **(107.40, 163.55) rot 270**, with 5V0 at pin 3 and GND at pin 4.
2. **U4 L1** → **(110.00, 167.30) rot 270**, SW pad under pin 6. **C13** → **(106.60, 167.30) rot 90**. **C14** → **(113.40, 167.70) rot 90**. **R6** → **(114.10, 164.15) rot 270**.
3. **U4 C11** (BST) → **(106.94, 161.95) rot 180**. **C10** (INTVCC) → **(107.12, 159.90) rot 90**. **C12** (CFF) → **(112.62, 161.30) rot 90**. **C6** → **(114.75, 159.60) rot 0**.
4. **INA Kelvin:** split the R4/R5/R7/R8 sense nets from the power nets (4-terminal shunt footprint or net-ties) before the autorouter finishes.
5. **U5 footprint:** shrink the courtyard to ±3.75. Then **C23 (150.72, 167.77) r0, C15 (151.30, 163.765) r0, C18 (145.75, 160.78) r90, C19 (143.25, 160.78) r90, C21 (149.32, 160.22) r90, C22 (147.70, 160.22) r90, C25 (148.00, 170.26) r270, C16 (149.25, 170.26) r270, C17 (145.75, 169.79) r0, C26 (141.28, 167.80) r180, C24 (141.28, 168.82) r180**. Also move **R13 (147.69, 157.60) r270, R35 (147.85, 172.45) r0, R26 (138.90, 169.70) r180**.
6. **U5 crystal:** **Y1 (143.40, 170.88) r270, C27 (141.10, 170.18) r180, C28 (145.75, 171.58) r0**.
7. **U8 TCXO** to the OSCin side: **Y2 (113.60, 111.40) r0, C47 (114.30, 108.70) r90, C48 (116.06, 112.45) r0, C49 (116.06, 113.47) r180, R37 (114.30, 114.17) r270**. Then **C59 (117.40, 110.18) r180, C50 (117.97, 111.70) r180, C60 (117.97, 114.00) r180, C46 (118.10, 108.10) r90**.
8. **U8 OUTA:** **C70 (128.30, 111.20) r0, R42 (126.82, 113.89) r90, C72 (128.30, 113.97) r0, C53 (127.585, 115.45) r0**.
9. **U7 choke decoupling:** **C42 (140.08, 111.55) r0**. RBIAS: **R33 (135.25, 115.86) r270, R34 (136.32, 115.86) r270, C40 (133.76, 115.385) r180, C39 (133.76, 116.405) r180, R28 (133.978, 117.76) r0**.
10. **INA VS caps and U3 cluster:** **C3 (115.70, 174.75) r0**, then **U3 (119.00, 156.80) r0, R7 (115.683, 155.301) r0, C4 (115.641, 156.652) r0, R8 (115.652, 158.239) r0, C5 (117.70, 159.05) r0**.

Runner-ups:
- The nRF ANT chain `start_x = ax - 0.85` with `('g', 1.9)`.
- Filter GND vias (6.1).
- The LMX loop-filter/SPI separation (3.7).
- F1/D1 next to J1: F1 (123.00, 166.90) r90, D1 (120.30, 166.90) r90, R12 (117.50, 164.40) r0.
- SPI series resistors at the nRF: R16/R17/R18 at (143.85/144.95/146.05, 158.60) r90, and R14 (141.60, 157.75) r0.
