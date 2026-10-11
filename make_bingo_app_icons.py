# DNR Tipp ikon (v10.419) — a DNR Liga ikon keretéből (háttér, pöttyök, sötét kártya,
# „DNR" felirat, fehér pirula) készül, hogy a DNR appcsalád ikonjai egy sorban álljanak.
# A belső rajz: eredményjelző (2 : 1) + céltábla, a pirulában „TIPP".
from PIL import Image, ImageDraw, ImageFont
im = Image.open('assets/dnr_liga_icon.png').convert('RGB')
d = ImageDraw.Draw(im)
CARD = im.getpixel((290, 300)); INK = CARD
CORAL = (239, 151, 133); GOLD = (232, 213, 132); WHITE = (255, 255, 255)
# a Liga rajza (oszlopok + csillag) és a pirula felirata ki
d.rectangle([300, 250, 720, 610], fill=CARD)
d.rounded_rectangle([392, 712, 632, 788], radius=38, fill=WHITE)
B = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
# céltábla
cx, cy = 512, 300
for r, c in [(46, GOLD), (32, CARD), (20, GOLD), (9, CORAL)]:
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
# eredményjelző: két fehér csempe, köztük korall kettőspont
f = ImageFont.truetype(B, 120)
for x0, txt in [(322, '2'), (562, '1')]:
    d.rounded_rectangle([x0, 380, x0 + 140, 585], radius=22, fill=WHITE)
    d.text((x0 + 70, 482), txt, font=f, fill=INK, anchor='mm')
for yy in (450, 515):
    d.ellipse([512 - 15, yy - 15, 512 + 15, yy + 15], fill=CORAL)
d.text((512, 751), 'TIPP', font=ImageFont.truetype(B, 44), fill=INK, anchor='mm')
im.save('assets/dnr_tipp_icon.png', optimize=True)

# DNR a tortán — négyzetes, fehér hátterű PWA-ikon a kör alakú logóból. Az
# átlátszó logó iOS főképernyőn fekete hátteret kapna.
logo = Image.open('assets/dnr_torta_logo.png').convert('RGBA')
sq = Image.new('RGBA', (1024, 1024), (255, 255, 255, 255))
lg = logo.resize((820, 820), Image.LANCZOS)
sq.alpha_composite(lg, (102, 102))
sq.convert('RGB').quantize(64, method=Image.MEDIANCUT).save('assets/dnr_torta_icon.png', optimize=True)
