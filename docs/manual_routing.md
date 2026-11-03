# Manual routing: remaining connections

**Board:** `BEACON_PhoneModule.kicad_pcb`, the state after the autorouter (backup in `route/routed_v9_inc.kicad_pcb`).

**Coordinates** are KiCad absolute, in mm, as shown in the PCB editor status bar. The board's top-left corner is at (100, 100).

**Tools:** use the interactive router (**X**). Press **V** while routing to drop a via, and **/** to switch layers. Press **B** to refill zones afterwards.

**Rules to keep:**
- **No tracks on In1.Cu (L2, solid GND) or In2.Cu (L3, 3V3 plane).** The DRC rejects tracks on L2. Route on F.Cu and B.Cu only.
- **Default nets:** 0.15 mm track, 0.15 mm clearance.
- **Power nets** (5V_BUS, 5V0, 3V3, VCC_SYN, REG_*): 0.4 mm where it fits, necking to ≥ 0.1 mm at fine-pitch pins.
- **USB D+/D−:** route as a pair (**6**, the diff-pair router), 0.20 mm wide with a 0.13 mm gap.

| # | Net | From | To | Suggested |
|---|---|---|---|---|
| 1 | 5V_BUS | track end (136.65, 172.50) F.Cu | track end (138.60, 163.63) F.Cu | F.Cu, 0.4 mm, follow the existing 5V_BUS run |
| 2 | 5V_BUS | track end (150.37, 158.61) F.Cu | track end (149.32, 161.00) F.Cu | F.Cu short link, 0.4 mm |
| 3 | 5V0 | U4 pad 3 (VIN1) (108.63, 162.54) | track end (110.00, 161.97) F.Cu | F.Cu stub; keep the VIN1 hot loop short |
| 4 | REG_INTVCC | U4 pad 17 (109.75, 160.60) | track end (108.81, 160.45) F.Cu | F.Cu stub, 0.2 mm |
| 5 | GND | C7 pad 2 (107.40, 164.03) | GND plane | drop a via next to the pad (to L2) |
| 6 | 3V3 | track end (138.83, 124.67) F.Cu | track end (133.15, 117.76) F.Cu | F.Cu or B.Cu; or drop a via at each end to the L3 3V3 plane |
| 7 | 3V3 | U5 ball AD14 (145.75, 162.26) | track (145.75, 161.26) F.Cu | 1 mm F.Cu stub straight up, 0.15 mm |
| 8 | I2C_SCL | track end (118.88, 159.79) F.Cu | track end (146.06, 159.73) B.Cu | long run (~27 mm): via at (118.9, 159.8), then B.Cu |
| 9 | I2C_SCL | track end (148.40, 157.40) B.Cu | U5 ball AD8 (147.25, 162.26) F.Cu | B.Cu to a via near AD8, short F.Cu stub into the ball |
| 10 | I2C_SDA | track end (121.03, 157.46) F.Cu | track end (142.11, 157.75) F.Cu | parallel to SCL (#8): B.Cu with vias at both ends |
| 11 | SYN_CE | via (144.50, 162.76) | track end (142.04, 160.80) F.Cu | F.Cu short link |
| 12 | VCC_SYN | U8 pad 15 (122.35, 114.14) | track end (120.35, 114.14) F.Cu | 2 mm F.Cu stub, 0.25 mm |
| 13 | SYN_SDI | via (145.48, 157.56) | U8 pad 17 (123.35, 114.14) | long B.Cu run toward the synth (beside the existing SPI lines), via near U8, F.Cu stub |
| 14 | SYN_OUTAM | track end (127.20, 113.76) F.Cu | U8 pad 22 (125.54, 112.95) | short F.Cu link (OUTAM termination) |
| 15 | SYN_CSB | U8 pad 24 (125.54, 111.95) | R18 pad 2 (146.05, 158.09) | long B.Cu run with the other SPI lines; vias at both ends |
| 16 | SYN_VTUNE | track end (123.46, 106.62) F.Cu | U8 pad 35 (122.85, 108.26) | short F.Cu link; keep Vtune short and away from SPI |
| 17 | NRF_DEC4_6 | via (148.00, 168.26) | track end (142.75, 167.26) F.Cu | B.Cu link between the via and a via near the track end |
| 18 | nRESET | track end (146.00, 151.42) B.Cu | via (146.00, 162.76) | B.Cu straight down, ~11 mm |
| 19 | USB_D− | track end (136.14, 173.45) F.Cu | U5 ball AD4 (148.25, 162.26) | route with #20 as a pair |
| 20 | USB_D+ | track end (136.14, 171.55) F.Cu | U5 ball AD6 (147.75, 162.26) | pair with #19; skew ≤ 1 mm |
| 21 | SWO | via (143.84, 161.74) | track end (144.73, 149.37) B.Cu | B.Cu, ~12 mm |
| 22 | UART_TX | U5 ball L1 (149.25, 165.76) | TP1 (152.05, 165.76) on B.Cu | via beside L1, then B.Cu to TP1 |
| 23 | UART_RX | U5 ball N1 (149.25, 165.26) | track end (151.91, 162.99) B.Cu | via beside N1, then B.Cu |
| 24–25 | GND | small F.Cu GND pour islands | – | fixed by the stitching pass afterwards (`scripts/stitch.py`); no action |

**When you're done,** save the board and say so. I'll then run only the finishing steps, which won't touch your tracks:
1. `stitch.py`: GND via fences and perimeter stitching.
2. `finish.py`: silkscreen and zone refill.
3. Final DRC, then `export_fab.py`.

Don't re-run `build_pcb.py`, `route.py`, `reroute.py` or `fanout.py`: they rebuild or replace the routing.
