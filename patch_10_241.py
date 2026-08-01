#!/usr/bin/env python3
# v10.241 — Tapper: a lenyomott tábla (és benne a profilkép) nem ugrik többé
#
# MÉRVE (Playwright, a tábla avatarjának bounding box-a lenyomás közben):
#     X: 45 → 49.68 px     szélesség: 58 → 56.26 px
# tehát a kép ~4,7 px-t ugrott OLDALRA, azonnal, majd elengedéskor vissza.
#
# Az ok: a táblán van egy `transform: scale(0.97)` lenyomásra, DE a transition
# felsorolásból pont a transform maradt ki:
#     transition:'box-shadow 0.15s, background 0.15s'
# Így a többi visszajelzés (árnyék, háttér) szépen átúszik, a méret viszont
# pattan. Ujjal ez a parti alatt folyamatosan ismétlődik — pontosan ez a
# "ugrálnak a profilképek" a játék közben.
#
# Ez volt az EGYETLEN ilyen hely: a többi feltételes scale mindenhol
# transitionnel megy (44066, 44119, 54389, 63559), és a Tapper TELEFONOS
# nézete is helyesen `transition:'transform 0.1s, box-shadow 0.15s'`-t használ.
# A host-tábla maradt ki.
#
# Két dolgot javítunk:
#   1. a transform is átúszik (0.12s), ahogy mindenhol máshol
#   2. a mérték 0.97 → 0.985. Egy teljes szélességű táblánál a 3% ~11 px-es
#      ugrás; a visszajelzés amúgy is erős (fényerő + kettős színes gyűrű),
#      nem a méretnek kell vinnie.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""          transition:'box-shadow 0.15s, background 0.15s',
          transform: holding && !released ? 'scale(0.97)' : 'scale(1)',""",
    """          // A transform IS legyen a listaban — nelkule a meret pattan, es a
          // taplan ulo profilkep ~5 px-t ugrik oldalra minden lenyomasnal.
          transition:'transform 0.12s, box-shadow 0.15s, background 0.15s',
          transform: holding && !released ? 'scale(0.985)' : 'scale(1)',""",
    'tapper tabla transform')

sub("const APP_VERSION = 'v10.240';", "const APP_VERSION = 'v10.241';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — a Tapper tabla lenyomasa atuszik, nem pattan')
