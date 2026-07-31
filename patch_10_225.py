#!/usr/bin/env python3
# v10.225 — a státuszsáv színe FOLYAMBAN LÉVŐ tartalomból, ne fix rétegből
#
# A v10.224 után az elrendezés helyes lett, de a sáv színe valós iPhone-on
# TOVÁBBRA IS barack maradt, pedig a szimulációban (Chromium) fehér volt.
#
# A magyarázat már ott volt a kódban, egy korábbi megfigyelés kommentjében:
#   "az iOS a status bar színét a folyamban lévő tartalomból veszi,
#    a fixed rétegeket üresnek látja"
# Vagyis a z55-ös csík azért nem festett, mert `position:fixed`. Eddig ez nem
# tűnt fel, mert a csík színe (T.bg) pont egyezett a mögötte lévő <body>
# háttérrel — így nem lehetett megkülönböztetni, hogy fest-e egyáltalán.
# Amint fehérre váltottam, kiderült: nem fest.
#
# Javítás: a színt a gyökér képernyő-konténer SAJÁT hátterére tesszük. Az
# folyamban lévő tartalom, és mivel a konténernek van
# `paddingTop:env(safe-area-inset-top)`-ja, a háttere pontosan a státuszsáv
# mögötti sávot festi ki — semmit nem mozdít el.
#
# A fix z55-ös csík megmarad (Androidon/böngészőben az fest), de ugyanabból az
# EGY konstansból kapja a színét, hogy a kettő ne tudjon szétcsúszni.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── 1) egyetlen közös konstans a BottleApp return-je elé ───
sub("""    return () => { window.removeEventListener('online', on); window.removeEventListener('offline', off); };
  }, []);
  return (""",
    """    return () => { window.removeEventListener('online', on); window.removeEventListener('offline', off); };
  }, []);
  // A státuszsáv mögötti sáv színe. Ahol fehér AppBar van a képernyő tetején,
  // ott fehér — így a fejléc a kijelző tetejéig ér, mint egy natív appban.
  // Ahol nincs fejléc (főoldal, játék közben, szoba létrehozása), ott a téma
  // háttere a helyes. EGY helyen definiálva: a gyökér-konténer háttere és a
  // fix festősáv is ezt használja, így nem tudnak szétcsúszni.
  const statusBarBg = (creatingRoom || screen === 'home' || screen === 'play') ? T.bg : T.surface;
  return (""",
    'statusBarBg konstans')

# ─── 2) a fix z55-ös csík a közös konstansból ───
sub("""        <div style={{ position:'fixed', top:0, left:0, right:0, height:'env(safe-area-inset-top)',
          background: (creatingRoom || screen === 'home' || screen === 'play') ? T.bg : T.surface,
          zIndex:55, pointerEvents:'none' }} />,""",
    """        <div style={{ position:'fixed', top:0, left:0, right:0, height:'env(safe-area-inset-top)',
          background: statusBarBg, zIndex:55, pointerEvents:'none' }} />,""",
    'z55 csik a kozos konstansbol')

# ─── 3) a LÉNYEG: a gyökér-konténer saját (folyamban lévő) háttere ───
sub("""      <div key={creatingRoom ? 'creating' : screen} style={{ height:'100dvh', width:'100%', display:'flex', flexDirection:'column', overflow:'hidden', boxSizing:'border-box', paddingTop:'env(safe-area-inset-top)', animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)` }}>""",
    """      <div key={creatingRoom ? 'creating' : screen} style={{ height:'100dvh', width:'100%', display:'flex', flexDirection:'column', overflow:'hidden', boxSizing:'border-box', paddingTop:'env(safe-area-inset-top)', background: statusBarBg, animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)` }}>""",
    'gyoker-kontener hattere')

sub("const APP_VERSION = 'v10.224';", "const APP_VERSION = 'v10.225';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — statuszsav szine folyamban levo tartalombol (gyoker-kontener hatter)')
