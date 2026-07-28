#!/usr/bin/env python3
"""Hianyzo jatek-bannerek eloallitasa a meglevok stilusaban.

A meglevo bannerekbol kimert parameterek (assets/*_banner.png):
  meret        800x120, atlatszo hatter
  szoveg       Nunito 900, sotetkek #1F3048
  arnyek       #EF8A6D, ~6 px-el lejjebb
  elrendezes   balra a jatek ikonja, mellette a nev nagybetuvel

A Nunito nem all rendelkezesre TTF-kent, ezert a projekt sajat
assets/fonts/nunito-latin.woff2 valtozofontjabol keszul a 900-as suly.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

W, H = 800, 120
INK, SHADOW = (31, 48, 72, 255), (239, 138, 109, 255)
SHADOW_DY = 6
# A "latin-ext" alkeszlet CSAK a kiegeszito karaktereket tartalmazza — az alap
# betuk (R, E, K, ...) nincsenek benne. A "latin" viszont mind a 230 kell
# glifat hozza, az É/Á/Ó ekezeteket is. Ellenorizve: hianyzik = semmi.
FONT_SRC = 'assets/fonts/nunito-latin.woff2'

def nunito(tmp, size):
    if not os.path.exists(tmp):
        f = TTFont(FONT_SRC); f.flavor = None
        inst = instantiateVariableFont(f, {'wght': 900}, inplace=False)
        inst.save(tmp)
    return ImageFont.truetype(tmp, size)

def build(game_id, label, icon_path, out_path, tmp_font):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    x = 44
    if icon_path and os.path.exists(icon_path):
        ic = Image.open(icon_path).convert('RGBA')
        s = 104
        ic = ic.resize((s, s), Image.LANCZOS)
        im.alpha_composite(ic, (x, (H - s) // 2))
        x += s + 22

    # a betumeret ugy, hogy a nev elferjen a maradek helyen
    size = 62
    while size > 30:
        f = nunito(tmp_font, size)
        if ImageDraw.Draw(im).textlength(label, font=f) <= W - x - 40:
            break
        size -= 2
    f = nunito(tmp_font, size)
    d = ImageDraw.Draw(im)
    bb = d.textbbox((0, 0), label, font=f)
    y = (H - (bb[3] - bb[1])) // 2 - bb[1] - SHADOW_DY // 2
    d.text((x, y + SHADOW_DY), label, font=f, fill=SHADOW)
    d.text((x, y), label, font=f, fill=INK)
    im.save(out_path)
    return out_path, size

if __name__ == '__main__':
    tmp = sys.argv[1] if len(sys.argv) > 1 else '/tmp/nunito900.ttf'
    for gid, label in [('erem', 'ÉREM DOBÁS'), ('tabu', 'TABU SZÓ'),
                       ('reakcio', 'REAKCIÓ TESZT'), ('szamsor', 'SZÁM SORREND')]:
        p, sz = build(gid, label, 'assets/%s_icon.png' % gid, 'assets/%s_banner.png' % gid, tmp)
        print('%-9s -> %s (%dpx)' % (gid, p, sz))
