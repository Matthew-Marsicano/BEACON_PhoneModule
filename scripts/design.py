"""BEACON Phone Module - netlist description (translated from BeaconPhoneModule.pdf and completed).

Run with KiCad's bundled Python:  D:/KiCAD/bin/python.exe -I scripts/design.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kigen import Design, SymbolLib  # noqa: E402
import parts  # noqa: E402

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

lib = SymbolLib()
parts.register(lib)
d = Design(lib)

R0402 = 'Resistor_SMD:R_0402_1005Metric'
R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0402 = 'Capacitor_SMD:C_0402_1005Metric'
L0402 = 'Inductor_SMD:L_0402_1005Metric'
L0603 = 'Inductor_SMD:L_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
R0805 = 'Resistor_SMD:R_0805_2012Metric'
FB0603 = 'Inductor_SMD:L_0603_1608Metric'
UFL = 'Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical'
SMA_EDGE = 'BEACON:SMA_Cinch_142-0711-821_EdgeLaunch'
PATCH_FP = 'BEACON:Taoglas_WDP.2458.25.4_Patch'
TP = 'TestPoint:TestPoint_Pad_D1.0mm'

_n = {}


def ref(prefix):
    _n[prefix] = _n.get(prefix, 0) + 1
    return f'{prefix}{_n[prefix]}'


def R(s, val, a, b, fp=R0402, **k):
    return s.add('Device:R', ref('R'), val, fp, {1: a, 2: b}, **k)


def C(s, val, a, b='GND', fp=None, **k):
    if fp is None:
        fp = C0805 if val == '22uF' else C0603 if val in ('4.7uF', '10uF') else C0402
    return s.add('Device:C', ref('C'), val, fp, {1: a, 2: b}, **k)


def L(s, val, a, b, fp=L0402, **k):
    return s.add('Device:L', ref('L'), val, fp, {1: a, 2: b}, **k)


def FB(s, a, b):
    return s.add('Device:FerriteBead_Small', ref('FB'), 'BLM18PG221SN1', FB0603, {1: a, 2: b},
                 props={'MPN': 'BLM18PG221SN1D', 'Manufacturer': 'Murata'})


def TPt(s, net):
    p = s.add('Connector:TestPoint', ref('TP'), net, TP, {1: net})
    p.in_bom = False
    return p


def FLAG(s, net):
    return s.add('power:PWR_FLAG', ref('#FLG'), 'PWR_FLAG', '', {1: net})


def UFL_J(s, net, mpn_note):
    return s.add('Connector:Conn_Coaxial', ref('J'), mpn_note, UFL, {1: net, 2: 'GND'},
                 props={'MPN': 'U.FL-R-SMT-1(10)', 'Manufacturer': 'Hirose'})


# ==========================================================================
# USB  (Altium USB.SchDoc)
# ==========================================================================
usb = d.sheet('USB', 'USB.kicad_sch', 'USB-C receptacle, VBUS protection and ESD')
usb.group('USB-C receptacle (short C-C cable to the phone) - Rd 5.1k on CC1 and CC2 advertises a sink')
usb.add('Connector:USB_C_Receptacle_USB2.0_16P', ref('J'), 'USB4105-GF-A',
        'Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal',
        {'A4': 'VBUS_C', 'A9': 'VBUS_C', 'B4': 'VBUS_C', 'B9': 'VBUS_C',
         'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'SH': 'GND',
         'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_D+', 'B6': 'USB_D+', 'A7': 'USB_D-', 'B7': 'USB_D-',
         'A8': None, 'B8': None},
        props={'MPN': 'USB4105-GF-A', 'Manufacturer': 'GCT'})
R(usb, '5.1k', 'CC1', 'GND')
R(usb, '5.1k', 'CC2', 'GND')
usb.group('VBUS protection: polyfuse + 6.0 V TVS')
usb.add('Device:Polyfuse_Small', ref('F'), '0.75A hold', 'Fuse:Fuse_1206_3216Metric', {1: 'VBUS_C', 2: '5V_BUS'},
        props={'MPN': 'NANOSMDC075F-2', 'Manufacturer': 'Littelfuse'})
usb.add('Device:D_Zener', ref('D'), 'SZSMF6.0AT1G', 'Diode_SMD:D_SOD-123F', {1: '5V_BUS', 2: 'GND'},
        props={'MPN': 'SZSMF6.0AT1G', 'Manufacturer': 'onsemi', 'Description': '6.0 V unidirectional TVS'})
C(usb, '1uF', '5V_BUS')
usb.group('USB D+/D- ESD (USBLC6: pins 1/6 and 3/4 are one line each - flow-through)')
usb.add('Power_Protection:USBLC6-2SC6', ref('U'), 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6',
        {1: 'USB_D+', 6: 'USB_D+', 3: 'USB_D-', 4: 'USB_D-', 2: 'GND', 5: '5V_BUS'},
        props={'MPN': 'USBLC6-2SC6', 'Manufacturer': 'STMicroelectronics'})
FLAG(usb, '5V_BUS')
FLAG(usb, 'GND')
usb.note('USB sheet notes\n'
         '- MagSafe puck: a USB-C receptacle at the bottom edge takes a short C-to-C cable to the\n'
         '  phone (the phone is host and 5 V source). Rd = 5.1k on both CC1 and CC2.\n'
         '  (The Altium drawing used a UP20 plug for the direct-plug dongle concept.)\n'
         '- USB 2.0 full-speed device; D+/D- run straight to the nRF52840 (internal series R).\n'
         '- Keep total VBUS capacitance <= 10 uF (USB 2.0 inrush).')

# ==========================================================================
# POWER  (Altium Power.SchDoc + Power_3V3.SchDoc + 2x Power_INA.SchDoc)
# ==========================================================================
pwr = d.sheet('Power', 'Power.kicad_sch', 'Power: current monitors and 3.3 V buck', paper='A2')


def ina(s, label, vin, vout, a0, shunt_ref_note):
    s.group(f'{label} INA219 current/voltage monitor - shunt {vin} -> {vout}, I2C addr '
            f'{"0x40" if a0 == "GND" else "0x41"}')
    p, n = f'{label}_SNS_P', f'{label}_SNS_N'
    R(s, '50m', vin, vout, fp=R0805, props={'MPN': 'ERJ-6BWFR050V', 'Tolerance': '1%',
                                            'Note': shunt_ref_note})
    R(s, '10', vin, p, props={'Note': 'Kelvin: route from shunt pad, do not share with force path'})
    R(s, '10', vout, n, props={'Note': 'Kelvin: route from shunt pad'})
    C(s, '100nF', p, n)
    s.add('Sensor_Energy:INA219AxDCN', ref('U'), 'INA219BIDCNR', 'Package_TO_SOT_SMD:SOT-23-8',
          {1: p, 2: n, 3: 'GND', 4: '3V3', 5: 'I2C_SCL', 6: 'I2C_SDA', 7: a0, 8: 'GND'},
          props={'MPN': 'INA219BIDCNR', 'Manufacturer': 'Texas Instruments'})
    C(s, '100nF', '3V3')


ina(pwr, '5V', '5V_BUS', '5V0', 'GND', 'Was 5 mOhm: 50 mOhm gives 0.8 A FS at PGA/1 and 0.2 mA LSB')
ina(pwr, '3V3', '3V3_OUT', '3V3', '3V3', 'Was 5 mOhm: 50 mOhm gives 0.8 A FS at PGA/1 and 0.2 mA LSB')

pwr.group('3.3 V Silent Switcher buck (LT80602): 5V0 -> 3V3_OUT, forced-continuous at a fixed ~506 kHz')
C(pwr, '4.7uF', '5V0', props={'Note': 'Bulk in (ADI: >= 4.7 uF); keeps VBUS total < 10 uF'})
C(pwr, '100nF', '5V0', props={'Note': 'Hot-loop cap, VIN1-GND1, as close as possible'})
C(pwr, '100nF', '5V0', props={'Note': 'Hot-loop cap, VIN2-GND2, as close as possible'})
lt = parts.LT80602_PINS
pwr.add('BEACON:LT80602', ref('U'), 'LT80602AFO+', 'BEACON:ADI_FC2QFN-17-1EP_3x3mm_LT80602',
        {lt['VIN1']: '5V0', lt['VIN2']: '5V0', lt['EP']: '5V0', lt['EN/UV']: '5V0', lt['SYNC/MODE']: 'REG_INTVCC',
         lt['TR/SS']: 'REG_SS', lt['RT']: 'REG_RT', lt['INTVCC']: 'REG_INTVCC', lt['BST']: 'REG_BST',
         lt['SW']: 'REG_SW', lt['BIAS/VOUT']: '3V3_OUT', lt['FB/VOS']: 'REG_FB', lt['PG/TJ']: '3V3_PG',
         lt['GND']: 'GND', lt['GND1a']: 'GND', lt['GND1b']: 'GND', lt['GND2a']: 'GND', lt['GND2b']: 'GND'},
        props={'MPN': 'LT80602AFO+', 'Manufacturer': 'Analog Devices', 'LCSC': 'C54448890',
               'Note': 'EP is internally VIN - pour it into the 5V0 plane, NOT GND'})
C(pwr, '18nF', 'REG_SS')
R(pwr, '37.4k', 'REG_RT', 'GND')
C(pwr, '2.2uF', 'REG_INTVCC', fp=C0603)
C(pwr, '100nF', 'REG_BST', 'REG_SW', props={'Note': 'FCM: ADI recommends 0.1 uF (was 1 uF)'})
L(pwr, '5.6uH', 'REG_SW', '3V3_OUT', fp='Inductor_SMD:L_Abracon_ASPI-4030S',
  props={'MPN': 'ASPI-4030S-5R6M-T', 'Manufacturer': 'Abracon', 'LCSC': 'C5224561',
         'Note': 'Isat 2.6 A / Irms 1.95 A vs ~0.56 A peak (replaces Wurth 74438357056, not on LCSC)'})
R(pwr, '634k', '3V3_OUT', 'REG_FB', props={'Note': 'Was 681k'})
C(pwr, '4.7pF', '3V3_OUT', 'REG_FB', props={'Note': 'Feed-forward (drawn as 4.8 pF)'})
R(pwr, '200k', 'REG_FB', 'GND', props={'Note': 'Was 220k: ADI max RFB-BOT is 205k'})
C(pwr, '22uF', '3V3_OUT')
C(pwr, '22uF', '3V3_OUT')
R(pwr, '10k', '3V3_OUT', '3V3_PG', props={'Note': 'PG pull-up ("PU in reg")'})
FLAG(pwr, '5V0')
FLAG(pwr, '3V3_OUT')
FLAG(pwr, '3V3')
pwr.note('Power sheet notes\n'
         '- CHANGE: the buck now runs from 5V0 (after the 5 V shunt) so the 5 V INA219 measures\n'
         '  the whole module input. In the Altium drawing the buck tapped 5V_BUS ahead of the shunt.\n'
         '- 5V0 also feeds the QPL9547 LNA (its recommended supply is 3.15-5.25 V, 5 V typ).\n'
         '- CHANGE: shunts 5 mOhm -> 50 mOhm. Expected 3V3 load ~0.45 A (LMX2582 ~0.25 A,\n'
         '  CC2595 ~0.1 A, nRF52840 + misc), so 5 mOhm only used 1/16th of the ADC range.\n'
         '- INA219 addresses: 5V monitor 0x40 (A0=A1=GND), 3V3 monitor 0x41 (A0=VS).\n'
         '- FIX: FB divider 681k/220k -> 634k/200k (ADI: RFB-BOT <= 205k). Vout = 0.8 x (1+634/200)\n'
         '  = 3.34 V, leaving headroom for shunt + bead drops to the LMX2582 (3.15 V min).\n'
         '- RT 37.4k -> fSW ~506 kHz (ADI eq. 2); L = 0.75 x Vout/fSW = 4.9 uH -> 5.6 uH;\n'
         '  CBST 1 uF (ADI Table 7). Pinout verified against ADI datasheet Rev 2, Table 3.\n'
         '- LT80602 exposed pad is internally VIN: it connects to 5V0, NOT GND.\n'
         '- CHANGE: SYNC/MODE GND (Burst) -> INTVCC (forced continuous): fixed 506 kHz keeps the\n'
         '  switching spurs at a known offset from the carrier; BST cap is 0.1 uF in FCM.')

# ==========================================================================
# MCU  (Altium MCU.SchDoc) - nRF52840 in normal-voltage mode, VDD = 3V3, DC/DC on REG1
# ==========================================================================
mcu = d.sheet('MCU', 'MCU.kicad_sch', 'nRF52840 MCU / BLE receiver, debug, UI', paper='A1')
mcu.group('nRF52840-QIAA (aQFN73)')
nrf = {
    # supplies
    'B1': '3V3', 'W1': '3V3', 'A22': '3V3', 'AD14': '3V3', 'AD23': '3V3', 'Y2': '3V3', 'AB2': None,
    'AD2': '5V_BUS', 'AC5': 'NRF_DECUSB', 'B7': 'GND', 'F23': 'GND', 'EP': 'GND',
    'C1': 'NRF_DEC1', 'A18': None, 'D23': 'NRF_DEC3', 'B5': 'NRF_DEC4_6', 'E24': 'NRF_DEC4_6', 'N24': None,
    'B3': 'NRF_DCC',
    # clocks / radio
    'B24': 'NRF_XC1', 'A23': 'NRF_XC2', 'D2': None, 'F2': None, 'H23': 'NRF_ANT',
    # debug / reset / USB
    'AA24': 'SWDCLK', 'AC24': 'SWDIO', 'AC13': 'nRESET', 'AD22': 'SWO', 'AD4': 'USB_D-', 'AD6': 'USB_D+',
    # synthesizer SPI + control (high-speed pins kept on the bottom edge, away from the radio)
    'AC15': 'SYN_SCK_M', 'AC17': 'SYN_SDI_M', 'AD18': 'SYN_CSB_M', 'AD16': 'SYN_MUXOUT', 'AC19': 'SYN_CE',
    # I2C to the INA219s
    'AD8': 'I2C_SCL', 'AD10': 'I2C_SDA',
    # RF front-end control (static levels only)
    'A12': 'PA_EN', 'G1': 'LNA_PD', 'B13': '3V3_PG',
    # UI / test
    'R24': 'LED', 'R1': 'BUTTON', 'L1': 'UART_TX', 'N1': 'UART_RX',
    'B11': 'SPARE_IO1', 'J1': 'SPARE_IO2', 'K2': 'SPARE_IO3',
}
all_nrf = {q['num'] for q in lib.pins('MCU_Nordic:nRF52840')}
for b in all_nrf - set(nrf):
    nrf[b] = None
mcu.add('MCU_Nordic:nRF52840', ref('U'), 'nRF52840-QIAA', 'Package_DFN_QFN:Nordic_AQFN-73-1EP_7x7mm_P0.5mm',
        nrf, props={'MPN': 'NRF52840-QIAA-R', 'Manufacturer': 'Nordic Semiconductor'})
mcu.group('Supply decoupling (Nordic PS v1.11 reference circuitry)')
C(mcu, '4.7uF', '3V3', props={'Note': 'VDD W1'})
C(mcu, '1uF', '3V3', props={'Note': 'VDD B1'})
C(mcu, '100nF', '3V3', props={'Note': 'VDD A22'})
C(mcu, '100nF', '3V3', props={'Note': 'VDD AD14'})
C(mcu, '100nF', '3V3', props={'Note': 'VDD AD23'})
C(mcu, '4.7uF', '3V3', props={'Note': 'VDDH Y2 (tied to VDD: normal-voltage mode)'})
C(mcu, '4.7uF', '5V_BUS', props={'Note': 'VBUS AD2'})
C(mcu, '4.7uF', 'NRF_DECUSB')
C(mcu, '100nF', 'NRF_DEC1')
C(mcu, '100pF', 'NRF_DEC3')
C(mcu, '1uF', 'NRF_DEC4_6')
C(mcu, '47nF', 'NRF_DEC4_6')
L(mcu, '10uH', 'NRF_DCC', 'NRF_DCC_L', fp=L0603, dnp=True,
  props={'MPN': 'LQM18PN100MFRL', 'Note': 'DNP: ferrite saturates in the MagSafe field - REG1 runs in LDO mode (DCDCEN=0)'})
L(mcu, '15nH', 'NRF_DCC_L', 'NRF_DEC4_6', dnp=True, props={'MPN': 'LQG15HS15NJ02D', 'Note': 'DNP with the 10 uH (LDO mode)'})
mcu.group('32 MHz crystal (CL = 8 pF -> 12 pF load caps)')
mcu.add('Device:Crystal_GND24', ref('Y'), '32MHz', 'Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm',
        {1: 'NRF_XC1', 3: 'NRF_XC2', 2: 'GND', 4: 'GND'},
        props={'MPN': 'ABM11W-32.0000MHZ-8-B1U-T3', 'Manufacturer': 'Abracon'})
C(mcu, '12pF', 'NRF_XC1')
C(mcu, '12pF', 'NRF_XC2')
mcu.group('ANT matching (Nordic v1.1: 0.8 pF / 4.7 nH / 0.5 pF) - RX_RF comes from the LNA')
C(mcu, '0.8pF', 'NRF_ANT', props={'MPN': 'GJM1555C1HR80BB01D', 'Note': 'Return to VSS_PA'})
L(mcu, '4.7nH', 'NRF_ANT', 'RX_RF', props={'MPN': 'LQG15HS4N7B02D', 'LCSC': 'C162543'})
C(mcu, '0.5pF', 'RX_RF', props={'MPN': 'GJM1555C1HR50BB01D'})
mcu.group('SWD (Tag-Connect TC2030-IDC-NL), I2C pull-ups, synth CE default-off')
mcu.add('Connector:Conn_ARM_SWD_TagConnect_TC2030-NL', ref('J'), 'TC2030-IDC-NL',
        'Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical',
        {1: '3V3', 2: 'SWDIO', 3: 'nRESET', 4: 'SWDCLK', 5: 'GND', 6: 'SWO'})
mcu.parts[-1].in_bom = False
R(mcu, '4.7k', '3V3', 'I2C_SCL')
R(mcu, '4.7k', '3V3', 'I2C_SDA')
R(mcu, '100k', 'SYN_CE', 'GND', props={'Note': 'Synth disabled until firmware enables it'})
for sig in ('SYN_SCK', 'SYN_SDI', 'SYN_CSB'):
    R(mcu, '33', sig + '_M', sig, props={'Note': 'Series termination (3x 33R from the Altium MCU sheet)'})
mcu.group('User LED and demo button')
R(mcu, '1.5k', 'LED', 'LED_A')
mcu.add('Device:LED', ref('D'), 'Red', 'LED_SMD:LED_0603_1608Metric', {1: 'GND', 2: 'LED_A'},
        props={'MPN': 'KT-0603R', 'Manufacturer': 'Hubei KENTO Elec'})
mcu.add('Switch:SW_Push', ref('SW'), 'B3U-1000P', 'Button_Switch_SMD:SW_SPST_B3U-1000P',
        {1: 'BUTTON', 2: 'GND'}, props={'MPN': 'B3U-1000P', 'Manufacturer': 'Omron',
                                         'Note': 'Firmware test / start demo TX (internal pull-up)'})
mcu.group('M2 mounting holes (enclosure heat-set inserts; 6 mm keepout both sides)')
for _i in range(4):
    mcu.add('Mechanical:MountingHole', ref('H'), 'M2', 'MountingHole:MountingHole_2.2mm_M2', {})
    mcu.parts[-1].in_bom = False
mcu.group('Test points')
for net in ('UART_TX', 'UART_RX', 'SPARE_IO1', 'SPARE_IO2', 'SPARE_IO3', 'I2C_SCL', 'I2C_SDA',
            'SYN_MUXOUT', 'PA_EN', 'LNA_PD', '3V3', '5V_BUS', 'GND'):
    TPt(mcu, net)
mcu.note('MCU sheet notes\n'
         '- Supply: VDD and VDDH both on 3V3 (normal-voltage mode); DCCH unused. REG1 runs in LDO\n'
         '  mode (firmware DCDCEN=0): the 10 uH ferrite would saturate in the MagSafe magnet field,\n'
         '  so the DC/DC inductors are DNP footprints. VBUS from USB for the USBD peripheral.\n'
         '- Removed wearable-only nets copied from the wearable MCU sheet: CTRL_SPDT, Mod_Sel0/1,\n'
         '  PMIC_Status0-2, Sensor_SDA/SCL/INT/EN, QSPI_CLK.\n'
         '- GPIO map: SYN_SCK P0.19, SYN_MUXOUT P0.20, SYN_SDI P0.21, SYN_CSB P0.22, SYN_CE P0.23,\n'
         '  I2C SCL P0.13 / SDA P0.15, PA_EN P0.02, LNA_PD P0.26, 3V3_PG P0.03, LED P1.06,\n'
         '  BUTTON P1.09, UART TX P0.06 / RX P0.08, spares P0.28 / P0.04 / P0.05, SWO P1.00.\n'
         '- P0.02, P0.03, P0.28 and P1.06 are radio-sensitive (<=10 kHz, standard drive):\n'
         '  used only for static enables, PG and the LED.\n'
         '- No 32.768 kHz crystal: use the internal LFRC (XL1/XL2 left open).')

# ==========================================================================
# RX FRONT END  (Altium RFFE.SchDoc)
# ==========================================================================
rx = d.sheet('RX_Frontend', 'RX_Frontend.kicad_sch', 'RX chain: antenna, BPF, QPL9547 LNA')
rx.group('RX antenna: Taoglas WDP.2458.25.4 ceramic patch (pin-fed, board ground = its ground plane) + pi match')
rx.add('BEACON:Taoglas_WDP2458', ref('AE'), 'WDP.2458.25.4.B.02', PATCH_FP, {1: 'RX_PATCH', 2: 'GND'},
       props={'MPN': 'WDP.2458.25.4.B.02', 'Manufacturer': 'Taoglas', 'Datasheet': 'https://www.taoglas.com/datasheets/WDP.2458.25.4.B.02.pdf',
              'Note': 'Taped to the board top; pin soldered on the bottom'})
C(rx, 'DNP', 'RX_PATCH', 'GND', dnp=True, props={'Note': 'Patch match shunt (tune)'})
R(rx, '0', 'RX_PATCH', 'RX_ANT', props={'Note': 'Patch match series arm (tune; 0R default)'})
L(rx, '22nH', 'RX_ANT', 'GND', dnp=True, props={'MPN': 'LQW15AN22NJ00D', 'Note': 'Optional ESD shunt choke (non-magnetic core)'})
rx.add('BEACON:DEA202450BT-1294D1-H', ref('FL'), 'DEA202450BT-1294D1-H', 'BEACON:TDK_DEA202450BT-1294D1-H_2012',
       {1: 'RX_ANT', 4: 'RX_BPF', 2: 'GND', 3: 'GND'},
       props={'MPN': 'DEA202450BT-1294D1-H', 'Manufacturer': 'TDK', 'LCSC': 'C1512913',
              'Note': 'Replaces Johanson 2450BP08C0100001T (no stock); IL 1.02 dB typ / 1.35 dB max, 1 W'})
rx.group('QPL9547 LNA (Qorvo EVB values; ~17.8 dB gain at 2.4 GHz)')
C(rx, '100pF', 'RX_BPF', 'LNA_IN', props={'Note': 'DC block'})
rx.add('BEACON:QPL9547', ref('U'), 'QPL9547TR7', 'BEACON:Qorvo_QPL9547_DFN-8-1EP_2x2mm_P0.5mm',
       {2: 'LNA_IN', 7: 'LNA_OUT', 1: 'LNA_VBIAS', 6: 'LNA_SD', 9: 'GND', 3: None, 4: None, 5: None, 8: None},
       props={'MPN': 'QPL9547TR7', 'Manufacturer': 'Qorvo'})
L(rx, '18nH', 'LNA_VCC', 'LNA_OUT', props={'MPN': '0402CS-18NXGRW', 'Note': 'RF choke'})
C(rx, '100pF', 'LNA_OUT', 'RX_ATT', props={'Note': 'DC block'})
R(rx, '0', 'RX_ATT', 'RX_RF', props={'Note': 'Pi pad series arm (0R = no attenuation)'})
R(rx, 'DNP', 'RX_ATT', 'GND', dnp=True, props={'Note': 'Pi pad shunt - fit to protect the nRF from TX leakage'})
R(rx, 'DNP', 'RX_RF', 'GND', dnp=True, props={'Note': 'Pi pad shunt'})
R(rx, '3.32k', 'LNA_VCC', 'LNA_VBIAS', props={'Note': 'Sets LNA bias current'})
R(rx, '10', '5V0', 'LNA_VCC', fp=R0603, props={'Note': 'RC supply filter with the LNA caps (was a ferrite bead: MagSafe field); 4.35 V at the LNA'})
C(rx, '10uF', 'LNA_VCC', props={'Note': 'RC filter'})
C(rx, '1uF', 'LNA_VCC')
C(rx, '100pF', 'LNA_VCC')
C(rx, '100pF', 'LNA_VCC')
R(rx, '0', 'LNA_PD', 'LNA_SD')
R(rx, '100k', 'LNA_SD', '3V3', props={'Note': 'LNA OFF at reset; firmware drives LNA_PD low to enable'})
FLAG(rx, 'LNA_VCC')
rx.note('RX notes\n'
         '- RX antenna: Taoglas WDP.2458.25.4 25x25 mm pin-fed patch at the board centre (MagSafe enclosure).\n'
         '  Feed runs on B.Cu from the pin, then an RF via to L1. Pi match footprints for tuning.\n'
         '- The LNA now runs from 5V0 (QPL9547 recommended 3.15-5.25 V).\n'
         '- LNA is OFF at reset (100k pull-up on Shut_Down); firmware drives LNA_PD low to enable.\n'
         '- LNA supply through a ferrite bead from 5V0 (keeps buck ripple off the LNA).\n'
         '- RX OVERLOAD: TX carrier leaking into the RX antenna is in-band and gets ~17 dB of gain.\n'
         '  Keep antenna-to-antenna isolation >= 30 dB, or fit the pi pad (R_ATT shunts) so the\n'
         '  nRF ANT pin stays below 0 dBm (abs max +10 dBm). The nRF must never transmit: its ANT\n'
         '  pin drives straight into the LNA output.\n'
         '- All RF lines: 50 Ohm grounded CPW, see the PCB stackup notes.')

# ==========================================================================
# TX PA  (Altium PA.SchDoc)
# ==========================================================================
pa = d.sheet('TX_PA', 'TX_PA.kicad_sch', 'TX chain: pad, CC2595 PA, LPF, antenna')
pa.group('PA supply (filtered 3V3) and 3 dB input pad (sets PA drive ~0 dBm)')
R(pa, '1', '3V3', 'VDD_PA', fp=R0603, props={'Note': 'RC supply filter (was a ferrite bead: MagSafe field)'})
C(pa, '10uF', 'VDD_PA')
C(pa, '100pF', 'VDD_PA')
R(pa, '294', 'CW_RF', 'GND')
R(pa, '17.8', 'CW_RF', 'PA_IN')
R(pa, '294', 'PA_IN', 'GND')
pa.group('CC2595 PA (TI EVM values) - +20.7 dBm typ at 0 dBm in')
pa.add('BEACON:CC2595', ref('U'), 'CC2595RGTR', 'Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias',
       {2: 'PA_IN', 8: 'PA_EN', 6: 'PA_RBIAS1', 7: 'PA_RBIAS2', 5: 'VDD_PA', 15: 'PA_AVDD1',
        10: 'PA_OUT', 12: 'PA_OUT', 1: 'GND', 3: 'GND', 4: 'GND', 9: 'GND', 11: 'GND', 13: 'GND',
        14: 'GND', 16: 'GND', 17: 'GND'},
       props={'MPN': 'CC2595RGTR', 'Manufacturer': 'Texas Instruments'})
C(pa, '100nF', 'VDD_PA', props={'Note': 'AVDD_BIAS pin 5'})
R(pa, '4.7', 'VDD_PA', 'PA_AVDD1')
C(pa, '100nF', 'PA_AVDD1')
R(pa, '20k', 'PA_RBIAS1', 'VDD_PA', props={'Note': 'Per CC2595EM schematic: RBIAS to 3.3 V (drawn to GND)'})
R(pa, '20k', 'PA_RBIAS2', 'VDD_PA', props={'Note': 'Per CC2595EM schematic: RBIAS to 3.3 V (drawn to GND)'})
R(pa, '100k', 'PA_EN', 'GND', props={'Note': 'PA off at reset'})
L(pa, '12nH', 'VDD_PA', 'PA_OUT', props={'MPN': 'LQW15AN12NG00D', 'LCSC': 'C86128', 'Note': 'RF_OUT DC feed, non-magnetic, >= 0.2 A (missing from the Altium drawing)'})
C(pa, '100nF', 'VDD_PA', props={'Note': 'Choke decoupling'})
pa.group('Output match (1.2 nH / 1.5 pF), DC block, 2.45 GHz low-pass, TX antenna connector')
L(pa, '1.2nH', 'PA_OUT', 'PA_MATCH', props={'MPN': 'LQG15HS1N2B02D', 'LCSC': 'C488336'})
C(pa, '1.5pF', 'PA_MATCH', props={'MPN': 'GJM1555C1H1R5BB01D'})
C(pa, '22pF', 'PA_MATCH', 'TX_LPF', props={'Note': 'DC block'})
pa.add('BEACON:2450LP07C0100001T', ref('FL'), '2450LP07C0100001T', 'BEACON:Johanson_2450LP07_0402_4T',
       {2: 'TX_LPF', 4: 'TX_ANT', 1: 'GND', 3: 'GND'},
       props={'MPN': '2450LP07C0100001T', 'Manufacturer': 'Johanson Technology'})
pa.add('Connector:Conn_Coaxial', ref('J'), 'TX antenna U.FL', UFL, {1: 'TX_ANT', 2: 'GND'},
       props={'MPN': 'U.FL-R-SMT-1(10)', 'Manufacturer': 'Hirose',
              'Note': 'For the Taoglas FXP70.07.0053A 2.4 GHz flex antenna (IPEX MHF1 / U.FL, 1.13 mm cable, 53 mm)'})
L(pa, '22nH', 'TX_ANT', 'GND', dnp=True, props={'MPN': 'LQW15AN22NJ00D', 'Note': 'Optional ESD shunt choke (non-magnetic core)'})
FLAG(pa, 'VDD_PA')
FLAG(pa, 'PA_AVDD1')
pa.note('TX notes\n'
        '- FIX: CC2595 RF_OUT (pins 10/12) is the PA collector and needs a DC feed: 12 nH\n'
        '  from VDD_PA as on the TI CC2595EM. It was missing from the Altium drawing.\n'
        '- FIX: RBIAS1/RBIAS2 20k go to VDD_PA per the TI EM schematic (the drawing tied\n'
        '  them to GND). The TI BOM table conflicts with this; confirm on first boards.\n'
        '- GND on every CC2595 GND pin and the EP (TODO "add GND connection to PA").\n'
        '- TX antenna: Taoglas FXP70.07.0053A flex antenna on a U.FL at the right edge (53 mm cable).\n'
        '- PA input pad: the LMX2582 gives several dBm; 3 dB pad plus OUTA_PWR register\n'
        '  sets ~0 dBm into the PA (abs max +10 dBm).')

# ==========================================================================
# CW SYNTHESIZER  (Altium CW_Synthesizer.SchDoc - was only a symbol)
# ==========================================================================
cw = d.sheet('CW_Synth', 'CW_Synth.kicad_sch', 'CW synthesizer: LMX2582 + TCXO', paper='A1')
cw.group('Filtered 3.3 V for the synthesizer (3.15-3.45 V)')
R(cw, '0', '3V3', 'VCC_SYN', fp=R0603, props={'Note': 'Synth supply link (no ferrite: MagSafe field). Optional LC: 1 uH metal-alloy + 0.22R'})
C(cw, '10uF', 'VCC_SYN')
C(cw, '100nF', 'VCC_SYN')
FLAG(cw, 'VCC_SYN')
cw.group('26 MHz TCXO reference (clipped sine), AC-coupled into OSCin')
cw.add('Oscillator:TG2520SMN-xx.xxxxxxMhz-xxxxNM', ref('Y'), '26MHz',
       'Oscillator:Oscillator_SMD_SeikoEpson_TG2520SMN-xxx-xxxxxx-4Pin_2.5x2.0mm',
       {1: None, 2: 'GND', 3: 'TCXO_OUT', 4: 'VCC_SYN'},
       props={'MPN': 'X1G0054210204', 'Manufacturer': 'Seiko Epson', 'LCSC': 'C7527389',
              'Note': 'TG2520SMN-family 26 MHz TCXO; confirm 3.3 V supply and clipped-sine output on receipt'})
C(cw, '100nF', 'VCC_SYN', props={'Note': 'TCXO VCC'})
C(cw, '100nF', 'TCXO_OUT', 'SYN_OSCP', props={'Note': 'AC coupling'})
R(cw, '49.9', 'TCXO_OUT', 'GND', dnp=True, props={'Note': 'Fit only for a 50 Ohm reference source'})
C(cw, '100nF', 'SYN_OSCM', 'GND', props={'Note': 'AC-ground OSCinM with the same cap as OSCinP'})
cw.group('LMX2582 PLL + VCO (TI SNAS680E Fig 8-11)')
lmx = {1: 'SYN_CE', 24: 'SYN_CSB', 16: 'SYN_SCK', 17: 'SYN_SDI', 20: 'SYN_MUXOUT', 8: 'SYN_OSCP', 9: 'SYN_OSCM',
       7: 'VCC_SYN', 11: 'VCC_SYN', 15: 'VCC_SYN', 21: 'VCC_SYN', 26: 'VCC_SYN', 37: 'VCC_SYN',
       23: 'SYN_OUTAP', 22: 'SYN_OUTAM', 19: None, 18: None, 12: 'SYN_CP', 35: 'SYN_VTUNE',
       3: 'SYN_VBIASVCO', 10: 'SYN_VREGIN', 27: 'SYN_VBIASVCO2', 29: 'SYN_VREFVCO2', 33: 'SYN_VBIASVARAC',
       36: 'SYN_VREFVCO', 38: 'SYN_VREGVCO', 5: None, 28: None, 30: None, 32: None}
for g in (2, 4, 6, 13, 14, 25, 31, 34, 39, 40, 41):
    lmx[g] = 'GND'
cw.add('BEACON:LMX2582', ref('U'), 'LMX2582RHAR',
       'Package_DFN_QFN:Texas_RHA_VQFN-40-1EP_6x6mm_P0.5mm_EP4.6x4.6mm_ThermalVias', lmx,
       props={'MPN': 'LMX2582RHAR', 'Manufacturer': 'Texas Instruments'})
cw.group('Supply decoupling: 0.1 uF on every Vcc pin, +10 uF on VccMASH / VccVCO / VccVCO2')
for pin in ('VccDIG 7', 'VccCP 11', 'VccMASH 15', 'VccBUF 21', 'VccVCO2 26', 'VccVCO 37'):
    C(cw, '100nF', 'VCC_SYN', props={'Note': pin})
for pin in ('VccMASH 15', 'VccVCO2 26', 'VccVCO 37'):
    C(cw, '10uF', 'VCC_SYN', props={'Note': pin})
cw.group('Internal regulator / VCO bias bypass caps (place at the pins)')
C(cw, '10uF', 'SYN_VBIASVCO')
C(cw, '1uF', 'SYN_VREGIN')
C(cw, '1uF', 'SYN_VBIASVCO2')
C(cw, '10uF', 'SYN_VREFVCO2')
C(cw, '10uF', 'SYN_VBIASVARAC')
C(cw, '10uF', 'SYN_VREFVCO')
C(cw, '1uF', 'SYN_VREGVCO')
cw.group('Loop filter: PFD 52 MHz, Icp 7.27 mA, LBW ~59 kHz, PM ~62 deg (docs/lmx2582_loop_filter.md)')
C(cw, '820pF', 'SYN_CP', props={'Note': 'C1_LF C0G, at CPout'})
R(cw, '150', 'SYN_CP', 'SYN_LF2', props={'Note': 'R2_LF'})
C(cw, '68nF', 'SYN_LF2', fp=C0603, props={'MPN': 'CL10B683KB8NNNC', 'LCSC': 'C31658',
                                        'Note': 'C2_LF X7R 50 V (no 68 nF C0G in 0603 at LCSC)'})
R(cw, '22', 'SYN_CP', 'SYN_LF3', props={'Note': 'R3_LF (3rd pole)'})
C(cw, '3.3nF', 'SYN_LF3', dnp=True, props={'Note': 'C3_LF - DNP (footprint kept)'})
R(cw, '0', 'SYN_LF3', 'SYN_VTUNE', props={'Note': 'R4_LF (4th pole)'})
C(cw, '3.3nF', 'SYN_VTUNE', props={'Note': 'C4_LF C0G at Vtune pin 35 (>= 3.3 nF required)'})
cw.group('RF output A: 50 Ohm pull-ups, 100 pF DC blocks; OUTAM terminated in 50 Ohm (B unused)')
R(cw, '49.9', 'VCC_SYN', 'SYN_OUTAP', props={'Note': 'Pull-up at pin'})
R(cw, '49.9', 'VCC_SYN', 'SYN_OUTAM', props={'Note': 'Pull-up at pin'})
C(cw, '100pF', 'VCC_SYN', props={'Note': 'Pull-up common node'})
C(cw, '100pF', 'SYN_OUTAP', 'CW_RF', props={'Note': 'DC block -> PA'})
C(cw, '100pF', 'SYN_OUTAM', 'SYN_OUTAM_T', props={'Note': 'DC block'})
R(cw, '49.9', 'SYN_OUTAM_T', 'GND', props={'Note': 'Balances OUTAP load'})
cw.note('CW synthesizer notes (completed from the TI typical application)\n'
        '- Carrier: 2400-2483.5 MHz ISM. VCO 3.55-7.1 GHz, CHDIV=2 -> 2.4 GHz on OUTA.\n'
        '- Reference: 26 MHz TCXO. The PFD can use the OSCin doubler (52 MHz) in fractional mode.\n'
        '- SPI: SCK/SDI/CSB from the nRF52840; MUXout = lock detect or SPI readback.\n'
        '- CE has a 100k pull-down on the MCU sheet: the synth stays off until firmware enables it.\n'
        '- OUTB powered down in firmware; pins left open.\n'
        '- Loop filter: PFD 52 MHz (OSC_2X), Icp 7.27 mA -> LBW ~59 kHz, PM ~62 deg. A wider loop is\n'
        '  not reachable with C4 >= 3.3 nF and would worsen 1-5 MHz phase noise (the tag band).\n'
        '- Spur-free channels with a 26 MHz TCXO: multiples of 13 MHz (2405, 2418, ..., 2483 MHz).\n'
        '- Register plan and per-channel words: docs/lmx2582_loop_filter.md (verify with TICS Pro).')

d.root_notes = [
    'BEACON Phone Module - inferred specifications (no spec doc supplied; derived from the Altium schematic)\n'
    '  * Plugs straight into the phone through a USB-C plug: USB 2.0 FS data + 5 V power (<= 500 mA).\n'
    '  * Illuminates the backscatter wearable with a 2.4 GHz ISM CW carrier: LMX2582 -> CC2595 PA, about +20 dBm\n'
    '    conducted into a U.FL for a Taoglas FXP70.07.0053A flex antenna, low-pass filtered for harmonics.\n'
    '  * Receives the backscattered signal on a Taoglas WDP.2458 ceramic patch: BPF -> QPL9547 LNA -> nRF52840.\n'
    '  * Housed in a MagSafe puck (beacon_phone_magsafe_2p5mm.scad): 55 x 78.45 mm board, 4x M2, USB-C cable to the phone.\n'
    '  * nRF52840 controls the synth (SPI), PA_EN, LNA shutdown and the USB link; it reads two INA219 monitors\n'
    '    (5 V input and 3.3 V rail).\n'
    '  * 3.3 V rail from an LT80602 Silent Switcher buck; expected load about 0.45 A.\n'
    'Top-sheet TODOs from the Altium file: RX/TX antenna connectors added; PA GND connected; MCU and CW synth completed.',
]


def build():
    os.makedirs(OUT, exist_ok=True)
    errs, singles, _ = d.check()
    for e in errs:
        print('ERROR', e)
    for n, v in sorted(singles.items()):
        print('single-pin net', n, v)
    if errs:
        sys.exit(1)
    for s in d.sheets:
        d.write_sheet(s, os.path.join(OUT, s.filename))
    d.write_root(os.path.join(OUT, 'BEACON_PhoneModule.kicad_sch'), 'BEACON Phone Module')
    d.write_custom_lib(os.path.join(OUT, 'BEACON.kicad_sym'))
    parts.write_footprints(os.path.join(OUT, 'BEACON.pretty'))
    with open(os.path.join(OUT, 'sym-lib-table'), 'w', newline='\n') as f:
        f.write('(sym_lib_table\n\t(version 7)\n\t(lib (name "BEACON")(type "KiCad")'
                '(uri "${KIPRJMOD}/BEACON.kicad_sym")(options "")(descr "BEACON project symbols"))\n)\n')
    with open(os.path.join(OUT, 'fp-lib-table'), 'w', newline='\n') as f:
        f.write('(fp_lib_table\n\t(version 7)\n\t(lib (name "BEACON")(type "KiCad")'
                '(uri "${KIPRJMOD}/BEACON.pretty")(options "")(descr "BEACON project footprints"))\n)\n')
    pro = os.path.join(OUT, 'BEACON_PhoneModule.kicad_pro')
    if not os.path.exists(pro):
        with open(pro, 'w', newline='\n') as f:
            json.dump({'meta': {'filename': 'BEACON_PhoneModule.kicad_pro', 'version': 3},
                       'sheets': [[d.root_uuid, 'Root']] + [[s.uuid, s.name] for s in d.sheets]}, f, indent=2)
    n_parts = sum(1 for p in d.all_parts() if not p.ref.startswith('#'))
    print(f'wrote {len(d.sheets)} sheets, {n_parts} parts')


if __name__ == '__main__':
    build()
