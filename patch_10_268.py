#!/usr/bin/env python3
# v10.268 — a result banner ne animálódjon kétszer
#
# A TÜNET: ha a nagy bannert KÉZZEL zárod be, mielőtt magától eltűnne, előbb
# lemegy kicsibe, aztán megint lejátszik egy animációt.
#
# AZ OK: két, egymásról nem tudó kicsinyítés van.
#   - a kézi koppintás azonnal `true`-ra állította az állapotot (ugrás a sávra),
#   - a 2600 ms-os automata időzítő viszont ettől függetlenül lefutott, és
#     `'shrinking'`-re állította → újra lejátszotta a zsugorodó animációt, majd
#     a végén megint `true`-ra váltott. Innen a második animáció.
#
# A JAVÍTÁS
#   1. Az időzítő csak akkor lép, ha még senki nem nyúlt hozzá (`false`).
#      Funkcionális állapotfrissítéssel, hogy ne egy elavult értéket nézzen.
#   2. A kézi koppintás sem ugrik, hanem ugyanazt a zsugorodó animációt indítja
#      — így egyetlen, egységes mozdulat van, akár vársz, akár koppintasz.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. az idozito csak akkor lep, ha meg senki nem nyult hozza ──
sub("""    const t = setTimeout(() => setResultMinimized('shrinking'), 2600);""",
    """    // CSAK akkor kicsinyitsen, ha meg senki nem nyult hozza. Ha a jatekos
    // kozben mar rakoppintott, ez az idozito masodszor is lejatszotta a
    // zsugorodo animaciot. Funkcionalis frissites, hogy ne elavult erteket lasson.
    const t = setTimeout(() => setResultMinimized(v => (v === false ? 'shrinking' : v)), 2600);""",
    'idozito ora')

# ── 2. a kezi koppintas is a zsugorodo animaciot inditja, nem ugrik ──
sub("""          <div key={'banner-' + gameResult.ts} onClick={() => setResultMinimized(true)} style={{ position:'fixed', inset:0, zIndex:250,""",
    """          <div key={'banner-' + gameResult.ts} onClick={() => setResultMinimized(v => (v === false ? 'shrinking' : v))} style={{ position:'fixed', inset:0, zIndex:250,""",
    'kezi kicsinyites')

sub("const APP_VERSION = 'v10.267';", "const APP_VERSION = 'v10.268';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — egyetlen animacio')
