#!/usr/bin/env python3
# v10.192 — a státuszsáv sávja a fejléc színét kapja
#
# Az app egy globális festősávval tölti ki a status bar mögötti zónát (z55),
# MINDIG az app háttérszínével. A kezdőképernyőn ez jó — ott tényleg a háttér
# van felül. Ahol viszont fehér fejléc (AppBar) áll a lap tetején, ott egy
# narancs csík vágódik a status bar és a fehér sáv közé.
#
# Ez eddig is így volt, csak nem látszott: a régi, főképernyőre mentett
# példány más beállítással települt. Újratelepítés után (viewport-fit=cover +
# black-translucent) a safe-area már nem nulla, és előjött.
#
# Megoldás: az AppBar maga fest egy sávot a status bar zónájába, a SAJÁT
# hátterével, a globális sáv fölé (z56). Egy helyen, minden fejléces képernyőre.
# Ugyanaz a minta, amit a DNR Pub képernyő már használ.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""function AppBar({ title, onBack, right, bg, left }) {
  return (
    <div className="appbar-shell" style={{ background: bg || T.surface, overflow:'hidden' }}>""",
    """function AppBar({ title, onBack, right, bg, left }) {
  // A status bar mogotti zonat a fejlec sajat szinere festjuk. A globalis
  // festosav (z55) az app hatteret teszi oda — fejleces kepernyon az egy
  // idegen csik a status bar es a feher sav kozott. Ez z56, tehat folotte van,
  // de a sheet-hatterek ala esik.
  const barBg = bg || T.surface;
  return (
    <React.Fragment>
      {typeof document !== 'undefined' && ReactDOM.createPortal(
        <div style={{ position:'fixed', top:0, left:0, right:0, height:'env(safe-area-inset-top)',
                      background:barBg, zIndex:56, pointerEvents:'none' }} />,
        document.body
      )}
    <div className="appbar-shell" style={{ background: barBg, overflow:'hidden' }}>""",
    'AppBar fej')

# a komponens lezarasa: a Fragment-et is be kell zarni
OLD_END = """      <div style={{ height:2, background:`linear-gradient(90deg, ${T.mint}, ${T.coral})`, opacity:0.7 }} />
    </div>
  );
}

function BubbleBackground() {"""
assert src.count(OLD_END) == 1, 'AppBar veg: %d' % src.count(OLD_END)
src = src.replace(OLD_END, """      <div style={{ height:2, background:`linear-gradient(90deg, ${T.mint}, ${T.coral})`, opacity:0.7 }} />
    </div>
    </React.Fragment>
  );
}

function BubbleBackground() {""", 1)

sub("const APP_VERSION = 'v10.191';", "const APP_VERSION = 'v10.192';", 'verzio')

open(P, 'w', encoding='utf-8').write(src)
print('OK — az AppBar festi a status bar zonajat a sajat szinere')
