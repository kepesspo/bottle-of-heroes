#!/usr/bin/env python3
# v10.223 — a v10.220 valódi oka: DUPLA safe-area padding
#
# A gyökér képernyő-konténer (BottleApp, `key={screen}`) MÁR RÉGÓTA tartalmaz
# egy `paddingTop:'env(safe-area-inset-top)'`-ot. Emiatt minden képernyő
# tartalma eleve a státuszsáv ALATT kezdődik, és abban a sávban a <body>
# barack háttere látszik.
#
# A v10.220-ban ugyanezt a paddingot MÉG EGYSZER hozzáadtam az .appbar-shell-hez
# és a PlayScreen fejlécéhez — így valós eszközön 2× 59pt lett belőle: a fehér
# fejléc tetején egy hatalmas üres sáv, a cím lelökve. (Böngészőben ez nem
# látszott, mert ott env(safe-area-inset-top) = 0, tehát 2×0 = 0.)
#
# Helyes megoldás: a dupla padding megszüntetése, és a státuszsáv mögötti
# csík MEGFESTÉSE a fejléc színével — így a fehér fejléc vizuálisan a kijelző
# tetejéig ér, anélkül hogy bármit elmozdítanánk.
#
# A csík a gyökér konténer padding-területére kerül (position:absolute; top:0),
# tehát pontosan azt a sávot fedi, amit eddig a barack <body> töltött ki.
# Színe: AppBar-os képernyőn fehér (T.surface), a főoldalon / játék közben /
# szoba-létrehozáskor a téma háttere (T.bg) — ott ugyanis nincs fejléc, ott a
# barack a helyes.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── 1) .appbar-shell: a v10.220-as dupla padding vissza ───
sub("    .appbar-shell { position:sticky; top:0; z-index:10; background:var(--app-surface,#FFFFFF); box-shadow:0 4px 18px rgba(20,30,50,0.05); border-bottom-left-radius:24px; border-bottom-right-radius:24px; padding-top:env(safe-area-inset-top); box-sizing:border-box; }",
    "    .appbar-shell { position:sticky; top:0; z-index:10; background:var(--app-surface,#FFFFFF); box-shadow:0 4px 18px rgba(20,30,50,0.05); border-bottom-left-radius:24px; border-bottom-right-radius:24px; }",
    'appbar-shell dupla padding vissza')

# ─── 2) PlayScreen fejléc: a v10.220-as dupla padding vissza ───
sub("      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, paddingTop:'max(12px, env(safe-area-inset-top))', paddingBottom:6, paddingLeft:16, paddingRight:16, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>",
    "      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, paddingTop:12, paddingBottom:6, paddingLeft:16, paddingRight:16, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>",
    'PlayScreen fejlec dupla padding vissza')

# ─── 3) a státuszsáv mögötti csík megfestése a fejléc színével ───
sub("""      <div key={creatingRoom ? 'creating' : screen} style={{ height:'100dvh', width:'100%', display:'flex', flexDirection:'column', overflow:'hidden', boxSizing:'border-box', paddingTop:'env(safe-area-inset-top)', animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)` }}>""",
    """      <div key={creatingRoom ? 'creating' : screen} style={{ position:'relative', height:'100dvh', width:'100%', display:'flex', flexDirection:'column', overflow:'hidden', boxSizing:'border-box', paddingTop:'env(safe-area-inset-top)', animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)` }}>
        {/* Státuszsáv mögötti csík. A konténer paddingTop-ja miatt a tartalom a
            státuszsáv alatt kezdődik; enélkül ott a <body> barack háttere
            látszana akkor is, ha a képernyő teteje egy fehér AppBar — így nem
            tűnne natív appnak. A csík pont a padding-területet fedi, semmit nem
            mozdít el. Főoldalon / játék közben nincs fejléc, ott a téma háttere
            a helyes szín. */}
        <div aria-hidden="true" style={{ position:'absolute', top:0, left:0, right:0,
          height:'env(safe-area-inset-top)', pointerEvents:'none', zIndex:1,
          background: (creatingRoom || screen === 'home' || screen === 'play') ? T.bg : T.surface }} />""",
    'statuszsav-csik')

sub("const APP_VERSION = 'v10.222';", "const APP_VERSION = 'v10.223';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — dupla safe-area padding megszuntetve + statuszsav-csik a fejlec szinevel')
