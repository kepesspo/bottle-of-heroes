#!/usr/bin/env python3
# v10.246 — a result banner belépője nem rángatja oldalra a profilképeket
#
# A "valaki iszik" eredménynél a banner belépő animációja fél másodperc alatt
# NÉGYSZER rántotta oldalra az egész kártyát:
#     50% translateX(-10px) → 65% +10px → 78% −5px → 90% +5px
# A profilképek ezzel együtt mozogtak — ez volt az "ugrálás" a nagy és a kis
# bannerben egyaránt.
#
# Marad a belépő "pop": kicsiből nagyra, egy finom visszahúzással. Vízszintes
# elmozdulás nincs, tehát a kép a helyén marad.
#
# A keyframe nevét is cseréljük: a "shake" már nem igaz, és egy hazudós név
# később megint félrevisz.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""    @keyframes resultShakeIn { 0%{transform:scale(0.5);opacity:0} 35%{transform:scale(1.06);opacity:1} 50%{transform:scale(1) translateX(-10px)} 65%{transform:translateX(10px)} 78%{transform:translateX(-5px)} 90%{transform:translateX(5px)} 100%{transform:translateX(0)} }""",
    """    /* Belépő "pop" — SZÁNDÉKOSAN nincs benne vízszintes elmozdulás: a korábbi
       változat négyszer rántotta oldalra a kártyát, és a profilképek ugráltak
       vele. A hangsúlyt a méret és a rugós visszahúzás adja. */
    @keyframes resultLoseIn { 0%{transform:scale(0.5);opacity:0} 55%{transform:scale(1.06);opacity:1} 78%{transform:scale(0.985)} 100%{transform:scale(1);opacity:1} }""",
    'keyframe')

sub("""        const anim = hasWin && !hasLose ? 'resultCalmIn .3s ease-out forwards' : 'resultShakeIn .5s ease-out forwards';""",
    """        const anim = hasWin && !hasLose ? 'resultCalmIn .3s ease-out forwards' : 'resultLoseIn .5s ease-out forwards';""",
    'hasznalat')

sub("const APP_VERSION = 'v10.245';", "const APP_VERSION = 'v10.246';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — nincs tobbe oldalra rangatas a result banner belepojeben')
