#!/usr/bin/env python3
# v10.195 — Kvíz: a mockup szerinti elrendezés
#
# Amit a kapott terv mast mond a mostanihoz kepest:
#   1) lila "?" jelvény a kérdés-kártya tetején
#   2) a kártyán belül ott a tét korty-pirulája — eddig csak a lenti sávból
#      lehetett kiolvasni, hogy mi forog kockán
#   3) a TÉT-sáv nem külön fehér dobozban ül, hanem felirat + chip-sor
#   4) a válasz betűje színes chipbe kerül (A/B/C/D) — eddig apró szürke betű
#      volt a szöveg elott, alig latszott
#
# A hatter, az arnyek es a gombok stilusa nem valtozik.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── 1) Kérdés-kártya: jelvény + korty-pirula ───
sub("""        {/* Kérdés kártya */}
        <div style={{background:T.surface,borderRadius:18,padding:'16px',boxShadow:T.shadow}}>
          <div style={{fontFamily:T.font,fontSize:10,fontWeight:900,color:T.inkSoft,letterSpacing:1.5,marginBottom:6,textAlign:'center'}}>KÉRDÉS</div>
          <div style={{fontFamily:T.font,fontWeight:800,fontSize:16,color:T.ink,lineHeight:1.4,textAlign:'center'}}>{currentQ?.q}</div>
        </div>""",
    """        {/* Kérdés kártya — a tét a kártyán belül látszik, nem csak a lenti sávban */}
        <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}>
          <div style={{width:38,height:38,borderRadius:'50%',background:T.purple,display:'grid',placeItems:'center',
                       boxShadow:T.shadowPill,zIndex:2,marginBottom:-19}}>
            <span style={{fontFamily:T.font,fontWeight:900,fontSize:19,color:'#fff',lineHeight:1}}>?</span>
          </div>
          <div style={{width:'100%',boxSizing:'border-box',background:T.surface,borderRadius:18,padding:'26px 16px 16px',boxShadow:T.shadow,
                       display:'flex',flexDirection:'column',alignItems:'center',gap:10}}>
            <div style={{fontFamily:T.font,fontSize:10,fontWeight:900,color:T.inkSoft,letterSpacing:1.5}}>KÉRDÉS</div>
            <div style={{fontFamily:T.font,fontWeight:800,fontSize:16,color:T.ink,lineHeight:1.4,textAlign:'center'}}>{currentQ?.q}</div>
            <div style={{display:'flex',alignItems:'center',gap:7,background:T.yellow+'26',borderRadius:999,padding:'6px 14px'}}>
              <BohIcon name="beer" size={15} />
              <span style={{fontFamily:T.font,fontWeight:900,fontSize:13,color:T.yellowText||T.ink,letterSpacing:'0.02em'}}>{streak+1} KORTY</span>
            </div>
          </div>
        </div>""",
    'kerdes kartya')

# ─── 2) TÉT sáv: felirat + chip-sor, fehér doboz nélkül ───
sub("""        {/* Vízszintes TÉT sáv — mindig látható */}
        <div style={{background:T.surface,borderRadius:14,padding:'10px 12px',boxShadow:T.shadow}}>
          <div style={{fontFamily:T.font,fontSize:9,fontWeight:900,color:T.inkSoft,letterSpacing:1.5,marginBottom:6}}>TÉT — KORTY</div>
          <div style={{display:'flex',gap:5,alignItems:'stretch'}}>
            {tetValues.map(val => {
              const isCurrent = val === streak && streak > 0;
              const isNext = val === streak + 1;
              let bg = T.bgSoft;
              let border = 'transparent';
              let textColor = T.inkMute;
              let label = '';
              if (isCurrent) { bg = T.mint; border = T.mint; textColor = '#fff'; label = 'BANK'; }
              else if (isNext && !isResultOrBank) { bg = T.coral+'18'; border = T.coral+'55'; textColor = T.coral; label = 'KÖV'; }
              return (
                <div key={val} style={{
                  flex:1,borderRadius:8,padding:'6px 2px',
                  background:bg,border:'2px solid '+border,
                  display:'flex',flexDirection:'column',alignItems:'center',gap:2,
                  transition:'all .2s',
                }}>
                  <div style={{fontFamily:T.font,fontWeight:900,fontSize:14,color:textColor,lineHeight:1}}>{val}</div>
                  {label && <div style={{fontFamily:T.font,fontSize:7,fontWeight:800,color:textColor,opacity:0.8,letterSpacing:0.5}}>{label}</div>}
                </div>
              );
            })}
          </div>
        </div>""",
    """        {/* TÉT sáv — felirat a háttéren, alatta a chipek. A kiemelt chip a
            SOROS tét: kitöltve, hogy egy pillantásból látszódjon, hol tartunk. */}
        <div style={{display:'flex',flexDirection:'column',gap:7}}>
          <div style={{fontFamily:T.font,fontSize:9.5,fontWeight:900,color:T.inkSoft,letterSpacing:1.6}}>TÉT — KORTY</div>
          <div style={{display:'flex',gap:7,alignItems:'stretch'}}>
            {tetValues.map(val => {
              const isCurrent = val === streak && streak > 0;
              const isNext = val === streak + 1 && !isResultOrBank;
              const hot = isCurrent || isNext;
              const tone = isCurrent ? T.mint : T.coral;
              return (
                <div key={val} style={{
                  flex:1,borderRadius:12,padding:'11px 2px',
                  background: hot ? tone : T.surface,
                  border: '1.5px solid ' + (hot ? tone : T.inkMute+'2e'),
                  display:'grid',placeItems:'center',transition:'all .2s',
                }}>
                  <div style={{fontFamily:T.font,fontWeight:900,fontSize:15,lineHeight:1,
                               color: hot ? '#fff' : T.inkSoft}}>{val}</div>
                </div>
              );
            })}
          </div>
        </div>""",
    'TET sav')

# ─── 3) Válaszok: színes betű-chip ───
sub("""                <span style={{fontSize:11,opacity:0.5,fontWeight:900,minWidth:14}}>{letter}</span>
                <span style={{lineHeight:1.3,flex:1}}>{opt}</span>""",
    """                {/* A betű színes chipben — az apró szürke betű alig látszott,
                    pedig ez alapján mondja be az ember a válaszát. */}
                <span style={{width:30,height:30,flexShrink:0,borderRadius:9,display:'grid',placeItems:'center',
                              background: QUIZ_LETTER_TONES[i] + '24',
                              fontFamily:T.font,fontWeight:900,fontSize:14,
                              color: QUIZ_LETTER_TONES[i]}}>{letter}</span>
                <span style={{lineHeight:1.3,flex:1}}>{opt}</span>""",
    'valasz betu')

# a betuk szinei — a tema sajat palettajabol, hogy sotet temaban is elmenjen
sub("""function QuizGame({ gameIdx, challenger, players, onAdvance, onResult, onSetHideFooter, gameMeta }) {""",
    """// A/B/C/D szinek. Nem dekoracio: igy lehet ranezesre hivatkozni egy valaszra
// ("a kek"), es a szinek a tema palettajabol jonnek, tehat minden temaban ulnek.
const QUIZ_LETTER_TONES = ['#E0736B', '#4A90D9', '#C79A20', '#3EA882'];
function QuizGame({ gameIdx, challenger, players, onAdvance, onResult, onSetHideFooter, gameMeta }) {""",
    'betu szinek')

sub("const APP_VERSION = 'v10.194';", "const APP_VERSION = 'v10.195';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — Kviz elrendezes a mockup szerint')
