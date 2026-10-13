# DNR egységes app-ikonok (v10.423) — a DNR Games ikon nyelvén.
# Futtatás: python3 make_unified_icons.py   → két fájl appanként az assets/-ba:
#   dnr_<app>_app.png   — 1024×1024, FEHÉR háttér (főképernyő-ikon, manifest, központ, admin)
#   dnr_<app>_mark.png  — 512×512, ÁTLÁTSZÓ háttér (nyitókép, az app saját oldalai)
# A Games ikonja (dnr_games_icon.png) a kiindulás — azt ez a szkript NEM írja.
# Közös keret: kék|narancs félkör háttér, talajvonal, vastag fekete kontúr,
# fehér „matrica"-sáv a tárgy és a háttér között. 2048-on rajzol, 1024-re kicsinyít.
import math, sys, os
from PIL import Image, ImageDraw, ImageFilter
S = 2048
INK = (10, 12, 14, 255); WHITE = (255, 255, 255, 255)
BLUE = (134, 167, 202, 255); ORANGE = (253, 170, 69, 255)
YELLOW = (253, 205, 101, 255); AMBER = (247, 174, 66, 255); WINE = (140, 42, 52, 255)
CREAM = (255, 247, 232, 255); ICE = (213, 226, 240, 255); CORAL = (232, 120, 96, 255)
GREEN = (96, 160, 110, 255); GREY = (70, 74, 82, 255)
LW = 44            # kontúr
GROUND = 1700

def background(base=WHITE):
    im = Image.new('RGBA', (S, S), base)
    d = ImageDraw.Draw(im)
    cx, cy, r = 1024, 1300, 800
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 270, fill=BLUE)
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 270, 360, fill=ORANGE)
    d.rectangle([cx - r, cy, cx + r, cy + r], fill=None)
    # alsó rész: a félkör a talajig ér (mint a Games-nél)
    d.rectangle([cx - r, cy, cx, GROUND], fill=BLUE)
    d.rectangle([cx, cy, cx + r, GROUND], fill=ORANGE)
    # a két alsó sarok lekerekítve (a kör folytatása)
    mask = Image.new('L', (S, S), 0); md = ImageDraw.Draw(mask)
    md.ellipse([cx - r, cy - r - 120, cx + r, cy + r + 120], fill=255)
    md.rectangle([0, GROUND, S, S], fill=0)
    out = Image.new('RGBA', (S, S), base); out.paste(im, (0, 0), mask)
    return out

def finish(obj, name, ground=True, gap=34):
    a = obj.split()[3]
    dil = a.filter(ImageFilter.GaussianBlur(gap * 0.55)).point(lambda v: 255 if v > 12 else 0)
    for base, suffix in ((WHITE, 'app'), ((255, 255, 255, 0), 'mark')):
        bg = background(base)
        bg.paste(Image.new('RGBA', (S, S), WHITE), (0, 0), dil)   # fehér „matrica"-sáv
        d = ImageDraw.Draw(bg)
        if ground:
            d.rounded_rectangle([240, GROUND - 4, S - 240, GROUND + 38], radius=21, fill=INK)
        bg.alpha_composite(obj)
        if suffix == 'app':
            out = bg.resize((1024, 1024), Image.LANCZOS).convert('RGB').quantize(128, method=Image.MEDIANCUT)
        else:
            out = bg.resize((512, 512), Image.LANCZOS).quantize(128, method=Image.FASTOCTREE)
        out.save(os.path.join(OUT, 'dnr_%s_%s.png' % (name, suffix)), optimize=True)

def layer():
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)

def rr(d, box, r, fill, w=LW):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=INK, width=w)

def poly(d, pts, fill, w=LW):
    d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=INK, width=w, joint='curve')
    for p in pts: d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=INK)

def line(d, a, b, w=LW, fill=INK):
    d.line([a, b], fill=fill, width=w)
    for p in (a, b): d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=fill)

def circ(d, cx, cy, r, fill, w=LW):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=INK, width=w)

# ── DNR Events: naptár + koccintó pohár
def events():
    im, d = layer()
    rr(d, [430, 560, 1500, 1660], 90, CREAM)
    # piros fejléc
    hd = Image.new('RGBA', (S, S), (0, 0, 0, 0)); hdd = ImageDraw.Draw(hd)
    hdd.rounded_rectangle([430, 560, 1500, 1660], radius=90, fill=WINE)
    m = Image.new('L', (S, S), 0); ImageDraw.Draw(m).rectangle([0, 0, S, 860], fill=255)
    im.paste(hd, (0, 0), Image.composite(hd.split()[3], Image.new('L', (S, S), 0), m))
    d.rounded_rectangle([430, 560, 1500, 1660], radius=90, outline=INK, width=LW)
    line(d, (452, 860), (1478, 860))
    for x in (640, 1290):
        rr(d, [x - 38, 440, x + 38, 660], 38, CREAM)
    # rács: 4×3 nap, egy kiemelt (sárga)
    for r_ in range(3):
        for c in range(4):
            x0 = 540 + c * 225; y0 = 960 + r_ * 210
            hot = (r_ == 1 and c == 2)
            d.rounded_rectangle([x0, y0, x0 + 150, y0 + 140], radius=28, fill=YELLOW if hot else ICE, outline=INK if hot else None, width=LW if hot else 0)
    # pezsgős pohár jobb lent
    g = [(1460, 1180), (1760, 1180), (1700, 1430), (1520, 1430)]
    poly(d, g, AMBER)
    line(d, (1610, 1440), (1610, 1640))
    line(d, (1520, 1650), (1700, 1650))
    for (x, y, rad) in [(1560, 1260, 16), (1640, 1320, 13), (1600, 1220, 11)]:
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=CREAM)
    finish(im, 'events')

# ── DNR a tortán: tálaló búra tányéron + villa/kés
def torta():
    im, d = layer()
    d.ellipse([380, 1520, 1670, 1680], fill=CREAM, outline=INK, width=LW)            # tányér
    d.ellipse([560, 1555, 1490, 1640], outline=INK, width=24)
    d.pieslice([500, 900, 1550, 1950], 180, 360, fill=ICE, outline=INK, width=LW)    # búra
    rr(d, [450, 1390, 1600, 1470], 40, YELLOW)                                       # perem
    circ(d, 1025, 840, 78, YELLOW)                                                  # fogantyú
    d.arc([640, 1040, 1150, 1550], 205, 245, fill=WHITE, width=44)                   # csillanás
    rr(d, [200, 1060, 290, 1650], 45, CREAM)                                         # villa
    rr(d, [150, 900, 340, 1100], 60, CREAM)
    for x in (180, 245, 310): line(d, (x, 760), (x, 960), w=40)
    poly(d, [(1760, 760), (1860, 760), (1860, 1180), (1760, 1180)], CREAM)          # kés
    d.pieslice([1760, 660, 1960, 860], 180, 270, fill=CREAM, outline=INK, width=LW)
    rr(d, [1750, 1160, 1870, 1650], 55, WINE)
    finish(im, 'torta')

# ── DNR Tipp: focilabda + szelvény pipákkal
def tipp():
    im, d = layer()
    # szelvény (balra döntve)
    tk = Image.new('RGBA', (S, S), (0, 0, 0, 0)); td = ImageDraw.Draw(tk)
    td.rounded_rectangle([420, 560, 1120, 1560], radius=60, fill=CREAM, outline=INK, width=LW)
    for i in range(4):
        y = 700 + i * 200
        td.rounded_rectangle([510, y, 610, y + 100], radius=22, fill=YELLOW if i != 2 else WHITE, outline=INK, width=34)
        td.line([(660, y + 50), (1010, y + 50)], fill=INK, width=34)
        if i != 2:
            td.line([(530, y + 52), (556, y + 80), (596, y + 22)], fill=INK, width=24, joint='curve')
    tk = tk.rotate(-8, resample=Image.BICUBIC, center=(770, 1060))
    im.alpha_composite(tk)
    # labda
    cx, cy, r = 1340, 1270, 400
    circ(d, cx, cy, r, WHITE)
    def pent(x, y, s, rot=0):
        pts = [(x + s * math.cos(math.radians(rot + 90 + k * 72)), y - s * math.sin(math.radians(rot + 90 + k * 72))) for k in range(5)]
        d.polygon(pts, fill=INK)
        return pts
    c = pent(cx, cy, 120)
    for k in range(5):
        ang = math.radians(90 + k * 72)
        px, py = cx + 290 * math.cos(ang), cy - 290 * math.sin(ang)
        line(d, (cx + 120 * math.cos(ang), cy - 120 * math.sin(ang)), (px, py), w=30)
        mask = Image.new('L', (S, S), 0); ImageDraw.Draw(mask).ellipse([cx - r + 22, cy - r + 22, cx + r - 22, cy + r - 22], fill=255)
        pl, pd = layer(); ppts = [(px + 105 * math.cos(math.radians(k * 72 + 90 + 180 + j * 72)), py - 105 * math.sin(math.radians(k * 72 + 90 + 180 + j * 72))) for j in range(5)]
        pd.polygon(ppts, fill=INK)
        im.paste(pl, (0, 0), Image.composite(pl.split()[3], Image.new('L', (S, S), 0), mask))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=LW)
    finish(im, 'tipp')

# ── DNR Bingó: bingókártya + filctoll-pötty
def bingo():
    im, d = layer()
    rr(d, [440, 520, 1460, 1660], 80, CREAM)
    d.rounded_rectangle([440, 520, 1460, 720], radius=80, fill=AMBER)
    d.rectangle([462, 640, 1438, 720], fill=AMBER)
    d.rounded_rectangle([440, 520, 1460, 1660], radius=80, outline=INK, width=LW)
    line(d, (462, 720), (1438, 720))
    hit = {(0, 1), (1, 1), (2, 1), (1, 3), (2, 0)}
    for r_ in range(3):
        for c in range(4):
            x0 = 540 + c * 220; y0 = 820 + r_ * 260
            d.rounded_rectangle([x0, y0, x0 + 160, y0 + 180], radius=30, fill=WHITE, outline=INK, width=30)
            if (r_, c) in hit:
                d.ellipse([x0 + 22, y0 + 32, x0 + 138, y0 + 148], fill=WINE)
    # filc
    pen = Image.new('RGBA', (S, S), (0, 0, 0, 0)); pd = ImageDraw.Draw(pen)
    pd.rounded_rectangle([1490, 760, 1650, 1420], radius=70, fill=WINE, outline=INK, width=LW)
    pd.rounded_rectangle([1490, 640, 1650, 820], radius=50, fill=YELLOW, outline=INK, width=LW)
    pd.polygon([(1520, 1400), (1620, 1400), (1570, 1540)], fill=INK)
    pen = pen.rotate(-22, resample=Image.BICUBIC, center=(1570, 1100))
    im.alpha_composite(pen)
    finish(im, 'bingo')

# ── DNR BOX: retro jukebox
def box():
    im, d = layer()
    # ív + test
    d.pieslice([560, 420, 1490, 1350], 180, 360, fill=WINE, outline=INK, width=LW)
    d.rectangle([560, 885, 1490, 1660], fill=WINE)
    d.line([(560, 885), (560, 1660)], fill=INK, width=LW); d.line([(1490, 885), (1490, 1660)], fill=INK, width=LW)
    line(d, (560, 1660), (1490, 1660))
    # színes ívsávok
    for i, col in enumerate([YELLOW, AMBER, ICE]):
        o = 90 + i * 70
        d.arc([560 + o, 420 + o, 1490 - o, 1350 - o], 180, 360, fill=col, width=56)
    # kijelző ablak (lemezek)
    rr(d, [700, 960, 1350, 1220], 40, CREAM)
    for x in (820, 1025, 1230):
        circ(d, x, 1090, 80, INK, w=0); d.ellipse([x - 22, 1068, x + 22, 1112], fill=YELLOW)
    # hangszóró-rács
    rr(d, [700, 1300, 1350, 1580], 40, GREY)
    for k in range(5):
        y = 1340 + k * 50; d.line([(760, y), (1290, y)], fill=CREAM, width=18)
    # hangjegy
    line(d, (1680, 560), (1680, 860), w=40)
    d.polygon([(1680, 560), (1820, 600), (1820, 660), (1680, 620)], fill=INK)
    circ(d, 1630, 880, 70, YELLOW)
    finish(im, 'box')

# ── DNR Pub: két koccintó korsó
def pub():
    im, d = layer()
    def mug(x, handle_left, ang):
        m = Image.new('RGBA', (S, S), (0, 0, 0, 0)); md = ImageDraw.Draw(m)
        hx0, hx1 = (x - 440, x - 200) if handle_left else (x + 200, x + 440)
        md.rounded_rectangle([hx0, 980, hx1, 1420], radius=110, fill=None, outline=INK, width=LW)
        md.rounded_rectangle([x - 250, 800, x + 250, 1630], radius=70, fill=AMBER, outline=INK, width=LW)
        for bx in (x - 130, x + 50): md.rounded_rectangle([bx, 980, bx + 70, 1480], radius=35, fill=YELLOW)
        for (fx, fy, fr) in [(x - 175, 790, 115), (x - 30, 730, 140), (x + 135, 770, 125)]:
            md.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], fill=CREAM, outline=INK, width=LW)
        md.rectangle([x - 228, 800, x + 228, 880], fill=CREAM)
        md.line([(x - 250, 890), (x + 250, 890)], fill=INK, width=LW)
        return m.rotate(ang, resample=Image.BICUBIC, center=(x, 1250))
    im.alpha_composite(mug(760, True, -9))
    im.alpha_composite(mug(1290, False, 9))
    for (x, y, r) in [(1025, 560, 34), (935, 470, 22), (1115, 480, 26)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=CREAM, outline=INK, width=20)
    finish(im, 'pub')

# ── DNR Liga: serleg dobogón
def liga():
    im, d = layer()
    rr(d, [380, 1390, 820, 1690], 30, ICE)
    rr(d, [780, 1260, 1270, 1690], 30, YELLOW)
    rr(d, [1230, 1450, 1670, 1690], 30, CREAM)
    d.ellipse([560, 1500, 640, 1580], fill=INK); d.ellipse([1410, 1530, 1490, 1610], fill=INK)
    d.ellipse([610, 520, 900, 860], outline=INK, width=LW)
    d.ellipse([1150, 520, 1440, 860], outline=INK, width=LW)
    d.chord([730, 160, 1320, 1010], 0, 180, fill=AMBER, outline=INK, width=LW)
    d.rectangle([730, 470, 1320, 590], fill=AMBER)
    line(d, (730, 470), (730, 590)); line(d, (1320, 470), (1320, 590)); line(d, (730, 470), (1320, 470))
    rr(d, [985, 1000, 1065, 1110], 20, AMBER)
    rr(d, [860, 1100, 1190, 1260], 34, WINE)
    st = [(1025 + (100 if k % 2 == 0 else 42) * math.cos(math.radians(-90 + k * 36)), 720 + (100 if k % 2 == 0 else 42) * math.sin(math.radians(-90 + k * 36))) for k in range(10)]
    d.polygon(st, fill=CREAM)
    d.arc([800, 560, 1000, 900], 200, 250, fill=WHITE, width=34)
    finish(im, 'liga')

OUT = sys.argv[1] if len(sys.argv) > 1 else 'assets'
for f in (events, torta, tipp, bingo, box, pub, liga): f()
print('ok')
