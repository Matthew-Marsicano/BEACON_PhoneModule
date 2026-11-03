# beacon_phone_magsafe_fxp70_inlid.scad: FXP70 flex in the lid, no side bay

**Source:** `beacon_phone_magsafe_lowprofile_fxp70.scad`. It was not modified (md5 0ec360474a45f7ddddcb2a2245f2440f). Neither were the lowprofile and rev_pcb files, the Downloads original or any KiCad file.

**What changed:** the 36 mm side bay is gone. The Taoglas FXP70.07.0053A flex now sits in a pocket in the **lid underside**, in the top band (board y 55-80, over the TX chain and synth). It radiates out through 0.8 mm of PETG. The board, J3 (U.FL at board 50.525, 66.0), the patch and its window are unchanged.

**Mode switch:** `fxp_mount = "lid"` is the default. `fxp_mount = "bay"` with `snap_right_y = [-38, -2]` and `snap_top_x = [0]` rebuilds the fxp70 side-bay variant. Its ECHO matches `fxp70_assembly.echo` line for line except the title.

**Result:**

| | lowprofile | fxp70 (bay) | **fxp70_inlid** |
|---|---|---|---|
| Outside | 59.2 x 82.65 x 11.41 | 95.1 x 82.65 x 11.41 | **59.2 x 82.65 x 11.41** |
| Flex to board ground | n/a | 10.0 in plane past the edge, 1.8 above | **4.15 above the L1 GND pour, 4.4 above L2** (flex over ground) |
| Flex to RX patch, edge to edge | n/a | 24.8 | **2.9 worst / 3.25 nominal** |
| Flex to RX patch, centre to centre | n/a | 55.2 | **29.1** |
| Flex to patch window | n/a | n/a | **1.4 worst / 1.6 nominal** (1.0 web + pocket clearance) |

The board outline, holes, TX notch, USB-C, patch, ring, clocking magnet, skin, pause (layer 29, Z 3.56) and Z stack are all unchanged. The `pcb_outline` DXF is **byte-identical** to `lowprofile_pcb_outline.dxf` (md5 18390473f7549610058dd7b00660f624, `cmp` clean).

Checked with OpenSCAD 2021.01 on 2026-11-02.

## 1. Why the flex goes where it does

The geometry leaves only one workable layout. Each constraint below rules out the alternatives.

**1. The flex only fits across a band, and only by running over the wall.**
* The open patch window is 28.4 square at the board centre (Y -25.93 to 2.47).
* That leaves 27.13 mm from the window to the outer top edge, and the same to the outer bottom edge.
* The flex is 24.9 ±0.2 by 26.9 ±0.2. A pocket needs 25.5 (24.9 + 0.2 tolerance + 2 x 0.2 clearance).
* So the 24.9 side must run across the band. It fits only if the pocket runs over the top wall: 1.0 lid web at the window, then 25.5 of pocket, which leaves a 0.62 lid rim at the outer edge.
* Beside the window (13.6 mm each side) nothing fits.

**2. The cable exit edge must face the window.**
* The cable leaves square out of a 26.9 edge.
* Seen from outside the lid (adhesive side, the datasheet "Bottom" view), the cable is 2.25 from the **+X** corner.
* The other 26.9 edge lies over the wall top, where the cable cannot exit.

**3. The cable exit must sit right of the patch.**
* The exit is 1.6 from the window edge, with no room to turn.
* So the cable must leave in the part-free strip right of the patch (board x > 41).
* With the 5 mm cable-to-patch rule, that puts the exit at X 18.36 (board x 45.86), and so the flex at **X -6.29 to 20.61**.

**4. The bottom band is out.**
* It mirrors the top band: there the exit lands left of the patch.
* From there the cable would need about 80 mm to reach J3 in the top band, but only 47.75 is free.
* The bottom band also holds the USB-C lid notch.

**5. The top band gives the shortest gentle route.** J3 is 11 mm from the exit in X/Y.

The real problem is the opposite of length: 47.75 mm of free cable has to go somewhere with no loop. The answer is one hairpin beside the window (section 3).

## 2. Mounting in the lid

* **Pocket:** cut into the lid underside, X -6.89 to 20.61, Y 3.47 to 28.98, 0.40 deep. The ceiling is at Z 10.61, leaving `lid_skin` **0.8** (0.2 + 5 x 0.12 lid layers) over the flex.
* **Flex:** adhesive side up, cable side down. It is pushed into the pocket's +X / +Y corner, so the cable X and the window distance are set by the pocket.
* **Height in the pocket:** the cable-side face is at Z 10.47 nominal (0.08 flex) and 10.31 worst (0.24 flex). That is above the lid underside (10.21), so the wall top never presses it.
* **Over the top wall:** the flex overhangs the board top edge by 1.5 and the cavity wall by 1.2.
* **Top-wall lid lip:** cut from x -7.19 to 20.91. The top bead moved from x 0 to **x -16**.
* **Printing:** the lid still prints outer face down with no supports. The pocket, groove, rails and keepers all face up.

| Clearance | Value |
|---|---|
| Flex copper above the board-top GND pour | **4.15** (L2 solid GND 4.4). Taoglas minimum 4, recommended 20 |
| Flex copper to the tops of the parts under it | 3.05 (all ≤ 1.1: 0402/0603, U8 VQFN-40, U7 VQFN-16, Y2 TG2520) |
| Worst solder joint (1.7) above those parts | 1.15 |
| Mated U.FL J3 to the flex | 0.92 in plane, 1.61 below, **1.85 in 3D** |
| Flex above the ring magnet top / phone face | 7.28 / 10.51 |
| Flex copper vs the patch top | 0.25 lower (nearly coplanar) |
| Parts under the flex | U8 LMX2582 (partly), U7 CC2595 PA, FL2, L9, the synth/PA passives |

## 3. Cable route (53 ±2 mm, 47.75 free, no loops)

**1. On the flex.** The cable lies on the flex's underside for 12.5 mm and exits toward -Y at x 18.36 ±0.4. The tolerance is the offset ±0.3 plus 0.1 for pushing.

**2. Groove.** A groove in the lid underside, 2.13 wide, runs to the first clip at y 1.07. Its ceiling falls from the pocket ceiling to the lid underside, so the cable top always stays inside it. The 3 mm of free cable takes up the ±0.4 exit tolerance as an S-bend with about 4.7 radius (asserted ≥ 4.5).

**3. Lid leg.** The cable runs against the lid underside at Z 9.65, held by two clip rails (0.8 thick, 45 degree snap ridges at the tips, 1.29 gap). The rails run from y 1.07 to -6.69.

**4. Hairpin: one tilted 180 degree bend, R 4.5.**
* It runs from the lid leg (inner, x 18.36) down to the board (outer, x 26.94).
* The legs are 8.58 apart in X and 2.72 in Z (plane tilted 17.6 degrees).
* Its ends sit at y -8.29 nominal, moving from -9.39 to -7.19 over the cable and flex tolerances. The lowest point is at y -13.89 (board y 37.1).
* It floats, and so takes up the ±2 cable tolerance. Nothing else has to slide.

**5. Board leg.** The cable lies on the board ground at its right edge (x 26.94, board x 54.44, 0.3 from the wall) from the hairpin to y 0.93. It sits under a lid keeper. The right-wall lid lip is notched from y -14.19 to 5.94.
* Right-wall beads: **-38 / -24 / 15** (lowprofile -32 / -2, bay -38 / -2).

**6. S-jog.** Two R 4.5 arcs of 55.6 degrees move the cable 3.91 to the plug axis (x 23.03) over 7.42 of Y. A second keeper sits at the jog's inflection.

**7. Lead.** A 3 mm straight lead goes into the crimp at y 11.35. The plug cable points **-Y** (toward USB-C), as in fxp70.

**Checks:**
* Path check 47.72 against 47.75 (chorded arcs).
* Everything at board level stays in the part-free strip, board x ≥ 41, y 21.8-63.0 (KiCad courtyards: R14 to y 21.17, AE1 to x 40.75, J3 from y 63.5).
* The cable leg nearest the patch is 5.05 from the patch footprint (assert ≥ `cable_rx_min` 5).
* The rails are 2.31 from the window.

**Loops:**
* The route turns 180 degrees (hairpin) and then 0 net (S-jog). It never closes on itself, so it is not a loop or a coil in the APN-11-8-004 section 17 sense.
* The cable runs straight for 12 mm from the antenna before its first real bend. Section 15 says bending more than 30 degrees near the antenna detunes it.

**Opening the lid:** with the shortest cable, the lid can lift about **12 mm** straight up with J3 still mated. Unplug J3 before taking the lid away; the flex and the lid leg stay in the lid.

## 4. RF assessment

All of this is an estimate. Nothing has been measured.

### Ground distance

APN-11-8-004 gives three relevant rules:
* Section 5: "at least a 20mm clearance from the main ground-plane".
* Section 9: at least 4 mm from metal, 20 mm or more for best gain.
* Section 14: 20 mm in all directions from components, metal and ground, otherwise "a reduction in antenna efficiency and a shift in tuned frequency will be observed".

This layout only just meets the 4 mm minimum:
* The flex is **4.15 above the L1 pour** and 4.4 above L2.
* It is **3.05 from the tops of the parts** under it.
* It is **1.85 from the J3 plug**.
* In the bay version, the flex was 10 mm in plane past the ground edge, with no ground under it.

### Performance hit versus the side bay

The estimate uses image theory: a horizontal current at height h over a ground plane. Radiated power per unit current, relative to free space, is 2[1 - 1.5(sin x/x + cos x/x² - sin x/x³)], with x = 2kh.

At h = 4.15 mm and 2.45 GHz, that gives **x 0.072, or -11.4 dB** in radiation resistance. The ECHO prints this.

What that does to efficiency, assuming the conductor and dielectric loss stays the same and the antenna is perfectly re-matched:

| Starting point | Efficiency | In-lid estimate |
|---|---|---|
| Datasheet on 2 mm ABS | 63.7 % | about 11 % (-7.5 dB) |
| Datasheet in free space | 30.5 % | about 3 % (-10 dB) |

Against the bay version (assumed near datasheet, perhaps -1 to -3 dB from the nearby ground edge):

* **Efficiency:** expect about **6-10 dB less radiated TX power**. That is roughly 2-3x less free-space range.
* **Bandwidth:** expect it to be far narrower (Q rises roughly as 1/R_rad, so about 10x). Without retuning, the antenna will probably not cover 2.40-2.48 GHz. Plan a pi match at J3 or the Taoglas tuning service (section 15).
* **Housing load:** 0.8 PETG above plus air below is less loading than the 2 mm ABS the antenna is tuned on (section 14).

The board is finite (0.45 x 0.64 λ), and the flex overhangs its top edge by 1.5 mm. Both make the real loss somewhat smaller than the infinite-plane figure, but not by much.

### TX/RX isolation

* The flex is 2.9-3.25 from the patch edge to edge, nearly coplanar with the patch top, and 29.1 centre to centre. In the bay version these were 24.8 and 55.2.
* The centre distance alone costs about 5.6 dB of free-space coupling. Edge proximity at about 0.025 λ will probably cost more.
* Expect roughly **6-15 dB less isolation** than the bay (not quantified). APN section 16: "keep the distance between antennas as large as possible".
* The cable's lid leg runs beside the patch at 5.05.
* Measure S21. Blocker B1 (about 45 dB needed) gets worse.

### Components under the antenna

* The flex sits about 3 mm above U8 (LMX2582 VCO/synth) and U7 (CC2595 PA). Section 14 asks for 20 mm, and section 17 says to keep the cable away from emitting chips.
* Risks: VCO pulling by the radiated TX, and PA feedback. Check the synth lock and the spectrum with the lid closed.

## 5. Local raise over the antenna (evaluated, not built)

| Option | Flex height over GND | Total height | Image-theory gain vs flat | Cost |
|---|---|---|---|---|
| **Flat lid (default)** | 4.15 | **11.41** | 0 | none |
| `lid_skin` 0.6 instead of 0.8 | 4.35 | 11.41 | about +0.4 dB | thinner skin over 27 x 25 |
| +1 mm boss on the outer face | 5.15 | 12.41 locally | **+1.85 dB** | see below |
| +2 mm boss | 6.15 | 13.41 locally | +3.4 dB | see below |

**Why a boss is hard to print:**
* **Face down:** the boss lies on the bed, and the rest of the 59 x 83 plate overhangs it. It needs support under the whole plate.
* **Face up:** the lip (2.6 deep), rails and keepers end up on the bed, and the plate bridges over them. Again it needs full support.
* **Inner standoff:** it cannot lift the flex above the lid's outer face. It only moves it toward the board, which is worse.

**Recommendation: keep the flat 11.41 lid.**
* +1.9 dB for +1 mm (a 9 % taller box) and a supported print is not clearly worth it.
* It closes only about a quarter of the 6-10 dB gap to the bay, and none of the isolation gap.
* If the measured link budget is short, the real fixes are, in order:
  1. Go back to the bay, or to a narrower one (about 15 mm would still put the flex beside the ground edge).
  2. Use a board-edge chip antenna with a ground clearance, at the next PCB spin.
  3. Ask Taoglas for a custom FXP70 cable exit (section 13: "The cable exit point can be moved"). An exit on a 24.9 edge would let the flex move left, off the synth, and further from J3.

## 6. Z stack and height

Unchanged from lowprofile and fxp70:

| Level | Z |
|---|---|
| floor | 4.16 |
| board | 4.76 / 6.36 |
| lid underside | 10.21 |
| **top** | **11.41** |

The U.FL mated top is at 8.86, 1.35 under the lid. The pocket uses 0.4 of the 1.2 lid. No local rise is used (section 5).

## 7. Asserts

All lowprofile and fxp70 asserts are kept and pass. The bay-specific ones are guarded by `fxp_bay`. The `print_plate`, `assembly` and `pcb_outline` `.echo` files have 0 ERROR / WARNING / Assertion.

**New asserts (lid mode):**
* **Lid and pocket:**
  * `lid_skin` ≥ 0.6;
  * pocket holds the worst flex + adhesive with 0.05 to spare;
  * flex above the lid underside;
  * window web ≥ 0.8, pocket clear of the window;
  * all pocket corners ≥ 0.5 inside the rounded outer outline;
  * pocket clear of the USB-C notch.
* **Flex:**
  * flex to patch footprint ≥ `lid_rx_min` 2.5;
  * flex above GND ≥ `ant_gnd_min` 4;
  * worst solder joint ≥ 0.3 over `top_band_h` parts;
  * flex cable and solder clear of the mated plug;
  * pocket not over the plug, or with `ufl_lid_clr` of air.
* **Lip and beads:**
  * top beads clear of the top-lip cut;
  * right beads clear of the right-wall notch;
  * at least 1 top and 2 right beads;
  * notch off the corner radii and covering the hairpin and board leg.
* **Cable route:**
  * bend radius ≥ 3.4;
  * hairpin feasible;
  * lid leg to patch ≥ `cable_rx_min` 5;
  * rails ≥ 1 from the window;
  * board leg on the board and off the wall;
  * jog offset within 2R;
  * lead ≥ 2;
  * first clip ≥ 3 from the flex and outside the pocket;
  * exit S-bend radius ≥ `cable_bend_r`;
  * rails ≥ 3 long at the shortest cable;
  * board-leg straight ≥ keeper + 1 at the shortest cable;
  * keepers on the straight, ≥ 0.5 tall, off the wall, window and lip;
  * path length = free length (±0.15);
  * route inside the part-free strip;
  * route clear of screw heads.
* **Vents:** vents off the pocket and ≥ `vent_keep` from the cable. The default `vent_c` [22, 65] is under the flex now, so `vent_slots = true` fires.

**Each was forced to fail once** with a readable message:

| Override | Message (abridged) |
|---|---|
| `lid_skin=1.0` | "Flex pocket 0.2 deep: worst-case flex + adhesive (0.3) must sit inside it" |
| `win_web=0.5` | "Only 0.5 mm of lid between the patch window and the flex pocket (min 0.8)" |
| `win_web=2.0` | "Flex pocket corner [-6.89, 29.98] leaves under 0.5 mm to the outer edge" |
| `lid_rx_min=3.5` | "Flex only 2.9 mm from the RX patch footprint" |
| `ant_gnd_min=5` | "Flex only 4.15 mm above the board GND" |
| `top_band_h=2.0` | "Worst flex solder joint comes within 0.3 mm of the top_band_h parts" |
| `snap_top_x=[0]` | "Top-wall snap bead at x 0 is in the lid-lip cut over the flex pocket" |
| `snap_right_y=[-38,-2]` | "Right-wall snap bead at y -2 is in the lid-lip notch over the cable" |
| `snap_right_y=[-38]` | "Keep at least one top-wall and two right-wall snap beads" |
| `cable_rx_min=6` | "Lid-leg cable only 5.05 mm from the RX patch" |
| `clip_off=2.5` | "First clip within 3 mm of the flex edge" |
| `fxp_c_off_tol=0.6 cable_rx_min=4` | "Free cable between the flex and the first clip bends tighter than 4.5" |
| `cable_len=60` | "Right-wall snap bead at y -24 is in the lid-lip notch" (hairpin drops) |
| `cable_len=44` / `lk_len=12` | "Board leg straight only 3.62 / 8.12 mm at the shortest cable" |
| `strip_x0=46` | "Cable hairpin / board leg leave the part-free strip" |
| `cable_lead=1.5` | "Straight lead behind the crimp under 2 mm" |
| `vent_slots=true` | "Vent slots cut into the lid flex pocket" |
| `fxp_mount="foo"` | "fxp_mount must be "lid" or "bay"" |

`cable_len=46` passes, which is correct: the rails are still 4.3 long.

**Regression checks:**
* `fxp_mount="bay" snap_right_y=[-38,-2] snap_top_x=[0]` reproduces `fxp70_assembly.echo` except the title line.
* `use_fxp=false use_sma=true snap_right_y=[-32,-2] snap_top_x=[0]` reproduces `lowprofile_assembly.echo`, with the same two cosmetic differences that fxp70 had.

## 8. Assembly

1. **Steps 1-5 (magnets, inserts, board, screws):** as fxp70. There is no SMA and no leg cut.
2. **Lid, upside down:**
   * Clean the pocket with IPA.
   * Peel the liner. Lay the flex adhesive side into the pocket (cable side up), with the cable corner at the pocket's +X / window corner.
   * Push it into the +X / top-wall corner and press for 10 s.
   * Press the cable into the clip rails.
3. **Close:**
   * Mate the plug on J3 straight down, cable toward -Y.
   * Lay the jog and the board leg along the board's right edge.
   * Lower the lid straight down; the slack forms the hairpin.
   * Check that the board leg is under its keeper, then press until the 6 beads click (right -38 / -24 / 15, left -32 / -2, top -16).
4. **Open:** lift no more than about 12 mm, then unplug J3.

## 9. Risks

1. **RF (main risk).** Expect 6-10 dB less TX efficiency than the bay, a narrow detuned match and 6-15 dB less TX/RX isolation (section 4). VNA in the closed box, with a hand and with the phone; S21 to the patch; check the synth lock. A retune or matching network is probably needed.
2. **Flex over the TX chain.** U8 and U7 are about 3 mm under the antenna. Watch for VCO pulling and PA instability.
3. **J3 is 1.85 mm from the flex corner.** That is below the 4 mm metal clearance. It cannot be improved without moving the cable closer to the patch, or a custom cable exit.
4. **Hairpin.**
   * It is free-floating by design. If the cable is stiffer than expected, it may push the board leg out from under the keeper or press the lid leg out of the rails.
   * Check the first build, and add a drop of tape on the board leg if needed.
   * A 180 degree bend at 4 x OD is assumed fine; no vendor gives a figure.
5. **Lid lip.** It is cut over 28 mm of the top wall and notched over 20 mm of the right wall. The lid is located by the remaining lip and 6 beads. Check how it survives prying and a drop.
6. **Flex retention.** It relies on 3M 467 on a printed surface (the pocket ceiling is a top surface, which is smooth). The wall top sits 0.1 under the worst flex and catches the outer edge if it peels. Nothing catches the window side except the cable clips.
7. **Thin rim.** The lid rim outside the pocket is 0.62 at the top edge. It is cosmetic, since the lid plate above is 0.8 continuous.
8. **Vents.** The default vent position is now under the flex. The vents stay off, or move to the bottom band.
9. **Board file changed during the session.** The parallel routing job rewrote `BEACON_PhoneModule.kicad_pcb` at 14:20, from `route/beacon_inc.ses`. All 161 footprint placements were re-extracted and are identical, so the route checks still hold.

## Files

| File | What |
|---|---|
| `beacon_phone_magsafe_fxp70_inlid.scad` | new model: `fxp_mount = "lid"` (default) or `"bay"`; legacy `use_sma` |
| `FXP70_INLID.md` | this note |
| `inlid_print_plate.echo` / `inlid_assembly.echo` / `inlid_pcb_outline.echo` | console (ECHO, asserts): 0 errors |
| `inlid_pcb_outline.dxf` | board outline, byte-identical to lowprofile |
| `inlid_assembly.png` | exploded assembly preview. The flex and cable are drawn in their assembled positions under the lifted lid |
| `inlid_routing_top.png` | top view without the lid: flex footprint, cable lid leg, hairpin, board leg, S-jog, J3 |
| `inlid_lid_underside.png` | lid seen from below with the flex, solder joints and lid-held cable: pocket, rails, keepers, lip cut and notch |
| `inlid_section_flex.png` | 2D section at x 7.16 (flex centre): patch in the window, 1.0 web, flex in the 0.4 pocket under 0.8 skin, over the top wall, board, ring |
| `inlid_section_exit.png` | 2D section at x 18.36 (cable exit): cable on the flex, groove, lid leg |
| `inlid_section_hairpin.png` | 2D section at y -5.69: lid leg in the clip rails, board leg on the GND, notched lip, patch |
| `inlid_print_plate.stl` / `inlid_assembly.stl` | CGAL `--render` exports (background), see Verification |

**New parts for previews:**
* `lid_under`;
* `section_ant` / `section_hairpin` / `section_ant_x` (OpenCSG cuts);
* `sec2d_ant` / `sec2d_exit` / `sec2d_hairpin` / `sec2d_ant_x`: flat colour-coded `projection(cut)` drawings. They take about 1.5 min each with CGAL; run them with `-D label=false` (the label is off these planes).

`sec_render=true` CGAL-renders the base and lid in the OpenCSG sections.

## Verification

* `.echo` exports were grepped for ERROR / WARNING / Assertion: none fired.
* The DXF passes `cmp` against `lowprofile_pcb_outline.dxf`.
* The source files' md5 values are unchanged:
  * rev_pcb 634b63af…
  * lowprofile 71405a6a…
  * fxp70 0ec36047…
* STL exports: CGAL `--render`, run in the background. Both finished with no ERROR or WARNING, and CGAL reports both as Simple: yes (2-manifold).
  * `print_plate`: 59 s, 23 volumes.
  * `assembly`: 2 min 56 s, 27 volumes.
* Previews are OpenCSG (`--preview`). The `inlid_section_*.png` drawings are true `projection(cut)` sections.
