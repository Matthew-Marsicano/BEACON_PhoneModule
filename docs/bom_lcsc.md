# BEACON Phone Module: JLCPCB assembly BOM with LCSC parts

Upload file: `docs/bom_lcsc.csv`. Its columns are `Comment, Designator, Footprint, LCSC Part #, MPN, Manufacturer, Basic/Extended, Stock, Notes`.
Source: `scripts/design.py`, exported as a grouped BOM with `kicad-cli sch export bom`. Stock and prices were checked on 2026-11-02.

## Summary

| | Count |
|---|---|
| BOM lines (after removing DNP, test points, Tag-Connect, mounting holes, PWR_FLAG) | **64** |
| Lines resolved to an LCSC part for JLC placement | **60** (130 placements per board) |
| - JLC Basic | 25 |
| - JLC Extended | **35**, including 3 "Preferred" extended (C12, C67, R38) |
| - Exact MPN or generic-spec match | 53 |
| - Flagged drop-in alternative or no-stock exact part | 7 (C67, FL2, L4, L7, L8, U4, Y2) |
| Lines to consign or hand-solder (LCSC # left blank) | **4** (AE1, FL1, J3, L1) |

Lines skipped as DNP or not in BOM: C31, C68 (C3_LF), L2, L3, L5, L9, R22, R23, R37. Also skipped: TP1-TP13, J2 (TC2030 Tag-Connect footprint), H1-H4 and all #FLG.

## Cost estimate: 5 assembled boards, parts only

The estimate uses LCSC ladder prices for 5 boards' worth of parts. Where LCSC sets a minimum order (typically 20-100 pcs for 0402 passives), the quantity is rounded up to it.

| Group | Cost (USD) |
|---|---|
| Basic parts (25 lines) | $11.70 |
| Extended parts (35 lines) | $234.55 |
| - of which the six ICs (LMX2582 $58.94, LT80602 $39.11, nRF52840 $38.71, QPL9547 $33.82, INA219 x2 $14.27, CC2595 $11.18) | $196.02 |
| **JLC-placed parts total** | **about $246** (about $231 without MOQ rounding) |
| Consigned parts at reference prices (AE1 $27.67, J3 $43.71, FL1 about $3.76, L1 about $7.50) | about $83 |
| **All parts, 5 boards** | **about $330, or about $66 per board** |

Not included:
- JLC feeder/setup fees: $3 per unique extended part. 32 extended lines at $3 is **about $96** (up to $105 if the 3 Preferred parts are also charged; JLC usually waives them on Economic PCBA). This is per order, not per board.
- JLC attrition extras, PCB fabrication, assembly/stencil fees, shipping and duties.
- The pre-order surcharge for FL2.

Prices are LCSC list prices and change daily. JLC's assembly price for the same C-number is usually equal or slightly lower.

## Extended parts (35 unique, $3 feeder fee each unless Preferred)

C9 18nF, C12 4.7pF (Pref), C26 47nF, C29 0.8pF, C30 0.5pF, C43 1.5pF, C66 820pF, C67 68nF (Pref), C69 3.3nF, D1, F1, FL2, J1, L4, L6, L7, L8, R3/R6 shunt, R9 37.4k, R10 634k, R24 3.32k, R29/R31 294R, R30 17.8R, R32 4.7R, R38 150R (Pref), SW1, U1, U2/U3, U4, U5, U6, U7, U8, Y1, Y2.

- **Values with no Basic equivalent at JLC:** R9, R10, R24, R29/31, R30, R32, C9, C26, C66, C69.
- **RF parts kept on the exact high-Q MPN on purpose:** C29, C30 and C43 use Murata GJM.
- **Possible savings:** move the loop-filter/RF values to E12/E24 Basic parts. Example: C43 could use C1552 FH 1.5pF (Preferred). This would remove a few feeder fees but needs a design review.

## Consign or hand-solder (LCSC # left blank in the CSV)

| Ref | Part | Reason |
|---|---|---|
| AE1 | Taoglas WDP.2458.25.4.B.02 patch | Hand-assembled by design: taped to the board top, pin soldered from the bottom. LCSC C6326031 is listed with 0 stock. |
| J3 | Cinch/Bel 142-0711-821 edge-launch SMA | Flange sits in the board notch, so solder by hand. LCSC C3174138 is listed with 0 stock. |
| FL1 | Johanson 2450BP08C0100001T BPF | Not on LCSC. LCSC only lists the 2450BP08**A** variant (C17268708, 0 stock). Buy from DigiKey/Mouser and consign or hand-solder. |
| L1 | Wurth 74438357056 5.6uH (MAPI-4030) | Not on LCSC. No stocked 4x4 5.6uH part meets Isat >= 3 A. Closest: C5224561 ABRACON ASPI-4030S-5R6M-T (Isat 2.6 A, check pads); see the CSV note. |

**Also likely hand-fed:** FL2 (2450LP07C0100001T, C17630068). The exact part is listed at LCSC but has 0 stock. Pre-order it into your JLC parts inventory; otherwise consign it or hand-solder.

## Flagged alternatives (check before ordering)

| Ref | Design part | BOM part (LCSC) | Difference |
|---|---|---|---|
| U4 | LT80602AFOA/VY+T | LT80602AFO+ (C54448890) | Same die and FC2QFN-17 3x3 package, without the /VY+T suffix (automotive screening, T&R). |
| Y2 | TG2520SMN 26.0000M-ECGNNM3 (C20844969, 0 stock) | Epson X1G0054210204 (C7527389), TG2520SMN-family 26 MHz | Check supply voltage (3.3 V), clipped-sine output and ppm grade in the Epson datasheet. |
| L4 | LQP15MN4N7B02D (C23769, 0 stock) | LQG15HS4N7B02D (C162543) | Same 4.7nH +/-0.1nH, but multilayer instead of thin-film (slightly lower Q). Thin-film alternative: C1330427 ATFC-0402-4N7B-T. |
| L8 | LQP15MN1N2B02D (C77117, 0 stock / obsolete) | LQG15HS1N2B02D (C488336) | Same 1.2nH +/-0.1nH, multilayer, 1 A. |
| L7 | LQW15AN12NJ00D (C82920, 0 stock) | LQW15AN12NG00D (C86128) | Same part with +/-2% tolerance. |
| C67 | 68nF 0603 "C0G preferred" | CL10B683KB8NNNC X7R 50V (C31658) | No 68nF C0G in 0603 is stocked. |
| FL2 | 2450LP07C0100001T | Same, C17630068 | 0 stock, so pre-order or consign. |

## Low-stock watch list (reserve or order early)

| Ref | Part | LCSC stock |
|---|---|---|
| U7 | CC2595RGTR | 10 |
| D1 | SZSMF6.0AT1G | 20 |
| Y1 | ABM11W-32.0000MHZ-8-B1U-T3 | 44 |
| U8 | LMX2582RHAR | 47 |
| L6 | 0402CS-18NXGRW | 49 |
| F1 | NANOSMDC075F-2 | 415 |
| J1 | USB4105-GF-A | 465 |
| U4 | LT80602AFO+ | 656 |

## Passive selection rules applied

- **Capacitor voltage ratings:** 16 V or more everywhere; 25 V on the 1uF and 10uF lines, which include 5V_BUS/5V0/LNA_VCC caps.
- **Capacitor dielectrics:** X5R/X7R for bulk and decoupling. C0G/NP0 for everything up to 1 nF, plus the 0.5/0.8/1.5/12/22/100/820 pF and 3.3 nF RF/loop-filter caps.
- **Resistors:** 1% thick film; JLC Basic parts (UNI-ROYAL 0402WGF/0603WAF) wherever the value exists.
- **Schematic data issue:** the D2 Manufacturer field should be **Hubei KENTO**. KT-0603R is not a Kingbright part.

## Method and data sources

- **Parametric search:** the jlcsearch community API parametric endpoints (`/resistors/list.json`, `/capacitors/list.json`) supplied the passives, with JLC stock and Basic/Preferred flags.
- **Exact C-code checks:** the jlcsearch `/api/search` keyword search returned unrelated results for MPN queries on 2026-11-02, so it was used only for exact C-code lookups.
- **Finding ICs and RF parts:** looked up by MPN through the normal lcsc.com search page in a browser (non-essential cookies declined) and through web search. Each C-code was then checked with LCSC's product-detail endpoint (`wmsc.lcsc.com/ftps/wm/product/detail`) for MPN, manufacturer, package, LCSC stock and price ladder.
- **"JLC n/a" in the Stock column:** jlcsearch had no JLC assembly stock figure for that code; the LCSC figure is shown instead. Confirm in the JLC BOM matcher at upload.
