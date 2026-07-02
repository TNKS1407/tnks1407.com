#!/usr/bin/env python3
"""TMC5240 daughterboard Rev.2b COMPACT — 50 x 36 mm, 4 layers (KiCad 7 / pcbnew API).

Same topology and J1/J3 pin order as Rev.2a. All corners mitered at 45 deg.
  F.Cu  : signals + GND pour
  In1.Cu: solid GND plane
  In2.Cu: 3V3 zone (left + bottom-center) + VS zone (right) + GND fill
  B.Cu  : ENC / CSN / REFL / REFR / DIAG0 / DIAG1 / UART_EN runs + GND pour

Run:  python3 generate_pcb_compact.py
"""
import pcbnew
from pcbnew import VECTOR2I, FromMM

FP_DIR = "/usr/share/kicad/footprints"
OUT = "tmc5240-daughterboard-compact"

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

# ---------------- placement (compact) ----------------
U1 = place("Package_DFN_QFN", "TQFN-32-1EP_5x5mm_P0.5mm_EP3.4x3.4mm_ThermalVias",
           "U1", "TMC5240ATJ+T", 25, 19.5, 0)
setnets(U1, {1:"IREF", 2:"GND", 3:"VDD1V8", 4:"GND", 5:"3V3", 6:"ENCN", 7:"ENCB",
             8:"ENCA", 9:"ENN", 10:"UART_EN", 11:"DIAG0", 12:"DIAG1",
             14:"CPI", 15:"CPO", 16:"VCP", 17:"VS", 18:"OUT1B", 19:"OUT2B",
             20:"VS", 21:"VS", 22:"OUT2A", 23:"OUT1A", 24:"VS", 25:"3V3",
             26:"CSN", 27:"SCK", 28:"SDI", 29:"SDO", 30:"GND", 31:"REFL",
             32:"REFR", 33:"GND"})

J1 = place("Connector_PinHeader_2.54mm", "PinHeader_1x12_P2.54mm_Vertical",
           "J1", "Pico 1x12", 4, 3.6, 0)
setnets(J1, {1:"GND", 2:"3V3", 3:"SCK", 4:"SDI", 5:"SDO", 6:"CSN", 7:"REFL",
             8:"REFR", 9:"ENN", 10:"DIAG0", 11:"DIAG1", 12:"GND"})

J2 = place("TerminalBlock", "TerminalBlock_bornier-2_P5.08mm", "J2", "+24V IN", 9.3, 4.5, 0)
setnets(J2, {1:"+24V_IN", 2:"GND"})

J3 = place("TerminalBlock", "TerminalBlock_bornier-4_P5.08mm", "J3", "MOTOR", 45.5, 12, -90)
setnets(J3, {1:"OUT1A", 2:"OUT2A", 3:"OUT2B", 4:"OUT1B"})

J4 = place("Connector_PinHeader_2.54mm", "PinHeader_1x05_P2.54mm_Vertical",
           "J4", "ENC 1x5", 17, 33.0, 90)
setnets(J4, {1:"3V3", 2:"ENCA", 3:"ENCB", 4:"ENCN", 5:"GND"})

F1 = place("Fuse", "Fuse_2920_7451Metric", "F1", "PPTC 3A/33V", 22.9, 4.5, 0)
setnets(F1, {1:"+24V_IN", 2:"24V_F"})

Q1 = place("Package_TO_SOT_SMD", "SOT-23", "Q1", "S-LP2408LT1G", 29.5, 4.5, 180)
setnets(Q1, {1:"Q1_G", 2:"VS", 3:"24V_F"})

D1 = place("Diode_SMD", "D_SMB", "D1", "SMBJ33A", 44.9, 6.7, 0)   # TVS: top-right, K=pad1 left
setnets(D1, {1:"VS", 2:"GND"})

D2 = place("Diode_SMD", "D_SOD-123", "D2", "BZT52C12", 32.75, 7, -90)
setnets(D2, {1:"VS", 2:"Q1_G"})

C1 = place("Capacitor_SMD", "CP_Elec_6.3x7.7", "C1", "100uF/35V", 37.55, 5.0, -90)
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

C2 = cap0805("C2", "1uF/50V",   38.3, 11.5, 0, "VS", "GND")
C3 = cap0805("C3", "1uF/50V",   31.5, 28.6, 0, "VS", "GND")
C4 = cap0603("C4", "100nF/50V", 34, 11.5, 0, "VS", "GND")
C5 = cap0603("C5", "100nF/50V", 35.5, 28.6, 0, "VS", "GND")
C6 = cap0603("C6", "22nF/50V",  26.6, 25.4, 0, "CPI", "CPO")
C7 = cap0805("C7", "1uF/50V",   29.6, 25.5, -90, "VCP", "VS")
C8 = cap0603("C8", "2.2uF",     16.6, 18.75, 0, "GND", "VDD1V8")
C9 = cap0603("C9", "100nF",     17.6, 21.5, -90, "3V3", "GND")

R1  = res0603("R1", "12k 1%", 19.9, 17.75, 0, "GND", "IREF")
R2  = res0603("R2", "10k", 7.35, 16.3, 0, "CSN", "3V3")
R3  = res0603("R3", "10k", 8.5, 23.92, 0, "ENN", "3V3")
R4  = res0603("R4", "10k", 7.35, 26.46, 0, "DIAG0", "3V3")
R5  = res0603("R5", "10k", 7.35, 29.0, 0, "DIAG1", "3V3")
R6  = res0603("R6", "10k", 9.2, 18.84, 0, "REFL", "GND")
R7  = res0603("R7", "10k", 9.2, 21.38, 0, "REFR", "GND")
R8  = res0603("R8", "10k", 30.1, 9.9, -90, "Q1_G", "GND")
R9  = res0603("R9", "10k", 19.0, 29.5, 0, "GND", "ENCA")
R10 = res0603("R10", "10k", 22.3, 29.5, 0, "GND", "ENCB")
R11 = res0603("R11", "10k", 25.6, 29.5, 0, "GND", "ENCN")

SJ1 = place("Jumper", "SolderJumper-3_P1.3mm_Bridged12_Pad1.0x1.5mm",
            "SJ1", "SPI/UART", 22.5, 26.9, 0)
setnets(SJ1, {1:"GND", 2:"UART_EN", 3:"3V3"})

H1 = place("MountingHole", "MountingHole_2.2mm_M2_DIN965_Pad", "H1", "M2", 47.3, 33.3, 0)
setnets(H1, {1: "GND"})
H2 = place("MountingHole", "MountingHole_2.2mm_M2_DIN965_Pad", "H2", "M2", 11.5, 33.6, 0)
setnets(H2, {1: "GND"})

assert abs(padpos(J1, 12)[1] - (3.6 + 11 * 2.54)) < 0.01
assert abs(padpos(J4, 5)[0] - (17 + 4 * 2.54)) < 0.01  # y=33.0
assert padpos(J3, 4)[1] > padpos(J3, 1)[1]
assert padpos(D1, 1)[0] < padpos(D1, 2)[0]  # K left (rot 0)
assert padpos(C1, 1)[1] < padpos(C1, 2)[1]
assert padpos(Q1, 3)[0] < padpos(Q1, 1)[0]

# ---------------- board outline ----------------
W, H = 50, 36
for (x1, y1, x2, y2) in [(0,0,W,0),(W,0,W,H),(W,H,0,H),(0,H,0,0)]:
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(mm(x1, y1)); s.SetEnd(mm(x2, y2))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(FromMM(0.1))
    board.Add(s)

F, B = pcbnew.F_Cu, pcbnew.B_Cu

def _seg(net, x1, y1, x2, y2, width, layer):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(mm(x1, y1)); t.SetEnd(mm(x2, y2))
    t.SetWidth(FromMM(width)); t.SetLayer(layer)
    t.SetNet(nets[net]); board.Add(t)

def track(net, pts, width=0.25, layer=F, miter=0.6):
    """Polyline with 45-deg mitered corners (chamfer up to `miter` mm)."""
    import math
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = out[-1], pts[i], pts[i + 1]
        d1 = (p1[0]-p0[0], p1[1]-p0[1]); d2 = (p2[0]-p1[0], p2[1]-p1[1])
        l1 = math.hypot(*d1); l2 = math.hypot(*d2)
        if l1 < 1e-6 or l2 < 1e-6:
            continue
        # only miter true corners (skip near-collinear)
        cosang = (d1[0]*d2[0]+d1[1]*d2[1])/(l1*l2)
        if cosang > 0.985:
            out.append(p1); continue
        c = min(miter, l1/2, l2/2)
        a = (p1[0]-d1[0]/l1*c, p1[1]-d1[1]/l1*c)
        b2 = (p1[0]+d2[0]/l2*c, p1[1]+d2[1]/l2*c)
        out.append(a); out.append(b2)
    out.append(pts[-1])
    for (x1, y1), (x2, y2) in zip(out, out[1:]):
        if abs(x1-x2) > 1e-6 or abs(y1-y2) > 1e-6:
            _seg(net, x1, y1, x2, y2, width, layer)

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
track("+24V_IN", [P(J2,1), (P(J2,1)[0], 7.6), (18.4, 7.6), (18.4, 4.9), P(F1,1)], 2.0, miter=1.2)
track("24V_F",  [P(F1,2), P(Q1,3)], 2.0)
qs = P(Q1, 2)
track("VS", [qs, (32.75, qs[1])], 1.2)
via("VS", 31.4, qs[1]); via("VS", 32.1, qs[1])
track("Q1_G", [P(Q1,1), P(R8,1)], 0.3)
track("Q1_G", [P(R8,1), (31.9, P(R8,1)[1]), (32.75, P(D2,2)[1]), P(D2,2)], 0.3)
track("GND",  [P(R8,2), (30.1, 11.6)], 0.3); via("GND", 30.1, 11.6)
track("VS", [P(D2,1), (32.75, qs[1])], 0.5)
track("VS",  [P(D1,1), (42.7, 5.5), (43.5, 5.5)], 1.0); via("VS", 42.7, 5.5); via("VS", 43.5, 5.5)
track("GND", [P(D1,2), (47.1, 5.5), (47.9, 5.5)], 1.0); via("GND", 47.1, 5.5); via("GND", 47.9, 5.5)
track("VS",  [P(C1,1), (36.35, 2.35), (36.35, 3.15)], 1.5); via("VS", 36.35, 2.35); via("VS", 36.35, 3.15)
track("GND", [P(C1,2), (36.35, 7.65), (36.35, 8.45)], 1.5); via("GND", 36.35, 7.65); via("GND", 36.35, 8.45)

# ---------------- U1 fanout: left column ----------------
p = {n: P(U1, n) for n in range(1, 33)}
track("IREF", [p[1], P(R1,2)], 0.25)
track("GND",  [P(R1,1), (18.35, 17.75)], 0.25); via("GND", 18.35, 17.75)
track("GND", [p[2], (21.9, p[2][1])], 0.2); via("GND", 21.9, p[2][1], 0.4, 0.2)
track("VDD1V8", [p[3], P(C8,2)], 0.25)
track("GND", [P(C8,1), (15.0, 18.75)], 0.25); via("GND", 15.0, 18.75)
track("GND", [p[4], (21.3, p[4][1])], 0.2); via("GND", 21.3, p[4][1], 0.4, 0.2)
track("3V3", [p[5], (17.6, p[5][1])], 0.3); via("3V3", 17.6, p[5][1])
track("3V3", [P(C9,1), (17.6, p[5][1])], 0.3)
track("GND", [P(C9,2), (17.6, 23.25)], 0.3); via("GND", 17.6, 23.25)
for pin, net, vx in [(6, "ENCN", 21.6), (7, "ENCB", 21.0), (8, "ENCA", 20.4)]:
    track(net, [p[pin], (vx, p[pin][1])], 0.2)
    via(net, vx, p[pin][1], 0.4, 0.2)
track("ENCN", [(21.6, p[6][1]), (21.6, 31.4), (P(J4,4)[0], 33.0)], 0.25, B)
track("ENCB", [(21.0, p[7][1]), (21.0, 31.4), (P(J4,3)[0], 33.0)], 0.25, B)
track("ENCA", [(20.4, p[8][1]), (20.4, 31.4), (P(J4,2)[0], 33.0)], 0.25, B)
track("ENCA", [P(R9,2),  P(J4,2)], 0.25)
track("ENCB", [P(R10,2), P(J4,3)], 0.25)
track("ENCN", [P(R11,2), P(J4,4)], 0.25)
track("GND", [P(R9,1),  (17.4, 29.5)], 0.25); via("GND", 17.4, 29.5)
track("GND", [P(R10,1), (22.6, 28.8), (22.6, 28.6)], 0.25); via("GND", 22.6, 28.6)
track("GND", [P(R11,1), (24.825, 28.6)], 0.25); via("GND", 24.825, 28.6)

# ---------------- U1 fanout: top row ----------------
track("3V3", [p[25], (p[25][0], 11.9), (20.0, 11.9)], 0.25, miter=0.3); via("3V3", 20.0, 11.9)
track("CSN", [p[26], (p[26][0], 12.6)], 0.25); via("CSN", p[26][0], 12.6, 0.4, 0.2)
track("CSN", [(p[26][0], 12.6), (5.2, 12.6), (5.2, P(J1,6)[1]), P(J1,6)], 0.25, B)
track("CSN", [P(R2,1), P(J1,6)], 0.25)
track("3V3", [P(R2,2), (8.7, 16.75), (8.7, 17.2)], 0.25); via("3V3", 8.7, 17.2)
track("SCK", [p[27], (p[27][0], 13.1), (9.5, 13.1), (9.5, P(J1,3)[1]), P(J1,3)], 0.25)
track("SDI", [p[28], (p[28][0], 13.6), (8.7, 13.6), (8.7, P(J1,4)[1]), P(J1,4)], 0.25)
track("SDO", [p[29], (p[29][0], 14.1), (7.9, 14.1), (7.9, P(J1,5)[1]), P(J1,5)], 0.25, miter=0.3)
track("GND", [p[30], (p[30][0], 14.8)], 0.2); via("GND", p[30][0], 14.8, 0.4, 0.2)
track("REFL", [p[31], (p[31][0], 15.3), (6.6, 15.3)], 0.25); via("REFL", 6.6, 15.3)
track("REFL", [(6.6, 15.3), (6.6, P(J1,7)[1]), P(J1,7)], 0.25, B)
track("REFL", [P(R6,1), P(J1,7)], 0.25)
track("GND", [P(R6,2), (10.9, 18.84)], 0.25); via("GND", 10.9, 18.84)
track("REFR", [p[32], (p[32][0], 16.0), (9.4, 16.0)], 0.25); via("REFR", 9.4, 16.0)
track("REFR", [(9.4, 16.0), (9.4, P(J1,8)[1]), P(J1,8)], 0.25, B)
track("REFR", [P(R7,1), P(J1,8)], 0.25)
track("GND", [P(R7,2), (10.9, 21.38)], 0.25); via("GND", 10.9, 21.38)

# ---------------- U1 fanout: bottom row ----------------
track("ENN",   [p[9],  (p[9][0], 24.75), (6.3, 24.75), (6.3, P(J1,9)[1]), P(J1,9)], 0.25)
track("ENN",   [P(R3,1), (6.3, P(J1,9)[1])], 0.25)
track("3V3",   [P(R3,2), (10.3, 23.92)], 0.25); via("3V3", 10.3, 23.92)
track("DIAG0", [p[11], (p[11][0], 25.25), (11.6, 25.25), (11.0, 25.85)], 0.25)
via("DIAG0", 11.0, 25.85)
track("DIAG0", [(11.0, 25.85), (11.0, 26.46), (5.0, 26.46), P(J1,10)], 0.25, B)
track("DIAG0", [P(R4,1), P(J1,10)], 0.25)
track("3V3",   [P(R4,2), (8.5, 26.46), (8.5, 25.85)], 0.25); via("3V3", 8.5, 25.85)
track("DIAG1", [p[12], (p[12][0], 25.75), (13.2, 25.75), (12.6, 26.35)], 0.25)
via("DIAG1", 12.6, 26.35)
track("DIAG1", [(12.6, 26.35), (12.6, 29.0), (5.0, 29.0), P(J1,11)], 0.25, B)
track("DIAG1", [P(R5,1), P(J1,11)], 0.25)
track("3V3",   [P(R5,2), (8.5, 29.0), (8.5, 28.4)], 0.25); via("3V3", 8.5, 28.4)
# UART_EN -> SJ1
track("UART_EN", [p[10], (p[10][0], 22.8)], 0.2); via("UART_EN", p[10][0], 22.8, 0.4, 0.2)
track("UART_EN", [(p[10][0], 22.8), (22.5, 26.35)], 0.25, B)
via("UART_EN", 22.5, 26.35)
track("UART_EN", [(22.5, 26.35), P(SJ1,2)], 0.25)
track("GND", [P(SJ1,1), (19.4, 26.9)], 0.25); via("GND", 19.4, 26.9)
track("3V3", [P(SJ1,3), (24.4, 26.45)], 0.25); via("3V3", 24.4, 26.45)
# charge pump
track("CPI", [p[14], P(C6,1)], 0.3)
track("CPO", [p[15], (p[15][0], 23.4), P(C6,2)], 0.3)
track("VCP", [p[16], (p[16][0], 22.9), (29.6, 23.9), P(C7,1)], 0.3)
track("VS",  [P(C7,2), (29.6, 27.3)], 0.5); via("VS", 29.6, 27.3)

# ---------------- U1 right column: VS + motor outputs ----------------
track("VS", [p[24], (28.9, 16.6)], 0.25)
via("VS", 28.9, 16.6)
track("VS", [p[20], (28.3, p[20][1])], 0.25)
track("VS", [p[21], (28.3, p[21][1])], 0.25)
track("VS", [(28.3, p[21][1]), (28.3, p[20][1])], 0.25)
track("VS", [(28.3, 19.5), (30.5, 19.5), (31.3, 19.4)], 0.5)
via("VS", 30.5, 19.5); via("VS", 31.3, 19.4)
track("VS", [p[17], (28.9, 21.9), (29.7, 21.9)], 0.25)
via("VS", 28.9, 21.9); via("VS", 29.7, 21.9)
for pin, net, jpin in [(23, "OUT1A", 1), (22, "OUT2A", 2), (19, "OUT2B", 3), (18, "OUT1B", 4)]:
    src = p[pin]
    tgt = P(J3, jpin)
    yat = lambda x: src[1] + (tgt[1] - src[1]) * (x - 29.9) / (41.5 - 29.9)
    track(net, [src, (29.9, src[1]), (30.9, yat(30.9))], 0.25)
    track(net, [(30.9, yat(30.9)), (32.9, yat(32.9))], 0.5)
    track(net, [(32.9, yat(32.9)), (41.5, tgt[1]), tgt], 1.0, miter=1.0)
track("VS",  [P(C4,1), (32.4, 11.5)], 0.4); via("VS", 32.4, 11.5)
track("GND", [P(C4,2), (35.7, 11.5)], 0.4); via("GND", 35.7, 11.5)
track("VS",  [P(C2,1), (36.5, 11.5)], 0.4); via("VS", 36.5, 11.5)
track("GND", [P(C2,2), (40.1, 11.5)], 0.4); via("GND", 40.1, 11.5)
track("VS",  [P(C3,1), (29.9, 28.6)], 0.4); via("VS", 29.9, 28.6)
track("GND", [P(C3,2), (33.1, 28.6)], 0.4); via("GND", 33.1, 28.6)
track("VS",  [P(C5,1), (34.0, 28.6)], 0.4); via("VS", 34.0, 28.6)
track("GND", [P(C5,2), (37.2, 28.6)], 0.4); via("GND", 37.2, 28.6)

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
zone("GND", pcbnew.In1_Cu, RECT(0.5, 0.5, 49.5, 35.5), 0, "gnd_in1")
zone("GND", pcbnew.In2_Cu, RECT(0.5, 0.5, 49.5, 35.5), 0, "gnd_in2")
zone("3V3", pcbnew.In2_Cu,
     [(1, 2), (21.5, 2), (21.5, 22.6), (26.5, 22.6), (26.5, 34.5), (1, 34.5)], 1, "3v3_in2")
zone("VS", pcbnew.In2_Cu, RECT(27.5, 1.2, 48.5, 29.5), 1, "vs_in2")
zone("GND", pcbnew.F_Cu, RECT(0.5, 0.5, 49.5, 35.5), 0, "gnd_f")
zone("GND", pcbnew.B_Cu, RECT(0.5, 0.5, 49.5, 35.5), 0, "gnd_b")

# keepout around SJ1 bridge graphic
ko = pcbnew.ZONE(board)
ko.SetIsRuleArea(True)
ko.SetDoNotAllowCopperPour(True)
ko.SetDoNotAllowTracks(False)
ko.SetDoNotAllowPads(False)
ko.SetDoNotAllowFootprints(False)
ko.SetDoNotAllowVias(False)
ko.SetLayer(pcbnew.F_Cu)
_ol = ko.Outline(); _ol.NewOutline()
for (x, y) in [(20.3, 25.9), (25.0, 25.9), (25.0, 27.9), (20.3, 27.9)]:
    _ol.Append(FromMM(x), FromMM(y))
board.Add(ko)

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
    silk(lab, 12.4, 3.6 + 2.54 * i, 0.7)
for i, lab in enumerate(["A1", "A2", "B2", "B1"]):
    silk(lab, 43.6, 12 + 5.08 * i, 0.8)
silk("+24V", 9.5, 9.4, 0.8); silk("GND", 14.6, 9.4, 0.8)
for i, lab in enumerate(["3V", "A", "B", "N", "G"]):
    silk(lab, 17 + 2.54 * i, 35.1, 0.7)
silk("SPI", 19.2, 25.4, 0.6); silk("UART", 25.9, 25.4, 0.6)
silk("TMC5240 Rev.2b", 40, 33.2, 0.9)
silk("24V 1.5Arms", 40, 34.8, 0.8)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
pcbnew.SaveBoard(OUT + ".kicad_pcb", board)
print("saved; footprints:", len(board.GetFootprints()), "tracks:", len(board.GetTracks()))
