#!/usr/bin/env python3
# v10.205 — "Quick Game" → "Villám Játék"
#
# Az egyetlen angol felirat volt a fokepernyon: a mellette allo Csatlakozas
# es Jatek magyar, ez meg nem. Ezen kivul a gomb ikonja mar most is villam
# (BohIcon "bolt"), tehat a nev ossze is er a kepevel.
#
# A felirat egyben be is kerul a TR tablaba (eddig kodba volt drotozva),
# igy egy helyen all a tobbi szoveggel.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("    quickGameSub: '2 véletlen játékos',",
    "    quickGame: 'Villám Játék', quickGameSub: '2 véletlen játékos',",
    'TR bejegyzes')

sub("""<span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.mint }}>Quick Game</span>""",
    """<span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.mint }}>{t('quickGame')}</span>""",
    'gomb felirat')

sub("const APP_VERSION = 'v10.204';", "const APP_VERSION = 'v10.205';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — Quick Game → Villám Játék')
