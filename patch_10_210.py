#!/usr/bin/env python3
# v10.210 — a logo koruli ket-ket szoveg (fooldalon: "DNR GAMES" felett +
# "Bottle of Heroes" alatt; nyito kepernyon: a cim + az alatta levo szlogen)
# szorosabban koveti a logot — a logo idokozben jelentosen megnott, a regi
# tavolsag mar tul lazanak hatott hozza kepest.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# fooldal: DNR GAMES <-> logo <-> Bottle of Heroes tavolsaga
sub('.home-brand      { display:flex; flex-direction:column; align-items:center; gap:18px; }',
    '.home-brand      { display:flex; flex-direction:column; align-items:center; gap:10px; }',
    'home-brand gap')
sub('''      .home-brand { gap:10px; }''',
    '''      .home-brand { gap:6px; }''',
    'home-brand gap (also alacsony kepernyon)')

# nyito kepernyo: logo <-> cim <-> szlogen tavolsaga
sub('''    #splash-title-wrap {
      position:relative; z-index:2; margin-top:18px;''',
    '''    #splash-title-wrap {
      position:relative; z-index:2; margin-top:10px;''',
    'splash cim tavolsaga')
sub('''    #splash-tagline {
      margin-top:10px;''',
    '''    #splash-tagline {
      margin-top:6px;''',
    'splash szlogen tavolsaga')

sub("const APP_VERSION = 'v10.209';", "const APP_VERSION = 'v10.210';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — a logo koruli szovegek szorosabbra huzva')
