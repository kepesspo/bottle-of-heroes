#!/usr/bin/env python3
# v10.279c — a kartya ala logo elforgatott retegek ne ussanak ra a listara
#
# A kartya-stack ket hatso lapja `bottom:-6px`-tel es elforgatva ul, tehat a
# konteneren TULNYULIK lefele. A kisebb kartyaval (48%) a "Kire igaz?" felirat
# pont ebbe a savba kerult. Egy kis also margo kell — a gap nem eleg, mert az a
# konteneren kivul szamol, a tulnyulas viszont azon belul rajzolodik.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""      {/* 62% -> 48%: a lista es a zaro gomb is elfer alatta gorgetes nelkul */}
      <div style={{ position:'relative', width:'100%', paddingTop:'48%' }}>""",
    """      {/* 62% -> 48%: a lista es a zaro gomb is elfer alatta gorgetes nelkul.
          A marginBottom a hatso lapok tulnyulasat fogja fel (bottom:-6 + forgatas). */}
      <div style={{ position:'relative', width:'100%', paddingTop:'48%', marginBottom:10 }}>""",
    'kartya margo')

open(P, 'w', encoding='utf-8').write(src)
print('OK')
