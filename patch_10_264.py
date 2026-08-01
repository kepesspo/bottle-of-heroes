#!/usr/bin/env python3
# v10.264 — Szerencsekerék: nem lehet oldalra görgetni
#
# A kerék egy NÉGYZET alakú div, amit elforgatunk. A kör maga beleírt, tehát
# látványban semmi nem lóg ki — a böngésző viszont az ELFORGATOTT NÉGYZET
# befoglalójával számol, az pedig √2-szer szélesebb. Chromiumban megmérve:
#
#   402 px-es kijelzőn a kerék 354 px, a forgatott befoglalója 500 px,
#   és a görgethető terület 402 helyett 451 px lett → oldalra lehetett húzni.
#   (360 px-en 397, 320 px-en 349 — mindig kilóg.)
#
# Ez a v10.251 óta látszik igazán, amióta a kerék kitölti a szélességet: előtte
# a beégetett 288 px mellett is kilógott, csak kevesebbel.
#
# Javítás: a kerék konténere levágja a túlnyúlást. A kör beleírt a négyzetbe,
# a mutató és a középső gomb is a konténeren belül van, tehát a levágás csak
# az üres sarkokat érinti — látványban semmi nem változik.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""      <div ref={wheelWrapRef} style={{ position:'relative', width:'100%', height:SIZE + 26 * k }}>""",
    """      {/* overflow:hidden — a kerek NEGYZET dobozat forgatjuk, es az elforgatott
          befoglaloja √2-szer szelesebb, amitol oldalra lehetett gorgetni. A kor
          beleirt a negyzetbe, tehat csak az ures sarkok vagodnak le. */}
      <div ref={wheelWrapRef} style={{ position:'relative', width:'100%', height:SIZE + 26 * k, overflow:'hidden' }}>""",
    'kerek kontener levagas')

sub("const APP_VERSION = 'v10.263';", "const APP_VERSION = 'v10.264';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — nincs oldalra gorgetes')
