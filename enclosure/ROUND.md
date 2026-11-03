# beacon_phone_magsafe_round.scad: rounded "pebble" shell

**Source:** `beacon_phone_magsafe_fxp70_inlid.scad`. It was not modified (md5 67a76b485a81efce0cb696b65e7903a0). Neither were the other `.scad` files, the Downloads original or any KiCad file (the board file was only read, for the mounting-hole footprint).

**What changed:** only the outside of the shell. The 0.4 mm chamfers are replaced by a continuous convex side profile, and the plan corners grow from r 5.1 to r 7.6. The board, its outline DXF, the Z stack, the cavity, the lid lip and its cuts and notches, the snap beads and grooves, the USB-C opening, the FXP70 pocket, the cable route, the patch window, the magnets and the skin are unchanged. Every ECHO line of `inlid_assembly.echo` is reproduced exactly, except the title, the `Outside:` line and the new `ROUND` lines (`diff` clean).

| | fxp70_inlid | **round** |
|---|---|---|
| Outside, widest | 59.2 x 82.65 x 11.41 | **61.2 x 84.65 x 11.41** (+1.0 per side at Z 6, nothing added in height) |
| Seam band (Z 10.21) | 59.2 x 82.65 | 60.24 x 83.69 |
| Flat phone face | 58.4 x 81.85 | **56.2 x 79.65**, r 6.1 (covers the ring and clocking magnet with 0.9 to spare) |
| Flat lid face | 58.4 x 81.85 | 57.7 x 81.15, r 6.85 |
| Plan corner radius | 5.1 | **7.6** at the nominal outline, 8.6 at the widest |
| Edges | 0.4 x 45 deg chamfers | 45 deg + R 4.5 bottom, convex R 25 side, R 2.5 + 60 deg top |

Checked with OpenSCAD 2021.01 on 2026-11-02.

## 1. Side profile

The profile is the outward offset `o(z)` of the plan outline from the nominal outline (cavity + 1.8 wall), the same on all four sides and round the corners. From the phone face up:

| Z | o | Segment |
|---|---|---|
| 0 | -1.5 | flat phone face edge (`bot_inset`) |
| 0 - 1.11 | -1.5 to -0.39 | 45 deg chamfer (`bot_ang`) |
| 1.11 - 3.92 | to +0.91 | R 4.5 round (`bot_r`) |
| 3.92 - 9.42 | +1.0 max at Z 6, +0.76 at Z 9.42 | convex side, R 25 (`bulge`, `bulge_z`, `side_r`) |
| 9.42 - 11.24 | to -0.46 | R 2.5 round (`top_r`), crossing the seam at o +0.52 |
| 11.24 - 11.41 | to -0.75 | 60 deg chamfer to the flat lid face (`top_inset`, `top_ang`) |

* All joints are tangent. The only creases are where the two chamfers meet the flat faces: 135 deg at the phone face and 120 deg at the lid face. Both are obtuse and print soft.
* At the seam the shell leans in 27 deg. The lid edge is a 63 deg wedge, not a knife edge, and it sits flush on a 2.3 mm wide wall top.
* The shell is one lofted `polyhedron` per part (26 rows x 68 points), so CGAL stays fast: base 74 s, lid 8 s.
* `profile2d` draws the profile against the flex pocket, the cavity, the ring pocket and the old chamfered outline (`round_profile.png`).

### Why the top edge is only R 2.5 / 0.75 inset

The FXP70 pocket runs over the top wall to **0.62 mm from the outer edge**, under only 0.8 mm of lid. Any rounding of the lid's top edge eats into that skin.
* With a 45 deg limit on the lid face (the lid prints face down), the top-face inset can be at most about 0.57 before the skin over the pocket edge drops below `lid_skin_min` 0.6. That is barely more than the old chamfer.
* Two things buy room:
  1. The bulge. It moves the seam band 0.52 outward, so the pocket rim at the seam is 0.93.
  2. A 60 deg limit at the lid face. That is 0.21 mm of step per 0.12 layer, half a 0.42 line, which is a safe overhang for PETG over the first 2 layers. Above Z 11.24 (assembled) the round gets steeper.
* The result passes at 0.62 skin and 0.93 rim at the pocket edge. Asserts check every point round the pocket outline against the actual rounded surface.
* Bigger top rounds need the pocket to move inward (not possible: the patch window web is already 1.0) or a thicker top wall. Without the pocket, the top edge could be about R 4.

### Lid crown (item 3): evaluated, not built

* A 0.5-1 mm crown would raise the middle of the lid to 11.9-12.4 mm, above the 11.41 limit.
* It also makes the lid unprintable face down: the outer face would no longer lie flat on the bed. Printing it face up puts the lip, rails and keepers on the bed, and they need full support.
* It does not help the patch window (deeper recess) or the flex (thicker skin, more dielectric loading).
* So it is off, and there is no parameter for it.

## 2. Plan corners and the board radius

**(a) Current board, r 3: outside radius 7.6** (auto; it was 5.1).
* The cavity corner must stay r 3.3 (pcb_r + 0.3 clearance). A larger outside radius therefore thins the corner wall along the diagonal: 0.76 mm nominal at R 7.6.
* The bulge brings it back to **1.02 mm minimum** over the cavity height. That makes the wall_min limit the binding one (`corner_r = 0` searches it in 0.1 steps).
* Without the bulge, the limit would be R 7.03.

**(b) Larger board radius.** The holes sit 3.5 mm from both edges. A corner arc of radius r passes the hole at distance r - sqrt(2)(r - 3.5) (for r > 3.5), so the largest radius for a keep circle of radius k is (sqrt(2) x 3.5 - k) / (sqrt(2) - 1):

| Keep circle round the hole (+0.5 margin) | max pcb_r | Outside radius (auto) | Extra changes needed |
|---|---|---|---|
| **6.0 mm standoff (your criterion)** | **3.5** | **8.1** | none |
| 4.9 KiCad courtyard (MountingHole_2.2mm_M2) | 4.83 (use 4.8) | 9.4 | `pcb_keep_d = 4.9` |
| 4.4 KiCad Cmts.User head circle | 5.43 | 9.7 | `pcb_keep_d = 4.4`, `snap_top_x = [-15]` |
| 3.8 screw head | 6.16 | 9.7 | `pcb_keep_d = 3.8`, `snap_top_x = [-15]` (6.16 also `snap_right_y = [-38, -24, 14.5]`, top -14.5) |
| 2.2 hole only | 8.09 | fails | the cavity corner alone (10.2) is past the pocket limit |

* **Your 6-8 mm estimate does not hold for the 6 mm standoff.** Because the straight edges are already exactly 3.5 from the holes, any radius above 3.5 brings the board edge closer than 3.0 + 0.5 to the hole. The 6-8 mm range corresponds to keeping only the screw head (6.16) or the bare hole (8.09) on the board.
* Past about r 5, the standoff cylinder in the base simply overlaps the cavity corner wall. That is harmless, since both are base plastic.
* **The outside radius saturates at 9.7** (from pcb_r of about 5.2 up). The binding limit is the FXP70 pocket corner at (20.61, 28.98), which enters the plan corner arc and loses skin. Up to pcb_r 7.6 the board and cavity corners still round further, but the outside does not.
* **Practical recommendation:**
  * pcb_r **3.5** (no other changes, standoff fully supported, outside 8.1);
  * or pcb_r **4.8** with `pcb_keep_d = 4.9` (courtyard still on the board, outside 9.4).
* Larger values buy only 0.3 more and need bead moves.

**Implementation:**
* `pcb_r` is the single switch.
* `corner_r = 0` (auto) follows it. Asserts check the keep circle (`pcb_keep_d`, `pcb_keep_m`), the TX notch and J3 against the board corner arcs.
* The existing bead and pry-notch corner asserts catch what else has to move.
* **DXF:** the default `pcb_r = 3` export `round_pcb_outline.dxf` is byte-identical to `inlid_pcb_outline.dxf` (md5 18390473f7549610058dd7b00660f624, `cmp` clean). Any other pcb_r changes only the four corner arcs of the outline (and the board in KiCad must follow).

## 3. Printability

* **Base, phone face down.**
  * The overhang is at most 45 deg: the bottom chamfer. The round above it only gets steeper, and above Z 6 the side goes inward. The assert measures every profile segment (`pf_ovh_base` 45.0).
  * The skin (0.68), the pause (layer 29, Z 3.56) and the print-in-place magnet pockets are unchanged.
  * The flat face still covers the ring and the clocking pocket with 0.9 mm to spare (assert ≥ `face_margin` 0.5), with 1.13 mm of plastic beside the pockets (assert ≥ 1.0).
* **Lid, outer face down.**
  * The first 0.17 mm (about 1.5 layers) is the 60 deg chamfer, a step of 0.21 per 0.12 layer.
  * Then the R 2.5 round steepens to 0 deg at Z 9.42 and is vertical at the lip side.
  * Assert: `layer_h x tan(top_ang) <= line_w / 2` and the measured max 60.0 deg.
  * In the slicer, make sure the first-layer "elephant foot" compensation does not eat the 0.75 inset face edge.
* **No supports** on either part.

## 4. Walls and functions after rounding

| Check | Value | Assert |
|---|---|---|
| Side wall, min over the cavity height | 1.59 (1.8 nominal, 2.8 at the bulge) | ≥ `wall_min` 1.0 |
| Cavity corner wall (diagonal) | 1.02 | ≥ 1.0 (sets the auto radius) |
| Behind the snap grooves (all 6, both ends) | 2.27 | ≥ 1.0 |
| Insert holes to the outside | 2.15 | ≥ 1.0 |
| Magnet pockets to the outside | 1.13 | ≥ `mag_side_min` 1.0 |
| Flex pocket rim / skin at its edge | 0.93 / 0.62 | ≥ 0.5 / 0.6 |
| Lid plate over the lip | full 1.2 (lid face inset 0.75 ≤ 0.96) | full lid_t |
| Footprint growth | +1.0 per side | ≤ `grow_max` 1.0 |
| Height | 11.41 | unchanged |

* The USB-C U-slot and the lid notch are lengthened by the bulge so they still cut clean through. The pry notch is cut deeper for the same reason; it keeps its 0.9 mm inner half by design, as before.
* The lid lip cut over the pocket, the right-wall notch, the beads, the FXP70 pocket, groove, rails and keepers, the patch window and the cable route are untouched. All their asserts pass.

## 5. Asserts

All fxp70_inlid asserts are kept and pass. The one exception is the flat-outline pocket-corner check, which is replaced by the rounded rim/skin check below.

**New asserts:**
* **Profile:**
  * the profile has a tangent solution and its rows rise monotonically;
  * bulge_z lies between the floor and the seam;
  * the top round sits above the widest section and the bottom round below it;
  * the top round is no taller than lid_t plus half the side above the bulge.
* **Overhangs:**
  * base ≤ 45;
  * lid ≤ top_ang, and the layer step ≤ line_w / 2.
* **Size:** footprint growth ≤ grow_max.
* **Walls:**
  * plan radius ≥ 1 at both faces;
  * corner_r ≥ concentric;
  * side wall, corner wall, snap grooves and inserts ≥ wall_min;
  * standoffs inside the shell.
* **Magnets:** flat-face margin and magnet side plastic.
* **Lid:**
  * flex pocket rim and skin, checked against the rounded edge all round the pocket;
  * full lid plate over the lip;
  * seam lean ≤ 45 deg (no knife edge).
* **Board:**
  * no auto radius possible (message names wall_min and the pcb_r limit);
  * pcb_r keep circle;
  * TX notch and J3 off the board corner arcs.

**Forced to fail once each:**

| Override | Message (abridged) |
|---|---|
| `bot_ang=50` | "Base overhang 50 deg (prints phone face down; max 45)" |
| `top_ang=62` | "Lid edge overhang 62 deg: 0.23 mm per layer is over half the 0.42 line" |
| `top_ang=70` / `bulge_z=8 side_r=10` | "Rounded profile has no tangent solution" |
| `bulge=1.3` | "Bulge grows the footprint 1.3 mm per side (max grow_max 1)" |
| `corner_r=8.5` | "Corner wall only 0.76 mm with corner_r 8.5" |
| `bot_inset=2.2` | "Flat phone face ends 0.2 mm past the magnet pockets" |
| `bot_inset=1.9` | "Only 0.83 mm of plastic beside a magnet pocket" |
| `top_inset=1.2` / `top_r=4` | "Rounded lid edge leaves 0.4 / 0.5 mm over the flex pocket edge" |
| `bulge=0 bulge_z=5` / `side_r=3` | "Flex pocket edge ... leaves 0.07 / 0.35 mm to the rounded outer edge" |
| `bulge_z=9.5` | "Top round starts below the widest section" |
| `pcb_r=4` | "Board corner r 4 comes within 0.29 mm of the 6 mm keep circle ... max pcb_r 3.5" |
| `wall_min=1.7` | "No outside corner radius from 5.1 up keeps wall_min (1.7) ..." |
| `tx_pos=73` | "Board notch at the old TX jack runs onto a board corner radius" |

The seam-lean, lid-over-lip, insert, standoff and J3-corner asserts are guarded, but other asserts fire first for every override tried, so they were not seen failing on their own.

## Files

| File | What |
|---|---|
| `beacon_phone_magsafe_round.scad` | new model. New parameter group *Rounded shell*; new parts `closed`, `sec2d_edge`, `profile2d` |
| `ROUND.md` | this note |
| `round_print_plate.echo` / `round_assembly.echo` / `round_pcb_outline.echo` | console (ECHO, asserts): 0 ERROR / WARNING / Assertion |
| `round_pcb_outline.dxf` | board outline, byte-identical to inlid / lowprofile |
| `round_assembly.png` | exploded assembly, iso |
| `round_closed_iso.png` / `round_bottom_iso.png` | closed shell from above / below (flat phone face) |
| `round_side.png` / `round_end.png` | orthographic silhouettes from +X (long side) and from -Y (USB-C end) |
| `round_profile.png` | the side profile at 1:1 against the pocket, cavity, ring pocket and the old chamfered outline |
| `round_section_flex.png` | true `projection(cut)` section at x 7.16 (flex centre): rounded top edge over the flex pocket, bottom edge at the USB end |
| `round_section_flex_detail.png` | crop of the top-wall edge of that section |
| `round_section_edge.png` | true section at y 0: both side walls, ring pocket, patch window |
| `round_print_plate.stl` / `round_assembly.stl` | CGAL `--render` exports (background), see Verification |

## Verification

* The `.echo` exports were grepped for ERROR / WARNING / Assertion: none.
* The DXF passes `cmp` against `inlid_pcb_outline.dxf`.
* The source `.scad` md5 values are unchanged.
* Previews are OpenCSG. The `round_section_*` images are CGAL projection cuts.
* STL exports: CGAL `--render`, run in the background. Both finished with no ERROR or WARNING, and CGAL reports both as Simple: yes (2-manifold).
  * `print_plate`: 1 min 52 s, 23 volumes.
  * `assembly`: 3 min 50 s, 27 volumes.
* The section PNGs took 1 min 54 s (`sec2d_ant`) and 2 min 35 s (`sec2d_edge`, with `label=false`).
