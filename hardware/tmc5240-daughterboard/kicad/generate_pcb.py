#!/usr/bin/env python3
"""TMC5240 daughterboard — programmatic PCB generation (KiCad 7 / pcbnew API).

Board: 60 x 42 mm, 4 layers:
  F.Cu  : signals + GND pour
  In1.Cu: solid GND plane
  In2.Cu: 3V3 zone (left + bottom-center) + VS zone (right) + GND fill
  B.Cu  : a few signal runs (ENC, CSN, REFL/R, UART_EN) + GND pour

J1 pin order chosen for crossing-free escape:
  1 GND, 2 3V3, 3 SCK, 4 SDI, 5 SDO, 6 CSN, 7 REFL, 8 REFR,
  9 ENN, 10 DIAG0, 11 DIAG1, 12 GND
J3 pin order: 1 OUT1A, 2 OUT2A, 3 OUT2B, 4 OUT1B (A1 A2 B2 B1)

Run:  python3 generate_pcb.py
"""
import pcbnew
from pcbnew import VECTOR2I, FromMM

FP_DIR = "/usr/share/kicad/footprints"
OUT = "tmc5240-daughterboard"

board = pcbnew.NewBoard(OUT + ".kicad_pcb")
board.SetCopperLayerCount(4)

NET_NAMES = ["+24V_IN", "24V_F", "VS", "GND", "3V3", "Q1_G",
             "SCK", "SDI", "SDO", "CSN", "ENN", "DIAG0", "DIAG1",
             "REFL", "REFR", "ENCA", "ENCB", "ENCN", "UART_EN",
             "IREF", "VDD1V8", "CPI", "CPO", "VCP",
             "OUT1A", "OUT2A", "OUT1B", "OUT2B"]
nets = {}
for n in NET_NAMES:
    ni = pcbnew.NETINFO_ITEM(board, n)
    board.Add(ni)
    nets[n] = ni

def mm(x, y):
    return VECTOR2I(FromMM(x), FromMM(y))

def place(lib, name, ref, value, x, y, rot=0):
    fp = pcbnew.FootprintLoad(f"{FP_DIR}/{lib}.pretty", name)
    assert fp, f"footprint {lib}/{name} not found"
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(mm(x, y))
    fp.SetOrientationDegrees(rot)
    board.Add(fp)
    return fp

def setnets(fp, mapping):
    for padnum, netname in mapping.items():
        found = False
        for pad in fp.Pads():
            if pad.GetNumber() == str(padnum):
                pad.SetNet(nets[netname])
                found = True
        assert found, f"{fp.GetReference()} pad {padnum} missing"

def padpos(fp, num):
    for pad in fp.Pads():
        if pad.GetNumber() == str(num):
            p = pad.GetPosition()
            return (pcbnew.ToMM(p.x), pcbnew.ToMM(p.y))
    raise KeyError(num)

# rotation notes (KiCad7, checked): two-pad parts rot -90 -> pad1 UP;
# pin headers rot 0 -> pins run +y (down); rot 90 -> pins run +x.

U1 = place("Package_DFN_QFN", "TQFN-32-1EP_5x5mm_P0.5mm_EP3.4x3.4mm_ThermalVias",
           "U1", "TMC5240ATJ+T", 28, 22, 0)
setnets(U1, {1:"IREF", 2:"GND", 3:"VDD1V8", 4:"GND", 5:"3V3", 6:"ENCN", 7:"ENCB",
             8:"ENCA", 9:"ENN", 10:"UART_EN", 11:"DIAG0", 12:"DIAG1",
             14:"CPI", 15:"CPO", 16:"VCP", 17:"VS", 18:"OUT1B", 19:"OUT2B",
             20:"VS", 21:"VS", 22:"OUT2A", 23:"OUT1A", 24:"VS", 25:"3V3",
             26:"CSN", 27:"SCK", 28:"SDI", 29:"SDO", 30:"GND", 31:"REFL",
             32:"REFR", 33:"GND"})   # pad13 OV left unconnected

J1 = place("Connector_PinHeader_2.54mm", "PinHeader_1x12_P2.54mm_Vertical",
           "J1", "Pico 1x12", 4, 5, 0)
setnets(J1, {1:"GND", 2:"3V3", 3:"SCK", 4:"SDI", 5:"SDO", 6:"CSN", 7:"REFL",
             8:"REFR", 9:"ENN", 10:"DIAG0", 11:"DIAG1", 12:"GND"})

J2 = place("TerminalBlock", "TerminalBlock_bornier-2_P5.08mm", "J2", "+24V IN", 12, 4.5, 0)
setnets(J2, {1:"+24V_IN", 2:"GND"})

J3 = place("TerminalBlock", "TerminalBlock_bornier-4_P5.08mm", "J3", "MOTOR", 55.5, 12, -90)
setnets(J3, {1:"OUT1A", 2:"OUT2A", 3:"OUT2B", 4:"OUT1B"})

J4 = place("Connector_PinHeader_2.54mm", "PinHeader_1x05_P2.54mm_Vertical",
           "J4", "ENC 1x5", 20, 38.5, 90)
setnets(J4, {1:"3V3", 2:"ENCA", 3:"ENCB", 4:"ENCN", 5:"GND"})

F1 = place("Fuse", "Fuse_2920_7451Metric", "F1", "PPTC 3A/33V", 24.6, 4.5, 0)
setnets(F1, {1:"+24V_IN", 2:"24V_F"})

Q1 = place("Package_TO_SOT_SMD", "SOT-23", "Q1", "S-LP2408LT1G", 32.5, 4.5, 180)
setnets(Q1, {1:"Q1_G", 2:"VS", 3:"24V_F"})

D1 = place("Diode_SMD", "D_SMB", "D1", "SMBJ33A", 41, 6.5, -90)     # pad1=K up
setnets(D1, {1:"VS", 2:"GND"})

D2 = place("Diode_SMD", "D_SOD-123", "D2", "BZT52C12", 36.5, 7.5, -90)  # pad1=K up
setnets(D2, {1:"VS", 2:"Q1_G"})

C1 = place("Capacitor_SMD", "CP_Elec_6.3x7.7", "C1", "100uF/35V", 47, 8, -90)  # pad1=+ up
setnets(C1, {1:"VS", 2:"GND"})

def part(lib, fpname, ref, val, x, y, rot, n1, n2):
    fp = place(lib, fpname, ref, val, x, y, rot)
    setnets(fp, {1: n1, 2: n2})
    return fp

def cap0603(ref, val, x, y, rot, n1, n2):
    return part("Capacitor_SMD", "C_0603_1608Metric", ref, val, x, y, rot, n1, n2)

def cap0805(ref, val, x, y, rot, n1, n2):
    return part("Capacitor_SMD", "C_0805_2012Metric", ref, val, x, y, rot, n1, n2)

def res0603(ref, val, x, y, rot, n1, n2):
    return part("Resistor_SMD", "R_0603_1608Metric", ref, val, x, y, rot, n1, n2)

C2 = cap0805("C2", "1uF/50V",   39, 13, 0, "VS", "GND")
C3 = cap0805("C3", "1uF/50V",   32.5, 30.5, 0, "VS", "GND")
C4 = cap0603("C4", "100nF/50V", 34, 13, 0, "VS", "GND")
C5 = cap0603("C5", "100nF/50V", 37, 30.5, 0, "VS", "GND")
C6 = cap0603("C6", "22nF/50V",  29.3, 27.4, 0, "CPI", "CPO")       # pad1 left = CPI
C7 = cap0805("C7", "1uF/50V",   32.1, 27.5, -90, "VCP", "VS")      # pad1 up = VCP
C8 = cap0603("C8", "2.2uF",     19.9, 21.25, 0, "GND", "VDD1V8")   # pad2 right -> pin3
C9 = cap0603("C9", "100nF",     21.0, 24.0, -90, "3V3", "GND")     # pad1 up

R1  = res0603("R1", "12k 1%", 22.9, 20.25, 0, "GND", "IREF")       # pad2 right, inline pin1
R2  = res0603("R2", "10k", 6.6, 15.2, -90, "3V3", "CSN")   # pad1 up
R3  = res0603("R3", "10k", 8.5, 25.32, 0, "ENN", "3V3")
R4  = res0603("R4", "10k", 7.35, 27.86, 0, "DIAG0", "3V3")         # pad1 left -> J1.10
R5  = res0603("R5", "10k", 7.35, 30.4, 0, "DIAG1", "3V3")          # pad1 left -> J1.11
R6  = res0603("R6", "10k", 8.5, 20.24, 0, "REFL", "GND")
R7  = res0603("R7", "10k", 8.5, 22.78, 0, "REFR", "GND")
R8  = res0603("R8", "10k", 33.6, 10.2, -90, "Q1_G", "GND")         # pad1 up
R9  = res0603("R9", "10k", 22.54, 34.8, -90, "GND", "ENCA")
R10 = res0603("R10", "10k", 25.08, 34.8, -90, "GND", "ENCB")
R11 = res0603("R11", "10k", 27.62, 34.8, -90, "GND", "ENCN")

SJ1 = place("Jumper", "SolderJumper-3_P1.3mm_Bridged12_Pad1.0x1.5mm",
            "SJ1", "SPI/UART", 26.75, 31.6, 0)
setnets(SJ1, {1:"GND", 2:"UART_EN", 3:"3V3"})

for i, (hx, hy) in enumerate([(3.2, 38.8), (56.8, 38.8), (56.8, 3.2)], 1):
    h = place("MountingHole", "MountingHole_2.7mm_M2.5_Pad", f"H{i}", "M2.5", hx, hy, 0)
    setnets(h, {1: "GND"})

assert abs(padpos(J1, 12)[1] - (5 + 11 * 2.54)) < 0.01, f"J1 dir {padpos(J1,12)}"
assert abs(padpos(J4, 5)[0] - (20 + 4 * 2.54)) < 0.01, f"J4 dir {padpos(J4,5)}"
assert padpos(J3, 4)[1] > padpos(J3, 1)[1], f"J3 dir {padpos(J3,4)}"
assert padpos(D1, 1)[1] < padpos(D1, 2)[1], "D1 pad1 must be up"
assert padpos(C1, 1)[1] < padpos(C1, 2)[1], "C1 pad1 must be up"
assert padpos(Q1, 3)[0] < padpos(Q1, 1)[0], "Q1 drain must face left"
cty = J3.GetCourtyard(pcbnew.F_CrtYd).BBox()
print("J3 courtyard x:", pcbnew.ToMM(cty.GetLeft()), "-", pcbnew.ToMM(cty.GetRight()))

# ---------------- board outline ----------------
W, H = 60, 42
for (x1, y1, x2, y2) in [(0,0,W,0),(W,0,W,H),(W,H,0,H),(0,H,0,0)]:
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(mm(x1, y1)); s.SetEnd(mm(x2, y2))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(FromMM(0.1))
    board.Add(s)

F, B = pcbnew.F_Cu, pcbnew.B_Cu

def track(net, pts, width=0.25, layer=F):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(mm(x1, y1)); t.SetEnd(mm(x2, y2))
        t.SetWidth(FromMM(width)); t.SetLayer(layer)
        t.SetNet(nets[net]); board.Add(t)

def via(net, x, y, dia=0.6, drill=0.3):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(mm(x, y))
    v.SetWidth(FromMM(dia)); v.SetDrill(FromMM(drill))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(nets[net]); board.Add(v)

def P(fp, n):
    return padpos(fp, n)

# ---------------- power input chain ----------------
track("+24V_IN", [P(J2,1), (P(J2,1)[0], 8.2), (22, 8.2), (22, 4.9), P(F1,1)], 2.0)
track("24V_F",  [P(F1,2), P(Q1,3)], 2.0)
qs = P(Q1, 2)
track("VS", [qs, (36.5, qs[1])], 1.2)
via("VS", 35.5, qs[1]); via("VS", 36.3, qs[1])
qg = P(Q1, 1)
track("Q1_G", [qg, P(R8,1)], 0.3)
track("Q1_G", [P(R8,1), (35.5, P(R8,1)[1]), (36.5, P(D2,2)[1]), P(D2,2)], 0.3)
track("GND",  [P(R8,2), (33.6, 11.9)], 0.3); via("GND", 33.6, 11.9)
track("VS", [P(D2,1), (36.5, qs[1])], 0.5)
track("VS",  [P(D1,1), (41, 3.0), (41.8, 3.0)], 1.0); via("VS", 41, 3.0); via("VS", 41.8, 3.0)
track("GND", [P(D1,2), (41, 9.8), (41.8, 9.8)], 1.0); via("GND", 41, 9.8); via("GND", 41.8, 9.8)
track("VS",  [P(C1,1), (47, 4.0), (47.8, 4.0)], 1.5); via("VS", 47, 4.0); via("VS", 47.8, 4.0)
track("GND", [P(C1,2), (47, 11.6), (47.8, 11.6)], 1.5); via("GND", 47, 11.6); via("GND", 47.8, 11.6)

# ---------------- U1 fanout: left column (pins 1-8) ----------------
p = {n: P(U1, n) for n in range(1, 33)}
track("IREF", [p[1], P(R1,2)], 0.25)
track("GND",  [P(R1,1), (20.9, 20.25)], 0.25); via("GND", 20.9, 20.25)
track("GND", [p[2], (24.9, p[2][1])], 0.2); via("GND", 24.9, p[2][1], 0.4, 0.2)
track("GND", [p[4], (24.3, p[4][1])], 0.2); via("GND", 24.3, p[4][1], 0.4, 0.2)
track("VDD1V8", [p[3], P(C8,2)], 0.25)
track("GND", [P(C8,1), (18.3, 21.25)], 0.25); via("GND", 18.3, 21.25)
track("3V3", [p[5], (21.0, p[5][1])], 0.3); via("3V3", 21.0, p[5][1])
track("3V3", [P(C9,1), (21.0, p[5][1])], 0.3)
track("GND", [P(C9,2), (21.0, 25.75)], 0.3); via("GND", 21.0, 25.75)
for pin, net, vx in [(6, "ENCN", 24.6), (7, "ENCB", 24.0), (8, "ENCA", 23.4)]:
    track(net, [p[pin], (vx, p[pin][1])], 0.2)
    via(net, vx, p[pin][1], 0.4, 0.2)
track("ENCN", [(24.6, p[6][1]), (24.6, 36.4), (P(J4,4)[0], 38.5)], 0.25, B)
track("ENCB", [(24.0, p[7][1]), (24.0, 36.4), (P(J4,3)[0], 38.5)], 0.25, B)
track("ENCA", [(23.4, p[8][1]), (23.4, 36.4), (P(J4,2)[0], 38.5)], 0.25, B)
track("ENCA", [P(R9,2),  P(J4,2)], 0.25)
track("ENCB", [P(R10,2), P(J4,3)], 0.25)
track("ENCN", [P(R11,2), P(J4,4)], 0.25)
track("GND", [P(R9,1),  (22.54, 33.1)], 0.25); via("GND", 22.54, 33.1)
track("GND", [P(R10,1), (25.7, 33.2)], 0.25);  via("GND", 25.7, 33.2)
track("GND", [P(R11,1), (27.62, 33.1)], 0.25); via("GND", 27.62, 33.1)

# ---------------- U1 fanout: top row (pins 25-32) ----------------
track("3V3", [p[25], (p[25][0], 14.6), (23.0, 14.6)], 0.25); via("3V3", 23.0, 14.6)
track("CSN", [p[26], (p[26][0], 15.1)], 0.25); via("CSN", p[26][0], 15.1, 0.4, 0.2)
track("CSN", [(p[26][0], 15.1), (27.0, 17.7), P(J1,6)], 0.25, B)
track("CSN", [P(R2,2), (6.6, 17.0), P(J1,6)], 0.25)
track("3V3", [P(R2,1), (6.6, 13.5)], 0.25); via("3V3", 6.6, 13.5)
track("SCK", [p[27], (p[27][0], 15.6), (9.5, 15.6), (9.5, P(J1,3)[1]), P(J1,3)], 0.25)
track("SDI", [p[28], (p[28][0], 16.1), (8.7, 16.1), (8.7, P(J1,4)[1]), P(J1,4)], 0.25)
track("SDO", [p[29], (p[29][0], 16.6), (7.9, 16.6), (7.9, P(J1,5)[1]), P(J1,5)], 0.25)
track("GND", [p[30], (p[30][0], 17.2), (26.4, 17.2)], 0.2); via("GND", 26.4, 17.2, 0.4, 0.2)
track("REFL", [p[31], (p[31][0], 18.5), (6.6, 18.5)], 0.25); via("REFL", 6.6, 18.5)
track("REFL", [(6.6, 18.5), (6.6, P(J1,7)[1]), P(J1,7)], 0.25, B)
track("REFL", [P(R6,1), P(J1,7)], 0.25)
track("GND", [P(R6,2), (10.3, 20.24)], 0.25); via("GND", 10.3, 20.24)
track("REFR", [p[32], (p[32][0], 19.3), (9.4, 19.3)], 0.25); via("REFR", 9.4, 19.3)
track("REFR", [(9.4, 19.3), (9.4, 21.0), (8.8, 21.6), (8.8, P(J1,8)[1]), P(J1,8)], 0.25, B)
track("REFR", [P(R7,1), P(J1,8)], 0.25)
track("GND", [P(R7,2), (10.3, 22.78)], 0.25); via("GND", 10.3, 22.78)

# ---------------- U1 fanout: bottom row (pins 9-16) ----------------
track("ENN",   [p[9],  (p[9][0], 26.8), (6.3, 26.8), (6.3, P(J1,9)[1]), P(J1,9)], 0.25)
track("ENN",   [P(R3,1), (6.3, P(J1,9)[1])], 0.25)
track("3V3",   [P(R3,2), (10.3, 25.32)], 0.25); via("3V3", 10.3, 25.32)
track("DIAG0", [p[11], (p[11][0], 27.3), (11.6, 27.3), (11.0, 27.9)], 0.25)
via("DIAG0", 11.0, 27.9)
track("DIAG0", [(11.0, 27.9), (11.0, 28.4), (5.0, 28.4), P(J1,10)], 0.25, B)
track("DIAG0", [P(R4,1), P(J1,10)], 0.25)
track("3V3",   [P(R4,2), (8.5, 27.86), (8.5, 27.4)], 0.25); via("3V3", 8.5, 27.4)
track("DIAG1", [p[12], (p[12][0], 27.8), (13.2, 27.8), (12.6, 28.4)], 0.25)
via("DIAG1", 12.6, 28.4)
track("DIAG1", [(12.6, 28.4), (12.6, 30.9), (5.0, 30.9), P(J1,11)], 0.25, B)
track("DIAG1", [P(R5,1), P(J1,11)], 0.25)
track("3V3",   [P(R5,2), (8.5, 30.4), (8.5, 29.9)], 0.25); via("3V3", 8.5, 29.9)
# UART_EN via B.Cu down to SJ1
track("UART_EN", [p[10], (p[10][0], 25.3)], 0.2); via("UART_EN", p[10][0], 25.3, 0.4, 0.2)
track("UART_EN", [(p[10][0], 25.3), (26.75, 30.9)], 0.25, B)
via("UART_EN", 26.75, 30.9)
track("UART_EN", [(26.75, 30.9), P(SJ1,2)], 0.25)
track("GND", [P(SJ1,1), (25.45, 30.7)], 0.25); via("GND", 25.45, 30.7)
track("3V3", [P(SJ1,3), (28.75, 32.4)], 0.25); via("3V3", 28.75, 32.4)
# charge pump
track("CPO", [p[15], (29.25, 25.6), P(C6,2)], 0.3)
track("CPI", [p[14], P(C6,1)], 0.3)
track("VCP", [p[16], (p[16][0], 24.9), (32.1, 25.85), P(C7,1)], 0.3)
track("VS",  [P(C7,2), (32.1, 29.3)], 0.5); via("VS", 32.1, 29.3)

# ---------------- U1 right column: VS + motor outputs ----------------
track("VS", [p[24], (31.5, 19.6)], 0.25)
via("VS", 31.5, 19.6)
track("VS", [p[20], (31.0, p[20][1])], 0.25)
track("VS", [p[21], (31.0, p[21][1])], 0.25)
track("VS", [(31.0, p[21][1]), (31.0, p[20][1])], 0.25)
track("VS", [(31.0, 22.0), (34.3, 22.0), (35.1, 21.9)], 0.5)
via("VS", 34.3, 22.0); via("VS", 35.1, 21.9)
track("VS", [p[17], (31.5, 24.5), (32.3, 24.5)], 0.25)
via("VS", 31.5, 24.5); via("VS", 32.3, 24.5)
for pin, net, jpin in [(23, "OUT1A", 1), (22, "OUT2A", 2), (19, "OUT2B", 3), (18, "OUT1B", 4)]:
    src = p[pin]
    tgt = P(J3, jpin)
    yat = lambda x: src[1] + (tgt[1] - src[1]) * (x - 33) / (52 - 33)
    track(net, [src, (33, src[1]), (34, yat(34))], 0.25)
    track(net, [(34, yat(34)), (36.5, yat(36.5))], 0.5)
    track(net, [(36.5, yat(36.5)), (52, tgt[1]), tgt], 1.0)
track("VS",  [P(C4,1), (32.5, 13)], 0.4); via("VS", 32.5, 13)
track("GND", [P(C4,2), (35.7, 13)], 0.4); via("GND", 35.7, 13)
track("VS",  [P(C2,1), (37.5, 13)], 0.4); via("VS", 37.5, 13)
track("GND", [P(C2,2), (40.7, 13)], 0.4); via("GND", 40.7, 13)
track("VS",  [P(C3,1), (31.0, 30.5)], 0.4); via("VS", 31.0, 30.5)
track("GND", [P(C3,2), (34.2, 30.5)], 0.4); via("GND", 34.2, 30.5)
track("VS",  [P(C5,1), (35.3, 30.5)], 0.4); via("VS", 35.3, 30.5)
track("GND", [P(C5,2), (38.7, 30.5)], 0.4); via("GND", 38.7, 30.5)

# ---------------- zones ----------------
def zone(netname, layer, pts, priority=0, name=""):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(nets[netname])
    z.SetAssignedPriority(priority)
    z.SetZoneName(name)
    z.SetMinThickness(FromMM(0.2))
    z.SetLocalClearance(FromMM(0.3))
    z.SetThermalReliefGap(FromMM(0.25))
    z.SetThermalReliefSpokeWidth(FromMM(0.4))
    ol = z.Outline()
    ol.NewOutline()
    for (x, y) in pts:
        ol.Append(FromMM(x), FromMM(y))
    board.Add(z)
    return z

RECT = lambda x1, y1, x2, y2: [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
zone("GND", pcbnew.In1_Cu, RECT(0.5, 0.5, 59.5, 41.5), 0, "gnd_in1")
zone("GND", pcbnew.In2_Cu, RECT(0.5, 0.5, 59.5, 41.5), 0, "gnd_in2")
zone("3V3", pcbnew.In2_Cu,
     [(1, 2), (24.5, 2), (24.5, 24.4), (30.0, 24.4), (30.0, 41), (1, 41)], 1, "3v3_in2")
zone("VS", pcbnew.In2_Cu, RECT(30.5, 2, 59, 32), 1, "vs_in2")
zone("GND", pcbnew.F_Cu, RECT(0.5, 0.5, 59.5, 41.5), 0, "gnd_f")
zone("GND", pcbnew.B_Cu, RECT(0.5, 0.5, 59.5, 41.5), 0, "gnd_b")

# ---------------- silkscreen ----------------
def silk(text, x, y, size=0.8, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(mm(x, y))
    t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
    t.SetTextThickness(FromMM(0.15))
    board.Add(t)

labels = ["GND", "3V3", "SCK", "SDI", "SDO", "CSN", "RFL", "RFR", "ENN", "DG0", "DG1", "GND"]
for i, lab in enumerate(labels):
    silk(lab, 6.9, 5 + 2.54 * i, 0.7)
for i, lab in enumerate(["A1", "A2", "B2", "B1"]):
    silk(lab, 50.4, 12 + 5.08 * i, 0.8)
silk("+24V", 12, 10.4, 0.8); silk("GND", 17.1, 10.4, 0.8)
for i, lab in enumerate(["3V", "A", "B", "N", "G"]):
    silk(lab, 20 + 2.54 * i, 41.0, 0.7)
silk("SPI", 23.4, 32.2, 0.6); silk("UART", 30.4, 32.2, 0.6)
silk("TMC5240 daughter Rev.2", 46, 34.5, 1.0)
silk("24V 1.5Arms", 46, 36.3, 0.9)

ko = pcbnew.ZONE(board)
ko.SetIsRuleArea(True)
ko.SetDoNotAllowCopperPour(True)
ko.SetDoNotAllowTracks(False)
ko.SetDoNotAllowPads(False)
ko.SetDoNotAllowFootprints(False)
ko.SetDoNotAllowVias(False)
ko.SetLayer(pcbnew.F_Cu)
_ol = ko.Outline(); _ol.NewOutline()
for (x, y) in [(24.9, 30.6), (28.7, 30.6), (28.7, 32.7), (24.9, 32.7)]:
    _ol.Append(FromMM(x), FromMM(y))
board.Add(ko)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
pcbnew.SaveBoard(OUT + ".kicad_pcb", board)
print("saved; footprints:", len(board.GetFootprints()), "tracks:", len(board.GetTracks()))
