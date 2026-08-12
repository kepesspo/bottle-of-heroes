# A „Ne ugyanazt!" jatek-ikonja — UGYANAZ a rajz, ami a bannerben van.
#
# ⚠️ MIERT UJRARAJZOLJUK, es miert nem a bannerbol vagjuk ki?
# A bannerben (800x120) az ikon regioja mindossze 127x93 px. Egy 512x512-es
# ikonna nagyitva (4x folott) latvanyosan elmosodna es pixelesedne — a tobbi
# jatek ikonja mind eles, 512-es vektoros rajz. Ezert a KET BUBOREK ugyanazokkal
# az aranyokkal es szinekkel ujra van rajzolva, ikon-felbontason.
#
# A geometria a bannerbol MERT ertekekbol jon (a regio 127x93, vonalvastagsag 6),
# aranyosan felskalazva — igy a ket rajz nem tud elcsuszni egymastol.
#
# Futtatas:  python3 make_neugyanazt_icon.py
from PIL import Image, ImageDraw

NAVY  = (26, 42, 74, 255)     # a banner sotet buborekja
CORAL = (240, 128, 96, 255)   # a banner korall buborekja
WHITE = (255, 255, 255, 255)

S = 512                        # ikon-meret, mint minden mas jatek-ikonnal
SRC_W, SRC_H = 127.0, 93.0     # a banner ikon-regiojanak merete
ART_W = 424.0                  # mekkora legyen a rajz a 512-es lapon (padding marad)
K = ART_W / SRC_W              # skala: 3.339
OX = (S - SRC_W * K) / 2.0     # vizszintes kozepre
OY = (S - SRC_H * K) / 2.0     # fuggoleges kozepre

def P(x, y):
    """Banner-koordinatabol ikon-koordinata."""
    return (OX + x * K, OY + y * K)

def box(x0, y0, x1, y1):
    a, b = P(x0, y0); c, d = P(x1, y1)
    return [a, b, c, d]

W = 6 * K                      # vonalvastagsag (a bannerben 6 px)

img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# ── 1. SOTET buborek (bal felso) + farok bal alul ──────────────────────────
# A farok TOMOR (nem korvonalas), ezert eloszor rajzoljuk, hogy a buborek
# feher toltese levagja a felso veget — igy a ketto egybefolyik.
d.polygon([P(16, 40), P(34, 40), P(16, 72)], fill=NAVY)
d.rounded_rectangle(box(0, 0, 80, 55), radius=14 * K, fill=WHITE, outline=NAVY, width=int(round(W)))

# ── 2. KORALL buborek (jobb also) + farok jobb alul ────────────────────────
# ⚠️ A SORREND szamit: a korall buborek a sotet FOLE kerul (a feher toltese
# eltakarja a sotet buborek jobb also sarkat) — pontosan ugy, ahogy a bannerben.
d.polygon([P(88, 62), P(110, 62), P(110, 92)], fill=CORAL)
d.rounded_rectangle(box(50, 26, 126, 80), radius=14 * K, fill=WHITE, outline=CORAL, width=int(round(W)))

# ── 3. A PIPA a korall buborekban ──────────────────────────────────────────
# Kulon szakaszokban rajzolva, kerek vegekkel — igy a tores pontja is tomor.
tick = [P(64, 52), P(78, 66), P(108, 38)]
d.line([tick[0], tick[1]], fill=CORAL, width=int(round(W * 1.5)), joint='curve')
d.line([tick[1], tick[2]], fill=CORAL, width=int(round(W * 1.5)), joint='curve')
for pt in tick:
    r = W * 0.75
    d.ellipse([pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r], fill=CORAL)

img.save('assets/neugyanazt_icon.png')
print('OK - assets/neugyanazt_icon.png (%dx%d)' % img.size)
