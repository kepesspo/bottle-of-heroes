#!/usr/bin/env python3
# v10.244 — a Büntetés lap ugyanolyan magas, mint a MENÜ lap
#
# MÉRVE (402×874, a lap doboz-magassága):
#     játékosok:      3        6        8
#     MENÜ:         365 px   365 px   365 px
#     BÜNTETÉS:     347 px   503 px   607 px
#
# A MENÜ magassága azért állandó, mert a "vezérlés" fül tartalma adja a
# mértéket, az "állás" fül pedig abszolút pozícióval belefér és magában
# görget. A Büntetés lapnak viszont semmi nem szabott határt: minden játékos
# egy sorral feljebb tolta, 6 fő fölött már jóval magasabbra ment.
#
# Javítás: a SheetOverlay kap egy `height` paramétert, és MINDKÉT játék
# közbeni lap ugyanazt az egy értéket használja. Egy szám, egy helyen — nem
# két külön szabály, ami később megint szétcsúszik. A nevek a lapon belül
# görögnek (ez a SheetOverlay-ben eddig is így volt), a "korty kiosztva"
# gomb pedig fixen alul marad.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. SheetOverlay: opcionális fix magasság ──
sub("""function SheetOverlay({ onClose, children, footer, title, zIndex }) {""",
    """function SheetOverlay({ onClose, children, footer, title, zIndex, height }) {""",
    'SheetOverlay szignatura')

sub("""          animation: closing ? 'none' : 'slideUp .3s cubic-bezier(.2,.9,.3,1)',
          maxHeight:'82vh',""",
    """          animation: closing ? 'none' : 'slideUp .3s cubic-bezier(.2,.9,.3,1)',
          height: height || undefined,
          maxHeight:'82vh',""",
    'SheetOverlay magassag')

# ── 2. közös érték: a játék közbeni lapok magassága ──
sub("""function SheetOverlay({ onClose, children, footer, title, zIndex, height }) {""",
    """// A JATEK KOZBENI lapok (MENÜ, Büntetés) egyforma magasak. A mertek a MENÜ
// "vezérlés" fulenek tartalma volt — ezt rogzitjuk, hogy a Buntetes ne a
// jatekosok szamatol fuggjon. Egy szam, egy helyen.
const PLAY_SHEET_H = 'min(365px, 82vh)';

function SheetOverlay({ onClose, children, footer, title, zIndex, height }) {""",
    'PLAY_SHEET_H')

# ── 3. mindkét lap ugyanazt kapja ──
sub("""          <SheetOverlay onClose={() => setShowMenu(false)}>""",
    """          <SheetOverlay onClose={() => setShowMenu(false)} height={PLAY_SHEET_H}>""",
    'menu lap')

sub("""    <SheetOverlay onClose={onClose} title="Büntetés — ki igyon?" footer={""",
    """    <SheetOverlay onClose={onClose} title="Büntetés — ki igyon?" height={PLAY_SHEET_H} footer={""",
    'buntetes lap')

sub("const APP_VERSION = 'v10.243';", "const APP_VERSION = 'v10.244';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — a ket jatek kozbeni lap egyforma magas')
