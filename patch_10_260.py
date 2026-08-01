#!/usr/bin/env python3
# v10.260 — Csak Egy Szó: elmarad a hamis „behajtott sarok"
#
# MI VOLT A BAJ
# A szó-kártya jobb felső sarkára két CSS-háromszög volt téve, hogy behajtott
# papírsarkot utánozzon. Chromiumban megmérve két hibája is volt:
#
#   1. A kártya sarka 20 px-re kerekített, a hajtás viszont 44 px-es, derékszögű
#      háromszög. A lekerekítés leharapta a háromszög csúcsát, így a 45 fokos él
#      nem ért el a kártya széléig — ez volt a „fura sarok".
#   2. A „kivágott" háromszög a LAP hátterét festi (T.bg), a kártya viszont
#      T.surfaceMuted. A két szín majdnem egyforma, de nem az, így nem lyuknak
#      látszott, hanem egy odakent foltnak. A hajtóka ráadásul tiszta fehér volt,
#      vagyis VILÁGOSABB a kártyánál — a papír hátoldala sosem világosabb.
#
# MIT PRÓBÁLTAM
# Szögletesre vettem azt az egy sarkot (20px 0 20px 20px), és a hajtókát a
# geometriailag helyes oldalra, sötétebb tónusban (bgDeep) tettem. A geometria
# rendbe jött, de a látvány nem: mivel a kártya színe majdnem a lap színe, az
# egész 44 px-es sarok egy kék négyzetnek látszott, nem hajtásnak.
#
# A DÖNTÉS
# A hajtás díszítés, nem hordoz információt. Az app minden más kártyája sima
# lekerekített doboz — ez így egységes is lesz. A jelentést a szem-ikon, a
# pöttyök és a „Tartsd lenyomva" felirat amúgy is elmondja.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""          {/* A lap: vilagos, behajtott sarokkal — a sotet doboz ugy nezett ki,
              mint egy hibauzenet, pedig ez a jatek fo felulete. */}""",
    """          {/* A lap vilagos — a sotet doboz ugy nezett ki, mint egy hibauzenet,
              pedig ez a jatek fo felulete. A korabbi hamis "behajtott sarok"
              kikerult: lasd patch_10_260.py */}""",
    'kommenт')

sub("""            {/* behajtott sarok */}
            <div style={{ position:'absolute', top:0, right:0, width:0, height:0,
                          borderTop:`44px solid ${T.bg}`, borderLeft:'44px solid transparent' }} />
            <div style={{ position:'absolute', top:0, right:0, width:0, height:0,
                          borderBottom:'44px solid ' + T.surface, borderLeft:'44px solid transparent',
                          filter:'drop-shadow(-2px 2px 3px rgba(20,30,50,0.16))' }} />
""", "", 'haromszogek torlese')

sub("const APP_VERSION = 'v10.259';", "const APP_VERSION = 'v10.260';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — nincs tobb hamis hajtott sarok')
