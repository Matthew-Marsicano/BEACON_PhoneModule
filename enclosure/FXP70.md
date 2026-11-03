# beacon_phone_magsafe_lowprofile_fxp70.scad: FXP70 flex TX antenna

**Source:** `beacon_phone_magsafe_lowprofile.scad`. It was not modified (md5 71405a6aee7cbfd742e92c31388dd7bd). Neither were the rev_pcb copy, the Downloads original or any KiCad file.

**What changed on the board:** the TX output is now J3, a Hirose **U.FL-R-SMT-1** at board (50.525, 66.0). That is KiCad (150.525, 112.45), rotation 0, value "TX antenna U.FL". It feeds a Taoglas **FXP70.07.0053A** flex antenna. The Cinch SMA and the GW.26.0111 monopole are gone.

**Result:**

| | lowprofile | fxp70 |
|---|---|---|
| Outside | 59.2 x 82.65 x 11.41 | **95.1 x 82.65 x 11.41** |
| Main body | | unchanged, 59.2 x 82.65 |
| Added | | antenna bay on the right, 35.9 x 38.7, flush with the bottom edge (Y -53.05 to -14.37) |

The board outline, holes, TX notch, USB-C, patch, ring, clocking magnet, skin, pause (layer 29, Z 3.56) and Z stack are all unchanged. The `pcb_outline` DXF is **byte-identical** to `lowprofile_pcb_outline.dxf` (md5 18390473f7549610058dd7b00660f624, `cmp` clean).

Checked with OpenSCAD 2021.01 on 2026-11-02.

## 1. FXP70.07.0053A: what the datasheet says

Sources:
* Taoglas datasheet SPE-12-8-013 rev G (2024-09-30), from taoglas.com/datasheets/FXP70.07.0053A.pdf.
* Taoglas application note **APN-11-8-004 rev C**, "Flexible PCB Antenna with Cable".

Both were downloaded directly, with no bot check involved. The product page returned 403 and was not retried.

| Item | Value | Source |
|---|---|---|
| Flex outline | **26.9 ±0.2 x 24.9 ±0.2** | drawing p.9 |
| Thickness | 0.08 (spec table), 0.2 (cover page), "Polymer 0.24t" (drawing BOM). The model uses **0.24 worst / 0.08 nominal** | p.1, 4, 9 |
| Adhesive | 3M 467 on the bottom side (the side away from the cable). 467MP is 0.058 thick | p.4, 9 |
| Cable | 53 ±2 mm of 1.13 mm mini-coax. It is soldered on the **top** side and lies on the flex for about 12.5 mm (scaled) | p.4, 9 |
| Cable exit | Square out of a 26.9 mm edge, centre **about 2.25** (dims 2 / 2.5 ±0.3) from one corner | p.9 |
| Solder joint | 0.3-1.7 thick (note 1) | p.9 |
| Plug | I-PEX MHF I (U.FL compatible). Detail A: 3.0 wide, 2.1 thick, 5.2 ±0.5 long | p.9 |
| Performance on 2 mm ABS | Efficiency 63.7 %, peak gain 1.1 dBi | p.4 |
| Performance in free space | Efficiency 30.5 %, peak gain -1.9 dBi | p.4 |
| Polarisation and pattern | Linear; omni pattern | p.4 |
| Tuning | Tuned for 2 mm ABS: return loss minimum at about 2.36 GHz, about -10 dB at 2.45 GHz, about -8 dB at 2.5 GHz | p.5 |
| Bend radius | **not given** | |

The FXP70 datasheet gives no clearance figures, so these come from APN-11-8-004:

* **Ground plane:** "at least a 20mm clearance from the main ground-plane".
* **Metal:** at least 4 mm from metal, 20 mm or more for best gain.
* **Mounting:** mount on plastic, ideally close to the outer housing, on 2-3 mm ABS. Other materials or thicknesses shift the tuning.
* **Housing:** no metal; avoid carbon-black colourants and nylon.
* **Cable:**
  * Bending it more than about 30 degrees near the antenna detunes it.
  * "The cable should not be looped".
  * Route it close to the device ground, and away from noisy chips.
* **Two antennas:** keep them far apart; neither antenna's cable should come close to the other antenna.

**U.FL height:** 2.5 mm maximum mated height (Hirose catalogue: 2.5 max / 2.4 nominal for the 1.13 mm cable plugs). The Hirose PDF itself was not opened, because Hirose returned 403 earlier (see docs/footprint_review.md).

## 2. Placement

**Why the antenna can't go inside the main body.** The board (55 x 78.45, solid L2 ground) fills the main cavity. Anything over it would be 1-4 mm from ground. A vertical mount on a side wall is not possible either: a 24.9 mm flex does not fit in an 11.4 mm tall box.

**The bay.** So the flex goes in a bay added to the right side, following the original GW.26.0111 idea of putting the radiator past the phone's edge. The old monopole reached X = 61.6. The bay's outer edge is at X = 65.5.

* **Orientation:** the flex lies flat (XY plane), cable side up, with the 26.9 mm cable edge facing the board (-X). The cable is at the flex's top (+Y) corner.
* **Mounting:** it is stuck adhesive side down into a **0.36 mm pocket** (3 layers, at least flex 0.24 + adhesive 0.06) on a **1.6 mm PETG shelf**.
  * The shelf is carried on 0.8 mm ribs along X at 6.5 mm pitch, with air below. That roughly matches Taoglas's 2 mm ABS reference without a solid block of plastic under the radiator.
  * Above the flex: 2.07 mm of air, then the 1.2 mm lid.
  * The pocket edges keep the flex flat and protect its edges. Three lid **hold-down pins** (d 2.4) stop 0.2 above the shelf top. That is 0.26 over the worst-case flex top, at the corners away from the cable. They catch the flex if the adhesive lets go, and they carry the lid wing.

| Clearance (defaults) | Value |
|---|---|
| Board ground edge (board x 55) to the pocket | **10.0 in plane**; flex 1.78 above the board top, so about 10.2 mm in 3D. That meets the 4 mm minimum but is half the 20 mm recommendation (`ant_gnd_gap`; each mm adds 1 mm of width) |
| Ring magnet (OD 54.1) | 10.45 in plane, 4.9 below |
| Phone face (Z 0) | pocket floor Z 8.00, flex top 8.14 |
| 71.6 mm wide phone, ring centred | flex inner edge **1.7 past** the phone edge (whole flex past the metal) |
| 77.8 mm wide phone (Plus / Pro Max) | flex overlaps the phone by **1.4 mm** of its 25.6 mm (8 mm above the face) |
| RX patch footprint to the pocket | **24.8 edge to edge, 55.2 centre to centre** (0.45 λ at 2.45 GHz) |
| Worst solder joint to the lid | 0.21 (`fxp_lid_air` 0.2) |

**RX isolation and polarisation.**

* **Geometry:** the patch (board centre, 25 sq, broadside +Z through the lid window) and the flex sit side by side along X. The flex is 2.6 below the patch top, near the patch's horizon, where a broadside patch has its lowest gain. The board's ground edge lies between them.
* **TX cable:** the cable runs over the board ground, 9.8 mm from the patch footprint (assert ≥ `cable_rx_min` 5), and never crosses the patch.
* **Polarisation:** the flex is linear and lies flat, so toward the patch it radiates mainly in-plane polarisation. The patch's horizon field in its E-plane is mostly normal to the board. That suggests some cross-polar help, but it is **not quantified**. Taoglas does not say which axis carries the patch's 2.4 GHz E-field (docs/antenna_connectors.md 1.2).
* **Measure:** TX-to-RX S21 with the patch at 0 and 90 degrees, and with the flex at both ends of its slide.
* **Expectation:** docs/schematic_review.md estimates about 45 dB of isolation is needed at 1 m. Two antennas on a dongle typically give 10-25 dB, so geometry alone will not close that gap (blocker B1 stands).

## 3. Cable path

* **At the plug:** J3's plug points **-Y**. The cable runs straight along board x 50.53 over the ground, 3 mm of lead behind the crimp, from board y 62.3 down to about 32.
* **The bend:** a **4.5 mm radius bend** (4 x OD) turns it +X. It ends at X 27.53, before the wall, so the cable crosses the wall square.
* **Into the bay:** the cable passes an **open-top slot** in the right wall (floor at the board top; the lid lip is notched there). It then climbs a **trough** cut in the shelf, 9 degrees up to the flex edge.
* **Loops:** none.
* **Free length:** the path is solved for the nominal free length, 53 - 5.25 on the flex = 47.75. A polyline check gives 47.74.
* **Cable tolerance:** the pocket is 2 mm longer at each Y end (`fxp_slide`), and the cable exit moves between Y -25.17 and -21.17. At assembly, the flex is placed where the cable is straight but not tight.
* **Strip is clear:** from the KiCad placements, the top side has **no parts** at board x > 38.9 between board y 20.85 and 62.29. Under the plug there is only J3 itself; C38 is at x 38.6, FL2/L9 at x ≤ 47.
* **Lid keepers:** three pads (4 x 3 at Y 4 and -9 over the board; 3 mm over the trough) stop 0.3 above the cable, so it cannot lift.
* **Bend radius:** no vendor gives one. 4.5 is a design value, and the assert floor is `cable_bend_min` 3.4 (3 x OD).

The right-wall snap bead at Y -32 sat on the slot. It moved to **-38** (`snap_right_y = [-38, -2]`; the left wall stays at -32 / -2). One extra bead sits on a short lid lip along the bay's inner top wall (X 46.65).

## 4. SMA geometry removed, Z stack re-derived

**What is off.** `use_sma = false` (default) disables all of the SMA geometry:

* the wall U-slot and barrel hole;
* the lid tongue;
* the 0.225 flange recess in the lid;
* the lid-lip notch at the jack;
* the flange and leg floor pockets;
* `sma_leg_cut` (assembly step 4a);
* the SMA asserts and ECHOes.

The board notch is now drawn by `board_notch = true`, independent of the antenna, so the routed outline and the DXF do not change.

**Regression check.** `use_fxp=false use_sma=true snap_right_y=[-32,-2]` reproduces the lowprofile console line for line, including the leg-cut line. The only difference is one added phrase ("29.6 mm from the left edge").

**Re-derived stack:**

| Limit | Needs | Binding? |
|---|---|---|
| USB-C overmold opening (`usb_z0 >= z_floor + 0.5`; it also protects the clocking pocket, 0.1 mm behind the wall cut) | board bottom ≥ 4.68, so 4.76 | **yes, bottom** |
| Patch feed pin pocket (Z 3.20, 1.56 under the board) | ok at 0.6 gap | no |
| USB stake pockets (Z 3.56) | ok | no |
| Insert stack | board bottom ≥ 4.40 | no |
| SMA leg / flange (lowprofile: forced the leg cut at gap 0.6, or gap 1.3 uncut) | | **gone** |
| Top: USB4105 3.31 + 0.5 | 3.85 | **yes, top** |
| Top: patch window 4.6 + 0.3 - 1.2 | 3.70 | no |
| Top: U.FL mated 2.5 + 0.5 (new `top_clear` term) | 3.00 | no |
| Top: flex solder joint over the shelf | sets the shelf height, not the lid | no |

**Total stays 11.41 mm (no change).** In the lowprofile default the SMA was already absorbed by the leg cut, the pockets and the lid recess. What the SMA removal buys is no leg cut and no 12.13 mm fallback. The remaining cut, as in LOWPROFILE.md, is a local lid recess over the USB4105 and L1 (about -0.45 mm). It was not taken, because the patch would end up flush with the lid face.

## 5. Asserts

All lowprofile asserts are kept, and all pass (print_plate, assembly and pcb_outline `.echo` files: 0 ERROR / WARNING / Assertion). The SMA-specific ones are guarded by `use_sma`, so they pass vacuously.

**New asserts:**

* **Configuration:** not both `use_fxp` and `use_sma`.
* **U.FL:**
  * on the board;
  * mated height + 0.5 under the lid;
  * plug clear of the lid lip;
  * vents ≥ `vent_keep` from the U.FL and cable.
* **Cable:**
  * bend ≥ 3.4;
  * lead ≥ 2 and a straight run left at the shortest cable;
  * slide ≥ cable tolerance;
  * path length = free length;
  * bend finished before the wall;
  * run clear of the lid lip;
  * where the bend enters the lip band, it is inside the lip notch;
  * ≥ 5 from the RX patch;
  * clear of all screw heads;
  * right-wall beads clear of the slot;
  * slot off the corners and inside the bay;
  * keepers: on the straight run, off the patch window and the lip, ≥ 0.5 tall.
* **Flex and bay:**
  * ≥ `ant_gnd_min` 4 from the board ground;
  * pocket outside the main wall;
  * ≥ `ant_rx_min` 20 from the patch;
  * ≥ 4 from the ring;
  * pocket depth within one layer of flex + adhesive;
  * solder joint ≥ 0.2 under the lid;
  * shelf ≥ 0.8 under the pocket;
  * room for ribs;
  * bay floor ≥ `floor_web`;
  * ≥ 0.4 of shelf round the pocket;
  * bay within the body length;
  * cable above the slot floor;
  * hold-down pins clear of the worst flex and always over the flex, off its cable.

**Each was forced to fail once** with a readable message:

| Override | Message |
|---|---|
| `use_sma=true` | "use_fxp and use_sma both on..." |
| `snap_right_y=[-32,-2]` | "Right-wall snap bead at y -32 runs into the cable slot" |
| `cable_bend_r=3` | "Cable bend radius below 3.4 mm" |
| `fxp_slide=1` | "fxp_slide must cover the cable length tolerance" |
| `ant_gnd_min=11` | "Flex pocket only 10 mm from the board ground" |
| `ant_rx_min=30` | "Flex pocket only 24.8 mm from the RX patch" |
| `cable_rx_min=12` | "TX cable only 9.76 mm from the RX patch" |
| `keeper_y=[10]` | "Cable keeper at y 10 is off the straight run" |
| `cable_len=80` | "TX cable runs over the screw head at board hole [51.5, 3.5]" |
| `holddown_gap=0` | "Hold-down pins press on the worst-case flex" |
| `shelf_t=1.0` | "Shelf under the flex pocket thinner than 0.8 mm" |
| `bay_snap_x=0` | "Snap bead [4, 0] runs onto a corner radius" |

`ufl_mated_h=3.5` does not fire an assert. By design, it raises `top_clear`: the lid underside goes 10.21 → 10.36 and the top to 11.56.

## 6. Assembly

1. **Magnets, inserts and board:** as lowprofile. There is no SMA and no leg cut. Clip any USB-C stakes that stand more than 1.0 below the board.
2. **Fit the antenna:**
   * Clean the pocket with IPA.
   * Mate the plug on J3 straight down, cable toward -Y (toward USB-C).
   * Lay the cable along the strip, round the bend, down the wall slot and up the trough.
   * Peel the liner and lay the flex in the pocket, cable side up, with the cable corner toward the board's top (+Y).
   * Slide the flex in Y until the cable is straight but not tight. Do not let it pull the plug sideways.
   * Press the flex down for 10 s.
3. **Close:** press the lid on (6 beads: right wall at -38 and -2, left wall at -32 and -2, top wall, and the bay's top wall). The keepers and pins drop over the cable and the flex.

## 7. Risks

1. **RF performance is not measured.**
   * The flex is 10 mm from the ground edge; Taoglas recommends 20. Expect lower efficiency and a frequency shift against the datasheet.
   * The shelf (1.6 PETG) plus lid (1.2 PETG over 2 mm of air) is not the 2 mm ABS reference.
   * The datasheet tuning on ABS already sits low (return loss minimum at 2.36 GHz). Less loading would move it up, which may help.
   * Check with a VNA in the closed box, with a hand and with the phone attached. Tuning knobs: `shelf_t`, `ant_gnd_gap`. Taoglas also offers a tuning service.
2. **TX/RX isolation** is set by about 25 mm of edge spacing, 55 mm between centres, and partial polarisation help. It will not reach the 45 dB in schematic_review on its own.
3. **Cable length tolerance.**
   * The slide covers the cable's ±2.
   * It does not cover the ±0.5 of the plug's crimp position. That shows up as a small bow, or as slight tension at the long and short extremes.
   * U.FL retention is low (about 30 mating cycles), so a tight cable can unseat the plug or lift it when the lid is removed.
4. **No vendor bend radius** for the 1.13 mm cable; 4.5 mm (4 x OD) is assumed.
5. **Datasheet ambiguities.**
   * Flex thickness: 0.08 / 0.2 / 0.24, so worst case is used.
   * Solder joint up to 1.7, which leaves only 0.21 under the lid.
   * Cable exit offset and on-flex length are scaled from the drawing (±0.3).
   * Measure the first antenna.
6. **Mechanics.**
   * The 36 mm wing overhangs the phone edge and changes grip and pocketing.
   * The lid wing is held by one bead, the main-body beads at Y -38 and the three pins. Check how it survives a drop and prying.
   * Plus / Pro Max phones put 1.4 mm of flex over the phone.
7. **Right-wall bead moved** from -32 to -38. Its end (Y -44) is now 3.95 mm from the start of the corner radius (Y -47.95), and the assert passes. The bead sits beside the H2 screw head, clear in X.
8. **Print plate** is about 198 x 83 mm (base 95.1 + 8 + lid 95.1).
   * The shelf bridges 6.5 mm between ribs.
   * The pocket is 3 layers deep in the shelf top.
   * No supports.
9. **Board notch.** The old 1.5 x 7.1 TX notch stays in the routed board. It is now unused, and harmless.
10. **Possible reference mismatch.** docs/schematic_review.md and docs/antenna_connectors.md call J3 the RX U.FL and J4 the TX U.FL. The PCB file has one U.FL, J3, valued "TX antenna U.FL". Not verified further; worth a check before fab.

## Files

| File | What |
|---|---|
| `beacon_phone_magsafe_lowprofile_fxp70.scad` | new model (FXP70 default, `use_sma` legacy) |
| `FXP70.md` | this note |
| `fxp70_print_plate.echo` / `fxp70_assembly.echo` / `fxp70_pcb_outline.echo` | console (ECHO, asserts): 0 errors |
| `fxp70_pcb_outline.dxf` | board outline, identical to lowprofile |
| `fxp70_assembly.png` | exploded assembly preview |
| `fxp70_routing_top.png` | top view without the lid: U.FL, cable path, bay, flex |
| `fxp70_section_cable.png` | section on the cable centreline (keep y ≤ y_c): board run, wall slot, trough, flex, lid keepers |
| `fxp70_section_flex.png` | section across the bay at the flex centre: ribs, shelf, pocket, trough keeper, bay lip and bead |
| `fxp70_lid_print.png` | lid in print orientation |
| `fxp70_print_plate.stl` / `fxp70_assembly.stl` | CGAL `--render` exports (background): 2 min 8 s and 3 min 38 s, no ERROR / WARNING, both Simple: yes (2-manifold) |

The previews are OpenCSG previews, not `--render`, so cut faces are drawn in one colour.
