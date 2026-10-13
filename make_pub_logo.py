# DNR Pub logó (v10.422) — a kapott kerek logóból (assets/src/dnr_pub_logo_src.webp):
#  * assets/dnr_pub_logo.png   — 512×512, ÁTLÁTSZÓ háttér (a központ köre, admin, nyitókép)
#  * assets/dnr_pub_icon.png   — 1024×1024, FEHÉR háttér (főképernyő-ikon, manifest:
#    iOS az átlátszót feketére festené)
# A fehér háttér a SARKOKBÓL elárasztva megy ki — a kör belső krémszíne marad, mert a
# sötét kontúr megállítja (ugyanaz a módszer, mint a splash DNR logónál).
from PIL import Image, ImageDraw
im = Image.open('assets/src/dnr_pub_logo_src.webp').convert('RGBA')
W, H = im.size
mask = Image.new('L', im.size, 0)
px = im.load()
from collections import deque
seen = bytearray(W * H)
q = deque([(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)])
def bgish(p): return p[0] > 225 and p[1] > 225 and p[2] > 225
mp = mask.load()
while q:
    x, y = q.popleft()
    if x < 0 or y < 0 or x >= W or y >= H: continue
    i = y * W + x
    if seen[i]: continue
    seen[i] = 1
    if not bgish(px[x, y]): continue
    mp[x, y] = 255
    q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
# a háttér átlátszó, a perem egy pixellel puhítva
from PIL import ImageFilter
alpha = Image.eval(mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.8)), lambda v: 255 - v)
im.putalpha(alpha)
bbox = im.getbbox()
im = im.crop(bbox)
s = max(im.size); sq = Image.new('RGBA', (s, s), (0, 0, 0, 0)); sq.alpha_composite(im, ((s - im.size[0]) // 2, (s - im.size[1]) // 2))
logo = sq.resize((512, 512), Image.LANCZOS)
logo.quantize(160, method=Image.FASTOCTREE).save('assets/dnr_pub_logo.png', optimize=True)
icon = Image.new('RGBA', (1024, 1024), (255, 255, 255, 255))
icon.alpha_composite(sq.resize((820, 820), Image.LANCZOS), (102, 102))
icon.convert('RGB').quantize(96, method=Image.MEDIANCUT).save('assets/dnr_pub_icon.png', optimize=True)
print('ok', bbox)
