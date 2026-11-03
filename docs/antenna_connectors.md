# BEACON_PhoneModule: antennas and edge connectors for the MagSafe enclosure

Date: 2026-11-02. Enclosure: `beacon_phone_magsafe_2p5mm_Latest.scad`, 2.5 mm ring variant. Board: 55.0 x 78.45 x 1.6 mm, 4 layers.

Board coordinates in this note follow the scad: the origin is the lower-left corner seen from the top side, +y points away from the USB-C edge, and units are mm. KiCad's Y axis points down, so a footprint's local "+Y" faces the USB-C edge when the footprint is placed at 0 degrees.

Proposed footprints (KiCad 10, s-expression version 20241229), in `docs/proposed_footprints/`:

| File | Part |
|---|---|
| `Taoglas_WDP.2458.25.4_Patch.kicad_mod` | RX patch, Taoglas WDP.2458.25.4.B.02 |
| `SMA_Cinch_142-0711-821_EdgeLaunch.kicad_mod` | TX jack, Cinch (Johnson) 142-0711-821 |

No 3D models are attached. Taoglas and Cinch both offer STEP files on request or through distributors.

**How the footprints were checked.** Both footprints were loaded with the pcbnew Python API (KiCad 10.0.7). They were placed on a 4-layer 55 x 78.45 test board that had the TX notch and GND pours on every layer, the pours were filled, and the board was run through `kicad-cli pcb drc`. The only violations were the five expected `copper_edge_clearance` hits on the SMA pads, which are set back 0.25 mm from the notch edge (see 2.4). Every pad-to-pad and pad-to-pour clearance passed.

---

## Sources and access

| Source | Result |
|---|---|
| taoglas.com/datasheets/WDP.2458.25.4.B.02.pdf | Downloaded. SPE-14-8-039-F, rev F, 2024-05-14. |
| taoglas.com/datasheets/GW.26.0111.pdf | Downloaded. SPE-11-8-035-M. |
| taoglas.com product pages | HTTP 403. Not needed: the PDFs above loaded directly. |
| gct.co/files/drawings/usb4105.pdf | Downloaded. Rev B4, 18/12/23. |
| cinch.com 142-0711-821 and 142-0701-801 product-information PDFs | Plain curl got HTTP 403. The same URLs fetched normally through the web-fetch tool (no spoofing) and were rendered locally. |
| amphenolrf.com (product pages and asset links found via DigiKey) | HTTP 403 every time. **No Amphenol drawing could be read.** |
| molex.com (drawings and product pages) | Connection reset or time-out. **No Molex drawing could be read.** |
| suddendocs.samtec.com (the URL in KiCad's footprint descr) | AccessDenied. |
| DigiKey | Product pages were readable through the web-fetch tool and were used only to find manufacturer datasheet links. Mouser and Farnell timed out or were refused. |

Because of this, the Amphenol, Molex and Samtec candidates below could only be judged from KiCad's own footprint fab outlines and from distributor text. None of them is recommended without its drawing.

---

## 1. RX antenna: Taoglas WDP.2458.25.4.B.02

### 1.1 Datasheet facts (SPE-14-8-039-F)

| Item | Value | Where |
|---|---|---|
| Type | Dual-band 2.4/5 GHz embedded ceramic patch, pin-fed, mounted with double-sided adhesive (Nitto 5015) | p.1, p.3, p.9 |
| Body | 25.1 +/-0.3 square x 4.0 +/-0.1 mm. One key corner is R2.81; the other three are R1.51. | p.9 |
| **Feed pin position** | **1.8 +/-0.2 mm right of centre and 1.8 +/-0.2 mm below centre** in the top view (key corner R2.81 at top-left, printing upright). That puts the pin 2.55 mm from the centre along the diagonal, toward the corner opposite the key. | p.9, both 1.8 dimensions |
| Pin diameter | 0.9 +/-0.2 mm | p.9 |
| Pin length | 2.4 +/-0.4 mm below the patch underside | p.9 (rev D change note: "patch pin length to 2.4mm") |
| Adhesive | 0.5 mm max | p.9 |
| Electrode or adhesive clearance around the pin, underside | The adhesive ring leaves a disc of about 10.6 mm free at the centre. The pin's own clearance ring is about 2.5 mm in diameter. Both are scaled from the drawing, not dimensioned. | p.9 bottom view |
| Recommended PCB hole and pad | **Not given.** The PCB layout page (p.13) shows only a plated feed hole with a small antipad in solid top copper, and a trace on the bottom. | p.13 |
| Ground plane | "Tuned for 70x70mm ground plane". The patch goes at the centre, with "a square symmetric ground plane shape and symmetric environment". | p.1, p.4, p.12 |
| Copper under the patch | Solid GND copper on the top side, with only the feed antipad cut out. The evaluation board is shown both with and without solder mask (p.12), so mask over the GND under the patch is acceptable. | p.12-p.14 |
| Feed on the evaluation board | Plated feed hole, then a stitched grounded-coplanar line on the **bottom** layer, then an edge SMA. **No matching network is shown or recommended.** | p.13, p.14 |
| Electrical, 2.4 GHz | 2400-2500 MHz. Return loss -19 dB minimum, but only **-2 dB at the band edges**. Efficiency 80 % maximum, 25 %+ at the edges. Peak gain 6 dBi. Linear polarization, 50 ohm. | p.4 |
| Return-loss plot | The 2.4 GHz dip is very narrow. It is centred at about 2.44-2.45 GHz and the -10 dB bandwidth is only about 20-25 MHz (read off the plot). | p.5 |
| Polarization | "Two distinct linear polarizations, on the 2.4 and 5GHz bands". **The datasheet does not say which patch axis carries the 2.4 GHz E-field.** The pattern plots are total gain only. | p.3, p.8 |

The first page prints the part number as "WPD.2458.25.4.B.02". That is a typo; every other page and the drawing say WDP.

### 1.2 Fit to this board and enclosure

- **Ground plane is smaller than the one the patch was tuned on.** The board is 55 x 78.45 mm, against the 70 x 70 mm tuning plane. Width drops from 0.57 to 0.45 wavelength, and the board is not square.
  - The datasheet gives no data for other ground planes, and this is a high-Q patch: -10 dB bandwidth is about 1 %.
  - Expect the resonance and the match to move by an amount of the same order as that bandwidth. The smaller plane tends to raise the frequency. The PETG radome (1.2 mm, with a 1.0 mm air gap per the scad) tends to lower it.
  - Gain and front-to-back ratio will drop somewhat.
  - **Measure S11 on the first board inside the closed enclosure before committing.** Taoglas also offers versions custom-tuned to your ground plane (p.3; minimum order quantity applies).
- **Bandwidth.** Even on the reference plane, the antenna does not cover the full 2400-2483.5 MHz ISM band (-2 dB return loss at the edges). If the BEACON RX channel plan uses more than about 2430-2455 MHz, this is the wrong antenna.
- **Placement.** The patch at the board centre (board 27.5, 39.225), with the default `patch_pos = []`, follows the datasheet's centred-placement rule and clears the TX jack (y = 66) and the USB-C edge.
  - The MagSafe ring sits under the board, centred at board (27.5, 50.95), with its steel backing toward the board. L1 and L2 GND separate it from the patch, so it mainly affects the back lobe.
- **Polarization versus TX.** The GW.26.0111 points out of the right edge along +X when straight, so its E-field is along X.
  - For best RX/TX isolation, orient the patch so its 2.4 GHz E-plane is along Y.
  - The datasheet leaves the axis open. Ask Taoglas, or measure TX-to-RX S21 on a prototype at 0 and 90 degrees of patch rotation; the footprint is symmetric enough to rotate.
  - The footprint below is drawn in the datasheet's orientation. At 0 degrees on the board, the feed sits at **board (29.3, 37.425)**: 1.8 mm toward +x and 1.8 mm toward the USB-C edge from the patch centre.
- **Pin and floor.**
  - The pin protrudes below the board by 2.4 - (0.3 to 0.5 tape) - 1.6 = 0.3-0.5 mm nominal, and up to 0.9 mm worst case.
  - The scad's `patch_pin = 2.8` check passes: 1.56 mm under the board, against 2.8 - 1.6 + 0.3 = 1.5 required.
  - Solder the pin by hand on the bottom after the patch is taped down. The datasheet gives no reflow rating for the assembled antenna.
- The scad's other patch values match the datasheet: `patch_sz 25.1`, `patch_tol 0.3`, `patch_h 4.1`, `patch_tape` at or below 0.5.

### 1.3 Feed, transition and matching network (recommendation; the datasheet has none)

- **Feed route.** The pin passes through the board and is soldered on L4 (B.Cu). From the feed pad, run the RX line on **L4 as a 0.30/0.20 mm CPWG over L3**. L3-L4 uses the same 0.2104 mm 7628 prepreg as L1-L2, so `docs/stackup_and_rules.md` section 2 applies unchanged.
  - **L3 must be a solid GND pour under the whole L4 RF run.** L3 is normally power/GND.
  - Alternatively, via back up to L1 immediately outside the patch outline.
- **Through-board transition.**
  - A 1.3 mm plated barrel in a 3.0 mm void on L1/L4 and a 4.0 mm void on L2/L3 behaves as a short coax of roughly 22-32 ohm.
  - It is only 1.6 mm long, about 0.02 wavelength in the board, so it adds roughly 0.4 nH and a few tenths of a pF.
  - Put 4-6 GND stitching vias on a circle of about 2.6 mm radius around the feed, leaving the L4 trace exit open.
- **Pi network.** Place three 0402 footprints (shunt, series, shunt) on L4 within 2-3 mm of the feed pad, on the CPWG.
  - Default fit: series 0 ohm, both shunts DNP.
  - Tune with a VNA on the assembled unit, with the lid on and the phone attached.
  - The pi network can recentre the match within roughly the patch's own bandwidth. It cannot move the radiating resonance far without losing efficiency.
- **Expected impedance at 2.45 GHz on this board.** Nominally 50 ohm, with -19 dB minimum return loss, on the 70 x 70 plane only. On 55 x 78.45 with the radome, the value is not predictable from the datasheet.
  - Plan for the resonance to sit 0-30 MHz away from 2.45 GHz and for the return loss to be anywhere from -6 dB to -20 dB until it is measured.
  - That is why the pi pads are recommended even though Taoglas shows none.

### 1.4 Footprint: `Taoglas_WDP.2458.25.4_Patch`

The origin is the patch centre. The footprint is drawn in the datasheet top-view orientation: R2.81 key corner at top-left, KiCad +Y toward the USB edge at 0 degrees.

| Element | Definition |
|---|---|
| Pad 1, RF feed | PTH, at (+1.8, +1.8). **Drill 1.30 mm** (pin 0.9 +/-0.2, so 1.1 maximum, plus solder clearance). **Pad 2.0 mm round on all copper layers**, local clearance 0.5 mm, giving a 3.0 mm GND void. |
| Pad 2, GND | Four overlapping F.Cu-only SMD rectangles that tile a **25.4 x 25.4 mm** square (25.1 + 0.3 tolerance). The square has a 3.0 x 3.0 mm cut-out at the feed, which the pour then fills back to a 3.0 mm round void. No mask opening and no paste, so mask stays over the GND under the adhesive, as on the evaluation board. Zone connection: solid. |
| Rule area `PATCH_NO_TRACKS_F` | F.Cu, 25.4 square: no tracks, no footprints. Pour, vias and pads are allowed, so GND stitching vias under the patch are permitted. |
| Rule area `PATCH_FEED_VOID_INNER` | In1.Cu and In2.Cu, 4.0 mm circle at the feed: no pour, tracks or vias. |
| Silk | 25.4 mm square outline drawn just outside the copper, with a chamfer mark at the R2.81 key corner. |
| Fab | Nominal 25.1 body with the real corner radii, a feed-pin circle, and FEED and KEY text. |
| Courtyard | F.CrtYd 26.5 mm square (patch maximum + 0.55). B.CrtYd 3.5 mm square around the pin, which keeps bottom-side parts off the protruding pin and solder. |
| Keep-out advice, not coded | Keep top-side parts taller than about 1 mm at least 3 mm outside the patch outline, and keep the surroundings symmetric (datasheet p.12). Keep L2 solid under the whole patch. |

---

## 2. TX antenna and SMA jack

### 2.1 Taoglas GW.26.0111

From SPE-11-8-035-M:

- 2.4 GHz monopole, 2400-2500 MHz, peak gain 2.24 dBi, efficiency 48.7 %, vertical (linear) polarization.
- Ø7.9 x 30 mm. Tested on a 150 x 90 mm ground plane.
- **Connector "SMA(M) ST"**: a male pin Ø0.9 +0.03/-0 mm inside a 1/4"-36 UNS-2B coupling nut, HEX 8, 8.4 +/-0.3 long.

So it is a **standard-polarity SMA plug (male)**, not RP-SMA, and the board needs a standard **SMA(F) jack (female socket)**. Cinch note 1 confirms the fit: its female contact is made to mate a 0.0355-0.0370 in (0.90-0.94 mm) male pin.

### 2.2 Chosen jack: Cinch Connectivity (Johnson) **142-0711-821** (gold; nickel version 142-0711-826)

"SMA 50 Ohm End Launch Jack Receptacle, Round Contact", 0-18 GHz, for **0.062 in (1.57 mm) board**. DigiKey lists it as active, Board Edge / End Launch.

| Dimension | Value | Meets the request? |
|---|---|---|
| Flange | **0.250 in (6.35) square x 0.065 in (1.65) thick** | Yes. scad assumes 6.5 x 1.6 x 6.5. |
| Barrel | 0.375 in (9.52) from the flange back face, so **7.87 mm out from the flange front face** | Yes, at least 7 mm. **6.07 mm** projects outside a 1.8 mm wall. |
| Thread on the barrel | Only the outer portion is threaded: about 4.7 mm of 1/4-36 after a smooth neck of about 2.8 mm (scaled from the drawing, not dimensioned). Starting about 1.0 mm outside the wall, **all ~4.7 mm of thread is outside the wall.** | Yes, the >= 4 mm outside the wall requirement is met. |
| Legs and contact | Four legs, 0.81 wide, 1.02 (upper) and 1.07 (lower) thick, set at the flange corners. Leg slot "A" 0.068 in (1.73) for the 1.57 board. Contact Ø0.76 round. Legs and contact run **0.150 in (3.81)** behind the flange. | |
| Barrel axis above the board top | **About 0.4 mm** (range 0.38-0.55). Not dimensioned. Derived from the drawing: the Ø0.76 contact lies on the board's top surface, and in the side view the body centre is about 1.2 mm above the slot centre. | Slightly below the 0.6-0.8 asked for. Set `sma_axis_z = 0.4` in the scad. |
| Body below the board | The flange bottom is about 2.78 mm below the board top, so about 1.2 mm under the board bottom. The lower legs hang 1.07 mm below the board bottom; the scad leaves 1.56 mm there. | The scad floor check passes: body bottom at 4.55 mm against a 4.36 mm limit. |

**Why not the others:**

| Candidate | Status |
|---|---|
| Cinch 142-0701-801 | Same family, but the flange is **9.52 wide x 7.92 high**. It does not fit `tx_nw` or the 6.85 mm U-slot. |
| **Amphenol RF 132134** | **A vertical PCB jack, not an edge-launch part.** KiCad has only `SMA_Amphenol_132134*_Vertical`. |
| Amphenol RF 132322 | Distributor text describes an end-launch jack for 0.062 in board with a 0.250 in square flange and round post contact, so it is a likely second source. The drawing could not be read (amphenolrf.com 403); do not use it until the drawing is checked. |
| Amphenol RF 132289 | Has a KiCad footprint. Its fab outline shows about a 10.2 mm span (±5.08), wider than 7 mm. Drawing could not be read. |
| Amphenol RF 901-10510-x | Not verified. |
| Molex 73251-1150 | DigiKey describes it as "Board Edge, End Launch". The Molex drawing could not be read (connection reset). KiCad's sibling footprint `73251-1153` shows a 9.5 mm wide flange; dimensions for 73251-1150 itself are unknown. |

### 2.3 KiCad stock footprints in `Connector_Coaxial.pretty` (KiCad 10.0.7)

SMA footprints present:

- `SMA_Amphenol_132134_Vertical`, plus the `-10`, `-11`, `-14` and `-16` vertical variants
- `SMA_Amphenol_132203-12_Horizontal`
- `SMA_Amphenol_132289_EdgeMount`
- `SMA_Amphenol_132291_Vertical`, `SMA_Amphenol_132291-12_Vertical`
- `SMA_Amphenol_901-143_Horizontal`, `SMA_Amphenol_901-144_Vertical`
- `SMA_BAT_Wireless_BWSMA-KWE-Z001` (vertical through-hole)
- `SMA_Molex_73251-1153_EdgeMount_Horizontal`, `SMA_Molex_73251-2120_EdgeMount_Horizontal`, `SMA_Molex_73251-2200_Horizontal`
- `SMA_Samtec_SMA-J-P-H-ST-EM1_EdgeMount`
- `SMA_Wurth_60312002114503_Vertical`, `SMA_Wurth_60312102114405_Vertical`

There is **no** `SMA_Amphenol_132134_EdgeMount` and **no** `SMA_Samtec_SMA-J-P-X-ST-EM1` (only `-H-`).

How the edge-mount footprints compare with the 142-0711-821:

| Stock footprint | Comparison |
|---|---|
| `SMA_Samtec_SMA-J-P-H-ST-EM1_EdgeMount` | Centre pad 1.27 x 3.2. GND pads 1.35 x 3.7 at ±2.825 (they span 2.15-3.5). The Cinch legs (2.36-3.175) would land on these pads, but the centre pad is shorter than the 3.81 contact and the gap to GND is 0.79 instead of 1.27. **Not a match.** |
| `SMA_Molex_73251-2120_EdgeMount_Horizontal` | Its fab shows a 6.35 x 1.02 flange and an 11.4 mm barrel. Its pads (1.78 centre, 2.665-wide GND at ±3.49) are effectively the Cinch layout. It is a different part with an unverified board thickness, so it is listed for reference only. |
| `SMA_Amphenol_132289_EdgeMount`, `SMA_Molex_73251-1153_EdgeMount_Horizontal` | Wider flanges and ground spans. They do not fit the notch. |

**Conclusion:** use the proposed `SMA_Cinch_142-0711-821_EdgeLaunch`.

### 2.4 Footprint: `SMA_Cinch_142-0711-821_EdgeLaunch`

The origin is the **board edge at the jack (the notch bottom) on the jack axis**. The barrel points +X, so on the right board edge the footprint is placed at 0 degrees. The board copper is at x < 0.

The land pattern comes from Cinch's end-launch table, row 142-0711-821/826: B = .070, C = .170, D = .380, E = .165 in. All copper is set back 0.25 mm from the routed edge.

| Element | Definition |
|---|---|
| Pad 1, centre (F.Cu) | **1.78 wide (B) x 4.19 long (E)**, from x = -0.25 to -4.44. A 45 degree taper then narrows it to the 0.30 mm CPWG at x = -5.18 (custom pad). |
| Pad 2, GND, top **and** bottom | Two pads per side, **4.19 x 2.67 mm**, spanning y = ±2.16 to ±4.83 (inner edge C/2, outer edge D/2). The legs (y ±2.36 to ±3.175) land in the middle of them. |
| GND vias | 12 tented vias, 0.3/0.5 mm, numbered pad "2": at x = -5.0 for y = ±2.6/±3.5/±4.4, and at y = ±5.3 for x = -3.6/-2.3/-1.0. Continue the 1.0 mm CPWG fence from x = -5.5 onward. |
| Rule area `SMA_LAUNCH_GAP_F` | F.Cu, x -4.44 to 0.2, y ±2.16: no pour. This keeps the **1.27 mm** Cinch gap between the centre pad and the GND pads; without it the pour would fill to 0.2 mm. |
| Rule area `SMA_LAUNCH_VOID_IN1` | In1.Cu, x -5.28 to 0.2, y ±2.16: no pour, tracks or vias. **The launch references In2.Cu, which must be GND there.** |
| Courtyard | F.CrtYd covers pads, flange and barrel, out to x = +9.97. B.CrtYd covers bottom pads, legs and flange. |
| Fab | Legs, contact, flange (back face 0.2 mm off the notch bottom), neck and thread. |
| Dwgs.User | Board-edge line and the enclosure notch outline (1.55 x 7.0 mm). |

**Why the In1 void matters.** Over L2 at 0.21 mm, a 1.78 mm pad is about **17 ohm** for 4.2 mm, roughly 1.6 pF of excess capacitance. That would give only about -4 dB return loss at 2.45 GHz. With L2 voided and L3 as the reference, the pad is about **55 ohm** (closed-form CPWG: W 1.78, G 1.27, h 1.29, Er 4.55). The solder fillet and contact bring it down toward 50 ohm. Cinch's own trace width "A" (.103 in, 2.62 mm) assumes a 2-layer board and does not apply here.

**Edge clearance.** The 0.25 mm setback is below the project's 0.3 mm `edge_clearance`. The current `.kicad_dru` already has a rule, "J3 edge-launch SMA pads run to the notch edge", that ignores edge clearance for `J3`. Point it at whatever reference the TX jack gets; in the schematic today, J3 is the RX U.FL and J4 is the TX U.FL.

### 2.5 Board notch versus flush mount

The scad puts the board edge 0.3 mm (`pcb_clr`) from the wall's inner face. The flange is 1.65 mm thick, so it cannot sit flush at the normal board edge: it would overlap the board by 1.35 mm. **The notch is the right solution, and it suits this jack.**

With the 142-0711-821:

- `tx_notch` = 1.65 + 0.2 - 0.3 = **1.55 mm deep**. The scad's default `sma_body` gives 1.5, which still works with a 0.15 mm gap behind the flange.
- `tx_nw` = 3.175 + 0.3 gives a **6.95 mm wide** notch. The footprint draws it as 7.0.
- The legs clamp the notch bottom over about 3.6 mm and the contact lands on pad 1. JLC's 1.0 mm router leaves R0.5 inner corners at the notch bottom; they clear the flange corners and legs.
- To mount the jack flush at a straight board edge instead, the whole right edge would have to move in by 1.35 mm, which means a 53.65 mm board. The notch is better.

The scad's U-slot is 6.85 mm wide (`sma_thread + sma_clr`). That is wider than the 6.35 mm flange flats, so the flange bears only on its four corners: the lower two against the wall and the upper two against the lid tongue. Corner overlap is about 1 mm. Tightening the antenna nut pulls the jack outward onto these corners, which is acceptable for an 8 in-lb mating torque only if the jack's solder joints are not relied on. If more bearing area is wanted, reduce `sma_clr` to about 0.25.

**Scad parameter updates for this jack** (the scad itself was not edited):

```
sma_axis_z = 0.4;
sma_body   = [6.35, 1.65, 6.35];
sma_barrel = 7.87;
```

These keep every assert passing: floor clearance 0.19 mm, 6.07 mm outside the wall.

---

## 3. USB-C receptacle

### 3.1 GCT USB4105-GF-A against the scad

| | scad | USB4105 (GCT drawing rev B4) |
|---|---|---|
| Width | 8.94 | 8.94 (shell 8.34 + tabs) |
| Length | 7.30 | 7.35 |
| Height | 3.26 | 3.31 |
| Centreline above the board top | 1.63 | **1.73** |
| Front face | flush with the board edge | The recommended PCB layout's "PCB Edge" line coincides with the front face. The first shell stakes are 2.60 behind it and the rear stakes 6.78 behind it. |

**It matches within 0.1 mm**, and the USB 2.0 16-pin top-mount receptacle is the right class of part, so no other receptacle is needed. Update the scad so the opening is centred on the real connector:

```
usb_z_on_pcb = 1.73;
usb_body     = [8.94, 7.35, 3.31];
top_parts_h  = 3.35;
```

With 1.63, a 6.5 mm cable overmold centred on the real 1.73 mm centreline would touch the top of the 6.7 mm opening, with zero margin.

The scad's original numbers (8.94 x 7.3 x 3.26) look like an HRO TYPE-C-31-M-12. Its KiCad footprint, `USB_C_Receptacle_HRO_TYPE-C-31-M-12`, uses the same pad and hole pattern and a 7.30 mm body, but HRO's drawing was not consulted here.

### 3.2 KiCad footprint `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`

- The origin is the **body centre**. The F.Fab body spans x ±4.47 and y ±3.675.
- The front (mating) face is at **local y = +3.675**, marked by a Dwgs.User "PCB edge" line from x -5 to 5. SMD pads A1-B12 sit at y = -3.68; shell slots at y = +1.075 and -3.105; NPTH pegs at y = -2.605.
- These agree with the GCT drawing: 2.60 + 3.675 - 1.075 = 0 (front stakes), and 7.35 / 2 = 3.675.

**Offset for a flush front face (`usb_overhang = 0`).** Place the footprint at 0 degrees (opening toward KiCad +Y, the USB-C edge at the bottom) with its origin **3.675 mm inside the board edge**:

- board coords (27.50, 3.675), for `usb_x = 0`;
- in KiCad, X = left edge + 27.50 and Y = bottom-edge Y - 3.675.

A positive `usb_overhang` d moves the origin to 3.675 - d.

### 3.3 Schematic consequence

The current USB sheet uses J1 = Same Sky **UP20 plug** with a single 5.1k Rd. A **receptacle** that is a sink (UFP) needs:

- **5.1k Rd on both CC1 (A5) and CC2 (B5)**;
- A6 tied to B6 and A7 tied to B7 for D+/D-;
- VBUS on A4/A9/B4/B9 and GND on A1/A12/B1/B12 plus the shell.

The phone then sources VBUS through a C-to-C cable. The `.kicad_dru` already carries a "GCT USB4105 stock footprint" hole-clearance rule for J1.

---

## 4. Summary

| Function | Part (MPN) | Footprint |
|---|---|---|
| RX antenna | Taoglas **WDP.2458.25.4.B.02**. Feed pin at **(+1.8, -1.8) mm from the patch centre in the datasheet top view** (right of and below centre, key corner R2.81 at top-left): 2.55 mm along the diagonal away from the key corner. Pin Ø0.9 +/-0.2 x 2.4 +/-0.4. | `docs/proposed_footprints/Taoglas_WDP.2458.25.4_Patch.kicad_mod` (feed at local (+1.8, +1.8), KiCad Y down) |
| TX connector | Cinch (Johnson) **142-0711-821** SMA(F) end-launch jack, 0.062 in board (142-0711-826 nickel) | `docs/proposed_footprints/SMA_Cinch_142-0711-821_EdgeLaunch.kicad_mod` |
| TX antenna | Taoglas **GW.26.0111**, standard SMA(M) plug | n/a |
| USB-C | GCT **USB4105-GF-A**, USB 2.0, 16-pin, top-mount | stock `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`, origin 3.675 mm inside the edge |

**Open items:**

1. Measure the patch on the real 55 x 78.45 board with the radome: S11, and S21 to TX in both patch rotations. Fit the pi network accordingly. If the RX band is wider than about 25 MHz, consider a broader-band antenna or Taoglas custom tuning.
2. Obtain the Amphenol 132322 drawing if a second-source jack is wanted.
3. Keep In2.Cu (L3) solid GND under the SMA launch and under the L4 patch feed line.
