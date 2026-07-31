#!/usr/bin/env python3
# v10.232 — a titkos 5-koppintás csak az első 6 profilt töltse be
#
# A "Minimum 2 fő szükséges" pirulára 5× koppintva eddig mind a 12 preset
# profil betöltődött. Ennyi játékossal a teszteléshez feleslegesen zsúfolt;
# 6 fő elég. A sorrend marad, tehát az első hat:
#   Sere · Kecsi · Luca · Tóth · Márk · Dani
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""      const newPlayers = PRESET_PLAYERS.map((p, i) => {""",
    """      // Csak az első 6 profil — 12 fő a teszteléshez feleslegesen zsúfolt.
      const newPlayers = PRESET_PLAYERS.slice(0, 6).map((p, i) => {""",
    'elso 6 profil')

sub("const APP_VERSION = 'v10.231';", "const APP_VERSION = 'v10.232';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — 5-koppintas: 12 helyett 6 profil')
