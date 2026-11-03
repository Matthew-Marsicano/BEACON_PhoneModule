# LMX2582 loop filter and register plan: 2.4 GHz CW carrier

Source: TI SNAS680E (LMX2582, rev. Aug 2022). Table, figure and register references below point to that document.
The loop-filter, noise, register and channel-plan calculations were done in plain-Python working scripts (not in this repository).

## 1. Recommendation

| Item | Value |
|---|---|
| Reference | 26 MHz TCXO, OSC_2X = 1 → **Fpd = 52 MHz** (R_PRE = 1, MULT = 1 bypass, R = 1) |
| VCO / output | 4800–4967 MHz, CHDIV = 2 (SEG1 ÷2), PLL_N_PRE = 2, Fout = 52·(N + NUM/52) MHz |
| N range | N = 46–47 (MASH 3rd order needs N ≥ 18, Table 7-2) |
| Charge pump | CP_IUP = CP_IDN = 31 (4.844 mA) × CP_ICOARSE = 2 (×1.5) = **7.27 mA** |
| Kvco used | 34 MHz/V (Table 7-3 interpolated: 4700 → 33, 5200 → 36 MHz/V) |
| **C1_LF** | **820 pF** C0G, 0402 (CPout node) |
| **R2_LF** | **150 Ω** 1 % |
| **C2_LF** | **68 nF** (C0G preferred, X7R ≥ 25 V acceptable, see §4.6) |
| **R3_LF** | **22 Ω** 1 % |
| **C3_LF** | **DNP** (keep the footprint) |
| **R4_LF** | **0 Ω** |
| **C4_LF** | **3.3 nF** C0G, 0402, at the Vtune pin (35), returned to VCO GND (pin 34) |
| Loop BW (open-loop 0 dB crossover) | **59.4 kHz** (closed-loop −3 dB ≈ 90 kHz) |
| Phase margin | **61.6°** (peak phase sits at crossover; gain margin ≈ 46 dB) |
| Lock (analog only, 4 MHz VCO step → 1 kHz) | ≈ 54 µs (plus VCO calibration time, see §5.6) |

Filter order: the 4th-order footprint is kept, but the optimum here is **3rd order** (C3 DNP, R4 = 0, so R3 and C4 form the third pole at 2.2 MHz). §4.3 explains why a populated C3 does not help once ≥ 3.3 nF has to sit on Vtune.

**I did not meet the 100–200 kHz loop-bandwidth target, and that is deliberate.** With ≥ 3.3 nF on Vtune and the loop gain this part can reach from a 26 MHz reference, the widest loop at 60–65° phase margin is about 65 kHz (§4.2). A 150 kHz loop needs C4 ≈ 1 nF and 12 mA. It also has 6–14 dB worse phase noise at 1–5 MHz offsets, which is the tag band (§4.7). The 60 kHz design also sits near the noise-optimal bandwidth (§4.5).

## 2. Datasheet data used

| Parameter | Value | Where |
|---|---|---|
| VCO range | 3.55–7.1 GHz, 7 cores; Vtune 0–2.5 V (0 V = max f) | §7.3.5 |
| kVCO | 3700: 28, 4200: 30, **4700: 33, 5200: 36** MHz/V, 5700: 41, 6200: 47, 6800: 51 | Table 7-3 |
| Charge pump | 0–12 mA. CP_IUP/CP_IDN 5-bit fields, any combination: bit4 1.25, bit3 2.5, bit2 0.625, bit1 0.312, bit0 0.156 mA (4.844 mA all set). CP_ICOARSE: 0 ×1, 1 ×2, 2 ×1.5, 3 ×2.5. TI recommends ICOARSE only 0 or 2 for lock-detect accuracy over temperature. | §6.5, Table 7-16 (R14) |
| PFD | 5–200 MHz normal (dual PFD); 0.25–5 MHz needs FCAL_LPFD_ADJ, PLL_N_PRE = 4; 200–400 MHz integer-only, PFD_CTL = 3 | §6.5, §7.3.3 |
| OSCin | 5–1400 MHz, 0.2–2 Vpp single-ended, must be AC-coupled | §6.5 note 3 |
| Doubler | in 5–200, out 10–400 MHz; needs 50 % duty cycle; do not combine with MULT | Table 7-1, §7.3.2 |
| Pre-R | in 10–1400, out 5–700 MHz | Table 7-1 |
| MULT | in 40–70 MHz, out 180–250 MHz (a 26 MHz input cannot use it without the doubler, which TI says not to combine) | Table 7-1, R10 |
| Post-R | in 5–250, out 0.25–125 MHz | Table 7-1 |
| Min N (fractional) | integer 9, MASH1 11, MASH2 16, **MASH3 18**, MASH4 30; PFD_DLY_SEL 1/1/2/**2**/8 | Table 7-2 |
| Fvco equation | Fvco = Fpd × PLL_N_PRE × (PLL_N + NUM/DEN) | §7.3.4 |
| Channel divider | ÷2 = SEG1 ÷2, total 2, VCO 3550–7100 allowed | Table 7-4 |
| PLL noise | PLL_FOM −231 dBc/Hz, flicker_norm −126 dBc/Hz | §6.5 |
| VCO open loop | 1.8 GHz out: −99.5/−123.6/−144.5/−157.2 at 10k/100k/1M/10M; 5.5 GHz: −89.7/−114.0/−134.9/−151.3 | §6.5 |
| Vtune capacitor | "Connect a 3.3-nF or more capacitor to VCO ground". Less shunt C at Vtune degrades VCO noise at 100 kHz–1 MHz. | pin table, §8.1.10 |
| Internal Vtune capacitance | **Not specified** in SNAS680E. I treated the external C as dominant. | — |
| Loop filter guidance | TI points to PLLatinum Sim. The Table 8-4 example (C1 4.7 nF / C2 100 nF / R2 68 Ω) is for Fpd 200 MHz and is where the schematic placeholders came from. | §8.1.10, Table 8-4 |
| Output power | 50 Ω pull-ups, single-ended: Fig 6-13 (5.4 GHz) ≈ 0 dBm at code 3, +1 at 4, +2.3 at 6, +3.4 at 8, +4.4 at 10, +5.2 at 12, +6.7 at 16, +7.9 at 20, saturates ≈ +9 at code 30. Fig 6-12 shows ≈ +1 dB more at 2.4 GHz than at 5.4 GHz. OUTx_POW valid codes 0–31 and 48–63. | Fig 6-12, 6-13, R46 |
| Lock / cal time | 590 µs typical default cal (7 GHz); ~20 µs possible with FCAL_FAST/ACAL_FAST and a 200 MHz cal clock | §8.1.8 |

Model check: the Table 8-4 filter at Fpd 200 MHz and 12 mA gives 183 kHz / 63° in my model, close to TI's stated 210 kHz / 70°.

The schematic placeholders are **not usable** at this loop gain. With Fpd 52 MHz and 7.27 mA they give fc = 31 kHz and PM = 46°. At Fpd 26 MHz they give 15 kHz and 30°.

## 3. Frequency plan

* **PFD choice: 52 MHz (OSC_2X = 1).** The MULT cannot be used, because its 40–70 MHz input means doubler + MULT, which TI discourages. That leaves 26 or 52 MHz. 52 MHz halves N (94 → 47 at the VCO/PFD level), so loop gain per mA doubles. That decides it, because the bandwidth is limited by the 3.3 nF Vtune cap (§4.2). PLL flat noise also improves by 3 dB: −117.4 → −120.4 dBc/Hz at 2.45 GHz.
  Risk: the doubler needs 50 % duty cycle. A clipped-sine TCXO into an AC-coupled differential buffer is usually close to 50 %, but a duty error appears as a 26 MHz-offset spur. Fallback: OSC_2X = 0 (§5.5).
* Fout = Fvco/2 = Fpd × (N + NUM/DEN). With **DEN = 52**, NUM steps are exactly **1 MHz**. For 500 kHz steps (for example 2483.5 MHz), use DEN = 104.
  `N = floor(Fout_MHz / 52)`, `NUM = Fout_MHz − 52·N`.
  2400 → N 46 / NUM 8. 2405 → 46/13. 2418 → 46/26. 2444 → 47/0. 2450 → 47/6. 2483 → 47/39.
* Minimum step resolution with DEN = 52: Fpd·PLL_N_PRE/DEN/CHDIV = 52·2/52/2 = 1 MHz (§7.3.4).

### 3.1 Spurs and the 1–10 MHz tag band

Because the TCXO is 26 MHz and Fvco = 2·Fout, these deterministic spur families (Table 8-1) land at these offsets:

* integer boundary (IBS): distance from Fout to the nearest multiple of 52 MHz
* fOUT % fOSC: distance from Fout to the nearest multiple of 26 MHz
* fVCO % fOSC: 2 × the distance from Fout to the nearest multiple of 13 MHz

Every channel **except the multiples of 13 MHz** has at least one of these families at a 1–10 MHz offset:

**Spur-clean channels: 2405, 2418, 2431, 2444, 2457, 2470, 2483 MHz.** On these the mixing products fall on the carrier or at ≥ 13 MHz. 2444 is integer-N (NUM = 0).

Other channels work, but their IBS is attenuated only by the loop: −37 dB at 1 MHz, −49 dB at 2 MHz, −65 dB at 5 MHz below the in-band level (§4.4). The fOSC mixing spurs depend on coupling and layout. Measure them before using such a channel for backscatter reads. Primary fractional spurs sit at 52/q MHz (q = reduced denominator of NUM/52), so with DEN = 52 they are always at whole-MHz offsets.

## 4. Loop filter design

### 4.1 Loop gain

K = Icp·Kvco/Ntot, with Ntot = Fvco/Fpd = 4900/52 = 94.23 (PLL_N_PRE included).
K = 7.266 mA × 34 MHz/V / 94.23 = **2622 A·Hz/V**.
Open loop G(s) = K·Z(s)/s, where Z(s) = Vtune/Icp is the transimpedance of the full network. Equivalently, G(s) = Kφ·Kv·Z/(N·s) with Kφ = Icp/2π A/rad and Kv = 2π·Kvco rad/s/V.

### 4.2 Starting point (Banerjee, 2nd-order passive, γ = 1)

Target fc = 60 kHz, φ = 62°, ωc = 2π·60k = 3.770e5 rad/s.

1. T1 = (sec φ − tan φ)/ωc = (2.130 − 1.881)/ωc = **0.661 µs**
2. T2 = 1/(ωc²·T1) = **10.64 µs**
3. A0 = C1+C2 = (K/ωc²)·√[(1+ωc²T2²)/(1+ωc²T1²)] = 1.845e-8 × 4.011 = **74.0 nF**
4. C1 = A0·T1/T2 = **4.60 nF**, C2 = A0 − C1 = **69.4 nF**, R2 = T2/C2 = **153 Ω**

This gives exactly 60.0 kHz / 62.0°. The key number is C1 = 4.6 nF of shunt capacitance in total. At least 3.3 nF of it must sit on Vtune, so the Vtune cap is **most of C1**.

The limit follows from this. Shunt C ≈ (sec φ − tan φ)·K/ωc² must be ≥ 3.3 nF, so for a given K and PM the bandwidth has a ceiling. From a numerical sweep with the full network and C4 = 3.3 nF:

| Icp, Fpd | max fc at PM 65° | max fc at PM 55–58° |
|---|---|---|
| 7.27 mA, 52 MHz | ≈ 66 kHz | ≈ 78 kHz |
| 12.1 mA (ICOARSE = 3), 52 MHz | ≈ 86 kHz | ≈ 100 kHz |
| 7.27 mA, 26 MHz | ≈ 47 kHz | ≈ 55 kHz |

So 100–200 kHz at 60–70° is not possible with C4 ≥ 3.3 nF.

### 4.3 Moving to the 3rd/4th-order network

At 60 kHz, C3/C4 behind small R3/R4 look like part of C1. I solved the full network numerically (Nelder-Mead on log-component values). Constraints: |G(jωc)| = 1, PM = target, dφ/dω = 0 at ωc (peak phase at crossover). The free degree of freedom was traded for attenuation at 1–2 MHz.

* With C4 fixed at 3.3 nF, the optimizer always drives **C3 → 0**. Any capacitance at LF3 just adds to the shunt total that is already too large. So C3 = DNP and R4 = 0, and R3 plus C4 form the extra pole.
* Sweeping R3 (C1, C2, R2 re-solved for 60 kHz / 62° each time):

| R3 | C1 | C2 | R2 | \|G\| at 1 MHz | \|G\| at 5 MHz |
|---|---|---|---|---|---|
| 0 Ω | 1.30 nF | 69.4 nF | 153 | −37.1 dB | −64.8 dB |
| 10 Ω | 1.08 nF | 69.6 nF | 153 | −37.0 | −64.9 |
| **22 Ω** | **0.81 nF** | **69.9 nF** | **152** | −36.9 | −65.3 |
| 47 Ω | 0.26 nF | 70.4 nF | 151 | −36.9 | −65.0 |
| ≥ 68 Ω | needs C1 → 0; no exact solution | | | | |

R3 = 22 Ω keeps a real C1 at CPout to absorb charge-pump current pulses, and it isolates the Vtune node a little (R3·C4 pole at 2.2 MHz). Any value from 10 to 47 Ω works.

### 4.4 Rounded values and re-check

Values: C1 820 pF (E12), C2 68 nF (E12), R2 150 Ω (E24), R3 22 Ω (E24), C3 DNP, R4 0 Ω, C4 3.3 nF (E12).

| Case | fc | PM |
|---|---|---|
| Ideal (0.81n / 69.9n / 152 / 22 / 3.3n) | 60.0 kHz | 62.0° |
| **Rounded, 4.9 GHz, Kvco 34** | **59.4 kHz** | **61.6°** |
| Rounded, 4.800 GHz (Kvco 33.6, N 92.3) | 59.8 kHz | 61.6° |
| Rounded, 4.967 GHz (Kvco 34.6, N 95.5) | 59.6 kHz | 61.6° |
| Kvco·Icp × 0.75 (process) | 46.0 kHz | 60.6° |
| Kvco·Icp × 1.25 | 72.5 kHz | 61.3° |
| All C −5 %, R +1 % | 60.1 kHz | 61.6° |
| All C +5 %, R −1 % | 58.6 kHz | 61.6° |

The phase-margin peak stays at about 61.6° in every case, so the design is robust. Only fc moves, roughly with √(Kvco·Icp).

Open-loop Bode plot, rounded values:

| f | \|G\| | ∠G | \|closed loop\| |
|---|---|---|---|
| 10 kHz | +20.8 dB | −149.7° | +0.7 dB |
| 30 kHz | +6.9 | −124.5 | +1.6 (peaking max 1.6 dB at 26 kHz) |
| 59.4 kHz | 0.0 | −118.4 | −0.2 |
| 100 kHz | −5.1 | −121.2 | −3.8 |
| 200 kHz | −12.7 | −134.2 | −11.4 |
| 500 kHz | −25.6 | −157.7 | −25.1 |
| 1 MHz | −36.9 | −171.6 | −36.8 |
| 2.2 MHz | −50.5 | +175.7 | −50.5 |
| 5 MHz | −65.3 | | −65.3 |
| 10 MHz | −78.9 | | −78.9 |
| 26 MHz (fOSC) | −100.8 | | −100.8 |
| 52 MHz (Fpd) | −118.2 | | −118.2 |

Zero at 15.6 kHz (R2C2). Phase crossover at about 1.7 MHz, gain margin about 46 dB.

### 4.5 Phase-noise estimate at 2.45 GHz output (model, excludes the TCXO)

Inputs to the model:

* VCO open-loop, interpolated from §6.5 and scaled to Fvco 4.9 GHz ÷2: −96.7 / −121 / −142 / −156 dBc/Hz at 10k / 100k / 1M / 10M.
* PLL flat and flicker from PLL_FOM and flicker_norm (§6.5, §8.1.9), −6 dB for CHDIV.
* Ideal MASH quantization noise, (2π)²/(12·Fpd)·|2 sin(πf/Fpd)|^(2(m−1)), with PLL_N_PRE² and 1/CHDIV².

Results, MASH 3rd order:

| Offset | 10 kHz | 30 kHz | 100 kHz | 300 kHz | 1 MHz | 2 MHz | 5 MHz | 10 MHz |
|---|---|---|---|---|---|---|---|---|
| Total (dBc/Hz) | −113 | −112 | −118 | −129 | −141 | −144 | −147 | −150 |

Integrated 1 kHz–20 MHz: about 1.07 mrad rms (69 fs). MASH 2 is worse: −130 at 1 MHz, about 102 fs. **Keep MASH_ORDER = 3.**

The VCO and PLL in-band curves cross at about 85 kHz, so 60 kHz open loop (≈ 90 kHz closed-loop −3 dB) is close to the noise optimum.

TCXO: Epson specifies −161 dBc/Hz at 100 kHz for the 26 MHz part. Scaled by 20·log(2441/26) = +39.5 dB, that is −121.5 dBc/Hz, comparable to the PLL floor. Its close-in noise (1–10 kHz) is not verified and may dominate inside the loop.

### 4.6 Components and layout

* C1 and C4: C0G/NP0, 0402, 50 V. Place C4 right at pin 35 (Vtune) with its ground via to VCO ground (pin 34 side), as §8.1.10 asks.
* C2 = 68 nF: prefer C0G (0805/1206). X7R ≥ 25 V is acceptable, since Vtune ≤ 2.5 V means little DC-bias loss and ±10 % moves fc by < 2 % (§4.4). But X7R dielectric absorption and microphonics slow the final ppm-level settling. Use C0G if lock time matters.
* R2/R3: thin film, 1 %, 0402.
* C3: leave the footprint DNP. R4: 0 Ω. Both are available for later tuning.
* Keep CPout (pin 12) to Vtune (pin 35) short and away from SPI and digital lines (§8.4.1).

### 4.7 Wider-bandwidth alternative (not recommended)

For about 150 kHz at 60° PM you need **Icp 12.1 mA (ICOARSE = 3, which TI warns against for lock-detect accuracy) and C4 = 1.0 nF**, below the 3.3 nF guidance. Rounded values: C1 270 pF, C2 18 nF, R2 240 Ω, R3 10 Ω, C4 1.0 nF → 154 kHz / 60.6°.

Lock time improves to about 24 µs, versus 54 µs. But the model gives −133 dBc/Hz at 1 MHz and at 5 MHz, versus −141 / −147, because ΣΔ noise is less filtered. VCO noise at 100 kHz–1 MHz also degrades by an unknown amount from the smaller Vtune C. That is the wrong trade for a backscatter reader whose tags sit at 1–10 MHz.

## 5. Register plan

Programming word = [R/W(1)=0][ADDR(7)][DATA(16)], MSB first, CSB-latched (§7.5). The field addresses below come from Figure 7-5 and Tables 7-5 to 7-49. Fixed bits are copied from Figure 7-5. Several reconstructed words match well-known defaults (R0 0x00221C, R7 0x0728B2, R9 0x090302 with doubler off, R10 0x0A10D8, R19 0x130965 …).

### 5.1 Key fields

| Field | Reg[bits] | Value | Reason / citation |
|---|---|---|---|
| OSC_2X | R9[11] | 1 | Fpd = 52 MHz (Table 7-11) |
| REF_EN | R9[9] | 1 | |
| PLL_R_PRE | R12[11:0] | 1 | bypass (Table 7-14) |
| MULT | R10[11:7] | 1 | bypass; 26 MHz is outside 40–70 MHz (Table 7-12, 7-1) |
| PLL_R | R11[11:4] | 1 | (Table 7-13) |
| PFD_CTL | R13[1:0] | 0 | dual PFD, Fpd < 200 MHz (Table 7-15) |
| FCAL_HPFD_ADJ / FCAL_LPFD_ADJ | R0[8:7] / R0[6:5] | 0 / 0 | 10 MHz ≤ Fpd ≤ 100 MHz (Table 7-5) |
| CP_IDN / CP_IUP | R14[11:7] / R14[6:2] | 31 / 31 | 4.844 mA; must be equal (Table 7-16) |
| CP_ICOARSE | R14[1:0] | 2 (×1.5) | 7.27 mA; 0 or 2 recommended for lock-detect accuracy |
| PLL_N_PRE | R37[12] | 0 (÷2) | better fractional performance (§7.3.4) |
| PLL_N | R38[12:1] | 46 or 47 | N = floor(Fout/52) |
| PLL_DEN | R40[15:0] (MSB), R41[15:0] (LSB) | 52 | 1 MHz steps (104 for 500 kHz) |
| PLL_NUM | R44 (MSB), R45 (LSB) | Fout − 52·N | |
| MASH_ORDER | R46[2:0] | 3 | N ≥ 18 (Table 7-2); best noise in §4.5 |
| PFD_DLY | R39[13:8] | 2 | Table 7-2 recommendation for MASH 3 |
| MASH_SEED / MASH_DITHER | R42/R43, R30[10] | 0 / 0 | change only to fight sub-fractional spurs |
| VTUNE_ADJ | R30[7:6] | 0 | fVCO < 6500 MHz (Table 7-25) |
| CHDIV_EN | R34[5] | 1 | |
| CHDIV_SEG1 / SEG1_EN | R35[2] / R35[1] | 0 (÷2) / 1 | Table 7-30, 7-4 |
| CHDIV_SEG2_EN / SEG3_EN | R35[7] / R35[8] | 0 / 0 | power down unused segments |
| CHDIV_SEG_SEL | R36[6:4] | 1 | segment 1 only |
| CHDIV_DISTA_EN / CHDIV_DISTB_EN | R36[10] / R36[11] | 1 / 0 | |
| CHDIV_DIST_PD | R31[7] | 0 | |
| VCO_DISTA_PD / VCO_DISTB_PD | R31[9] / R31[10] | 1 / 1 | the direct VCO path is unused |
| OUTA_MUX | R47[12:11] | 0 | channel-divider output (Table 7-42) |
| OUTA_PD | R46[6] | 0 | |
| OUTA_POW | R46[13:8] | 3 (start) | see §5.4 |
| OUTB_PD | R46[7] | 1 | RFoutB unused |
| OUTB_POW / OUTB_MUX | R47[5:0] / R48[1:0] | 0 / 0 | don't care |
| LD_EN | R0[13] | 1 | |
| MUXOUT_SEL | R0[2] | 1 | lock detect on MUXout (0 = SPI readback) |
| LD_TYPE | R61[0] | 1 | Vtune lock detect (0 = calibration-done status) |
| MUXOUT_HDRV | R59[5] | 0 | 1 for ~3 mA drive on a long trace |
| CAL_CLK_DIV | R1[2:0] | 0 | cal clock = OSCin = 26 MHz (< 200 MHz, Table 7-6) |
| ACAL_CMP_DLY | R4[15:8] | 5 | rule 2·N·Tcal > 200 ns: 2·5·38.5 ns = 385 ns (Table 7-8) |
| FCAL_FAST / ACAL_FAST | R64[8] / R64[9] | 0 / 0 initially | try 1/1 once basic lock works (§8.1.8) |

### 5.2 Full start-up sequence, Fout = 2450 MHz (N 47, NUM 6, DEN 52, OUTA_POW 3)

Per §7.5.1:

1. Power up.
2. Make sure the TCXO is running.
3. Write `R0 = 0x002216` (RESET = 1).
4. Write R64 down to R1 as below.
5. Write `R0 = 0x00221C` (FCAL_EN = 1, which calibrates and locks).

```
R64 0x40007F   R62 0x3E0000   R61 0x3D0001   R59 0x3B0000   R48 0x3003FC
R47 0x2F00C0   R46 0x2E03A3   R45 0x2D0006   R44 0x2C0000   R43 0x2B0000
R42 0x2A0000   R41 0x290034   R40 0x280000   R39 0x278204   R38 0x26005E
R37 0x254000   R36 0x240411   R35 0x23021B   R34 0x22C3EA   R33 0x212A0A
R32 0x20210A   R31 0x1F0601   R30 0x1E0034   R29 0x1D0084   R28 0x1C2924
R25 0x190000   R24 0x180509   R23 0x178842   R22 0x162300   R20 0x14012C
R19 0x130965   R14 0x0E0FFE   R13 0x0D4000   R12 0x0C7001   R11 0x0B0018
R10 0x0A10D8   R9  0x090B02   R8  0x081084   R7  0x0728B2   R4  0x040543
R2  0x020500   R1  0x010808   R0  0x00221C
```

Only registers in Figure 7-5 are listed. Do not write any others. OUTA_POW changes only R46: `0x2E(POW)A3`, for example 0x2E06A3 for code 6.

### 5.3 Channel change (§7.5.2)

Write R38 (N), R45/R44 (NUM). R41/R40 (DEN) only if DEN changes. Then `R0 = 0x00221C`.

| Fout (MHz) | R38 | R45 |
|---|---|---|
| 2405 | 0x26005C | 0x2D000D |
| 2418 | 0x26005C | 0x2D001A |
| 2431 | 0x26005C | 0x2D0027 |
| 2444 | 0x26005E | 0x2D0000 |
| 2450 | 0x26005E | 0x2D0006 |
| 2457 | 0x26005E | 0x2D000D |
| 2470 | 0x26005E | 0x2D001A |
| 2483 | 0x26005E | 0x2D0027 |

R44 = 0x2C0000 for all channels. General rule: R38 = 0x260000 | (N<<1), R45 = 0x2D0000 | NUM.

### 5.4 OUTA_POW for the RFoutA → 100 pF → pad → CC2595 chain

This assumes 50 Ω pull-ups on both OUTAP and OUTAM. **OUTAM must also be terminated**: 100 pF into 50 Ω to GND, as in the Fig 6-13 test condition and §6.5 note 2. Estimates are Fig 6-13 values (5.4 GHz) +1 dB for 2.45 GHz (Fig 6-12), roughly ±1.5 dB.

| Power needed at the OUTAP pin (into 50 Ω) | Pad loss for 0 dBm at CC2595 | OUTA_POW |
|---|---|---|
| ≈ 0 dBm | 0 dB | 2–3 |
| ≈ +3 dBm | 3 dB | 6 |
| ≈ +6 dBm | 6 dB | 12 |
| ≈ +8 dBm (near the 50 Ω pull-up limit) | — | 20–24 |

Start at 3 and trim on the bench. Above about code 28 the 50 Ω pull-up saturates (Fig 6-13), so add current only up to that point.

### 5.5 Fallback without the doubler (if the TCXO duty cycle gives 26 MHz spurs)

* R9 = 0x090302 (OSC_2X = 0)
* DEN = 26 (R41 = 0x29001A)
* N = floor(Fout/26) = 92–95, NUM = Fout − 26·N
* Keep the same filter and set ICOARSE = 3: R14 = 0x0E0FFF (12.1 mA) → 50.5 kHz / 61.1°.
* Or keep ICOARSE = 2: 32.5 kHz / 56.8°.

### 5.6 Hop time and fast hopping

Analog settling, rounded filter, linear model (Talbot inverse Laplace): VCO frequency error after a step reaches < 1 kHz at 50 µs (2 MHz step), 54 µs (4 MHz), 60 µs (10 MHz) and 64 µs (20 MHz). Add about 15 µs to reach < 100 Hz. After each R0/FCAL, Vtune restarts at mid-rail, so the residual step can reach ±1.25 V × 34 MHz/V ≈ ±40 MHz at the VCO.

VCO calibration usually dominates. The default is 590 µs (§8.1.8). The ~20 µs figure assumes a 200 MHz cal clock, but here the cal clock is only 26 MHz, so expect longer. I have not verified the cal time at 26 MHz.

For < 100 µs hops, build a per-channel VCO table once at boot:

1. Calibrate each channel normally.
2. Read back rb_VCO_SEL (R68[7:5]), rb_VCO_CAPCTRL (R69[7:0]) and rb_VCO_DACISET (R70[8:0]). This needs MUXOUT_SEL = 0 temporarily, since readback is on MUXout.
3. To hop, set VCO_SEL_FORCE = 1 + VCO_SEL (R23), VCO_CAPCTRL_OVR = 1 (R8[10]) + VCO_CAPCTRL (R22) and VCO_IDAC_OVR = 1 (R8[13]) + VCO_IDAC (R19, keep 250–450).
4. Write N/NUM and R0. With the overrides set, FCAL/ACAL are bypassed (Tables 7-10, 7-17, 7-19) and only the ~55 µs analog settle remains.

ΔT_CL = 125 °C (§6.5) suggests one table holds over temperature.

A cheaper middle ground is FCAL_VCO_SEL_STRT = 1 with VCO_SEL set to the core above the target, plus ACAL_VCO_IDAC_STRT ≈ 350 (§8.1.8). The whole hop band (VCO 4800–4967 MHz) is probably inside one or two cores.

## 6. Unverified or assumed items

1. **Kvco** is the Table 7-3 typical value (34 MHz/V). The datasheet gives no min/max. A ±25 % change moves fc to 46–73 kHz, while PM stays ≈ 61°.
2. **Internal Vtune/VCO capacitance** is not specified. The model ignores it, which is fine if it is ≪ 3.3 nF.
3. **CP_IUP/CP_IDN bit weights**: Table 7-16 lists bit4 = 1.25 mA and bit3 = 2.5 mA, an odd order that may be a typo. Code 31 (all bits, 4.844 mA) is the same either way. That is why I chose it.
4. **Register words** were rebuilt from the Figure 7-5 text extraction (fixed bits read from the PDF). Spot-checks match known TI defaults for R0, R1, R2, R7–R13, R19–R25, R28–R34, R36, R37, R39. The R35, R46, R47, R48 and R64 fixed bits were not cross-checked against a TICS Pro export. **Generate a TICS Pro (LMX2582 profile) register file with these settings and diff it before committing firmware.**
5. **Which VCO core** covers 4.8–4.97 GHz is unknown. Read it back with rb_VCO_SEL.
6. Calibration time with the 26 MHz cal clock and FCAL_FAST/ACAL_FAST is unknown. Measure it with lock detect on MUXout.
7. Whether DEN (R40/R41) must be rewritten on every hop is unclear. §7.5.2 lists it, but it should not matter when DEN does not change.
8. OUTA_POW codes are read off the figures (±1.5 dB), and the pad attenuation is not known here.
9. Phase-noise figures are model estimates: ideal MASH, VCO interpolated between the 1.8 GHz and 5.5 GHz tables, TCXO close-in noise not included. The TG2520SMN doubler suitability (duty cycle) is not verified.
10. The **OSCin network** is outside the loop-filter scope but matters. AC-couple OSCinP and also AC-couple OSCinM to GND with the same cap, since TI asks for matched termination on both sides (§8.1.3). Do not fit the 50 Ω shunt resistors from Fig 8-11 with a clipped-sine TCXO. The TG2520SMN expects a ~10 kΩ load; confirm in its datasheet.

## Sources

* TI LMX2582 datasheet SNAS680E: https://www.ti.com/lit/ds/symlink/lmx2582.pdf
* Epson TG2520SMN datasheet (phase noise −161 dBc/Hz at 100 kHz offset, 26 MHz): https://www.mouser.lt/datasheet/3/97/1/TG2520SMN_en.pdf and [LCSC copy](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2205171716_Seiko-Epson-X1G0054210312_C3013795.pdf)
* D. Banerjee, *PLL Performance, Simulation and Design* (passive filter equations used in §4.2)
