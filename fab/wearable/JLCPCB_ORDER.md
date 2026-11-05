# BEACON Wearable: JLCPCB order sheet

Fab outputs for the wearable tag. The design itself is the Altium project "Backscatter Radio Capstone - Wearable"
(team Altium 365 repo); these files were exported with `BEACON_Wearable_JLCPCB.OutJob` from its commit `66d48ca`
(2026-11-03, "Added silkscreen") plus the Top Solder mask fix below (PCB1.PcbDoc saved 2026-11-04, not yet
committed to Altium 365).

### 2026-11-04: Top Solder mask fix on the RF switch outputs

The exposed-copper openings on the four 0.335 mm doglegs from the HMC190B switches to their series caps
(NetC11_1, NetC13_1, NetC16_1, NetC17_1: U2-3/U2-6/U4-3/U4-6 to C11/C13/C16/C17) were stair-stepped
rectangles, offset to one side of the trace. Each is now one region that follows the trace at +/-0.625 mm
(the same 1.25 mm opening as the straight RF lines), with round joins at the bends, a 0.105 mm mask web to
every other-net pad, via and trace, and the 0.2 mm web across the 0402 caps kept. Only `PCB1.GTS` changed
geometrically (XOR 3.35 mm2, all inside x 18.8-22.3, y 1.0-15.0 mm); every other layer and both drill files
are geometrically identical to the previous export.

## Files to upload

| Step on jlcpcb.com | File in `fab/wearable/` |
|---|---|
| 1. Add Gerber file | `BEACON_Wearable_gerbers.zip` (upload as is, don't unzip) |
| 2. PCB Assembly: BOM | `BEACON_Wearable_BOM_JLC.csv` |
| 3. PCB Assembly: CPL | `BEACON_Wearable_CPL_JLC.csv` |

After step 1, JLC should show **4 layers, 30 x 30 mm**. `gerbers/` holds the same files unzipped.

The zip has top/bottom copper (GTL/GBL), inner layers (G1 = L2 GND, G2 = L3 power), silkscreen (GTO/GBO),
paste (GTP/GBP), mask (GTS/GBS), the board outline (`PCB1.GM`, from the board shape: 30 x 30 mm, R3 corners)
and Excellon drill files (`PCB1-Plated.TXT`, `PCB1-NonPlated.TXT`). Units mm, format 4:4, origin at the
board's bottom-left corner for Gerbers, drill and CPL.

## PCB options

| Option | Setting |
|---|---|
| Base material | FR-4 |
| Layers | 4 |
| Dimensions | 30 x 30 mm (detected from the Gerbers) |
| Thickness | 0.8 mm |
| Impedance control | Yes, stackup **JLC04081H-7628** (matches the Altium stackup, 0.77 mm) |
| Via covering | **Epoxy filled & capped (via-in-pad, POFV): required.** 55 vias have their hole inside a pad: 8 nRF52840 (U5) ball pads (0.15 mm vias on AC13, AC15, AC19, AD14, AD18, B11, B13, K2), 16 thermal vias in the U5 exposed pad and 5 in the U1 (AEM30940) pad, 22 in the J3 U.FL ground pads, and GND vias in B1-2, C23-1, C29-1, R13-1. Tented vias would wick solder out of these joints |
| Min via hole / diameter | 0.15 mm / 0.25 mm (228 holes at 0.15 mm, JLC's 4-layer minimum) |
| Surface finish | **ENIG** (nRF52840 aQFN73) |
| Outer copper | 1 oz |
| Inner copper | 0.5 oz |
| Mark on PCB | Remove mark, or specify a location |
| Everything else | Default |

## Assembly

| Item | What to do |
|---|---|
| Type | Standard PCBA, **both sides**: 32 parts top, 50 bottom (82 placed) |
| Not stocked at JLC (as of the 11/2 BOM check) | B1 74AUP2G04, B2 GRF6011, U1 AEM30940, U2-U4 HMC190BMS8E, L3 22 uH (no LCSC part). Pre-order into your JLC parts inventory or consign them |
| J1 | Through-hole: needs THT assembly or hand soldering |
| J2 | Tag-Connect TC2030-NL pads only, nothing to place |
| TP1-TP15 | Test pads, not placed |
| DNP | R1, R19, R20 (Prod variant), already left out of the BOM and CPL |
| Placement preview | Check pin 1 and rotation of D1, U1, U5, U6, B1, B2, U2-U4, Y1, J3, and the polarity of D2/D3. Bottom-side parts use Altium's bottom-view convention |

Then review the DFM report and the price, and place the order.

## Known DFM items

- Copper pours run to the board edge on all four layers (no board-outline clearance rule in the design).
  JLC wants about 0.3 mm. Expect a DFM warning and exposed copper on the routed edge unless the pours
  are pulled back and the files re-exported.
- Schematic and PCB designators disagree around the RF input: the schematic's R18 (0 ohm, RF_In to GND, fitted
  in Prod) is `R19` on the PCB, and the PCB's `R18` is the schematic's R17 (VSEL to CTRL_SPDT). Because the BOM
  and CPL use PCB designators, DNP `R19` leaves the RF_In shunt unplaced, which is what the RF path needs, but
  the schematic says the opposite. Re-annotate / Update PCB in Altium before the next export.
- The Mechanical 1 outline in the PcbDoc is missing its top straight edge. The Gerber outline (`PCB1.GM`) comes
  from the board shape instead and is closed.
