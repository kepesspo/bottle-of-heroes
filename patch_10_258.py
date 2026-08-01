#!/usr/bin/env python3
# v10.258 — a korty-kapszula ne takarjon tartalmat
#
# A mockupban a lelógó kapszula üres kártyák sarkára lógott rá, és jól nézett
# ki. Élesben viszont az első dolog, ami a fejléc alatt jön, gyakran EGY SOR
# SZÖVEG — az Imposztornál például a játékleírás —, és annak a jobb végét
# egyszerűen letakarta. Olvashatatlan szöveg nem elfogadható ár egy jelvényért.
#
# A javítás: a fejléc annyival mélyebb lesz, amennyit a kapszula lelóg. A
# látvány ugyanaz (a kapszula továbbra is a gyűrűről lóg le a háttérbe), csak
# nem takar semmit. Ára ~42 px függőlegesen, és CSAK ott, ahol van kapszula.
#
# Ezzel a wildcard-sáv külön behúzása is feleslegessé vált — nincs mit kikerülni.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. a fejléc foglaljon helyet a lelógó résznek ──
sub("""      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, paddingTop:12, paddingBottom:6, paddingLeft:16, paddingRight:16, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>""",
    """      {/* A korty-kapszula lelog a gyuru ala. Ha csak "rálógna" a tartalomra,
          letakarna a jatekleirasok jobb veget — ezert a fejlec foglal neki
          helyet. Latvanyban ugyanaz, csak nem takar semmit. */}
      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, paddingTop:12, paddingBottom: stakeText ? 48 : 6, paddingLeft:16, paddingRight:16, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>""",
    'fejlec helyfoglalas')

# ── 2. a wildcard-sáv behúzása feleslegessé vált ──
sub("""        <div style={{ flexShrink:0, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box',
                      /* a korty-kapszula a jobb szelen lelog ide — hagyjunk neki helyet,
                         kulonben a "Szabalyszego?" gomb ala kerulne */
                      padding: stakeText ? '2px 76px 6px 16px' : '2px 16px 6px' }}>""",
    """        <div style={{ flexShrink:0, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box', padding:'2px 16px 6px' }}>""",
    'wildcard sav vissza')

sub("const APP_VERSION = 'v10.257';", "const APP_VERSION = 'v10.258';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — a kapszula nem takar tartalmat')
