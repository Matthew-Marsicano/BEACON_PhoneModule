# beacon_phone_magsafe_lowprofile.scad: low-profile enclosure

**Source:** `beacon_phone_magsafe_2p5mm_rev_pcb.scad`. It was not modified (md5 634b63af67f6ab321d70f311d5b1cf30), and neither were the Downloads original or any KiCad file.

**Result:** the default total height drops from **14.32 to 11.41 mm**, which is 2.91 mm or 20 % less. Outside it is still 59.2 x 82.65.

**Unchanged:** the board, its holes, TX notch, USB-C, patch position, ring, clocking magnet, skin (0.68) and the pause layer (29, Z 3.56). The `pcb_outline` DXF is byte-identical to the rev_pcb one.

Checked with OpenSCAD 2021.01 on 2026-11-02.

## Z stack

| Level (Z above the phone face) | rev_pcb | lowprofile | Set by |
|---|---|---|---|
| skin / magnet top / pause / floor top | 0.68 / 3.23 / 3.56 / 4.16 | same | fixed |
| board bottom | 5.72 | **4.76** | `pcb_gap` 0.6. This is the minimum the USB-C overmold opening allows (existing assert `usb_z0 >= z_floor + 0.5` needs ≥ 4.68, snapped to a layer) |
| board top | 7.32 | **6.36** | |
| lid underside / base wall top | 12.72 | **10.21** | `top_clear` 3.85 = USB4105 3.31 + 0.5 |
| lid top | 14.32 | **11.41** | `lid_t` 1.2 |

## What was evaluated

Savings are applied in order, starting from 14.32.

| # | Item | Choice | Z saved | Trade-off |
|---|---|---|---|---|
| 3 | `pcb_gap` with local floor pockets | Gap 1.5 → 0.6. Pockets under the patch pin, the SMA flange and far lower leg, and the USB-C stakes | **0.96** (0.24 without the leg cut) | One SMA leg must be cut before soldering (see below) |
| 1 | Patch: window, radome or smaller gap | **Open window**, 28.4 sq (1.5 mm round the patch) | 0.32 on its own, because the USB opening then sets the lid | Patch electrode exposed (ESD, scratches). Best RF match to Taoglas's air-above characterisation |
| 2 | Stepped lid: low plate plus raised bosses | **Not used.** A raised boss on the outer face cannot print face-down without supports. Instead the lid stays flat and the tall items get openings or recesses: | | |
| | ... USB-C overmold opening | `usb_open_top`: the U runs up through a notch in the lid | 1.005 (5.08 → 4.075) | 12.6 x 2.3 notch in the back's bottom edge; the overmold sits flush (0.07 below the face) |
| | ... SMA flange (+3.575) | 0.225 recess in the lid underside | 0.225 (4.075 → 3.85) | 0.975 mm of lid is left over a 7.4 x 2.2 strip |
| 5 | `lid_t` / `lip_h` | lid 1.6 → **1.2**; lip 3.0 → **2.6** | **0.40** | Lip 2.6 keeps 1.25 mm under the lip for ≤ 1.1 parts. Snap groove assert needs ≥ 2.2 |
| 4 | Heat-set insert stack | **Unchanged** (M2 x 3, M2 x 4 screw, 2.4 mm engaged) | 0 | Not limiting: the stack needs board bottom ≥ 4.40 and the board sits at 4.76. The holes already sit beside the ring (r 33.9 / 53.2). M2 x 2 or self-tapping would only help below 4.4, which the USB assert forbids |
| | **Total** | | **2.91** | |

### 1. Patch options

All heights are above the board top. Patch stack: 4.1 max + 0.3 tape nominal (0.5 max).

| Option | Lid top | Total | Notes |
|---|---|---|---|
| **Open window** (default) | 5.05 | **11.41** | Patch top 0.65 (worst 0.45) below the lid face |
| Flat lid with thin radome: `patch_window=false`, `patch_gap` 0.7, `patch_cover` 0.8 | 5.90 | 12.26 | 0.7 air nominal, 0.5 worst (assert `patch_air_min`). Detunes more than rev_pcb's 1.4 air under 1.2 PETG, so tune on the bench |
| rev_pcb radome (1.0 + 0.4 recess, 1.2 cover, lid 1.6) | 7.00 | 14.32 | reproduced exactly as a regression check |

### 3. The bottom side is not just flat pads

The KiCad file and `docs/antenna_connectors.md` show four things that hang below the board:

* **Patch feed pin** at board (29.3, 37.425): up to 1.2 below the board.
  * It is inside the ring island, so there is solid plastic below it.
  * It gets a pocket of d 4.0 down to Z 3.2, which gives 1.56 of room.
  * **No trimming needed.**
* **Cinch SMA flange**: 1.175 below the board.
  * It gets a pocket to Z 3.32, which gives 0.265 of room.
  * It is outside the ring, with 1.19 of plastic to the ring pocket.
* **Cinch lower legs**: 0.81 wide x **1.07 thick**, running 3.81 behind the flange.
  * Leg 2 (board y 68.4-69.2) is outside the ring. Its pocket leaves 0.82 of wall.
  * **Leg 1 (board y 62.8-63.6, on the bottom GND pad at y 62.5) lies over the ring magnet** for about 2 mm of its length (r 25.3, while the pocket runs to 27.2). It cannot be pocketed without breaking the 0.6 cap. The options:
    * **Default `sma_leg_cut = true`:** cut it to a 0.5 mm stub **before soldering J3**. The stub's pocket leaves 0.73 of wall to the ring.
    * **`sma_leg_cut = false` + `pcb_gap = 1.3`:** board bottom 5.48, total **12.13**. The leg then rides 0.25 over the cap.
* **USB4105 shell stakes**: 4 THT slots at board (23.18/31.82, 2.60/6.78).
  * Their length is not in docs/. `usb_stake_below` assumes 1.0.
  * Pockets go down to the pause height (Z 3.56, so 1.2 of room). They sit 0.52 beside the clocking-bar pocket.
  * Measure the stakes on the first board, and clip them if they are longer.

## Configurations

All rows were run, and all are assert-clean except where an assert is noted.

| Settings | Total |
|---|---|
| defaults (window, USB open top, leg cut) | **11.41** |
| `sma_leg_cut=false pcb_gap=1.3` | 12.13 |
| `patch_window=false` (radome) | 12.26 |
| radome + no leg cut (`patch_window=false sma_leg_cut=false pcb_gap=1.3`) | 12.98 |
| `usb_open_top=false` (lid bridges the overmold opening) | 12.64 |
| `vent_slots=true` | 11.41 |
| rev_pcb settings (`pcb_gap 1.5, lid_t 1.6, lip_h 3.0, usb_open_top=false, patch_window=false, patch_gap 1.4, patch_cover 1.2`, pockets off) | 14.32 (same Z stack and ECHO as rev_pcb) |

**Further cuts I did not take:**

* `lid_t` 1.0 would save 0.2. The windowed lid becomes a floppy frame, and the overmold would stand 0.13 proud.
* `top_clear` about 3.4, with local recesses over the USB and L1, would save about 0.45. The patch would end up flush with the lid face, and the lip would be at its 2.2 minimum.
* `mag_clr_z` 0.1 would save 0.12. It leaves only 0.21 of headroom at the pause.

## Parameter changes (rev_pcb → lowprofile)

| Parameter | rev_pcb | lowprofile |
|---|---|---|
| `pcb_gap` | 1.5 | **0.6** |
| `lid_t` | 1.6 | **1.2** |
| `lip_h` | 3.0 | **2.6** |
| `patch_window` | false | **true** |
| `patch_gap` | 1.0 (lid underside) | **0.7**. It now means the air under the radome, and is used only when `patch_window=false` |
| `patch_cover` | 1.2 | **0.8** (radome only) |

**How `top_clear` is now computed.** It is the max of four terms, and each applies only where it is still relevant:

* parts + 0.5;
* the USB opening, unless `usb_open_top` is set;
* the patch, which depends on the window or radome mode;
* the SMA minus the allowed recess.

**The window cut.** It was `patch_fp + 1` (26.4). It is now `radome_w` (28.4), with r 1 corners, because the patch now stands up into it.

**New parameters:**

* `edge_parts_h` 1.1
* `usb_open_top`
* `lid_local_min` 0.8
* `sma_lid_clr` 0.5
* `patch_tape_max` 0.5
* `patch_recess_min` 0.3
* `patch_air_min` 0.5
* floor pockets:
  * `pocket_wall` 0.6
  * `pin_pocket`, `patch_pin_off` [1.8, -1.8], `pin_pocket_d` 4
  * `sma_pocket`, `sma_leg_below` 1.07, `sma_leg_l` 3.81, `sma_leg_y`, `sma_leg_cut`, `sma_leg_stub` 0.5, `sma_pocket_clr` 0.25
  * `usb_stake_pocket`, `usb_stakes`, `usb_stake_below` 1.0, `usb_stake_pkt`
* sections: `sec_off`

**New parts:** `section_patch` (cut through the feed pin) and `section_sma` (cut on the jack axis + `sec_off`).

The preview ghosts now also show the feed pin, the SMA legs (cut length) and the USB stakes.

## Asserts

**All rev_pcb asserts are kept.** Two of them now check the local pocket floor instead of the global floor. The expressions are the same, and they are identical when the pockets are off:

* feed pin: `z_pcb_bot - z_pin_floor >= patch_pin - pcb_t + 0.3`
* jack body: `sma_z - sma_body[2]/2 >= z_sma_floor + 0.2`

**New asserts:**

* lid structure:
  * `lid_t` ≥ 1.0;
  * `pcb_gap` ≥ 0.3;
  * lip-band clearance ≥ `edge_parts_h` + 0.1;
  * screw heads clear of the lip band;
  * SMA recess leaves ≥ `lid_local_min`;
* patch:
  * `patch_tape` ≤ max;
  * window: margin ≥ 1.0 and patch top ≥ 0.3 below the face;
  * radome: worst-case air ≥ 0.5;
* USB:
  * the opening fits the wall unless `usb_open_top`;
* pin pocket:
  * clear of the ring, the clocking pocket and the label;
* pocket floors:
  * all ≥ `floor_web`;
* SMA:
  * flange pocket off the ring;
  * each leg pocket off the ring, so the stub length is checked;
  * each leg clears its floor;
  * an uncut leg over the ring clears the cap;
* USB stakes:
  * they clear their floor;
  * they are ≥ 0.5 from the clocking pocket and its corner reliefs;
  * they are off the ring.

**Each new assert was forced to fail once**, with a readable message:

| Override | Message |
|---|---|
| `sma_leg_cut=false` | "...lies over the ring and hits the cap: set sma_leg_cut = true (cut it) or pcb_gap = 1.3" |
| `pin_pocket=false` | feed-pin assert |
| `sma_pocket=false` | jack-body assert |
| `usb_stake_pocket=false` | stakes |
| `lip_h=3.0` | "Only 0.85 mm under the lid lip" |
| `lid_t=0.9` | lid thickness |
| `pcb_gap=0.3` | the existing "USB-C opening runs into the floor" |
| `patch_window=false patch_gap=0.5` | radome air |
| `sma_leg_stub=1.5` | stub pocket hits the ring |

## Assembly changes

* **4a (new, default build):** before soldering J3, cut the lower leg on the USB-C side to a 0.5 mm stub behind the flange, then file it flat.
  * That is the leg on the B.Cu GND pad at board (51.15, 62.51).
  * The console prints `ASSEMBLY: CUT SMA lower leg at board x 49.84-53.65, y 62.83-63.64`.
* **4b:** the patch pin needs no trimming. Measure the USB-C shell stakes, and clip them if they are more than 1.0 below the board.
* **Patch window:** optionally put a 50-100 µm polyimide or PET label on the patch top. This guards against ESD and scratches.
* The other steps (pause, magnets, inserts, screws M2 x 4, snap lid) are unchanged.

## Risks

1. **SMA leg cut.**
   * **If it is forgotten, the board cannot seat**: the leg hits the ring cap by 0.47 mm.
   * Cutting removes one of four ground and solder legs. The 2.4 GHz impact is expected to be small, because the bottom pad stays stitched to the top pad. The enclosure clamps the flange (wall and tongue), so the solder joints are not the torque path.
   * If the board is already assembled, cutting after soldering leaves the leg remnant soldered on the pad. It must be desoldered, so it is better to use `sma_leg_cut=false` (12.13).
2. **Open patch window.**
   * The top electrode is touchable and DC-connected to the RX feed (ESD).
   * The ceramic is exposed to scratches and dirt.
   * The lid edges are 1.5 mm from the patch sides, level with its top 0.55-0.75 mm.
   * Re-check the match with a VNA. The radome option costs 0.85 mm.
3. **USB stake length** is assumed (≤ 1.0 below the board). It is not dimensioned in docs/.
4. **0.6 mm floor gap** under a bridged cap. Cap pillowing or board bow above about 0.4 would touch. The standoffs remain the datum. Keep the bottom side free of anything taller than flat pads (the asserts only know the parts listed).
5. **Lip band 1.25 mm.** Any future part over 1.1 tall within 1.1 mm of the board edge collides. Today only L3 (0402) is in the band. SW1 (B3U) ends 0.22 mm inboard of it.
6. **USB notch in the lid.** It leaves a 12.6 x 2.3 open slot at the back's bottom edge, and the receptacle front is visible through it.
7. **Magnets 0.96 mm closer to the board.** The magnet tops are now 1.53 below the board bottom (was 2.49), which matters for any magnetically sensitive part (`docs/magnetics_thermal.md`).
8. **Local lid recess over the SMA** leaves 0.975 mm. It is not a span. The tongue root is at full 1.2.

## Verification

* **ECHO / asserts.** `print_plate`, `assembly` and `pcb_outline` were exported with `-o .echo`. The files were grepped for ERROR/WARNING/Assertion and none fired.
  * Note: OpenSCAD 2021.01 writes assert failures into the `.echo` file, not the console, and still exits 0.
* **DXF.** `lowprofile_pcb_outline.dxf` md5 18390473f7549610058dd7b00660f624. This is identical to a fresh export of the rev_pcb file and to the stored `rev_pcb_pcb_outline.dxf` (`cmp`).
* **Previews.** These are OpenCSG preview PNGs, not `--render`. Preview draws all cut faces in one scheme colour.
* **STL exports.** `--render` exports were run in the background at the end. Both finished with no ERROR or WARNING, and CGAL reports both as Simple: yes (2-manifold).
  * `print_plate`: 1 min 36 s.
  * `assembly`: 3 min 25 s.

## Files

| File | What |
|---|---|
| `beacon_phone_magsafe_lowprofile.scad` | new model, recommended defaults |
| `LOWPROFILE.md` | this note |
| `lowprofile_print_plate.echo` / `lowprofile_assembly.echo` / `lowprofile_pcb_outline.echo` | console (ECHO, asserts) |
| `lowprofile_pcb_outline.dxf` | board outline (identical to rev_pcb) |
| `lowprofile_assembly.png` | exploded assembly preview |
| `lowprofile_section_patch.png` | section at x = feed pin: window, patch, pin pocket |
| `lowprofile_section_sma.png` | section on the jack axis: flange pocket, tongue, lid recess |
| `lowprofile_section_sma_leg.png` | section through the cut lower leg (stub, ring cap) |
| `lowprofile_lid_print.png` | lid in print orientation (flat face down) |
| `lowprofile_print_plate.stl` / `lowprofile_assembly.stl` | CGAL exports (background) |
