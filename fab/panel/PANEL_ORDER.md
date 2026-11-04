# BEACON panel: phone module + wearable on one JLCPCB order

One 100 x 92.45 mm, 4-layer panel holding one phone module (55 x 78.45 mm) and one wearable
(30 x 30 mm). Both boards share one set of board fees (4-layer, ENIG, epoxy-filled vias, impedance),
one assembly setup and one shipment, and the 16 parts used on both boards are charged one
Extended-part fee each instead of two.

Built at the Gerber level from each board's released fab files, so neither design changed:
phone module `fab/gerbers` (KiCad) and wearable `fab/wearable/gerbers` (Altium, commit `66d48ca`).
`scripts/build_panel.py` rebuilds the Gerbers and drills (needs `gerbonara` and `shapely`),
`scripts/build_panel_bom.py` rebuilds the BOM and CPL.

## Layout

| Item | Value |
|---|---|
| Panel | 100 x 92.45 mm, origin at the bottom-left corner |
| Phone module | origin at (6.5, 7.0) |
| Wearable | origin at (63.5, 31.225) |
| Rails | 5 mm top and bottom, 4.5 mm side frames |
| Separation | 2 mm milled slots, 11 tabs 3 mm wide, each with 4 x 0.5 mm mouse-bite holes on the board edge. No part within 3 mm of a tab |
| Fiducials | 3 per side on the rails, 1.0 mm copper with a 2.0 mm mask opening, at (10, 2.5), (90, 2.5), (10, 89.95) |

## Files to upload

| Step on jlcpcb.com | File in `fab/panel/` |
|---|---|
| 1. Add Gerber file | `BEACON_Panel_gerbers.zip` (upload as is) |
| 2. PCB Assembly: BOM | `BEACON_Panel_BOM_JLC.csv` |
| 3. PCB Assembly: CPL | `BEACON_Panel_CPL_JLC.csv` |

After step 1, JLC should show **4 layers, 100 x 92.45 mm**. Designators carry a board suffix:
`_P` phone module, `_W` wearable (the silkscreen still shows the plain names).

## PCB options

| Option | Setting |
|---|---|
| Delivery format | **Panel by Customer** |
| Different design in panel | **2** |
| PCB Qty | number of panels (5 panels = 5 phone modules + 5 wearables) |
| Thickness | **1.6 mm** (the phone module and its enclosure are designed for it; the wearable gets thicker). 0.8 mm also works electrically |
| Impedance control | Yes. JLC04161H-7628 for 1.6 mm (JLC04081H-7628 for 0.8 mm). Both have the same 0.2104 mm 7628 L1-L2 dielectric, so the 50 ohm traces on both boards hold either way |
| Via covering | **Epoxy filled & capped (POFV): required** for both boards (via-in-pad on the nRF52840s, exposed pads, U.FL ground pads) |
| Min via hole / diameter | 0.15 mm / 0.25 mm |
| Surface finish | ENIG |
| Outer / inner copper | 1 oz / 0.5 oz |
| Mark on PCB | Specify a location on a rail, or remove |

## Assembly

| Item | What to do |
|---|---|
| Type | Standard PCBA, **both sides** (phone module top only, wearable both sides) |
| PCBA Qty | number of panels to assemble (each panel = 1 phone module + 1 wearable) |
| Tooling holes | Added by JLCPCB (on the 5 mm rails) |
| Already swapped for JLC stock | B1_W -> SN74AUP2G04DCKR (C2865392), L3_W -> Sunlord WPN4012H220MT (C370621) |
| No LCSC part | AE1_P (Taoglas patch antenna), J3_P (U.FL): consign or hand-solder |
| Short or no JLC stock | B2_W GRF6011, U1_W AEM30940, U2-U4_W HMC190B (pre-order, consign or hand-solder); U6_W MAXM86161 and D1_W SMS7630 (low stock, reserve) |
| J1_W | Through-hole: THT assembly or hand solder |
| Placement preview | Check pin 1 and rotation per the two boards' own order sheets (`fab/JLCPCB_ORDER.md`, `fab/wearable/JLCPCB_ORDER.md`) |

## After delivery

Snap each board out at the tabs and sand the nubs flat, especially on the wearable's edges.

## Known issues

- The wearable's copper pours reach its board edge on all four layers, so its mouse-bite holes and
  routed edge cut through plane copper. Expect a DFM comment.
