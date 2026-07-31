#!/usr/bin/env python3
# v10.222 — visszavonva: a fooldal ket sarok-elemenek safe-area-top fixje
#
# A v10.220-as fix (env(safe-area-inset-top) a bal felso koszonto + jobb
# felso Beallitasok/Statisztika gombparon) REGRESSZIOT okozott: a .home-inner
# sajat top paddingje (84px, fix ertek) NEM volt osszehangolva ezzel — igy
# valodi eszkozon (nagyobb safe-area-inset-top ertekkel) a lejjebb tolt
# sarok-elemek belelogtak a "DNR GAMES" sorba.
#
# A .home-inner fix 84px paddingje eddig is eleg tavolsagot adott a
# regi, fix top:14-es sarok-elemeknek — ezert egyszeruen visszaallitjuk
# azt, es NEM prybaljuk meg kulon safe-area-avatta tenni oket, amig a
# .home-inner sajat paddingja nincs egyeztetve vele.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""        {/* Top-left: version + announcement */}
        <div style={{ position:'absolute', top:'max(14px, env(safe-area-inset-top))', left:18, zIndex:20, display:'flex', flexDirection:'column', gap:8, alignItems:'flex-start', maxWidth:'calc(100vw - 220px)', pointerEvents:'none' }}>""",
    """        {/* Top-left: version + announcement */}
        <div style={{ position:'absolute', top:14, left:18, zIndex:20, display:'flex', flexDirection:'column', gap:8, alignItems:'flex-start', maxWidth:'calc(100vw - 220px)', pointerEvents:'none' }}>""",
    'fooldal bal felso koszonto - vissza')

sub("""        <div style={{ position:'absolute', top:'max(14px, env(safe-area-inset-top))', right:18, zIndex:10, display:'flex', background:T.surface, borderRadius:18, boxShadow:T.shadow, overflow:'hidden' }}>""",
    """        <div style={{ position:'absolute', top:14, right:18, zIndex:10, display:'flex', background:T.surface, borderRadius:18, boxShadow:T.shadow, overflow:'hidden' }}>""",
    'fooldal jobb felso gombpar - vissza')

sub("const APP_VERSION = 'v10.221';", "const APP_VERSION = 'v10.222';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — fooldal sarok-elemek visszaallitva fix top:14-re')
