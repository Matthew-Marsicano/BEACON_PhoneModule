# BEACON_PhoneModule: footprint review (pre-fab)

Date: 2026-11-02. Convention: KiCad top view, mm, +y down, coordinates relative to the footprint origin.
Corrections are given as `pad -> (x, y) w x h`. No project files were edited. Only this file was written.

| # | Part | Footprint | Verdict |
|---|------|-----------|---------|
| 1 | LMX2582RHAR | Texas_RHA_VQFN-40-1EP_6x6mm_P0.5mm_EP4.6x4.6mm_ThermalVias | PASS (minor: EP 4.6 vs TI 4.5) |
| 2 | CC2595RGTR | VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias | PASS |
| 3 | QPL9547TR7 | Qorvo_DFN-8-1EP_2x2mm_P0.5mm | **FAIL**: EP and pads wrong |
| 4 | Johanson 2450BP08C0100001T | BEACON:Johanson_2450BP08_1.1x0.9mm | PASS (orientation correct; lands 0.04 mm oversize) |
| 5 | Johanson 2450LP07C0100001T | BEACON:Johanson_2450LP07_0402_4T | Orientation PASS, **land sizes FAIL** |
| 6 | Same Sky UP20-C-F-G-FL-P12-TR | BEACON:USB_C_Plug_SameSky_UP20-C-F-G-FL-P12 | **FAIL (critical)**: mirrored pin order, wrong pad row Y, wrong shell slot X |
| 7 | U.FL / ABM11W / TG2520SMN / SZSMF6.0A | stock | PASS for pinout. U.FL, ABM11W, Epson and onsemi lands not checked against vendor PDFs |

---
## 1. LMX2582RHAR: PASS (optional EP tweak)
Source: https://www.ti.com/lit/ds/symlink/lmx2582.pdf (SNAS680E, 48 pp). Package Option Addendum p.40 lists the part as VQFN (RHA) 40. The mechanical pages (pp.45-47) are **RHA0040H** (4219055/B):
- Package EP is **4.5 +/-0.1 square**. Terminals are 0.2-0.3 x 0.3-0.5 at 0.5 pitch, body 6.0.
- Land pattern (p.46): EP **4.5 x 4.5**; 40 pads **0.6 x 0.25**, centres on a **5.8** square (so +/-2.9); optional 0.2 mm vias at 1.27/1.46 pitch. Paste (p.47): 9 x 1.26 sq at 1.46 pitch, 70 %.
- **Answer to the key question:** LMX2582 uses RHA0040H with a 4.5 x 4.5 EP. That is not RHA0040B (4.15), D (2.9) or E (3.52x2.62). KiCad has no RHA0040H footprint. The generic `EP4.6x4.6` footprint is the closest match.
- Stock footprint: EP 4.6 x 4.6 (0.05/side larger than TI). Pads 0.875 x 0.25 at +/-2.9375 (span 2.50-3.375, TI span 2.60-3.20). The pad-to-EP gap is 0.20 mm, which fabs fine. Pin 1 is at (-2.9375,-2.25), at the top of the left column, numbered counter-clockwise. This matches TI Fig 5-1.
- Optional exact match: `41 -> (0,0) 4.5 x 4.5`. Side pads `1-10 -> (-2.9, -2.25 + 0.5*(n-1)) 0.6 x 0.25`, and the same for the other sides at +/-2.9. The 16 x 0.2 mm vias in the stock footprint are fine.

## 2. CC2595RGTR: PASS
Source: https://www.ti.com/lit/ds/symlink/cc2595.pdf, pp.11-12, **RGT0016C** (4222419/E).
- Package EP is **1.68 +/-0.07**. Land: EP 1.68 sq; pads 0.6 x 0.24, centres on a 2.8 square (+/-1.4); 0.2 mm vias at +/-0.58.
- Stock footprint: EP 1.68 sq, pads 0.825 x 0.25 at +/-1.4625, 4 vias 0.2 mm at +/-0.59. Pin 1 is at (-1.4625,-0.75), counter-clockwise. Matches.

## 3. QPL9547TR7: FAIL
Source: Qorvo QPL9547 datasheet Rev D (2023-10-11), p.7 pad config and p.8 "Recommended PCB Layout Pattern" (local copy `dl_qpl/qpl9547.pdf`).
- Package: 2.00 x 2.00, EP **0.80 x 1.60**, 0.5 pitch, terminals 0.30 x 0.25. Pin 1 is at the top-left (Vbias), pins 1-4 down the left side, 5-8 up the right side.
- Qorvo land: 8 pads **0.430 x 0.250**, centres at x = **+/-0.915**, y = -0.75/-0.25/+0.25/+0.75. EP **0.800 x 1.600**. Solder mask openings are 0.53 x 0.35 and 0.90 x 1.70. 0.25 mm finished vias are required under the paddle (note 3).
- The stock footprint has EP **0.6 x 1.2** and pads 0.48 x 0.25 at +/-0.89. Its descr points to a different Qorvo part (da000896). Pin 1 position is correct.
- **Corrections:** `9 -> (0,0) 0.80 x 1.60`. `1..4 -> (-0.915, -0.75/-0.25/+0.25/+0.75) 0.43 x 0.25`. `5..8 -> (+0.915, +0.75/+0.25/-0.25/-0.75) 0.43 x 0.25`. Add 2-3 vias (0.25 finished / 0.35 drill) inside the EP, e.g. at (0,-0.5), (0,0), (0,+0.5).

## 4. Johanson 2450BP08C0100001T (BPF): PASS, no mirror
Source: Johanson 2450BP08C0100001T datasheet p.2 (dims, "Bottom view", "Top view", terminal table) and p.3 "Recommended Mounting Configuration" (renders `img/bp_p2.png`, `bp_top.png`, `bp_p3.png`).
- The **numbered Top view** (pads dotted, so seen through the part, with the coloured mark) shows pin 1 IN at the left middle, **5 at top-middle, 4 at top-right, 2 at bottom-middle, 3 at bottom-right**. The p.3 mounting drawing, also a top view ("mount with coloured mark up"), agrees: the input line enters the single left pad and the output line leaves the **upper-right** pad (pin 4).
- The bottom view is flipped top-to-bottom, not left-to-right. That is why the single IN pad is on the left in both views: only the two rows swap. Your current placement is correct, so do not mirror it.
- Dimensions: b = 0.18 (pad width), c = 0.205 (gap), giving 0.385 column pitch. a = 0.25 (pad height), d = 0.25 (row gap), giving rows at +/-0.25. The p.3 land measures 0.18 x 0.25 at x = -0.385/0/+0.385. Pixel-measured: 0.17 x 0.24, column pitch 0.39, row pitch 0.505.
- Current pads are 0.22 x 0.29. That is +0.04 mm each way and leaves a 0.165 mm column gap, which is acceptable. To match Johanson exactly, set all 5 pads to **0.18 x 0.25** with no position change: `1 -> (-0.385,0)`, `5 -> (0,-0.25)`, `4 -> (0.385,-0.25)`, `2 -> (0,0.25)`, `3 -> (0.385,0.25)`. Johanson also shows GND copper with vias next to pins 2/3/5.

## 5. Johanson 2450LP07C0100001T (LPF): orientation PASS, lands FAIL
Source: Johanson 2450LP07C0100001T datasheet p.2 (dims, Top view, pins: 1 GND, 2 I/O, 3 GND, 4 I/O) and p.3 "Recommended PCB Configuration" (renders `img/lp_p2.png`, `lp_top.png`, `lp_p3.png`).
- The top view shows 1 on the top long side, 3 on the bottom long side, 4 at the left end and 2 at the right end. Your numbering matches.
- Terminals: body 1.00 x 0.50; GND terminals a = 0.30 long, c = 0.10 deep; I/O terminals b = 0.30 long.
- The recommended land, dimensioned and pixel-checked (about 47 px/mm), has two sizes:
  - GND lands are **0.30 (x) x 0.45 (y)**, with a 0.2 gap between them.
  - I/O lands are **0.45 (x) x 0.30 (y)**, with a 0.7 gap between inner edges.
- Your GND pads (0.36 x 0.22 at y +/-0.32) span y 0.21-0.43. They overlap the 0.15-0.25 terminal by only about 0.04 mm, so the solder joint is unreliable. Your I/O pads are 0.25 x 0.35.
- **Corrections:** `1 -> (0,-0.325) 0.30 x 0.45`, `3 -> (0,+0.325) 0.30 x 0.45`, `4 -> (-0.575,0) 0.45 x 0.30`, `2 -> (+0.575,0) 0.45 x 0.30`. The minimum gap from GND to I/O is 0.20 mm.

## 6. Same Sky UP20-C-F-G-FL-P12-TR: FAIL (critical)
Source: https://www.sameskydevices.com/product/resource/up20-c-f-g-fl-p12-tr.pdf (rev 1.01, 09/12/2024). p.2 mechanical (front view: A12 left, A1 right). p.3 "Recommended PCB Layout, Top View": I extracted the vector geometry, scale 17.97 pt/mm, using pad pitch and 5.50 span as checks.

Datasheet geometry, with the PCB edge at y = 0 and distances measured into the board:
- 12 pads 0.30 x 1.00 at 0.50 pitch, spanning 5.50. The pad edge nearest the board edge is **1.06** inside it, so pad centres are **1.56** in. The far pad edge is 0.66 beyond the slot centre (2.06).
- Shell: 2 plated slots, centres **+/-4.30** (dim 8.60 between centres), **1.40** inside the edge. Drill is an oval **0.45 x 1.80**. Copper is **0.85 wide x 2.25 long** (0.25 to 2.50 from the edge, rounded only at the inner end). Each slot pad also has an **L-shaped SMD copper extension**: x from +/-3.30 (dim 6.60) to the slot's outer edge (1.43 wide), y 0.25-1.25 (1.00 tall). The annulus is hatched, so the slots are plated. The text does not state "plated" explicitly.
- **Pin order:** in the datasheet top view the plug points *away from the board* toward the bottom of the page, and the order left to right is A12 A7 A6 A5 B9 B10 B11 B12 A4 A3 A2 A1. This agrees with the p.2 front view.

Your footprint has the board at +y and the plug body at -y (F.Fab -11.25..0). That is the datasheet drawing rotated 180 deg, so the order must reverse. **The current A12 to A1 order is a mirror image.** Physically, the mirror would put:
- the phone's B9 VBUS contact on your B12 (GND) pad,
- B12 GND on your B9 (5V_BUS) pad,
- A4 VBUS on CC,
- D+/D- on the unused SS pads.

That is a VBUS-to-GND short and no USB data.

Corrections, keeping your orientation (edge y = 0, board +y):
- Signal pads, all at y = **+1.56**, 0.30 x 1.00 (currently at y 1.16):
  `A1 -2.75, A2 -2.25, A3 -1.75, A4 -1.25, B12 -0.75, B11 -0.25, B10 +0.25, B9 +0.75, A5 +1.25, A6 +1.75, A7 +2.25, A12 +2.75`
- Shell PTH (both "SH"): `(+/-4.30, 1.40)` oval **0.85 x 2.20**, drill oval **0.45 x 1.80**, *.Cu/*.Mask. Currently they are at +/-3.80, y 1.30, 1.0 x 2.25. Optionally size them 0.85 x 2.25 centred at y 1.375 to match the copper exactly.
- Add the SMD shell extensions ("SH", F.Cu/F.Paste/F.Mask): `(-4.01, 0.75) 1.42 x 1.00` and `(+4.01, 0.75) 1.42 x 1.00`.
- Check: A12/A1 pad edge (2.90) to extension (3.30) is 0.40 mm clearance.
- Alternatively, keep the datasheet order and flip the footprint so the board is at -y (pads at y = -1.56). Either way, the A12 pad must be on the left when the plug points down the screen.

Board edge and thickness:
- **No cutout is required.** The layout shows a straight PCB edge. The plug sits on the top surface with its body overhanging the edge, and the shell tabs drop into the plated slots.
- The datasheet specifies no board thickness. From the p.2 side view, the tabs extend about 0.75 mm below the body (scaled, not dimensioned), so 0.8-1.6 mm boards work and the tabs will not protrude through 1.6 mm.
- Place the footprint so Dwgs "PCB EDGE" sits exactly on Edge.Cuts. Same Sky offers a vendor footprint ("PCB Footprint" link) that I did not download, so cross-check against it.

## 7. Quick sanity checks
- **Hirose U.FL-R-SMT-1** (stock): signal pad 1.05 x 1.0 at (-1.525, 0); GND pads 2.2 x 1.05 at (0, +/-1.475). This is consistent with the commonly published Hirose land. The Hirose PDF returned HTTP 403 (bot check, not circumvented), so this is **NOT verified** against the vendor drawing.
- **Abracon ABM11W 2016** (stock): pads 0.9 x 0.8 at (+/-0.7, +/-0.55), numbered counter-clockwise: 1 bottom-left, 2 bottom-right, 3 top-right, 4 top-left. Pins 1/3 are diagonal (crystal) and 2/4 are GND. That matches the standard ABM11W pinout and your net mapping (1 XC1, 3 XC2, 2/4 GND). Pinout PASS; Abracon land size **not verified** (abracon.com is outside the allowed list).
- **Epson TG2520SMN** (stock): pads 1.0 x 0.8 at (+/-0.7, +/-1.05); 1 top-left, 2 bottom-left, 3 bottom-right, 4 top-right. The KiCad symbol gives 1 NC, 2 GND, 3 OUT, 4 Vcc, and your mapping is 1 None, 2 GND, 3 TCXO_OUT, 4 VCC_SYN. Consistent; TG2520SMN has no Vcont. The Epson PDF was **not fetched**.
- **onsemi SZSMF6.0AT1G, SOD-123F** (stock): pads 1.1 x 1.1 at +/-1.4. KiCad diode convention is pad 1 = cathode, and Device:D_Zener pin 1 = K. Your net mapping (1 = 5V_BUS, 2 = GND) puts the cathode (band) on the rail, which is correct for a TVS. Cathode PASS; onsemi SOD-123FL land size **not verified**.

## Not verified / follow-ups
- U.FL, ABM11W, TG2520 and SOD-123FL lands were not compared with vendor PDFs (Hirose 403; other domains not fetched).
- USB-C: tab length and board thickness are inferred, not dimensioned. Compare against Same Sky's downloadable footprint before fab.
- The package renders used for these checks (LMX2582 p45/46, CC2595 p11/12, USB-C views, LT80602 land) were working files and are not in this repository.
