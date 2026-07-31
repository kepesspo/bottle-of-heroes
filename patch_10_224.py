#!/usr/bin/env python3
# v10.224 — a státuszsáv-csík kövesse a fejléc színét
#
# A VALÓDI ok (végre kimérve): az appban MÁR RÉGÓTA van egy státuszsáv-festősáv
# (BottleApp, portál a body-ba, position:fixed, z-index:55), és az a kód
# saját kommentje szerint "MINDIG az app háttérszínét kapja" — vagyis mindig
# barack (T.bg). Ezért látszott a fehér AppBar fölött barack sáv: nem hiányzott
# a festés, hanem rossz színnel festett.
#
# Ez a z55-ös csík magyarázza a v10.220 kudarcát is: az .appbar-shell-nek adott
# padding-top csak lejjebb tolta a fejléc TARTALMÁT, a sávot viszont továbbra is
# a z55-ös csík takarta barackkal — így lett dupla üres hely a cím fölött.
# (És a v10.223-as saját csíkom is emiatt volt hatástalan: z-index 1 < 55.)
#
# Javítás: a MEGLÉVŐ z55-ös csík kapja a fejléc színét azokon a képernyőkön,
# ahol van AppBar (fehér = T.surface); ahol nincs fejléc — főoldal, játék
# közben, szoba létrehozása —, ott marad a téma háttere.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── 1) a meglévő z55-ös csík színe kövesse a fejlécet ───
sub("""      {/* Status bar festősáv: a bar mögötti zóna MINDIG az app háttérszínét kapja,
          bármelyik képernyő/overlay van alatta (z55: appbar fölött, sheet-backdrop alatt). */}
      {ReactDOM.createPortal(
        <div style={{ position:'fixed', top:0, left:0, right:0, height:'env(safe-area-inset-top)', background:T.bg, zIndex:55, pointerEvents:'none' }} />,
        document.body
      )}""",
    """      {/* Status bar festősáv (z55: appbar fölött, sheet-backdrop alatt).
          A színe KÖVETI a képernyő tetejét: ahol fehér AppBar van, ott fehér —
          így a fejléc vizuálisan a kijelző tetejéig ér, mint egy natív appban.
          Ahol nincs fejléc (főoldal, játék közben, szoba létrehozása), ott a
          téma háttere a helyes szín. */}
      {ReactDOM.createPortal(
        <div style={{ position:'fixed', top:0, left:0, right:0, height:'env(safe-area-inset-top)',
          background: (creatingRoom || screen === 'home' || screen === 'play') ? T.bg : T.surface,
          zIndex:55, pointerEvents:'none' }} />,
        document.body
      )}""",
    'z55 csik szine')

# ─── 2) a v10.223-ban hozzáadott saját csík felesleges (z1 < z55) — ki ───
sub("""      <div key={creatingRoom ? 'creating' : screen} style={{ position:'relative', height:'100dvh', width:'100%', display:'flex', flexDirection:'column', overflow:'hidden', boxSizing:'border-box', paddingTop:'env(safe-area-inset-top)', animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)` }}>
        {/* Státuszsáv mögötti csík. A konténer paddingTop-ja miatt a tartalom a
            státuszsáv alatt kezdődik; enélkül ott a <body> barack háttere
            látszana akkor is, ha a képernyő teteje egy fehér AppBar — így nem
            tűnne natív appnak. A csík pont a padding-területet fedi, semmit nem
            mozdít el. Főoldalon / játék közben nincs fejléc, ott a téma háttere
            a helyes szín. */}
        <div aria-hidden="true" style={{ position:'absolute', top:0, left:0, right:0,
          height:'env(safe-area-inset-top)', pointerEvents:'none', zIndex:1,
          background: (creatingRoom || screen === 'home' || screen === 'play') ? T.bg : T.surface }} />""",
    """      <div key={creatingRoom ? 'creating' : screen} style={{ height:'100dvh', width:'100%', display:'flex', flexDirection:'column', overflow:'hidden', boxSizing:'border-box', paddingTop:'env(safe-area-inset-top)', animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)` }}>""",
    'v10.223 sajat csik ki')

sub("const APP_VERSION = 'v10.223';", "const APP_VERSION = 'v10.224';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — a z55-os statuszsav-csik mostantol a fejlec szinet koveti')
