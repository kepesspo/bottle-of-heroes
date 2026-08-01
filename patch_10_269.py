#!/usr/bin/env python3
# v10.269 — az állás-sorok alól eltűnik a „fura árnyék"
#
# A sorok a nagy, KÁRTYÁRA hangolt T.shadow-t viselték: 5 px tömör perem +
# egy 12 px-re tolt, 28 px szórású réteg. A sorok között viszont csak 10 px a
# rés, tehát a szomszédos sorok szórt árnyéka EGY SÁVVÁ folyt össze — pont az a
# szürke elkenődés, ami a Szerencsekerék körül is látszott.
#
# Ez a csapda már le van írva a témában, a `shadowPill` mellett:
#   „a T.shadow kartyara van hangolva … kis elemen az elszakad a gombtol, es a
#    szomszedok szort arnyeka egy savva folyik ossze”
# Vagyis a megoldás is megvolt már, csak ez a lista nem használta: a pirula-
# méretű árnyék (2 px tömör + 2/6 px szórás) ugyanaz a formanyelv, arányosan
# kicsinyítve — a sorok elválnak, de nem kenődnek egymásba.
#
# Ugyanez a sor a parti végi eredmény-listában is fut, ott ugyanígy javul.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""    <div style={{ background:T.surface, borderRadius:14, boxShadow: T.shadow, border: 'none', padding:'10px 14px', display:'flex', alignItems:'center', gap:12, position:'relative', overflow:'hidden' }}>""",
    """    {/* shadowPill, NEM T.shadow: a sorok kozott csak 10 px a res, es a nagy
        arnyek 28 px-es szorasa a szomszeddal egy savva folyt ossze. Lasd a
        temaban a shadowPill kommentjet es patch_10_269.py */}
    <div style={{ background:T.surface, borderRadius:14, boxShadow: T.shadowPill, border: 'none', padding:'10px 14px', display:'flex', alignItems:'center', gap:12, position:'relative', overflow:'hidden' }}>""",
    'LeaderRow arnyek')

sub("const APP_VERSION = 'v10.268';", "const APP_VERSION = 'v10.269';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — pirula-arnyek az allas-sorokon')
