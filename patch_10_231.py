#!/usr/bin/env python3
# v10.231 — a safe-area diagnosztika a TESZT DB mód mögé kerül
#
# A hibakereséshez kellett, és visszatérő hiba lévén érdemes megtartani —
# de a normál felhasználónak nem való a Beállítások aljára. A TESZT DB mód
# eleve a "most hibát keresünk" jelzés (a főoldalon a verziószámra 3×
# koppintva kapcsolható), így ott a helye.
#
# Dokumentáció: docs/safe-area.md
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""              {/* Ideiglenes diagnosztika a PWA-s safe-area hibakereseshez.
                  Ha a layout jo, ez kikerul. */}
              {(() => {
                const v = (typeof window !== 'undefined' && window.__bohVh) || {};""",
    """              {/* Safe-area / státuszsáv diagnosztika — csak TESZT DB módban.
                  Visszatérő hibaosztály, ezért bent marad, de a normál
                  felhasználó elől elrejtve. Leírás: docs/safe-area.md */}
              {(() => {
                try { if (!(typeof window.isTestDb === 'function' && window.isTestDb())) return null; } catch (e) { return null; }
                const v = (typeof window !== 'undefined' && window.__bohVh) || {};""",
    'diagnosztika teszt-db moge')

sub("const APP_VERSION = 'v10.230';", "const APP_VERSION = 'v10.231';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — diagnosztika csak TESZT DB modban')
