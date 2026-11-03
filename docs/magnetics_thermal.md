# BEACON phone module: MagSafe magnet fields, RF effects of the ring, and thermal budget

Scope: the 4-layer, 55 x 78.45 x 1.6 mm board in the closed PETG MagSafe enclosure
(`C:\Users\marsi\Downloads\beacon_phone_magsafe_2p5mm_Latest.scad`, default parameters), against the parts in
`scripts/design.py`. Coordinates follow `enclosure_constraints.md`:
* **Board coordinates**: origin at the lower-left corner seen from the component side, USB-C edge at y = 0.
* **Ring centre**: board (27.5, 50.95).
* **Clocking bar**: x 24.5 .. 30.5, y 0.45 .. 19.75.
* **RX patch footprint**: x 14.8 .. 40.2, y 26.5 .. 51.9.
* **Distances**: "r" is the radius from the ring centre. Heights z are measured from the phone face.

Note: the current `build_pcb.py` still places parts on a 63 x 28 mm outline (`BW, BH = 63.0, 28.0`). Every placement rule below is for the 55 x 78.45 board the enclosure needs.

---

## 0. Inputs and the Z stack

| Item | Value | Source |
|---|---|---|
| `skin_t` | 0.20 + 4 x 0.12 = **0.68 mm** | scad (Bambu 0.12 Fine) |
| Magnet pocket | z 0.68 .. 3.23 (2.55 mm deep) | scad `mag_t` |
| `z_pause` / `z_floor` | 3.56 / **4.16 mm** | scad |
| `z_pcb_bot` / `z_pcb_top` | **5.72 / 7.32 mm** | scad: `snap_up(max(z_floor + 1.5, 4.4))` |
| Gap from the magnet pocket top to the PCB bottom / top | 2.49 / 4.09 mm | |
| Outside of the box | 59.2 x 82.65 x 14.32 mm | scad header and ECHO |
| Ring | 54.1 OD x 46 ID. Drawing MS54X46X25MM-5PK: 18 arc segments with the **outer half N and the inner half S** on the face. Magnet 2.0 mm on a 0.25 mm steel plate (2.25 mm overall on the drawing; the listing says 2.55). The drawing says N48 and the listing says N52; Ni-Cu-Ni; max **80 °C**. | totalElement product page and drawing |
| Clocking bar | 6 x 19.3 x 2.55 mm. The vendor gives **no pole layout or backing**, so it is modelled as bare and magnetised through its thickness (worst case). | totalElement install guide |

Heights used for the parts:
* PCB top, z 7.32: the bottom of every part, and the worst case.
* z 8.3: the middle of a 0603/0402 ferrite chip.
* z 8.9: the middle of the core of the 3.1 mm-tall MAPI inductor.

## 1. Static field at the board

### Method
* **Ring**: axisymmetric finite-volume magnetostatic solver (scalar potential, nonuniform grid to ±300 mm). Br = 1.44 T, μr(rec) = 1.05.
  * The 0.25 mm steel plate is modelled as ideal soft steel saturating at Js = 1.9 T. It carries radial flux equal to the smaller of what it collects from the poles and Js x t.
  * Steel saturation decides the answer. The poles put about 2.9 T·mm of flux into the plate, but 0.25 mm of steel carries only about 0.48 T·mm. A plain secant-μ nonlinear solve oscillates there, so the saturated-polarisation form is used.
  * Validation against closed-form solutions with no steel: on-axis within 3 %, and 4 off-axis points within 3 % (direct integration of the face charges). The FV result reads slightly low.
* **"On phone" case**: adds a 1 mm, matching two-pole phone-side array 0.8 mm under the phone face. This is a crude stand-in for the iPhone array.
* **Clocking bar**: closed-form rectangular charge-sheet solution (checked against brute-force integration). It is superposed on the ring field and ignores interaction with the ring steel.
* Scripts are in the session scratchpad (`...\scratchpad\mag\ringfv.py`, `bar.py`, `boardmap.py`).

### 1a. Ring, |B| (mT) against radius

| r from ring centre (mm) | 0 | 10 | 15 | 18 | 20 | 22 | 24 | 25 | 26 | 27 | 28 | 30 | 32 | 35 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Two-pole + 0.25 steel (expected)**, PCB bottom z 5.72 | 1.0 | 1.7 | 3.2 | 5.2 | 7.7 | 13 | 23 | 26 | 26 | 23 | 19 | 10 | 5.8 | 2.7 | 1.0 |
| same, **PCB top z 7.32** | 1.1 | 1.7 | 2.6 | 3.3 | 3.5 | 4.3 | 6.6 | 7.7 | 8.5 | **8.8** | 8.3 | 6.1 | 4.1 | 2.2 | 0.9 |
| same, chip mid-height z 8.3 | 1.1 | 1.6 | 2.2 | 2.4 | 2.2 | 2.0 | 3.2 | 4.1 | 4.9 | 5.4 | 5.4 | 4.5 | 3.3 | 1.9 | 0.9 |
| same, **on the phone**, PCB top | 1.1 | 1.6 | 2.3 | 2.9 | 3.7 | 6.0 | 9.2 | 10.3 | **10.8** | 10.6 | 9.7 | 7.1 | 4.8 | 2.6 | 1.1 |
| Two-pole, **no steel**, PCB top | 0.4 | 0.8 | 2.2 | 4.8 | 8.5 | 14 | 19 | **19.3** | 18 | 16 | 14 | 8.9 | 5.4 | 2.6 | 0.9 |
| Two-pole + 0.55 steel, PCB top | 1.7 | 2.9 | 5.0 | 6.8 | 8.0 | 8.3 | 7.7 | 8.0 | 8.6 | 8.8 | 8.5 | 6.7 | 4.8 | 2.9 | 1.4 |
| *Single-pole ring + 0.55 steel (other vendors), PCB top* | 7.7 | 10.6 | 16 | 24 | 32 | 41 | 49 | 51 | **51** | 49 | 45 | 34 | 24 | 14 | 6.5 |

On the phone face the two-pole ring gives 350-450 mT over the annulus (a plausibility check: it holds the phone).

**What the steel does.**
* **Two-pole ring.** The plate is a flux return between the N and S halves, even saturated. It lowers the upward field by about 55 % at the board top (19 → 9 mT, about -7 dB) and by about 48 % at the board bottom (49 → 26 mT). It cannot do more because 0.25 mm of steel is deeply saturated. Twice the steel thickness barely changes the peak.
* **Single-pole ring** (one pole per face). The steel is just a pole piece and does *not* shield: with steel 51 mT, without 51.5 mT. If the ring is ever sourced from another vendor, check its pole layout.
* **Two-pole field falls off fast.** It drops by about 10x per 4 mm of height over the annulus: 280 → 26 → 7.7 → 2.2 mT at z 3.5 / 5.7 / 7.3 / 9.5.

### 1b. Clocking bar, |B| (mT), modelled bare and single-pole (worst case)

| Position | PCB bottom 5.72 | PCB top 7.32 | z 8.9 |
|---|---|---|---|
| Over the bar centre | 170 | **105** | 69 |
| Over a bar long edge (x = 24.5 / 30.5) | | 88 | |
| 1 / 3 / 5 / 7 / 12 mm beyond the long edge | | 76 / 52 / 33 / 22 / 8 | |
| 1.2 / 3.2 / 6.2 mm beyond the top end (toward the ring) | 93 / 46 / 18 | 58 / 35 / 16 | 39 / 26 / 14 |

**Distance from the bar outline beyond which |B| stays below a threshold, at PCB top:**

| Threshold | Distance |
|---|---|
| 40 mT | 4.0 mm |
| 20 mT | 7.2 mm |
| **10 mT** | **10.8 mm** |
| 5 mT | 15.0 mm |
| 2 mT | 22 mm |

These distances are nearly height-independent at component heights. If the real bar turns out to be two-pole across its 6 mm width, the field at the board would be about 3-5x lower. Measure it.

### 1c. Board map at PCB top: ring on the phone + bar
Map at 2.5 mm cells, board coordinates; y runs from the top edge (y 76) down to the USB-C edge.

Legend: `.` < 5 mT, `-` 5-10, `+` 10-20, `o` 20-40, `O` 40-80, `#` > 80 mT. `P` marks a patch cell that is below 10 mT.
```
      x(mm) 1    6    11   16   21   26   31   36   41   46   51
y= 76.2  . . . - - - + + + + + + + + + + - - - . . .
y= 73.8  . . - - - + + - - - - - - - - + + - - - . .
y= 71.2  . - - + + - - - . . . . . . - - - + + - - .
y= 68.8  - - + + - - . . . . . . . . . . - - + + - -
y= 66.2  - - + - - . . . . . . . . . . . . - - + - -
y= 63.8  - + + - . . . . . . . . . . . . . . - + + -
y= 61.2  - + - . . . . . . . . . . . . . . . . - + -
y= 58.8  + + - . . . . . . . . . . . . . . . . - + +
y= 56.2  + - - . . . . . . . . . . . . . . . . - - +
y= 53.8  + - . . . . . . . . . . . . . . . . . . - +
y= 51.2  + - . . . . P P P P P P P P P P . . . . - +
y= 48.8  + - . . . . P P P P P P P P P P . . . . - +
y= 46.2  + - - . . . P P P P P P P P P P . . . - - +
y= 43.8  + + - . . . P P P P P P P P P P . . . - + +
y= 41.2  + + - . . . P P P P P P P P P P . . . - + +
y= 38.8  - + - - . . P P P P P P P P P P . . - - + -
y= 36.2  - + + - . . P P P P P P P P P P . . - + + -
y= 33.8  - - + + - . P P P P P P P P P P . - + + - -
y= 31.2  . - - + + - P P P P P P P P P P - + + - - .
y= 28.8  . . - - + + + P P P P P P P P + + + - - . .
y= 26.2  . . . - - + + + + - - - - + + + + - - . . .
y= 23.8  . . . . - - + + o o o o o o + + - - . . . .
y= 21.2  . . . . . - + + o O O O O o + + - . . . . .
y= 18.8  . . . . . - + o o O # # O o o + - . . . . .
y= 16.2  . . . . - - + o O O # # O O o + - - . . . .
y= 13.8  . . . . - - + o O O # # O O o + - - . . . .
y= 11.2  . . . . - - + o O O # # O O o + - - . . . .
y=  8.8  . . . . - - + o O O # # O O o + - - . . . .
y=  6.2  . . . . - - + o O O # # O O o + - - . . . .
y=  3.8  . . . . - - + o O O # # O O o + - - . . . .
y=  1.2  . . . . - - + + o O # # O o + + - - . . . .
```

**Placement zones at PCB top (expected two-pole + steel ring, single-pole bar):**

| Zone | Where (board coords) | \|B\| |
|---|---|---|
| **Z1** (best) | Inside the ring, r < 17 mm, off the patch. The usable part is the lens above the patch, y 52.4 .. 67.9, x 10.5 .. 44.5 at its widest. Also ~4 mm strips beside the patch, x 10.5 .. 14.8 and 40.2 .. 44.5. | < 3 mT |
| **Z2** | Bottom corners: x < 9.5 or x > 45.5, y < 20. More generally, r > 34 mm and more than 15 mm from the bar outline. | < 5 mT |
| **Z3** | The annulus band, r 21.5 .. 31.5 mm, away from the bar. This is the outer ring of the board: left, right and top edges. | 5-11 mT |
| **Z4** (keep-out for magnetic cores) | Within 10.8 mm of the bar outline: about x 13.7 .. 41.3, y 0 .. 30.5. This includes the USB-C receptacle (x 23.0 .. 32.0, y 0 .. 7.3). Within 7.2 mm (x 17.3 .. 37.7, y 0 .. 27) it exceeds 20 mT; directly over the bar, 80-105 mT. | > 10 mT |

**Uncertainty.**
* **Expected ring case**: about ±50 %. The spread comes from magnet thickness (2.0 vs 2.3 mm), the steel model, Br (N48 vs N52) and segment gaps.
* **Clocking bar**: about +0 / -80 %, because its pole layout is unknown.
* **Mitigation**: before committing the layout, measure one assembled base at z ≈ 7.3 (the PCB-top plane) with a Hall gaussmeter or a DRV5055-type linear Hall sensor. A phone magnetometer saturates at about 5 mT and is not suitable.

## 2. Sensitivity of the board parts

The physics: a soft-magnetic body with permeability μ ≫ 1/N (N is the demagnetising factor along the field) in an external field B_ext carries an internal bias of B_int ≈ B_ext / N.
* B_int is nearly independent of μ, so a "high-current" ferrite is no more tolerant than a low-current one. Only the material's saturation Bs and the body shape matter.
* For a 0603 chip (1.6 x 0.8 x 0.8), N ≈ 0.2 along the length and ≈ 0.4 across it.
  * A field along the chip length biases the ferrite at about 5 x B_ext.
  * A vertical field biases it at about 2.5 x B_ext.
* NiZn ferrite has Bs ≈ 0.3-0.4 T at 25 °C, about 0.25-0.3 T hot. Incremental μ falls noticeably once the bias exceeds about 0.25 Bs.

| Part | Core | Mechanism | Est. effect at **Z3 (≤ 11 mT)** | Effect over the **bar (80-105 mT)** | Rule |
|---|---|---|---|---|---|
| **LQM18PN100MFRL**, 10 µH nRF DC/DC | Multilayer NiZn ferrite, closed path, low Isat (tens to ~100 mA class) | DC bias of the whole body | 5-25 % L loss (orientation dependent) | Saturated: L collapses toward the air-core value; DC/DC ripple and spurs rise, and regulation may fail | **Most sensitive part.** Run REG1 as an LDO (DCDCEN = 0) and depopulate it with the 15 nH. If the DC/DC must stay, put the pair in Z1 only. |
| **BLM18PG221SN1D** x3 (VDD_PA, VCC_SYN, LNA_VCC) | NiZn ferrite bead. 220 Ω @ 100 MHz, 1.4 A, 0.1 Ω (distributor data) | Same, plus each bead's own DC current (0.25 A on VCC_SYN) | 5-20 % impedance loss: tolerable | Impedance largely gone, so buck harmonics and digital noise pass to the synth, PA and LNA | Place in Z1/Z2 (< 5 mT). Otherwise substitute (section 2a). Never in Z4. |
| **Wurth 74438357056** (WE-MAPI, 4.1 x 4.1 x 3.1 max, 5.6 µH, Isat 10 % 3.9 A, Isat 30 % 8.1 A, RDC 46.5 mΩ). The footprint says MAPI-4020, but the datasheet height (3.1 max) is a 4030 body: check the 3D model and the 3.3 mm `top_parts_h`. | Metal-alloy powder, distributed gap, Bs ≈ 1.2-1.5 T, μ_eff ~ 20-40 | Bias B_int ≈ 2.5-3 x B_ext | ≤ 2 % L drop | About 5-15 % L drop and some loss of Isat headroom. Peak current is only about 0.56 A (0.36 A load + ±0.2 A ripple), 7x below Isat 10 %, so it would still work. Pull force is about 0.4 N (40 gf), toward the magnet, which the solder handles. | Anywhere outside Z4. No substitution needed. |
| 15 nH LQG15HS15NJ02D; 4.7 nH LQP15MN4N7B02D; 1.2 nH LQP15MN1N2B02D; 18 nH Coilcraft 0402CS-18NXGRW | Ceramic multilayer, thin-film, ceramic-core wirewound: μr = 1 | Only the Ni barrier of the terminations is magnetic | None | None | No restriction |
| **12 nH CC2595 RF_OUT DC feed** (no MPN) and the **22 nH DNP ESD chokes** | Unspecified | A generic "0402 inductor" could be a ferrite multilayer part | | | **Specify a non-magnetic part**, e.g. Murata LQW15AN12NJ00D / LQW15AN22NJ00D (wirewound, non-magnetic core) or LQG15HS12NJ02D / 22N. The 12 nH carries most of the PA's ~0.1 A, so confirm its rated current is ≥ 0.2 A. |
| 32 MHz crystal ABM11W; 26 MHz TCXO TG2520SMN | Quartz (non-magnetic). The only magnetic material is the lid, seal ring or leads (Kovar / Ni). | Small static frequency pull plus a tiny force | Negligible (≪ 1 ppm) | Still a static, sub-ppm-order offset; the BLE ±40 ppm and CW-carrier budgets absorb it. Nothing moves relative to the magnets, so there is no vibration-induced modulation. | Prefer outside Z4 (free to do) |
| **LMX2582 VCO** | On-chip spiral inductors and varactors, no magnetic material | A static B does nothing measurable to on-die LC tanks at these levels | None | None | No restriction. VCO calibration absorbs any static offset. |
| nRF52840, LT80602, CC2595, QPL9547, INA219 | Silicon, no Hall elements | None | None | None | No restriction |
| INA219 shunts (ERJ-6BW 50 mΩ metal plate) | Non-magnetic resistive alloy | Magnetoresistance ≪ 1 ppm at 0.1 T | None | None | No restriction. Kelvin routing still applies. |
| USB-C receptacle GCT USB4105-GF-A (directly over the bar) | Shell is steel sheet if ferromagnetic (check the datasheet material) | Attraction, plus slight shunting of the bar's back-side flux | | Up to ~1-2 N pull if the shell is plain steel; the through-hole shell legs take it | OK. Do not rely on the solder pads alone: keep the THT shell tabs. |
| **Phone magnetometer / Hall sensors** | | The ring and bar are a standard MagSafe accessory set at Apple's positions. The board adds only DC current loops: ~0.35 A on 3V3 and 5V0, switched on/off with TX. | | | Route 5V0 and 3V3 as L3 pours directly over the L2 GND plane, return under supply, so the loop area is ≪ 1 cm². That keeps the TX on/off step below about 0.1 µT at the phone's compass, against Earth's ~50 µT. Keep the buck hot loop tight (also for EMI). |

### 2a. Substitutions, so the design does not depend on bead placement or on the ring's real pole layout
| Rail | Now | Replace with | Notes |
|---|---|---|---|
| LNA_VCC (5V0, 65 mA) | BLM18PG221SN1D | **10 Ω 0603** (e.g. ERJ-3EKF10R0V) + LNA_VCC bulk 1 µF → **10 µF** | Drop 0.65 V → 4.35 V, inside QPL9547's 3.15-5.25 V. Corner 1.6 kHz, so about 50 dB at 506 kHz. Dissipates 42 mW. Re-check the bias current; R 3.32k is referenced to LNA_VCC. |
| VDD_PA (3V3, ~0.1 A) | BLM18PG221SN1D | **1.0 Ω 0603** (e.g. ERJ-3RQF1R0V) + the existing 10 µF | Drop 0.1 V. CC2595 Pout varies 4 dB over 2-3.6 V, so this costs about 0.2-0.3 dB. Corner 16 kHz, so about 30 dB at 506 kHz. |
| VCC_SYN (3V3, 0.25 A, **≥ 3.15 V**) | BLM18PG221SN1D | Keep the bead **only in Z1/Z2**. Otherwise use a **1 µH metal-alloy** chip (Bs > 1 T: e.g. Murata DFE201610E-1R0M=P2 or Coilcraft XFL2010-102ME, candidates to verify) **+ 0.22 Ω series damping** into the existing ~40 µF | 1 µH / 40 µF resonates at 25 kHz with Z0 ≈ 0.16 Ω, so 0.22 Ω gives Q < 1. Gives about 50 dB at 506 kHz, better than the bead (a bead is only a few Ω at 0.5 MHz). Budget: 3.34 - 0.018 (shunt) - 0.055 - DCR → about 3.25 V. |
| nRF REG1 | LQM18PN100MFRL + LQG15HS15NJ02D | **DNP both; firmware DCDCEN = 0** (LDO mode) | Costs about 2 mA at 3.3 V (under 10 mW against a 1.6 W budget). It also removes an MHz-range switcher next to the RX radio. |

## 3. Ring, steel and phone at RF (2.45 GHz)

* **Patch (Taoglas WDP.2458.25.4.B.02) and the steel ring behind the ground plane.**
  * At 2.45 GHz the copper skin depth is about 1.3 µm, so the solid L2 GND (plus the L1 and L4 GND pours) is opaque. The ring sits 2.5-4 mm behind it.
  * The patch's fields are between the patch and L2, and in the half-space above. The ring only sees currents that wrap around the board edges.
  * This matters a little here because the annulus runs right under three board edges: x 0.3 / 54.7 at y ≈ 51, and y 78.15 at the top. The ring also passes under the patch's lower edge (board y 26.5-28).
  * The steel plate is a closed loop of about 157 mm circumference. Its n = 1 loop mode is near 1.9 GHz and n = 2 near 3.8 GHz, so 2.45 GHz falls between them, and steel (with Ni plating) makes any mode very low-Q.
  * Expected effect: a few-MHz detune and at most a few tenths of a dB of loss. It is small next to the phone, so no layout action is needed beyond the GND rules below.
* **The phone matters more than the ring.**
  * The phone's internal metal (frame, MagSafe coil and ferrite shield, battery, board shields) sits about 7-9 mm below L2 (board bottom at z 5.72, plus about 1-2 mm inside the phone).
  * Together with the board ground it forms a parallel-plate region. Board-length resonance is about 1.9 GHz (78 mm) and width resonance about 2.7 GHz (55 mm).
  * The patch was characterised on a **70 x 70 mm symmetric ground**, and Taoglas calls symmetry critical. Ours is 55 x 78.45 with a phone behind it.
  * Expect:
    * a resonance shift of tens of MHz against the 2400-2500 MHz band;
    * a different back lobe (front-to-back improves: the phone acts as a reflector);
    * about 1-2 dB of gain change.
  * Actions:
    * Tune the pi match (DNP shunt + 0R) **with the module on a phone**.
    * Stitch the board perimeter with GND vias at ≤ 3 mm pitch on all 4 layers, so the inner layers don't radiate from the edge.
    * Keep L2 and L4 solid under and around the patch, with no slots over the ring.
    * If the shift is larger than the match can absorb, Taoglas offers custom-tuned variants (MOQ).
* **TX antenna (Taoglas GW.26.0111 on the right-edge SMA, y = 66).**
  * The jack is about 4.5 mm outside the ring OD and behind the board ground. The ring's effect is negligible.
  * The phone is the dominant perturbation: shadowing of roughly 10 dB or more toward the phone side, and some detune. This is why the radiator sits past the phone edge.
  * A +20 dBm CW carrier a few cm from the phone's 2.4 GHz antennas will desense the phone's own Wi-Fi/BT on nearby channels.
  * TX-to-RX isolation is set by the patch null and the geometry; the ring doesn't change it. The ≥ 30 dB requirement in `DESIGN_NOTES.md` still stands.
* **SAR (outside the brief, but it drives the duty cycle).** At 2.45 GHz and 5 mm separation, the 47 CFR 1.1307(b)(3) exemption threshold works out to about 3 mW (about 10 mW at 10 mm). A 100 mW handheld CW source therefore needs an RF-exposure evaluation. Time-averaged duty cycling (section 4) helps both SAR and temperature.

## 4. Thermal

### Dissipation (continuous TX + RX)
| Load | Power |
|---|---|
| LMX2582: 0.25 A x 3.34 V | **0.84 W** |
| QPL9547: 65 mA x 5 V | 0.33 W |
| CC2595: 98 mA x 3.34 V = 0.33 W DC, minus ~0.12 W RF out | 0.21 W |
| Buck loss (1.21 W out at 90 %) | 0.13 W |
| nRF52840 | 0.03 W |
| Shunts + polyfuse + beads | 0.05 W |
| **Heat in the box** (RF leaving through the SMA is about 0.085 W) | **≈ 1.58 W** |

USB input is 0.33 A x 5 V = 1.67 W, under the 0.5 A budget. The LMX is 53 % of the heat, more than the PA.

### Lumped model
The board is the hot node, with two paths out. Effective emissivity 0.9; still air outside.

* **Down to the phone: R_dn ≈ 15 K/W.**
  * 1.56 mm air gap (conduction + radiation): about 10 K/W.
  * 4.16 mm PETG floor (k 0.2): about 4.8 K/W.
  * Contact: about 0.5 K/W.
* **Up and out to ambient: R_up ≈ 33 K/W.**
  * 5.4 mm internal air plus radiation: about 21 K/W.
  * 1.6 mm lid: about 1.6 K/W.
  * Outer convection + radiation over 9 x 10^3 mm²: about 10 K/W.
* **Parallel: ≈ 10.5 K/W.**
* **Time constant:** heat capacity is about 41 J/K, so τ ≈ 7 min. Steady state takes about 30 min, so TX bursts of a few minutes don't reach it.
* **LMX junction:** Tj = T_board + 0.84 W x (ψJB 5.3 + ~12 K/W local spreading). From TI SNAS680: RθJA 30.5, RθJB 5.4, ψJB 5.3 °C/W.

| Scenario (continuous TX+RX) | Board | LMX Tj | Magnets | Lid outside |
|---|---|---|---|---|
| Desk: phone 35 °C, room 25 °C | 48 °C | 63 °C | 38 °C | 32 °C |
| In hand: phone 38 °C, 25 °C | 50 °C | 65 °C | 40 °C | 33 °C |
| Phone 40 °C, ambient 30 °C | 53 °C | 68 °C | 43 °C | 37 °C |
| Phone 40 °C, ambient 35 °C | 55 °C | 69 °C | 43 °C | 41 °C |
| Same, poor contact (2 K/W) | 56 °C | 70 °C | 44 °C | 41 °C |
| Phone 40 °C, 35 °C, full sun, dark lid (~4.7 W absorbed) | 70 °C | 84 °C | ~46 °C | **~78 °C** |
| Same, white lid (α ≈ 0.25) | 59 °C | 73 °C | ~44 °C | 50 °C |
| Phone 40 °C / 30 °C, with a 15 x 15 mm, 3 W/mK gap pad under the LMX | 48 °C | 62 °C | 43 °C | 35 °C |

Duty cycle (TX chain off between bursts, LNA and nRF on), phone 40 °C, ambient 30 °C:

| TX duty | Average power | Board |
|---|---|---|
| 100 % | 1.58 W | 53 °C |
| 50 % | 0.99 W | 47 °C |
| 25 % | 0.69 W | 44 °C |
| 10 % | 0.51 W | 42 °C |

**What the numbers say.**
* **Magnets.** They sit in the floor right on the phone, so they follow the phone: phone +3-6 K, about 38-46 °C in every realistic case. That is far below the 80 °C rating. Br falls reversibly by about 0.12 %/K, so at 45 °C the pull is about 2-3 % lower than at 25 °C.
  * The real 80 °C risks are the heat-set insert iron (the scad already warns), a 90-100 °C print bed, and a hot car dashboard (60-90 °C), not the electronics.
  * For comparison, press summaries of Apple's Accessory Design Guidelines quote N45SH (an "SH" 150 °C grade) for MagSafe arrays. If the product must survive cars, ask for an SH-grade ring.
* **PETG.** Tg is about 80 °C and HDT about 70 °C. Normal use keeps the walls at 35-55 °C, which is fine. Full sun on a dark lid takes the lid to about 75-80 °C, at the softening point (snap beads and insert bosses creep).
  * Print the lid light-coloured (white or natural).
  * Keep PETG. Do not use PLA (Tg ~60 °C).
  * ABS/ASA would be thermally better but are ruled out by the print-in-place bed temperature next to the magnets.
* **Touch.** The lid outside reaches 32-41 °C in normal use, below the ~43 °C long-contact touch limits typically applied (IEC 62368-1 TS1 class).
* **The phone.** About 0.8-1 W goes into the phone's back. It warms by a few K and can push an already-hot phone (> 40 °C) toward its own thermal limits and charging throttle. The phone cannot MagSafe-charge with the module on, and the module occupies the USB-C port.

### Thermal layout rules
* **LMX2582 (U8, RHA-40, EP 4.5 mm).**
  * Use a 5 x 5 via array in the EP (0.25-0.3 mm drill, about 0.9-1.0 mm pitch), solidly connected to L2 GND and to an L4 GND pour of at least 15 x 15 mm directly under it. L4 faces the floor and the phone, the dominant heat path (R_dn < R_up).
  * Ask JLC to tent or plug the vias (they are in an EP, so solder wicking matters), or use the footprint's 0.2 mm vias.
* **QPL9547 and CC2595.** Fill the EPs with vias per the datasheets (Qorvo calls for vias under the paddle; the CC2595 footprint already has ThermalVias). Add L1 and L4 GND pours around them.
* **LT80602.** Its EP is **VIN (5V0)**. Use vias into a 5V0 pour on L3, never GND. Its 0.13 W is easy.
* **Spacing.** Keep the three hot parts (LMX 0.84 W, LNA 0.33 W, PA 0.21 W) at least about 15 mm apart and off the patch footprint. They can sit over the ring: magnetically they are insensitive, and the floor under the ring has NdFeB (k ≈ 8 W/mK) in it.
* **Copper.** Flood unused L1/L4 area with GND, stitched at ≤ 3 mm. The pours double as heat spreaders. 1 oz outer layers are enough.
* **Optional.** A 1.5-1.8 mm soft gap pad (≥ 3 W/mK, compressed into the 1.56 mm floor gap) under the LMX lowers the board by about 5 K. It does send more heat into the phone. Treat it as a fallback if the measured board temperature exceeds 60 °C.

### Firmware limits
1. **Sensors.** Read the nRF52840 TEMP sensor (±5 °C class accuracy) every 1 s. Read both INA219s at ≥ 10 Hz.
2. **Soft limit, nRF die ≥ 60 °C.** Cap TX duty at 50 %, or step OUTA_PWR / the PA drive down. Release below 55 °C.
3. **Hard limit, nRF die ≥ 68 °C.** At this point the LMX Tj is about 85 °C, the lid about 45 °C and the magnets under 50 °C.
   * Turn TX off: PA_EN low, then SYN_CE low.
   * Turn the LNA off.
   * Resume only after the die drops below 55 °C.
4. **Overcurrent.** If the 5 V INA219 reads > 0.45 A for > 100 ms, or 3V3 drops below 3.2 V, shut TX down and flag a fault.
5. **Idle states.**
   * Synth CE low whenever not transmitting (TI quotes 3.7 mA for register powerdown; CE low is lower).
   * LNA_PD high (off) outside RX windows. At 0.33 W, the LNA is the second-largest load.
6. **TX watchdog.** The host must re-arm TX every N s. Hop channels for FCC 15.247 anyway, and use the time-averaged duty cycle as the RF-exposure and thermal knob.
7. **Sizing.** Continuous operation is thermally acceptable in normal conditions (board ≤ 56 °C). A 25-50 % duty is still the recommended default for margin (sun, hot phone) and for SAR.

---

## Ranked layout rules

1. **Nothing with a magnetic core within 11 mm of the clocking-bar outline.**
   * Keep-out: board x 13.7 .. 41.3, y 0 .. 30.5.
   * Field there: > 10 mT at the board top; 80-105 mT over the bar. This is where the USB-C receptacle sits.
   * Applies to ferrite beads, LQM-type ferrite inductors and the buck inductor.
   * Prefer 15 mm (x < 9.5 or x > 45.5 in the bottom strip) for ferrites.
2. **nRF52840 REG1 in LDO mode.** DNP the LQM18PN100MFRL (10 µH) and LQG15HS15NJ02D (15 nH), and set DCDCEN = 0. This is the most field-sensitive part, and LDO mode costs under 10 mW. If the DC/DC is kept, the pair must sit in Z1: r < 17 mm from the ring centre (27.5, 50.95), off the patch, where the field is < 3 mT.
3. **Ferrite beads: placement or substitution.**
   * Place them only where the field is < 5 mT: Z1 (inside r < 17), or Z2 (r > 34 and more than 15 mm from the bar).
   * Or, robustly:
     * LNA bead → 10 Ω 0603 + 10 µF.
     * PA bead → 1.0 Ω 0603 + 10 µF.
     * Synth bead → 1 µH metal-alloy (e.g. Murata DFE201610E-1R0M=P2 or Coilcraft XFL2010-102ME, verify) + 0.22 Ω damping.
   * Never put a bead in the annulus band r 21.5-31.5 mm if the ring's pole layout is unverified: a single-pole ring would put 40-51 mT there.
4. **Specify non-magnetic RF inductors for every unspecified L.**
   * 12 nH PA feed: LQW15AN12NJ00D or LQG15HS12NJ02D, rated current ≥ 0.2 A.
   * 22 nH ESD chokes: LQW15AN22NJ00D or LQG15HS22NJ02D.
   * The existing LQP15, LQG15 and 0402CS parts are fine anywhere.
5. **WE-MAPI 74438357056 (buck L): anywhere outside rule 1's keep-out.**
   * Expect ≤ 2 % L change over the ring and ≤ 15 % even over the bar. Peak current is 0.56 A against Isat 10 % of 3.9 A.
   * Fix the footprint/3D name: the datasheet height is 3.1 max, a 4030 body, not 4020. It still fits the 3.3 mm top-part limit.
6. **Crystal (32 MHz) and TCXO (26 MHz): keep outside rule 1's keep-out** (free to do). Elsewhere the effect is negligible. No restriction on the LMX2582, nRF, PA, LNA, LT80602, INA219 or shunts.
7. **Ground and RF.**
   * Keep L2 solid and L4 GND poured over the whole ring footprint and under the patch, with no slots.
   * Stitch the board perimeter with GND vias at ≤ 3 mm, all layers.
   * Tune the patch pi match with the module on a phone. The patch was characterised on a 70 x 70 mm ground; ours is 55 x 78.45.
   * The steel ring behind the ground plane needs no other action.
8. **Thermal copper.**
   * LMX2582: 5 x 5 EP via array to L2 and a ≥ 15 x 15 mm L4 GND pour under it.
   * QPL9547 and CC2595: EP via arrays plus L1/L4 pours.
   * LT80602 EP into a **5V0** pour.
   * Hot parts at least 15 mm apart and off the patch.
9. **Supply routing.** 5V0 and 3V3 as L3 pours over the L2 GND plane, with minimal loop area. This also keeps DC-field steps at the phone's magnetometer below about 0.1 µT.
10. **Thermal limits.**
    * Design for about 1.6 W continuous. Expected: board ≤ 56 °C, LMX Tj ≤ 70 °C and magnets ≤ 46 °C with the phone at 40 °C and ambient at 35 °C.
    * Firmware throttles at nRF TEMP 60 °C and shuts TX and the LNA off at 68 °C (5 °C hysteresis), plus the INA219 overcurrent trip at 0.45 A.
    * Default TX duty is 25-50 %.
    * The N52 80 °C limit is reached only by external heat (sun, car, insert iron), never by the electronics.
    * PETG is fine. Print the lid light-coloured; never PLA.
11. **Verify before layout freeze.** Measure the field of one assembled base at z ≈ 7.3 mm with a Hall gaussmeter. Over the annulus, about 9 mT confirms the two-pole + steel model and about 50 mT means single-pole. Also measure over the bar, where 105 mT is the bare single-pole worst case. If the annulus reads > 20 mT, apply rule 3's substitutions unconditionally.

## Sources
* totalElement MagSafe magnet installation guide: https://totalelement.com/pages/magsafe-magnet-instructions (orientation, clocking magnet position 31.2 mm, 0.5-0.9 mm skin)
* totalElement 54 x 46 x 2.5 mm ring product page and drawing MS54X46X25MM-5PK (dated 2024-06-04): https://totalelement.com/products/54-x-46-x-2-5mm-magsafe-neodymium-rare-earth-magnet-phone-attachment-ring-assembly-with-alignment-magnet-5-pack and https://cdn.shopify.com/s/files/1/1025/0137/files/MS54X46X25MM-5PK.PDF (18 segments, outer N / inner S, 2.0 mm magnet on steel plate, 2.25 overall, Ni-Cu-Ni, 80 °C)
* Würth Elektronik 74438357056 datasheet: https://www.we-online.com/en/components/products/datasheet/74438357056.pdf
* TI LMX2582 datasheet SNAS680E (ICC 250 mA; thermal table RθJA 30.5, RθJB 5.4, ψJB 5.3 °C/W); TI CC2595 SWRS090A (Pout +20.7 dBm, PAE 40 %, TA ≤ 85 °C); Qorvo QPL9547 datasheet Rev D (IDD 65 mA at 5 V, θJC 38.6 °C/W, TCASE ≤ 105 °C)
* Taoglas WDP.2458.25.4.B.02 spec SPE-14-8-039-F (tuned and characterised on a 70 x 70 mm ground plane, symmetric ground recommended, Tf 0 ± 20 ppm/°C)
* Murata BLM18PG221SN1D ratings (220 Ω @ 100 MHz, 1.4 A, 0.1 Ω), as reported by distributors; Murata's product pages did not render. No published DC-bias or external-field data was found for BLM18PG or LQM18PN, so those thresholds are from the demagnetisation estimate above.
* Apple Accessory Design Guidelines, MagSafe section, via press summaries (MacRumors / 9to5Mac, Nov 2020): N45SH magnets, NiCuNi plating
* 47 CFR 1.1307(b)(3)(i)(B): RF-exposure exemption formula (ERP_20cm = 3060 mW for 1.5-6 GHz)
