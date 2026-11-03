# beacon_phone_magsafe_2p5mm_rev_pcb.scad: changes from the original

Source: `C:\Users\marsi\Downloads\beacon_phone_magsafe_2p5mm_Latest.scad` (not modified, md5 b3ffe7b6887f3f23b007b2d4a06878be).
Purpose: match the enclosure to the final PCB parts in `BEACON_PhoneModule.kicad_pcb`. Each change was checked against
`docs/antenna_connectors.md`, `docs/enclosure_constraints.md` and `docs/magnetics_thermal.md`.
Checked with OpenSCAD 2021.01, headless, on 2026-11-02.

## Parameter changes

| Parameter | Original | rev_pcb | Reason / doc |
|---|---|---|---|
| `usb_z_on_pcb` | 1.63 | **1.73** | GCT USB4105-GF-A centreline (antenna_connectors 3.1) |
| `usb_body` | [8.94, 7.3, 3.26] | **[8.94, 7.35, 3.31]** | GCT drawing rev B4 (3.1). Used for the preview and the hole-vs-USB assert |
| `top_parts_h` | 3.3 | **3.35** | USB4105 is 3.31 tall. `top_clear` is still 5.4, set by the patch |
| `sma_axis_z` | 0.7 | **0.4** | Cinch 142-0711-821. Derived from the drawing, range 0.38-0.55, not dimensioned (2.2) |
| `sma_body` | [6.5, 1.6, 6.5] | **[6.35, 1.65, 6.35]** | 0.250 in square x 0.065 in flange (2.2) |
| `sma_barrel` | 7.0 | **7.87** | 0.375 in from the flange back face (2.2) |
| `sma_clr` | 0.5 | **0.25** | Optional change suggested in 2.5. See the TX slot section below |
| `tx_notch_d` (new) | (derived 1.5) | **1.5** | Holds the board notch at the KiCad Edge.Cuts depth. 0 = original auto formula |
| `tx_notch_w` (new) | (derived 7.1) | **7.1** | Holds the notch at the KiCad Edge.Cuts width. 0 = auto |
| `vent_slots` and `vent_c`, `vent_n`, `vent_len`, `vent_w`, `vent_pitch`, `vent_keep` (new) | n/a | **off**; [22, 65], 4, 20, 1.2, 3.0, 10 | Optional lid vents (magnetics_thermal 4) |

These are unchanged: `usb_x` 0, `tx_pos` 66, `tx_side` right, `patch_pos` [] (board centre), `pcb_w`/`pcb_l` auto (55 x 78.45), `pcb_holes` [] (auto corners), `pcb_r`, `hole_inset`, and all shell, magnet and layer parameters.

### Why the notch is pinned

In the original, the notch size comes from `sma_body`: depth `sma_body[1] + 0.2 - tx_gap`, width `sma_body[0] + 0.6`. With the Cinch flange values that gives **1.55 x 6.95**. That no longer matches the routed board, whose Edge.Cuts notch is 1.5 x 7.1 (board x 53.5-55.0, y 62.45-69.55). So the two new parameters keep the notch at the KiCad geometry. The Cinch flange still fits:

* 0.15 mm gap behind the flange (1.5 + 0.3 - 1.65). antenna_connectors 2.5 says 1.5 "still works with a 0.15 mm gap".
* 0.375 mm each side across the width ((7.1 - 6.35) / 2).

A new assert checks this fit: notch + gap >= flange + 0.1, and half-width >= flange/2 + 0.2.

The J3 footprint's Dwgs.User notch sketch is drawn 1.55 x 7.0 and does not match the Edge.Cuts (1.5 x 7.1). This is cosmetic, because only Edge.Cuts is routed. It was not changed, since the KiCad files are out of scope here.

### TX slot and tongue with `sma_clr` 0.25

* The slot is 6.6 wide on a 6.35 barrel, so it clears by 0.125 mm per side, and the board drops in from above with the barrel in the slot.
* The lower arc of the wall hole and the arc of the lid tongue are concentric with the barrel. Both have 0.125 mm radial clearance.
* Flange bearing area rises from 5.2 to 6.6 mm² (+27 %): 3.36 mm² on the wall, 3.24 mm² on the tongue. This was computed numerically.
* There is a new assert: radial clearance >= 0.1.
* **Risk.** The barrel axis height (0.38-0.55) is not dimensioned by Cinch. If the real axis sits more than about 0.12 above 0.4, the tongue touches the neck. Measure the first jack. If it sits at about 0.5 or higher, set `sma_axis_z` to the measured value, or set `sma_clr` back to 0.4-0.5.
* The thread itself starts about 1 mm outside the wall (2.2), so only the smooth neck sits in the slot.

### Thermal and lid (magnetics_thermal 4)

* The header now says to print the **lid in light-coloured PETG** (white or natural). In full sun at 35 °C a dark lid reaches about 78 °C, which is above PETG's HDT of about 70 °C. A white lid reaches about 50 °C.
* The console also reminds you of this.
* **Optional vents** (`vent_slots = true`): 4 slots of 20 x 1.2 mm through the lid plate, centred at board (22, 65). That is over U8, the LMX2582, at board (22.6, 67.25), which is the largest heat source at 0.84 W.
* Asserts keep the vents:
  * 1 mm inside the lid lip;
  * at least 3 mm from the RX radome square;
  * at least `vent_keep` (10 mm) from the TX jack body.
* Deliberately moving them into the patch, the TX jack or the lip fires each of these asserts.
* The vents print without supports, since the lid prints outer face down.

## Verification

* **Asserts.** None fired, for `print_plate`, `assembly`, `pcb_outline` or `vent_slots = true`.
  * Every ECHO file and log was searched for `ERROR`/`WARNING`.
  * OpenSCAD 2021.01 exits 0 even when an assert fails, so the exit code alone proves nothing.
* **Geometry.** Both STLs are simple (2-manifold) after CGAL.
* **Derived values.** These are identical to the original (wrapper `include` plus echo of every derived variable):
  * outside 59.2 x 82.65 x 14.32;
  * cavity and outer radii;
  * board 55 x 78.45 at `pcb_x0` -27.5 and `pcb_y0` -50.95;
  * holes;
  * Z stack (floor 4.16, board 5.72/7.32, seam 12.72, top 14.32);
  * pause after layer 29 at Z 3.56;
  * screw M2 x 4 with 2.4 engaged;
  * snap geometry;
  * patch centre;
  * `tx_along`, `tx_notch` and `tx_nw`.
* **What changed:**

  | Value | Original | rev_pcb |
  |---|---|---|
  | `usb_zc` | 8.95 | 9.05 |
  | `usb_z0` | 5.60 | 5.70 (limit 4.66) |
  | `sma_z` | 8.02 | 7.72 |
  | `sma_hole` | 6.85 | 6.60 |
  | jack body rect | | follows the 6.35 x 1.65 flange |

* **New margins:**
  * jack body to floor: 0.385 (was 0.61). The assert needs 0.2, so 0.185 is spare;
  * barrel outside the wall: 6.07 (was 5.2);
  * patch, USB and TX hole keep-outs: unchanged or larger.
* **DXF compared with the KiCad Edge.Cuts:**
  * Method: the DXF was converted to KiCad coordinates with `kicad_x = 100 + x` and `kicad_y = 178.45 - y`.
  * Outline: maximum deviation is 0.004 mm in both directions, which is the arc facet chord error.
  * Holes: the 4 holes match H1-H4 exactly in position and diameter (2.2).
  * Byte-for-byte, the DXF is identical to the original's `pcb_outline`.
  * There is no mismatch above 0.05 mm.
* **Footprint positions.** These agree with the scad:
  * AE1 patch at board (27.5, 39.225);
  * J1 USB4105 at (27.5, 3.675), so the front face is flush;
  * J3 Cinch at the notch bottom (53.5, 66).

## Files

| File | What |
|---|---|
| `beacon_phone_magsafe_2p5mm_rev_pcb.scad` | updated copy |
| `rev_pcb_print_plate.stl` / `.echo` | print plate (base + lid) and its console |
| `rev_pcb_assembly.stl` / `.echo` | exploded assembly (lid lifted 18) |
| `rev_pcb_pcb_outline.dxf` / `.echo` | board outline for KiCad |
| `rev_pcb_echo_diff.txt` | ECHO diff, derived-variable diff, DXF vs Edge.Cuts report |
| `rev_pcb_assembly.png` | `--render`, exploded assembly |
| `rev_pcb_assembly_preview.png` | coloured preview, close-up |
| `rev_pcb_section.png` / `rev_pcb_section_preview.png` | x >= 0 half section, `--render` and coloured preview |
| `rev_pcb_tx_jack_section.png` | ortho cut through the jack axis (y = 15.05), lid seated: flange, slot, tongue, notch |
| `rev_pcb_lid_vents_on.png` | lid with `vent_slots = true` (top view) |
