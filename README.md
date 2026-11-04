# BEACON Phone Module

KiCad 10 project for the BEACON phone module: a MagSafe-mounted board with an nRF52840, a 2.4 GHz receive chain
(patch antenna → BPF → LNA → nRF) and a CW transmit chain (LMX2582 synthesizer → CC2595 PA → U.FL to a Taoglas
FXP70 flex antenna). It is powered over USB-C.

**Ordering boards:** follow [`fab/JLCPCB_ORDER.md`](fab/JLCPCB_ORDER.md) (files to upload, board options, parts to check).
The wearable tag's JLCPCB package (exported from its Altium project) is in [`fab/wearable/`](fab/wearable/JLCPCB_ORDER.md).
To order both boards together, [`fab/panel/`](fab/panel/PANEL_ORDER.md) has a combined panel (one of each) with a merged BOM and CPL.

## Opening the project

Open `BEACON_PhoneModule.kicad_pro` in KiCad 10. The project's own libraries are referenced relative to the project
folder (`BEACON.kicad_sym`, `BEACON.pretty`, `BEACON_Routed.pretty`), so no library setup is needed.

| Path | Contents |
|---|---|
| `*.kicad_sch` | Root schematic + 6 sheets: USB, Power, MCU, RX_Frontend, TX_PA, CW_Synth |
| `BEACON_PhoneModule.kicad_pcb` | 4-layer board, 55 × 78.45 mm |
| `BEACON_PhoneModule.kicad_dru` | Custom design rules (JLCPCB limits, RF CPWG, USB pair, nRF aQFN escape) |
| `docs/` | Design notes, stackup and impedance, BOM (LCSC), reviews, hand-routing notes |
| `scripts/` | Python scripts used to generate and post-process the board (run with KiCad's Python) |
| `enclosure/` | OpenSCAD enclosure variants, STL and renders |
| `fab/` | JLCPCB outputs: Gerber/drill zip, BOM, CPL, PDFs, STEP, the one-zip package and the order sheet |
| `fab/wearable/` | Wearable tag JLCPCB outputs (Altium export): Gerber/drill zip, BOM, CPL, OutJob, order sheet |

## Board rules worth knowing

- **Stackup:** JLC04161H-7628, 1.6 mm. L1 signals and RF, **L2 solid GND (no tracks)**, L3 3V3 / VCC_SYN planes,
  L4 signals and USB pair.
- **No GND traces.** GND is copper fills on every layer plus vias; each GND pad has its own via to L2.
  3V3 and VCC_SYN pads have vias to their L3 areas. 5V0 and 5V_BUS are fills.
- **RF:** 50 Ω CPWG, 0.335 mm track, 0.203 mm gap, L1 only. RF and the USB D+/D− pair are locked; don't move them.
- **Vias:** 0.45/0.25 mm everywhere; 0.30/0.15 mm only as via-in-pad on the nRF (U5) balls. Order with
  JLC via-in-pad (POFV, filled and capped), ENIG and impedance control.
- Run DRC (Inspect → Design Rules Checker) before every commit. The remaining work is tracked in GitHub Issues.

## Working together

- **One person edits the PCB at a time.** `.kicad_pcb` is text, but two people's board edits don't merge cleanly.
  Say in the issue or team chat when you take the board, and push when you hand it back.
- Schematic sheets can be edited in parallel by different people (one sheet each).
- Save in KiCad, close the editor, then commit. Keep commits small and say what changed.

## Finishing steps (after routing is complete)

Run from this folder with KiCad's Python (`D:/KiCAD/bin/python.exe -I` on the original machine; adjust the path):

1. `scripts/stitch.py`: GND via fences along RF lines, perimeter and 3 mm grid stitching.
2. `kicad-cli pcb drc --format json -o drc.json BEACON_PhoneModule.kicad_pcb`, then `scripts/bridge_fills.py drc.json`
   to join any fill islands that are left unconnected.
3. `scripts/finish.py`: silkscreen clean-up and zone refill.
4. Final DRC with `--schematic-parity --refill-zones`, then `scripts/export_fab.py` (Gerbers, drill, BOM, CPL, STEP).
