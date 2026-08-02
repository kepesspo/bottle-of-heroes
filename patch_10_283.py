#!/usr/bin/env python3
# v10.283 — halványabb hőfok-lap: a Szerencsekerék palettájából (a "H" valtozat)
#
# A telitett zold/narancs/voros harsany volt, es kilogott a tobbi kepernyo
# hangulatabol. Az uj szinek a `WHEEL_TONES` tombbol valok — abbol a hat
# pasztellbol, ami MA IS a Szerencsekerek cikkelyeit festi:
#     alap    #C9E8D2   (a kerek zoldje)
#     kozepes #F5E0AC   (a kerek sargaja)
#     vad     #F2C4C4   (a kerek rozsaszinje)
# A lap halvany marad, de a JELVENY a szin telitett valtozatat kapja feher
# felirattal — igy egy pillanat alatt kimondja a szintet, anelkul hogy az egesz
# kepernyot elvinne.
#
# KET DOLOG, AMI EGYUTT VALTOZIK A HATTERREL
#
#   1. A SZOVEG FIX SOTET, NEM `T.ink`.
#      Pasztell hattéren a feher olvashatatlan, a `T.ink` viszont a SOTET
#      temakban vilagos — ott ugyanugy eltunne. Mivel a lap szine temafuggetlen,
#      a tintanak is annak kell lennie. Ezert `CARD_INK = '#14202F'`.
#
#   2. Halkabb arnyek. A telitett lap alatt egy eros arnyek meg mukodott; egy
#      halvany lap alatt ugyanaz piszkosnak latszik.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""  // HOFOK-PALETTA — szandekosan FIX, nem a T.* tokenekbol.
  // 8 tema van, de az, hogy mennyire durva a kerdes, nem valtozhat temarol
  // temara. A feher szoveg mindharom hattéren olvashato.
  const SPICE = {
    alap:    { label:'ALAP',    emoji:'🌶', from:'#4FC2A0', to:'#2E9A70' },
    kozepes: { label:'KÖZEPES', emoji:'🔥', from:'#F0A93C', to:'#D97706' },
    vad:     { label:'VAD',     emoji:'🔥', from:'#E06050', to:'#C0392B' },
  };
  const lv = SPICE[card.l] || SPICE.alap;""",
    """  // HOFOK-PALETTA — a Szerencsekerek pasztelljeibol (lasd WHEEL_TONES).
  // Szandekosan FIX, nem a T.* tokenekbol: 8 tema van, de az, hogy mennyire
  // durva a kerdes, nem valtozhat temarol temara.
  //   `bg`    — a lap halvany hattere (a kerek egy-egy cikkelyszine)
  //   `badge` — ugyanaz telitve, a jelvenynek, feher felirattal
  const SPICE = {
    alap:    { label:'ALAP',    emoji:'🌶', bg:'#C9E8D2', badge:'#4FA97F' },
    kozepes: { label:'KÖZEPES', emoji:'🔥', bg:'#F5E0AC', badge:'#D69A2E' },
    vad:     { label:'VAD',     emoji:'🔥', bg:'#F2C4C4', badge:'#D46A6A' },
  };
  const lv = SPICE[card.l] || SPICE.alap;
  // A lap szine temafuggetlen, tehat a tintanak is annak kell lennie: pasztellen
  // a feher olvashatatlan, a `T.ink` viszont a SOTET temakban vilagos.
  const CARD_INK = '#14202F';""",
    'paletta')

OLD = """      <div style={{ width:'100%', borderRadius:26, padding:'20px 20px 22px', color:'#fff',
                    position:'relative', overflow:'hidden',
                    background:`linear-gradient(150deg, ${lv.from}, ${lv.to})`,
                    boxShadow:'0 8px 22px -6px rgba(20,30,50,0.35)' }}>
        <span style={{ position:'absolute', width:190, height:190, right:-70, top:-60,
                       borderRadius:'50%', border:'2px solid rgba(255,255,255,0.16)' }} />
        <span style={{ position:'absolute', width:120, height:120, left:-45, bottom:-45,
                       borderRadius:'50%', border:'2px solid rgba(255,255,255,0.16)' }} />
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', position:'relative' }}>
          <span style={{ display:'inline-flex', alignItems:'center', gap:5, background:'rgba(255,255,255,0.22)',
                         borderRadius:999, padding:'4px 10px', fontFamily:T.font, fontWeight:900, fontSize:10,
                         letterSpacing:'0.1em' }}>
            <span style={{ fontSize:11 }}>{lv.emoji}</span>{lv.label}
          </span>
          <span style={{ fontFamily:T.font, fontSize:11, fontWeight:700, opacity:0.85, fontVariantNumeric:'tabular-nums' }}>
            <span style={{ fontWeight:900, opacity:1 }}>{String(cardNum).padStart(2,'0')}</span>/{total}
          </span>
        </div>
        <div style={{ fontFamily:T.font, fontSize:12.5, fontWeight:600, opacity:0.85, margin:'14px 0 5px', position:'relative' }}>{t('sohanemPrefix')}</div>
        <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:allitasFs, lineHeight:1.2,
                      letterSpacing:'-0.02em', position:'relative' }}>{card.t}.</div>
      </div>"""

NEW = """      <div style={{ width:'100%', borderRadius:26, padding:'20px 20px 22px', color:CARD_INK,
                    position:'relative', overflow:'hidden', background:lv.bg,
                    boxShadow:'0 6px 18px -8px rgba(20,30,50,0.30)' }}>
        <span style={{ position:'absolute', width:190, height:190, right:-70, top:-60,
                       borderRadius:'50%', border:'2px solid rgba(20,32,47,0.07)' }} />
        <span style={{ position:'absolute', width:120, height:120, left:-45, bottom:-45,
                       borderRadius:'50%', border:'2px solid rgba(20,32,47,0.07)' }} />
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', position:'relative' }}>
          {/* a jelveny a szin TELITETT valtozata: a lap csendes marad, de a
              szint egy pillanat alatt kimondja */}
          <span style={{ display:'inline-flex', alignItems:'center', gap:5, background:lv.badge, color:'#fff',
                         borderRadius:999, padding:'4px 10px', fontFamily:T.font, fontWeight:900, fontSize:10,
                         letterSpacing:'0.1em' }}>
            <span style={{ fontSize:11 }}>{lv.emoji}</span>{lv.label}
          </span>
          <span style={{ fontFamily:T.font, fontSize:11, fontWeight:700, opacity:0.6, fontVariantNumeric:'tabular-nums' }}>
            <span style={{ fontWeight:900, opacity:1 }}>{String(cardNum).padStart(2,'0')}</span>/{total}
          </span>
        </div>
        <div style={{ fontFamily:T.font, fontSize:12.5, fontWeight:600, opacity:0.7, margin:'14px 0 5px', position:'relative' }}>{t('sohanemPrefix')}</div>
        <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:allitasFs, lineHeight:1.2,
                      letterSpacing:'-0.02em', position:'relative' }}>{card.t}.</div>
      </div>"""
sub(OLD, NEW, 'halvany lap')

sub("const APP_VERSION = 'v10.282';", "const APP_VERSION = 'v10.283';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — pasztell lap, telitett jelveny')
