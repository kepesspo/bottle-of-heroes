#!/usr/bin/env python3
# v10.265 — Szerencsekerék: elmarad a „A kiválasztott" kártya · a kicsi sáv árnyéka
#
# 1. A kerék alatt megjelenő „A KIVÁLASZTOTT" kártya kikerül. Amikor készült,
#    még nem volt result banner ehhez a játékhoz; most viszont a kör végén
#    úgyis feljön a nagy kártya ugyanezzel (név, avatar, korty), tehát ez
#    ugyanazt mondta el kétszer, két különböző formában.
#    A `winner` állapot MARAD: a kör lezárásához (onResult/onAdvance) kell.
#
# 2. A kicsi sávnak ugyanaz az árnyéka lesz, mint az app többi kártyájának
#    (T.shadow): tömör alsó perem + lágy elmosás. Eddig egy saját, felfelé is
#    szóró árnyéka volt — az elütött a többi felülettől.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. a "A kivalasztott" kartya kikerul ──
sub("""      {/* A kivalasztott — a kerek megall, de a nev a cikkelyben aprobb, mint
          amit egy asztal tuloldalarol el lehet olvasni. */}
      {winner && (
        <div style={{ width:'100%', boxSizing:'border-box', background:T.surface, borderRadius:18,
                      padding:'12px 16px', boxShadow:T.shadow, display:'flex', alignItems:'center', gap:13,
                      animation:'popIn .3s' }}>
          <div style={{ width:52, height:52, borderRadius:'50%', overflow:'hidden', flexShrink:0,
                        background:winner.color, display:'grid', placeItems:'center' }}>
            {winner.img
              ? <img src={winner.img} alt="" style={{ width:'100%', height:'100%', objectFit:'cover' }} />
              : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:'#fff' }}>{(winner.name||'?').charAt(0).toUpperCase()}</span>}
          </div>
          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:9.5, color:T.inkSoft, letterSpacing:1.6 }}>A KIVÁLASZTOTT</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.ink, lineHeight:1.2,
                          overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{winner.name}</div>
          </div>
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:1, flexShrink:0 }}>
            <BohIcon name="beer" size={20} />
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, lineHeight:1 }}>1</span>
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:8.5, color:T.inkSoft, letterSpacing:1.2 }}>KORTY</span>
          </div>
        </div>
      )}
""",
    """      {/* A korabbi "A KIVÁLASZTOTT" kartya kikerult: a kor vegen ugyis feljon a
          result banner ugyanezzel (avatar, nev, korty). A `winner` allapot marad,
          a kor lezarasahoz kell. Lasd patch_10_265.py */}
""",
    'kivalasztott kartya torlese')

# ── 2. a kicsi sav arnyeka = a tobbi kartyaé ──
sub("""          <div style={{ background:T.surface, borderRadius:16, overflow:'hidden', width:'100%',
                        boxShadow:'0 -2px 10px rgba(20,30,50,0.10), 0 8px 22px rgba(20,30,50,0.22)' }}>""",
    """          {/* Ugyanaz az arnyek, mint az app tobbi kartyajan (T.shadow) — eddig
              sajat, felfele is szoro arnyeka volt, az elutott a tobbitol. */}
          <div style={{ background:T.surface, borderRadius:16, overflow:'hidden', width:'100%', boxShadow:T.shadow }}>""",
    'kicsi sav arnyek')

sub("const APP_VERSION = 'v10.264';", "const APP_VERSION = 'v10.265';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — nincs dupla kiirás, egyseges arnyek')
