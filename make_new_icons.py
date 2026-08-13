#!/usr/bin/env python3
"""Az ot uj paros jatek ikonja (512x512), a tobbi jatek-ikon stilusaban.

A meglevo ikonokbol kimert stilus (pl. assets/otdolog_icon.png):
  meret     512x512, atlatszo hatter, a rajz kb. a kozepso 80%-ban
  kontur    sotetkek #1A2A4A, vastag (~20 px), lekerekitett vegek
  toltes    feher, egy-ket akcentus (korall #F08060, sarga #F5B93B,
            menta #4FC2A0, piros #E0544B)

⚠️ A BANNER ebbol az ikonbol keszul (`make_banners.py`), tehat a ket felulet
nem tud elcsuszni egymastol — ugyanaz a rajz kicsinyitve.
Futtatas:  python3 make_new_icons.py
"""
import math
from PIL import Image, ImageDraw

S = 512
INK   = (26, 42, 74, 255)
WHITE = (255, 255, 255, 255)
CORAL = (240, 128, 96, 255)
AMBER = (245, 185, 59, 255)
MINT  = (79, 194, 160, 255)
RED   = (224, 84, 75, 255)
SKY   = (91, 160, 219, 255)
W = 20                      # alap vonalvastagsag


def new():
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def line(d, pts, fill=INK, w=W):
    d.line(pts, fill=fill, width=w, joint='curve')
    r = w / 2.0
    for (x, y) in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=fill)


# ── 1. CHICKEN — robbantógomb szikrával ────────────────────────────────────
def icon_chicken(path):
    im, d = new()
    # talp
    d.rounded_rectangle([88, 312, 424, 428], radius=36, fill=WHITE, outline=INK, width=W)
    # a gomb kupolaja — ELOSZOR, hogy a talp feher toltese levagja az aljat
    d.pieslice([168, 200, 344, 376], 180, 360, fill=RED, outline=INK, width=W)
    d.rounded_rectangle([88, 312, 424, 428], radius=36, fill=WHITE, outline=INK, width=W)
    # a kupola pereme a talp folott
    d.rounded_rectangle([160, 290, 352, 326], radius=18, fill=RED, outline=INK, width=W)
    # szikra
    cx, cy = 256, 168
    for a in range(0, 360, 60):
        x0 = cx + 32 * math.cos(math.radians(a)); y0 = cy - 32 * math.sin(math.radians(a))
        x1 = cx + 78 * math.cos(math.radians(a)); y1 = cy - 78 * math.sin(math.radians(a))
        line(d, [(x0, y0), (x1, y1)], AMBER, 16)
    im.save(path); return path


# ── 2. UJJOSSZEG (Morra) — kez + szam-jelveny ──────────────────────────────
def icon_fingerit(path):
    im, d = new()
    # ⚠️ VASTAG ujjak, huvelyk nelkul. A 20 px-es kontur MINDKET oldalon eszi a
    # szelesseget: egy 66 px-es ujjbol csak 26 px feher mag marad, ami 32 px-es
    # kartya-ikonon 1,6 px — merve osszemosodott. 100 px-es ujj ~60 px magot ad.
    for x, top in ((136, 126), (256, 100)):
        d.rounded_rectangle([x, top, x + 100, 340], radius=50, fill=WHITE, outline=INK, width=W)
    # tenyer — a feher toltese vagja le az ujjak aljat
    d.rounded_rectangle([120, 288, 392, 448], radius=54, fill=WHITE, outline=INK, width=W)
    # a tipp az OSSZEGRE: korall jelveny „?"-lel
    d.ellipse([326, 62, 462, 198], fill=CORAL, outline=INK, width=W)
    line(d, [(368, 112), (388, 98), (412, 112), (412, 134), (394, 146)], WHITE, 17)
    d.ellipse([384, 160, 406, 182], fill=WHITE)
    im.save(path); return path


# ── 3. IGEN–NEM — kerdes-buborek pipaval es kereszttel ─────────────────────
def icon_igennem(path):
    im, d = new()
    # ⚠️ A farok ELOSZOR, tomoren: a buborek feher toltese vagja le a felso
    # veget, igy a ketto egybefolyik (ugyanaz a minta, mint a „Ne ugyanazt!"-nal).
    d.polygon([(160, 220), (232, 220), (168, 320)], fill=INK)
    d.rounded_rectangle([72, 76, 440, 268], radius=48, fill=WHITE, outline=INK, width=W)
    # „?" a buborekban
    line(d, [(212, 140), (244, 116), (282, 140), (282, 176), (250, 194)], INK, 24)
    d.ellipse([234, 212, 266, 244], fill=INK)
    # a ket korong KULON, a buborek alatt — nem lognak ra
    d.ellipse([88, 340, 216, 468], fill=RED, outline=INK, width=W)
    line(d, [(126, 378), (178, 430)], WHITE, 22)
    line(d, [(178, 378), (126, 430)], WHITE, 22)
    d.ellipse([296, 340, 424, 468], fill=MINT, outline=INK, width=W)
    line(d, [(330, 406), (354, 432), (392, 376)], WHITE, 22)
    im.save(path); return path


# ── 4. ULTIMÁTUM — mérleg (alkudozás) ──────────────────────────────────────
def icon_ultimatum(path):
    im, d = new()
    # oszlop es talp
    line(d, [(256, 132), (256, 384)], INK, W)
    d.rounded_rectangle([164, 384, 348, 424], radius=20, fill=WHITE, outline=INK, width=W)
    # gerenda
    line(d, [(112, 172), (400, 172)], INK, W)
    d.ellipse([232, 108, 280, 156], fill=AMBER, outline=INK, width=W)
    # ket serpenyo
    for x, col in ((112, CORAL), (400, MINT)):
        line(d, [(x, 172), (x, 232)], INK, 14)
        d.pieslice([x - 76, 196, x + 76, 312], 0, 180, fill=col, outline=INK, width=W)
    im.save(path); return path


# ── 5. MENNYI? — műszer (becslés) ──────────────────────────────────────────
def icon_mennyi(path):
    im, d = new()
    d.pieslice([56, 128, 456, 528], 180, 360, fill=WHITE, outline=INK, width=W)
    line(d, [(56, 328), (456, 328)], INK, W)
    # osztasok a peremen belul
    for a_ in (196, 222, 248, 284, 310, 336):
        r0, r1 = 130, 168
        x0 = 256 + r0 * math.cos(math.radians(a_)); y0 = 328 + r0 * math.sin(math.radians(a_))
        x1 = 256 + r1 * math.cos(math.radians(a_)); y1 = 328 + r1 * math.sin(math.radians(a_))
        line(d, [(x0, y0), (x1, y1)], INK, 12)
    # mutato + agy
    line(d, [(256, 328), (348, 216)], CORAL, 24)
    d.ellipse([222, 294, 290, 362], fill=AMBER, outline=INK, width=W)
    # ⚠️ A „?" JELVENYBE kerult: a muszer lapjara rajzolva az osztasokba utkozott.
    d.ellipse([320, 60, 452, 192], fill=CORAL, outline=INK, width=W)
    line(d, [(360, 108), (380, 94), (404, 108), (404, 130), (386, 142)], WHITE, 16)
    d.ellipse([376, 156, 396, 176], fill=WHITE)
    im.save(path); return path


ICONS = [
    ('chicken',   icon_chicken),
    ('fingerit',  icon_fingerit),
    ('igennem',   icon_igennem),
    ('ultimatum', icon_ultimatum),
    ('mennyi',    icon_mennyi),
]

if __name__ == '__main__':
    for gid, fn in ICONS:
        p = fn('assets/%s_icon.png' % gid)
        print('OK', p)
