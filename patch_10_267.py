#!/usr/bin/env python3
# v10.267 — a kicsi result sáv annyi széles, mint alatta a játék-vezérlő
#
# Eddig a nagy kártyához igazodott (80vw, max 340), így a képernyő alján két
# különböző szélességű sáv állt egymás alatt: a result sáv keskenyebb volt, mint
# a MENÜ / Ki játszik / Kövi sor. Most mindkettő a képernyő széleitől 16-16
# px-re fut, tehát pontosan egymás alá esnek.
#
# A zsugorodó átmenet (a nagy kártyából a sávvá) is ezt a szélességet veszi fel,
# hogy ne ugorjon egyet a legvégén.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""        // A kicsi sav UGYANOLYAN SZELES, mint a nagy kartya — a lekicsinyites
        // igy nem ugrik szelesseget.
        const CARD_W = { width:'80vw', minWidth:260, maxWidth:340 };""",
    """        const CARD_W = { width:'80vw', minWidth:260, maxWidth:340 };
        // A kicsi sav a JATEK-VEZERLO savval azonos szeles: mindketto a kepernyo
        // szeleitol 16-16 px-re fut (a footer padding:'8px 16px'), igy pontosan
        // egymas ala esnek. Lasd patch_10_267.py
        const BAR_W = { left:16, right:16 };""",
    'BAR_W')

sub("""                  <div style={{ ...CARD_W, animation:'resultShrinkOut .35s cubic-bezier(.4,0,.6,1) forwards' }} onAnimationEnd={() => setResultMinimized(true)}>""",
    """                  <div style={{ width:'calc(100% - 32px)', animation:'resultShrinkOut .35s cubic-bezier(.4,0,.6,1) forwards' }} onAnimationEnd={() => setResultMinimized(true)}>""",
    'zsugorodas szelesseg')

sub("""                     style={{ position:'fixed', bottom:'calc(96px + env(safe-area-inset-bottom, 0px))', left:'50%', transform:'translateX(-50%)', ...CARD_W, zIndex:45, animation:'bohFadeIn .18s ease-out', cursor:'pointer' }}>""",
    """                     style={{ position:'fixed', bottom:'calc(96px + env(safe-area-inset-bottom, 0px))', ...BAR_W, zIndex:45, animation:'bohFadeIn .18s ease-out', cursor:'pointer' }}>""",
    'sav szelesseg')

sub("const APP_VERSION = 'v10.266';", "const APP_VERSION = 'v10.267';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — a sav a jatek-vezerlovel azonos szeles')
