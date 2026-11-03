# Enclosure constraints on the PCB (BEACON phone module, MagSafe 2.5 mm ring)

Source: `C:\Users\marsi\Downloads\beacon_phone_magsafe_2p5mm_Latest.scad`, default parameters (read-only).
The numbers come from OpenSCAD 2021.01 (`C:\Program Files\OpenSCAD\openscad.com`) run headless. That run gave the file's own ECHO lines, plus a wrapper that `include`s the file and echoes every derived variable. They were cross-checked against `beacon_phone_magsafe_2p5mm_Latest.stl`: outside 59.2 x 82.65, base height 12.72, and Z levels 4.16 floor / 5.72 board bottom / 8.02 SMA axis / 10.57 snap all match. No assert fires at the defaults.

Machine-readable version: `enclosure_constraints.json`, in the same folder. Units are mm.

## Coordinate frames

* **Board coords** (as the scad defines them): origin at the board's lower-left corner seen from the component (top) side. The USB-C edge is at the bottom (y = 0), +x is right, +y is toward the top of the phone.
* **Enclosure coords**: origin at the MagSafe ring centre on the phone-contact face. +Y points to the top of the phone, +X is right seen from the back of the phone, +Z is away from the phone. The axes are parallel to the board axes, with no rotation or mirror.
* `x_enc = x_board - 27.5`, `y_enc = y_board - 50.95`. The reverse is `x_board = x_enc + 27.5`, `y_board = y_enc + 50.95`.
* KiCad's Y axis points down. With the board lower-left at KiCad (X0, Y0): `kicad_x = X0 + x`, `kicad_y = Y0 - y`.

Z stack (enclosure Z, 0 = phone face):

| z | what |
|---|---|
| 0.00 - 0.68 | skin under the magnets |
| 0.68 - 3.23 | ring magnet and clocking bar (2.55 thick) |
| 3.56 | pocket tops (print pause) |
| 4.16 | cavity floor top (sealed cap) |
| 5.72 | **board bottom** |
| 7.32 | **board top** |
| 9.72 | bottom of the lid lip |
| 12.72 | lid underside (seam) |
| 13.12 | lid underside over the patch radome (recess 0.4) |
| 14.32 | lid outer face |

## Board

* **55.00 x 78.45 x 1.6**, corner radius 3.0. The board edge sits 0.3 from the cavity wall on every side. Cavity inner wall in board coords: x -0.3 .. 55.3, y -0.3 .. 78.75, r 3.3.
* **Outline**, CCW: (3,0) -> (52,0) -> arc c(52,3) -> (55,3) -> (55,62.45) -> (53.5,62.45) -> (53.5,69.55) -> (55,69.55) -> (55,75.45) -> arc c(52,75.45) -> (52,78.45) -> (3,78.45) -> arc c(3,75.45) -> (0,75.45) -> (0,3) -> arc c(3,3) -> (3,0). This matches the scad's `part="pcb_outline"` render exactly.
* **TX notch** (right edge): x 53.5 .. 55.0, y 62.45 .. 69.55, which is 1.5 deep and 7.1 wide. Depth = `sma_body[1] + 0.2 - tx_gap` = 1.6 + 0.2 - 0.3. Half-width = `sma_body[0]/2 + 0.3` = 3.55. The inner corners are square in the scad, and the router radius (about 0.5) still clears the jack body.
* **Mounting holes**: (3.5, 3.5), (51.5, 3.5), (3.5, 74.95), (51.5, 74.95), each 2.2 diameter.
  * Keep pads clear over **6.0 diameter on both sides**. A 6 mm standoff fills the gap under each hole.
  * Top side: M2 pan head, 3.8 diameter x 1.6 tall. The scad's checks use a 2.2 radius, so plan a 4.4 diameter keepout.
  * Fastening: 4x M2 x 4 screws into M2 x 3 heat-set inserts, 2.4 of thread engaged.

## Sketch (board coords, top view, 1 column = 1.25 mm, 1 row = 2.5 mm)

```
   y   |x: 0       10      20      30      40      50  55
  77.5 |  ~HH~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~HH~         TOP edge (lip band; snap bead x 21.5-33.5)
  75.0 | HHHHH.......oooooooooooooooooooo.......HHHHH        holes (3.5,74.95) (51.5,74.95)
  72.5 | ~HHH.....ooooooo............ooooooo.....HHH~
  70.0 | ~.....oooooo....................oooooo...~~~
  67.5 | ~....oooo..........................oooo....T  <- TX notch y 62.45-69.55, x 53.5-55
  65.0 | ~..ooooo............................ooooo..T     SMA axis y 66, 0.7 above board top
  62.5 | ~.oooo................................oooo.        (lip cut away y 62.25-69.75)
  60.0 | ~oooo..................................oooo~
  57.5 | ~ooo....................................ooo~
  55.0 | ~ooo....................................ooo~
  52.5 | ~ooo.......::::::::::::::::::::::.......ooo~   <- radome 28.4 sq (y to 53.425)
  50.0 | ~ooo.......:PPPPPPPPPPPPPPPPPPPP:.......ooo~      ring centre (27.5, 50.95)
  47.5 | ~ooo.......:PPPPPPPPPPPPPPPPPPPP:.......ooo~
  45.0 | ~ooo.......:PPPPPPPPPPPPPPPPPPPP:.......ooo~   side snap beads, both walls,
  42.5 | ~oooo......:PPPPPPPPPPPPPPPPPPPP:......oooo~     y 42.95-54.95 and 12.95-24.95
  40.0 | ~.oooo.....:PPPPPPPPPPPPPPPPPPPP:.....oooo.~   <- RX patch centre (27.5, 39.225)
  37.5 | ~..oooo....:PPPPPPPPPPPPPPPPPPPP:....oooo..~      footprint 25.4 sq
  35.0 | ~...ooooo..:PPPPPPPPPPPPPPPPPPPP:..ooooo...~
  32.5 | ~.....ooooo:PPPPPPPPPPPPPPPPPPPP:ooooo.....~
  30.0 | ~.......ooo:PPPPPPPPPPPPPPPPPPPP:ooo.......~
  27.5 | ~..........:PPPPPPPPPPPPPPPPPPPP:..........~
  25.0 | ~..............oooooooooooooo..............~
  22.5 | ~..........................................~
  20.0 | ~..........................................~
  17.5 | ~..................cccccc..................~   <- clocking magnet pocket
  15.0 | ~..................cccccc..................~      x 24.35-30.65, y 0.3-19.9
  12.5 | ~..................cccccc..................~      (under the board)
  10.0 | ~..................cccccc..................~
   7.5 | ~..................cccccc..................~
   5.0 | ~HHHH.............UUUUUUUU.............HHHH~   <- USB-C body x 23.03-31.97, y 0-7.3
   2.5 | ~HHHH.............UUUUUUUU.............HHHH~      holes (3.5,3.5) (51.5,3.5)
   0.0 |   ~~~~~~~~~~~~~~~.UUUUUUUU.~~~~~~~~~~~~~~~      BOTTOM edge: USB opening x 21.2-33.8,
                                                          lip cut away x 20.9-34.1, pry notch x 39.5-47.5
legend:  ~ lid-lip band (2.4 max height, 1.1 from edge)   H 6 mm standoff/pad keepout
         o ring-magnet pocket annulus r 22.85-27.2 (below the board)   c clocking-magnet pocket (below)
         P patch footprint incl. tolerance   : radome margin   U USB-C body   T SMA jack body (off board)
```

## Magnets, projected onto the board (they sit below the board and do not touch it)

* **Ring annulus**: centre (27.5, 50.95). The pocket runs from r 22.85 to 27.20, which includes 0.15 radial clearance; the magnet itself is r 23.00 - 27.05. In board coords it covers x 0.3 .. 54.7 and y 23.75 .. 78.15.
* **Clocking magnet**: the pocket is x 24.35 .. 30.65, y 0.30 .. 19.90, with 0.8 diameter corner reliefs. The magnet itself is x 24.5 .. 30.5, y 0.45 .. 19.75.
* **Distance below the board bottom (z 5.72)**:

  | to | distance |
  |---|---|
  | cavity floor | 1.56 |
  | pocket tops | 2.16 |
  | magnet tops | 2.49 |
  | magnet bottoms | 5.04 |
  | phone face | 5.72 |

  Magnetically sensitive parts (magnetometer, Hall sensors, ferrite inductors) sit within about 2.5 of N52 magnets over most of the board.

## USB-C (bottom edge)

* **Receptacle**: centre x = 27.5, front flush with the board edge (overhang 0). The body is 8.94 W x 7.3 L x 3.26 H, which covers x 23.03 .. 31.97 and y 0 .. 7.3.
* **Centreline**: 1.63 above the board top (enclosure z 8.95).
* **Wall opening**: 12.6 W x 6.7 H, r 1.5, spanning x 21.2 .. 33.8.
  * It is an open-top U through the wall that the lid closes. Its bottom is 1.72 below the board top, which is 0.12 below the board bottom.
  * The lid lip is cut away over x 20.9 .. 34.1.
* **Hole keepout rectangle**: x 21.2 .. 33.8, y -2.1 .. 7.3. Hole centres must stay at least 3.3 from it.

## RX patch (Taoglas WDP.2458.25.4.B.02, top side)

* **Centre**: (27.5, 39.225), which is the board centre (enclosure (0, -11.725)).
* **Footprint including tolerance**: 25.4 square (25.1 + 0.3), covering x 14.8 .. 40.2 and y 26.525 .. 51.925.
* **Radome region**: 28.4 square, covering x 13.3 .. 41.7 and y 25.025 .. 53.425. Over it the lid is recessed 0.4, leaving a 1.2 radome. The lid underside there is 5.8 above the board top.
* **Heights**: 0.3 tape + 4.1 patch = 4.4 above the board top. The design air gap is 1.0; the actual gap under the radome is 1.4.
* **Feed pin**: 2.8 long. It protrudes 1.2 below the board bottom (the scad ignores the tape), leaving 0.36 to the floor.

## TX jack (edge-launch SMA(F), right edge)

* **Position**: y = 66 on the right edge (enclosure y 15.05). The board notch is x 53.5 .. 55.0, y 62.45 .. 69.55.
* **Body**: 6.5 W x 1.6 thick x 6.5 H, covering x 53.7 .. 55.3 and y 62.75 .. 69.25.
  * It bears on the inner wall face and sits 0.2 beyond the notch floor.
  * In Z it runs from 2.55 below to 3.95 above the board top, so it reaches 0.95 below the board bottom with 0.61 to the floor.
* **Barrel axis**: 0.70 above the board top (enclosure z 8.02). The thread is 6.35, the wall hole 6.85, and 5.2 of thread stands outside the wall.
* **Lid**: the lip is cut away over y 62.25 .. 69.75. A 6.55 tongue closes the slot.
* **Allowed `tx_pos` on the right or left edge**, from the corner and snap-bead asserts at the default beads: [6.925, 8.525], [29.375, 38.525] or [59.375, 71.525].

## Height limits

| region | max part height | note |
|---|---|---|
| top side, general | **5.40** above the board top | zero margin to the lid underside. Set by the patch (4.4 + 1.0). The scad's design value for ordinary parts is `top_parts_h` 3.3 (+0.5) |
| top side, within **1.1** of the board edge (lid-lip band) | **2.40** above the board top | echo: "2.4 mm within 1.1 mm of the board edge, under the lid lip". The band follows the outline, with inner corner r 1.9. Exceptions: bottom edge x 20.9-34.1 and right edge y 62.25-69.75, where the lip is cut away |
| top side, inside the radome square | 5.80 | the lid is recessed 0.4 there |
| bottom side | **1.56** below the board bottom | floor at z 4.16, no margin. Use 1.26 to keep the scad's 0.3 margin. `pcb_gap` = 1.5 |
| bottom side, patch feed pin | pin protrudes 1.2 | 0.36 left (1.56 - 1.2). The assert needs ≥ 0.3 |
| bottom side at holes | 0 | 6 mm standoffs |

## Other things near the edge

* **Lid lip**: 1.2 thick, 3.0 deep. It overlaps the board from the edge to 1.1 inboard; its outer face is 0.1 outside the board edge.
* **Snap beads**: 12 long, on the lip's outer face, clicking outward into 0.35-deep wall grooves. Their centre is 3.25 above the board top (± 0.75). They add no intrusion beyond the lip band. Positions:
  * left and right walls: y 12.95 .. 24.95 and 42.95 .. 54.95
  * top wall: x 21.5 .. 33.5
* **Pry notch**: bottom wall, x 39.5 .. 47.5. It is cut in the outer half of the wall at the seam (z 11.52 .. 12.72) and does not reach over the board.
* **Screw heads**: 3.8 diameter. They reach to 1.6 from the edges, which is 0.5 inboard of the lip band. The head top is 1.6 above the board, below the 2.4 lip bottom.

## Asserts in the scad that constrain the PCB

All values are at the defaults. "Line" is the line number in the .scad.

| line | condition | limit | value now |
|---|---|---|---|
| 318 | `pcb_W > 0 && pcb_L > 0` | > 0 | 55 x 78.45 |
| 322 | stock screw fits: `screw_L > 0`, longest of [3,4,5,6,8,10] ≤ z_pcb_top - tip_z | ≤ 4.70 | M2 x 4 |
| 323 | `engage = screw_L - pcb_t >= 1.5` | ≥ 1.5 | 2.4 |
| 324 | screw head clears the lid lip: `z_pcb_top + screw_head_h + 0.3 <= z_seam - lip_h` (or ≤ top_clear) | head h + 0.3 ≤ 2.4 | 1.9 |
| 343 | `z_hole_bot >= floor_web` | ≥ 1.0 | 2.32 |
| 344 | cavity corner (r = pcb_r + 0.3) clear of the ring pocket: `norm([cav_x-cav_r, cav_y1-cav_r]) >= ring_ro` | ≥ 27.2 | 34.65 |
| 347 | `usb_z0 >= z_floor + 0.5` (opening vs floor) | ≥ 4.66 | 5.60 |
| 348 | `abs(usb_x) + usb_open_w/2 <= cav_x - cav_r`: USB opening off the corners | ≤ 24.5, so board usb centre x 9.3 .. 45.7 | 6.3 |
| 349 | lid lip clears the board: `z_seam - lip_h >= z_pcb_top + 0.5` | ≥ 7.82 | 9.72 |
| 351 | each hole: `dist(hole, ring centre) >= ring_ro + 0.5 + standoff_d/2` or `<= ring_ri - 0.5 - standoff_d/2` | ≥ 30.7 or ≤ 19.35 | 53.17 (bottom holes), 33.94 (top holes) |
| 356 | each hole: `dist(hole, clock pocket rect) >= standoff_d/2 + 0.5` | ≥ 3.5 | 20.85 |
| 359 | each hole: `dist(hole, USB rect) >= max(standoff_d, screw_head_d)/2 + 0.3` | ≥ 3.3 | 17.7 |
| 364 | each hole on board: `pcb_hole_d/2 + 0.5` from every edge | ≥ 1.6 | 3.5 |
| 367 | each hole: `dist(hole, radome square) >= screw_head_d/2 + 0.3` | ≥ 2.2 | 23.6 |
| 370 | each hole: `dist(hole, jack body rect) >= max(standoff_d, screw_head_d)/2 + 0.3` | ≥ 3.3 | 6.11 (hole 51.5,74.95) |
| 373 | patch footprint (25.4 sq) ≥ 1 from every board edge | ≥ 1.0 | 14.8 / 26.5 |
| 376 | `z_pcb_bot - z_floor >= patch_pin - pcb_t + 0.3` | ≥ 1.50 | **1.56 (0.06 spare)** |
| 379 | TX jack off the corner radius: `tx_along ± (max(tx_jw, sma_hole/2) + 0.5)` inside the straight wall | tx_pos 6.925 .. 71.525 | 66 (5.5 spare to the top corner) |
| 382 | `tx_gap >= 0 && tx_notch > 0` (board edge within jack thickness of the wall) | notch > 0 | 1.5 |
| 384 | `sma_z - sma_body[2]/2 >= z_floor + 0.2` (jack body vs floor) | ≥ 4.36 | 4.77 |
| 386 | `sma_z - sma_hole/2 >= skin_t + 0.6` | ≥ 1.28 | 4.595 |
| 387 | `sma_barrel - wall_t >= 4.0` (jack part choice) | ≥ 4.0 | 5.2 |
| 389 | TX on the bottom edge must be ≥ max(tx_jw, sma_hole/2) + usb_open_w/2 + 1 from USB | ≥ 10.725 | n/a (right edge) |
| 391 | patch footprint and jack body rects at least 1 apart | ≥ 1 | 13.5 |
| 332 | snap bead vs TX slot on the same wall: `abs(bead - tx_along) >= snap_len/2 + max(tx_jw, sma_hole/2) + 1` | ≥ 10.425 | 17.05 (bead at board y 48.95) |
| 334 | snap bead vs USB opening, bottom wall | ≥ 13.3 | n/a (no bottom beads) |
| 339 | pry notch vs USB: `abs(pry_x - usb_x) >= usb_open_w/2 + pry_w/2 + 1` (also pry on the straight wall, and vs TX if bottom) | ≥ 11.3, so board usb centre x ≤ 32.2 with pry_x = 16 | 16 |

Asserts that do not involve the PCB: 315 (skin 0.5-0.8), 319 (magnet headroom), 321 (cap layers), 326-328 (snap interference, groove vs wall top, groove vs wall thickness), 330 (bead vs corner), 346 (clock pocket vs bottom wall) and 378 (patch_cover range).

Combined USB constraint at the defaults: board usb centre x must be in 9.3 .. 32.2. It is 27.5 now.

## Raw ECHO output (defaults)

```
=== BEACON MagSafe enclosure, 2.55 mm ring ===
Skin over magnets: 0.68 mm (5 layers); pocket depth 2.88 mm, 0.33 mm headroom; cap 5 layers to 4.16 mm
PAUSE: after layer 29 (top at Z = 3.56 mm), i.e. before the layer that ends at Z = 3.68 mm. Insert magnets, then resume.
Outside: 59.2 x 82.65 x 14.32 mm; ring centre 29.6 mm below the top edge
PCB: 55 x 78.45 x 1.6 mm, corner r 3, underside 5.72 mm above the phone
Ring centre in board coords: [27.5, 50.95]
Mounting holes in board coords: [[3.5, 3.5], [51.5, 3.5], [3.5, 74.95], [51.5, 74.95]]; keep 6 mm pads clear on both sides
Part height: under board 1.56 mm, over board 5.4 mm (2.4 mm within 1.1 mm of the board edge, under the lid lip)
PCB screws: 4x M2 x 4 pan/cheese head, top-down through the board, 2.4 mm of thread in M2 x 3 heat-set inserts
Lid: snap fit, 5 beads x 12 mm, 0.25 mm interference, bead centre 2.15 mm below the seam
USB-C: centreline 8.95 mm above the phone face, opening 12.6 x 6.7 mm
RX patch: centre [27.5, 39.23] in board coords, [0, -11.73] from the ring centre; 1.4 mm air under a 1.2 mm radome
TX jack: right board edge at 66 mm; board notch 1.5 x 7.1 mm; axis 8.02 mm above the phone face, 5.2 mm of thread outside the wall
```
