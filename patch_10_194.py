#!/usr/bin/env python3
# v10.194 — a "Szoba létrehozása…" képernyő kap egy illusztrációt
#
# Eddig csak a felirat es harom pattogo pont volt rajta. Most a nyilo ajto
# rajza all folotte — atlatszo hatterrel, hogy sotet temaban is mukodjon.
#
# A kep NEM tolti ki a helyet fixen: a magassaga a rendelkezesre allo
# teruleghez igazodik (max 44vh), kulonben kis kepernyon a felirat lecsuszna.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""            <>
              <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay }}>Szoba létrehozása…</div>
              <div style={{ display:'flex', gap:6 }}>{[0,1,2].map(i => <span key={i} style={{ width:10, height:10, borderRadius:'50%', background:T.mint, animation:`dotBounce 1.2s ${i*0.15}s infinite ease-in-out` }}/>)}</div>
            </>""",
    """            <>
              <img src="assets/room_door.png" alt=""
                style={{ width:'min(62vw, 260px)', maxHeight:'44vh', objectFit:'contain',
                         display:'block', userSelect:'none',
                         filter:'drop-shadow(0 10px 22px rgba(20,30,50,0.16))',
                         animation:'roomDoorIn .5s cubic-bezier(.2,.85,.3,1.05)' }}
                draggable="false" />
              <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, textAlign:'center' }}>Szoba létrehozása…</div>
              <div style={{ display:'flex', gap:6 }}>{[0,1,2].map(i => <span key={i} style={{ width:10, height:10, borderRadius:'50%', background:T.mint, animation:`dotBounce 1.2s ${i*0.15}s infinite ease-in-out` }}/>)}</div>
            </>""",
    'creatingRoom tartalom')

# a bejovo animacio — a kulcskepek a tobbi mellett
sub("""    #splash-logo-wrap {""",
    """    @keyframes roomDoorIn {
      from { opacity:0; transform: translateY(14px) scale(0.94); }
      to   { opacity:1; transform: none; }
    }
    #splash-logo-wrap {""",
    'keyframes')

sub("const APP_VERSION = 'v10.193';", "const APP_VERSION = 'v10.194';", 'verzio')

open(P, 'w', encoding='utf-8').write(src)
print('OK — az ajto-illusztracio bekerult a szoba-letrehozo kepernyore')
