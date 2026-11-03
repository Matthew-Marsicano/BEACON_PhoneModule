# FL1 replacement: 2.45 GHz LTCC band-pass filter stocked at LCSC/JLCPCB

**Recommendation: TDK DEA202450BT-1294D1-H, LCSC C1512913.**
- Footprint: `docs/proposed_footprints/TDK_DEA202450BT-1294D1-H_2012.kicad_mod`
- Runner-up: TDK DEA202450BT-2175A1-H (C76723). Use it if cellular rejection matters more than noise figure; see section 6.

The Johanson 2450BP08C0100001T currently in the design (FL1) is not stocked. **No** Johanson 2450BP variant has stock at LCSC or JLCPCB (section 2), so another manufacturer is needed.

Data was collected 2026-11-02:
- LCSC "RF Filters" catalog (catalogId 1176, all 3136 rows), from the `wmsc.lcsc.com/ftps/wm/product/query/list` catalog-listing endpoint.
- JLCPCB stock and Basic/Extended status, from the JLCPCB parts-library component-list endpoint.
- Datasheets, from the LCSC CDN copies.

Values marked "~" are my readings from the datasheet's typical plots. Everything else is a datasheet table value: typ / min (rejection) or typ / max (insertion loss).

---

## 1. Chosen part: TDK DEA202450BT-1294D1-H

| Item | Value |
|---|---|
| LCSC # | **C1512913** |
| Stock | LCSC 1965, JLCPCB 1969 (`canPresaleNumber` 1965). JLC minimum feed qty 5 |
| JLC library | **Extended** (not Basic, not Preferred), so the extended-part setup fee applies |
| Price (JLC) | $0.2183 (1-49), $0.1728 (50-149), $0.1533 (150-499), $0.129 (500+) |
| Package | 2.00 x 1.25 mm (EIA 0805), **T = 0.80 mm max**, 4 bottom-only terminals, MSL 1 |
| Insertion loss | **1.02 typ / 1.35 max** at 2412-2484 MHz, 25 C. **1.70 max** at -40 to +85 C. Plot markers: 0.91 dB at 2412, 1.02 dB at 2484, ~0.95 dB at 2400 |
| Return loss / VSWR | 22 typ / 10 min dB; VSWR 1.17 typ / 1.92 max (2412-2484). Plot: 22.9 dB at 2412, 27.5 dB at 2484 |
| Rejection at 1.9 GHz | ~14 dB (plot) |
| Rejection at 1608-1656 MHz | 23 typ / 20 min dB |
| Rejection at 2.2 GHz | ~4 dB (plot; the 3 dB point is at about 2235 MHz) |
| Rejection at 2.7 GHz | ~7-8 dB (plot; the 3 dB point is at about 2600 MHz) |
| Rejection at 4824-4968 MHz (2nd harmonic) | 30 typ / 20 min dB. Plot markers: 32.0 dB at 4824, 30.0 dB at 4968 |
| Rejection at 5628-5796 MHz (5 GHz Wi-Fi) | 27 typ / 20 min dB. Markers: 26.6 / 28.5 dB |
| Other rejection | 804-828 MHz: 42 / 30 min dB. 3216-3312 MHz: 49 / 30 min dB. 4020-4140 MHz: 52 / 40 min dB. 7200-7500 MHz: 44 / 35 min dB |
| Power handling | **1 W max** (+30 dBm). The +20 dBm leakage case is 10 dB below this |
| Impedance | 50 ohm in and out. **No external matching parts required** |
| Datasheet | TDK spec sheet Ver.1.0, Oct 2017, 9 pages, via LCSC: https://datasheet.lcsc.com/datasheet/pdf/21e478ccbe38ab150c1e4ae8c08eb514.pdf?productCode=C1512913 . Terminal table on p.2, specs on p.3, plots on p.4-5, recommended land pattern and evaluation board on p.6 |
| Lifecycle | Listed "Active" at Future Electronics. I found no TDK NRND/EOL notice for this P/N. Some sibling DEA parts are NRND, e.g. DEA162450BT-1288B1, which is flagged in its own datasheet |

**Why this part:**
- It is the only candidate that meets all of the following at once:
  - IL max <= 1.5 dB
  - Stock in the thousands
  - Height <= 1.0 mm
  - A datasheet that gives both a terminal table and a dimensioned land pattern
- Its skirts are much steeper than the other low-loss parts. The 3 dB bandwidth is about 2235-2600 MHz, against about 2200-2800 MHz for the Walsin and Megsine parts. That gives it the best 2.7 GHz rejection of the low-loss options.
- It is rated 1 W.

Its weaknesses:
- It gives modest close-in rejection: about 14 dB at 1.9 GHz and about 4 dB at 2.2 GHz.
- The guaranteed IL window is 2412-2484 MHz, not 2400-2483.5 MHz. The typical curve is flat down to 2400 MHz (~0.95 dB), but 2400-2412 MHz is not guaranteed.

**Noise figure.** The BPF sits before the LNA, so its loss adds directly. BPF loss of 1.0 dB typ (1.35 dB max) plus the QPL9547 at about 0.5 dB gives about 1.5 dB typ (1.85 dB max) at the LNA reference plane. The pi match and 100 pF DC-block losses come on top.

---

## 2. Johanson 2450BP family: nothing stocked

Every Johanson 2450BP code LCSC lists has **0** stock at both LCSC and JLC. JLC was queried for the starred codes; the rest show 0 at LCSC.

| MPN | LCSC # | LCSC / JLC stock | LCSC-listed IL |
|---|---|---|---|
| 2450BP08A0100001T * | C17268708 | 0 / 0 | 1 dB |
| 2450BP08A0100T * | C2651093 | 0 / 0 | 1 dB |
| 2450BP14D0100001T * | C17261146 | 0 / 0 | 1.7 dB |
| 2450BP14D0100T | C5493789 | 0 | 1.7 dB |
| 2450BP14E0100001T / 14F0100(001)T | C17505402 / C17473911 / C2651088 | 0 | 2.5-2.8 dB |
| 2450BP15E0100E * / 15E0100001E * | C2649319 / C17198472 | 0 / 0 | 1.5 dB |
| 2450BP15B100E / 15B0100001E / 15H0100001E / 15C / 15F / 15Q | C2649321 / C17665001 / C17496623 / C17666877 / C2662160 / C2662123 ... | 0 | 1.5-2.8 dB |
| 2450BP18C100CE / 18C0100E001E / 18C0100C001E | C2651098 / C17347471 / C17303950 | 0 | 2.5 dB |
| 2450BP39C/D... (2.5 x 2.0 mm, about 10 codes) | C2662125, C2651044, C2651059, C17564164, ... | 0 | 1.2-2.5 dB |
| 2450BP07A0100(001)T | C2651085 / C17346114 | 0 | 2.5 dB |

None of these can be bought, so I did not compare their datasheets.

Other families also had no usable stock:
- ACX: only BF1608-L2R4DAAT/LF (C42388012) is listed, with 0 stock.
- Yageo: BPF1608LM02R2400A (C412138), BPF1608LM03R2400A, BPF1005LM03R2400A and BPF2012LL03R2400A all have 0 stock.
- Taoglas LBP.2450.X.A/B/C.30: 0 stock.
- Abracon ADFC18-2450 has 0 stock and ADFC15-2450 has 8.
- Taiyo Yuden FI212B245027-T: 50 pcs at $1.15.
- Mini-Circuits BFCG-252+: 22 pcs at $4.30.

---

## 3. Stocked candidates compared

All are JLC **Extended**; none of them is Basic. "JLC" is JLCPCB assembly stock. Prices are JLC 1-piece prices, with the 100-piece price in brackets.

| MPN (maker) | LCSC # | LCSC / JLC stock | Price | IL in 2.40-2.50 GHz, typ / max (over temp) | 1.9 GHz | 2.2 GHz | 2.7 GHz | 4.8-5.0 GHz | Package, height, terminals | Power | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **DEA202450BT-1294D1-H** (TDK) | **C1512913** | 1965 / 1969 | $0.218 ($0.173) | **1.02 / 1.35 (1.70)**, specified 2412-2484 | ~14 (1608-1656: 23/20) | ~4 | ~7-8 | 30 / 20 | 2012, 0.80, 4 (1 IN, 2 GND, 3 OUT, 4 GND) | 1 W | **Chosen** |
| DEA202450BT-2175A1-H (TDK) | C76723 | 770 / 777 | $0.101 ($0.079) | 1.43 / **2.0** (plot ~1.25 at 2400, ~1.03 at 2480) | **40 / 34** (1710-1990) | **37 / 28** (2170) | ~2 (plot: IL 2.0 dB at about 2715) | 34.4 / 30 | 2012, 1.00, 3 (1 IN, 2 GND, 3 OUT) | not stated | Runner-up: best cellular rejection, IL max over budget |
| DEA202450BT-3030A1 (TDK) | C307660 | 240 / 243 | $0.182 | 1.0 / 1.3 (1.5) | 19 / 17 (1710-1990) | ~4-5 | ~0 (passband runs to about 3.0 GHz) | 35 / 30 | 2012, 1.00, 5 | 1 W | Low IL but no 2.7 GHz rejection; low stock |
| DEA142450BT-3028A1 (TDK) | C2651046 | 60 / 60 | $0.065 | 0.90 / 1.05 (1.25) | 20 / 17 (1710-1990) | n/r | n/r | 35 / 30 | 1.4 x 1.1, 0.60, 5 | n/s | Excellent IL, but only 60 pcs |
| DEA162450BT-1295A1 (TDK) | C695579 | 4045 / 4048 | $0.125 ($0.099) | 1.36 / 1.65 (1.95) | n/r (1608-1656: 21/19) | n/r | n/r | 45 / 40 | 0603, 0.60, 4 | n/s | IL max over budget |
| DEA162450BT-1288B1 (TDK) | C574022 | 430 / 436 | $0.108 | 1.03 / 1.3 (1.6) | n/r | n/r | n/r | 40 / 20 | 0603, 0.70, 3 | n/s | **NRND** per its datasheet |
| LFB212G45SG8A127 (Murata) | C341536 | 3765 / 3765 | $0.189 ($0.151) | max 1.50 (1.70) | ~ (10 min at 2.0 GHz) | n/r | n/r | 34 min | 2012, **1.05 max**, 4 | 500 mW | Too tall (> 1.0 mm). LCSC copy has no land pattern |
| LFB182G45SG9B740 (Murata) | C86154 | 7615 / 7616 | $0.150 ($0.118) | max 1.8 (2.1) | n/s | n/s | n/s | 34 min | 0603, 0.70, 4 | 500 mW | IL too high |
| RFBPF1606A10T (Walsin) | C51899377 | 3560 / 3561 | $0.030 | max **0.95 (1.10)** | ~11 | ~4 | **~2** | 30 min (plot ~45) | 0603, 0.65, 3 (1 IN, 2 GND, 3 OUT) | 3 W | Lowest IL and cheapest, but the passband is about 2.2-2.8 GHz, so it gives almost no 2.5-2.7 GHz rejection |
| RFBPF1608060AAT (Walsin) | C474007 | 3900 / 3908 | $0.073 | max 0.95 (1.25) | ~10 | ~4 | ~3 | 30 min | 0603, 0.65, 3 | 2 W | Same trade-off as the A10T |
| MBPF18M2450-N86 (Microgate) | C49274341 | 2030 / 2035 | $0.059 | max 1.8 (2.1) | 35 min (1710-1990) | ~30+ | ~2-3 | 25 min | 0603, 0.60, 4 | 2 W | IL too high; slow upper skirt |
| MLBF2450D16 (Megsine) | C52139904 | 900 / 900 | $0.073 | 0.8 / 1.25 | ~0 | ~0 | ~0 | 30 min | 0603, 3 | 2 W | **Reject.** The plotted passband is about 2.1-4.1 GHz, so it is effectively a high-pass |

n/r = not read from the plot; n/s = not specified.

The 5150-5950 MHz Walsin and CND-tek parts (RFBPF1608060K98Q1C, K88Q1C, KG8D1T, RFBPF1607K378D1T) matched my keyword search but are **5 GHz** filters, so they are not candidates.

**Physics note.**
- No LTCC part here rejects LTE B7/B41 at 2.5-2.6 GHz, which sits in or on every candidate's skirt. Rejecting it needs a SAW/BAW coexistence filter, at the cost of more insertion loss and therefore NF.
- The +20 dBm in-band CW leak cannot be filtered by any BPF either. Its handling stays with the LNA bypass/attenuation measures in `schematic_review.md` B1.

---

## 4. Pinout (top view) and the footprint mapping used

Source: datasheet p.2, "SHAPES AND DIMENSIONS".
- In the **Top view**, terminals are drawn dotted (seen through the body) and the dark marking square is over terminal (4).
- The **Bottom view** is the top view flipped top-to-bottom: (4) and (2) stay at the left and right ends, and (1) and (3) swap rows.

```
     TOP VIEW (marking up), KiCad 0 deg, +y = down the board

                     RX_BPF (from antenna / pi match)
                              |
      /---------------------- | ----------------------+
     /  +------+          +-------+          +------+ |
     |  |######|          |  (1)  | pad 1 IN  |      | |
     |  | (4)  |          +-------+          | (2)  | |
     |  | GND  |                             | GND  | |
     |  |pad 3 |          +-------+          |pad 2 | |
     |  |      |          |  (3)  | pad 4 OUT |      | |
     |  +------+          +-------+          +------+ |
     +----------------------- | ----------------------+
                              |
                     LNA_IN (to 100 pF DC block)

     ###### = TDK body marking (over terminal 4)
```

| TDK terminal | Function | Footprint pad | Position (mm) | Size (mm) |
|---|---|---|---|---|
| (1) | **Input** | **1** | (0, -0.325) | 0.35 x 0.35 |
| (3) | **Output** | **4** | (0, +0.325) | 0.35 x 0.35 |
| (2) | GND | 2 | (+0.65, 0) | 0.45 x 1.00, solid zone connection |
| (4) | GND (marking end) | 3 | (-0.65, 0) | 0.45 x 1.00, solid zone connection |

**Footprint mapping: 1 = IN, 4 = OUT, 2/3 = GND.** This follows the requested convention (pin 1 = IN, pin N = OUT, the rest GND). The datasheet's own numbering is 1 = IN, 3 = OUT, 2/4 = GND, so footprint pad 3 is TDK terminal (4) and footprint pad 4 is TDK terminal (3). This cross-reference is also written in the footprint `descr`.

**Symbol.**
- The existing `BEACON:2450BP08C0100001T` symbol has 1 = IN and 4 = OUT, so those pins line up with this footprint.
- It also has a 5th pin (pin 5, GND), which has no pad here. Either drop pin 5 or make a 4-pin `DEA202450BT-1294D1-H` symbol (1 IN, 2 GND, 3 GND, 4 OUT). I did not edit the library.

**Reversibility.**
- The land pattern is symmetric under a 180 deg rotation, and a passive LTCC filter is reciprocal (S21 = S12).
- However, TDK labels the ports Input and Output and characterises only that orientation. S11 and S22 are not guaranteed equal.
- Treat the part as **polarised**: marking at the left end (pad-3 side), IN up toward the antenna. Check the marking position in the JLC placement preview. A 180 deg error would still filter but would be off-spec.

**Port geometry, which differs from the Johanson part.**
- IN and OUT are on **opposite long sides**, across the 1.25 mm width, 0.30 mm apart edge to edge. They are not on the two ends.
- The GND terminals are the two ends.
- This suits the straight-down RX chain: place the part at 0 deg with its long axis horizontal (perpendicular to the RF line). Bring the RX_BPF line in from above into pad 1 and take LNA_IN out from below from pad 4, as on TDK's evaluation board (p.6).

---

## 5. Footprint `TDK_DEA202450BT-1294D1-H_2012.kicad_mod`

Land pattern source: datasheet p.6, "RECOMMENDED LAND PATTERN". I pixel-checked it at about 122 px/mm and all dimensions are consistent.
- **Horizontally:** GND land 0.45, gap 0.25, RF land 0.35, gap 0.25, GND land 0.45, for a total of 1.75 mm.
- **Vertically:** the GND lands are 1.00 tall. The RF lands are 0.35 tall with a 0.30 gap between them (0.35 + 0.30 + 0.35 = 1.00).
- **Package terminals (p.2):** GND terminals A1 0.40 x A2 0.95; RF terminals B1 0.30 x B2 0.30; C1 0.30; C2 0.35. Every land covers its terminal.

Pad table, read back with `pcbnew.FootprintLoad()` in KiCad 10.0.7 (4 pads; all SMD rectangles on F.Cu/F.Paste/F.Mask):

| Pad | Net role | X (mm) | Y (mm) | W x H (mm) | Zone connect |
|---|---|---|---|---|---|
| 1 | IN | 0.000 | -0.325 | 0.350 x 0.350 | inherit |
| 2 | GND | +0.650 | 0.000 | 0.450 x 1.000 | solid |
| 3 | GND | -0.650 | 0.000 | 0.450 x 1.000 | solid |
| 4 | OUT | 0.000 | +0.325 | 0.350 x 0.350 | inherit |

Minimum copper gaps are 0.25 mm (RF to GND) and 0.30 mm (pad 1 to pad 4).

Graphics:
- **F.Fab:** a 2.00 x 1.25 body outline with a 0.25 chamfer at the top-left (the IN / marking corner). A filled square marks TDK's marking over pad 3. Text labels: `IN`, `OUT`, `${REFERENCE}`.
- **F.SilkS:**
  - Outline at x = +/-1.07 and y = +/-0.76, with the same top-left chamfer.
  - The outline is broken at |x| < 0.40 on the top and bottom edges so it does not cross the 0.30/0.20 CPWG entries.
  - A filled pin-1 dot at (-0.62, -0.98), above and left of pad 1.
  - Silk clears all pads by 0.19 mm or more.
- **F.CrtYd:** a rectangle +/-1.25 x +/-0.875 (body + 0.25).
- I also plotted it with `kicad-cli fp export svg` to check visually.

The style matches the other files in this folder: version 20241229, generator pcbnew 10.0, a UUID on every item, and Datasheet and Description properties. Paste is 1:1 with the pads and mask uses the board default, since TDK does not specify a stencil.

---

## 6. Matching parts and layout notes

- **Matching: none.** The datasheet specifies 50 ohm nominal in and out, and the evaluation board (p.6) feeds the lands directly from 50 ohm lines with no shunt or series parts. Keep the existing antenna pi match; it matches the patch, not the filter. If you want a tuning option, a DNP 0402 shunt site on RX_BPF next to pad 1 is harmless, but the datasheet does not call for one.
- **Line entry:** the board's CPWG is W 0.30 / G 0.20 (`stackup_and_rules.md`). It enters the 0.35 mm RF lands with no taper needed. The GND lands sit 0.25 mm from the RF lands, so they form the CPWG ground right up to the pad.
- **Grounding:** TDK's evaluation board pours GND solidly over both end lands, with a row of about 3-4 through vias on each side flanking the lands. On this board:
  - Tie pads 2/3 into the L1 GND pour (the footprint sets solid zone connection).
  - Add at least 2 GND vias (0.50 / 0.30) per end, within about 0.5 mm of the lands.
  - Keep L2 solid GND under the whole part.
  - Poor end grounding is the usual way these filters lose their stop-band.
- **Isolation:** IN and OUT are only 0.30 mm apart. Do not route anything else between or near them, and keep the input and output lines straight and collinear (up and down), as on the evaluation board.
- **Power:** rated 1 W, against at most about +20 dBm of leakage, so there is margin.
- **If cellular rejection becomes the driver**, the runner-up is **TDK DEA202450BT-2175A1-H** (C76723, 770 in stock at JLC):
  - Rejection: 34 dB min at 1710-1990 MHz, 28 dB min at 2170 MHz, 30 dB min at 4.8-5.0 GHz.
  - It costs about 0.4 dB more typical IL (1.43 typ / 2.0 max), and it has essentially no 2.7 GHz rejection.
  - It is 2012, 1.00 mm max, with 3 terminals (1 IN, 2 GND, 3 OUT). **IN and OUT are on opposite ends** (along the 2.0 mm length) and the GND land is in the centre.
  - Land pattern (datasheet p.2): 0.275 / 0.25 / 0.60 / 0.25 / 0.275 mm across, 0.95 mm tall. It would need its own footprint.

---

## 7. Sources

- TDK DEA202450BT-1294D1-H spec sheet (via LCSC C1512913): https://datasheet.lcsc.com/datasheet/pdf/21e478ccbe38ab150c1e4ae8c08eb514.pdf?productCode=C1512913
- TDK DEA202450BT-2175A1-H: https://datasheet.lcsc.com/datasheet/pdf/32569ff8ee110c8d1568725b7d70c8c9.pdf?productCode=C76723
- TDK DEA202450BT-3030A1: https://datasheet.lcsc.com/datasheet/pdf/1114f027cf893086b2bacebf817c90e4.pdf?productCode=C307660
- TDK DEA142450BT-3028A1: https://datasheet.lcsc.com/datasheet/pdf/8f326bceee9638e4faf6eddbf048634e.pdf?productCode=C2651046
- TDK DEA162450BT-1295A1: https://datasheet.lcsc.com/datasheet/pdf/36f2df8159dbd9e41315a0e9a83a9336.pdf?productCode=C695579
- Murata LFB212G45SG8A127: https://datasheet.lcsc.com/datasheet/pdf/1bed5724a130c362c78c448607d7775f.pdf?productCode=C341536
- Murata LFB182G45SG9B740: https://datasheet.lcsc.com/datasheet/pdf/a46da49fbebea0b433695578a218abd2.pdf?productCode=C86154
- Walsin RFBPF1606A10T: https://datasheet.lcsc.com/datasheet/pdf/bddacaaee038e30c94326894affb7a74.pdf?productCode=C51899377
- Walsin RFBPF1608060AAT: https://datasheet.lcsc.com/datasheet/pdf/66fec45f2a2f6af8cf4f8112fb17a0b9.pdf?productCode=C474007
- Microgate MBPF18M2450-N86: https://datasheet.lcsc.com/datasheet/pdf/77f63cbf2a40aad785f42cb2cf99de47.pdf?productCode=C49274341
- Megsine MLBF2450D16: https://datasheet.lcsc.com/datasheet/pdf/559fba32798124bfcbb9c898e917a6f7.pdf?productCode=C52139904
- Lifecycle "Active" listing: https://futureelectronics.com/p/semiconductors--wireless-rf--rf-filters--band-pass/dea202450bt-1294d1-h-tdk-4153676
