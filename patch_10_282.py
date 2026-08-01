#!/usr/bin/env python3
# v10.282 — Én még soha: HŐFOK-LAP (az "F" irany)
#
# A lap szine a fuszerszint: zold -> narancs -> voros. A jelveny igy nem plusz
# informacio, hanem megerosites — a tetet LATOD, mielott elolvasnad.
#
# A HAROM HOFOK-SZIN FIX, NEM TEMAFUGGO
#   8 tema van, es a lap jelentese (mennyire durva a kerdes) nem valtozhat
#   temarol temara. Ezert a szinek beegetve allnak, nem a T.* tokenekbol jonnek.
#   A feher szoveg mindharom hattéren olvashato.
#
# EGYUTT VALTOZO RESZEK
#   * a fuszer-jelveny es a lapszam a lap FOLE kiraktuk a v10.280-ban — most
#     visszakerul a lapra, mert ott mar a szin adja a kontextust, es igy egy
#     zart, plakatszeru elem lesz;
#   * a betumeret a szoveg hosszahoz igazodik: a "vad" lapok kozott van 70+
#     karakteres, ott a 24 px szetesne;
#   * a "Kire igaz?" cimke -> "Ki iszik?", kozepre igazitva. A regi szoveg a
#     folotte levo instrukciot ismetelte ("…jelold, kire igaz"); az uj azt
#     mondja, ami a sorokban tortenik.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─────────────────────────────────────────────────────────────────────────────
# 1. A hofok-paletta a regi levelMap helyett
# ─────────────────────────────────────────────────────────────────────────────
sub("""  const levelMap = { alap:{label:'ALAP',color:T.mint,emoji:'🌶'}, kozepes:{label:'KÖZEPES',color:T.yellow,emoji:'🔥'}, vad:{label:'VAD',color:T.coral,emoji:'🔥'} };
  const lv = levelMap[card.l] || levelMap.alap;""",
    """  // HOFOK-PALETTA — szandekosan FIX, nem a T.* tokenekbol.
  // 8 tema van, de az, hogy mennyire durva a kerdes, nem valtozhat temarol
  // temara. A feher szoveg mindharom hattéren olvashato.
  const SPICE = {
    alap:    { label:'ALAP',    emoji:'🌶', from:'#4FC2A0', to:'#2E9A70' },
    kozepes: { label:'KÖZEPES', emoji:'🔥', from:'#F0A93C', to:'#D97706' },
    vad:     { label:'VAD',     emoji:'🔥', from:'#E06050', to:'#C0392B' },
  };
  const lv = SPICE[card.l] || SPICE.alap;
  // A "vad" lapok kozott van 70+ karakteres — ott a 24 px szetesne.
  const hossz = (card.t || '').length;
  const allitasFs = hossz > 62 ? 19 : hossz > 42 ? 21.5 : 24;""",
    'hofok paletta')

# ─────────────────────────────────────────────────────────────────────────────
# 2. A lap
# ─────────────────────────────────────────────────────────────────────────────
OLD_CARD = """      {/* ── A LAP — a Szerencsekerek formanyelve (v10.280) ──
          Ott azt talaltuk el, hogy EGY nagy, kozepre igazitott hos-elem all a
          kepernyon, folotte egy halk instrukcio, es a metaadat NEM zsufolodik
          bele. Ehhez kepest itt harom elforgatott lap ult egymas hegyen-hatan,
          a jelvennyel es a lapszammal a lapon belul.
          Most: a hatso lapok kikerultek, a metaadat a lap FOLE kerult egy halk
          sorba, es a lap egyetlen tiszta felulet, amin az ALLITAS a foszereplo. */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', width:'100%', padding:'0 2px' }}>
        <div style={{ display:'flex', alignItems:'center', gap:5, background:`${lv.color}20`, borderRadius:999, padding:'4px 10px' }}>
          <span style={{ fontSize:12 }}>{lv.emoji}</span>
          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:tierInk(lv.color), letterSpacing:'0.06em' }}>{lv.label}</span>
        </div>
        <span style={{ fontFamily:T.font, fontSize:11.5, fontWeight:600, color:T.inkSoft, fontVariantNumeric:'tabular-nums' }}>
          <span style={{ fontWeight:900, color:T.ink }}>{String(cardNum).padStart(2,'0')}</span>/{total}
        </span>
      </div>
      <div style={{ width:'100%', minHeight:150, background:T.surface, borderRadius:28,
                    boxShadow:'0 4px 18px rgba(20,30,50,0.10)', display:'flex', flexDirection:'column',
                    alignItems:'center', justifyContent:'center', gap:8, padding:'22px 22px 24px' }}>
        <div style={{ fontFamily:T.font, fontSize:13, fontWeight:600, color:T.inkSoft }}>{t('sohanemPrefix')}</div>
        <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:23, color:T.ink, lineHeight:1.26,
                      textAlign:'center', letterSpacing:'-0.01em' }}>{card.t}.</div>
      </div>"""

NEW_CARD = """      {/* ── A HŐFOK-LAP ──
          A lap SZINE a fuszerszint. Igy a tet lathato, mielott elolvasnad: egy
          voros lap felfordulasa onmagaban esemeny. A jelveny nem plusz info,
          hanem megerosites. A halvany korok adnak melyseget a lapos szinnek. */}
      <div style={{ width:'100%', borderRadius:26, padding:'20px 20px 22px', color:'#fff',
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
sub(OLD_CARD, NEW_CARD, 'hofok lap')

# ─────────────────────────────────────────────────────────────────────────────
# 3. "Kire igaz?" -> "Ki iszik?", kozepre
# ─────────────────────────────────────────────────────────────────────────────
sub("""        <DrinkDistributor players={players||[]} onFinish={handleFinish} max={1} title="Kire igaz?" />""",
    """        <DrinkDistributor players={players||[]} onFinish={handleFinish} max={1} title="Ki iszik?" center />""",
    'cimke')

sub("""function DrinkDistributor({ players, onFinish, title, max, resetKey }) {""",
    """function DrinkDistributor({ players, onFinish, title, max, resetKey, center }) {""",
    'center prop')

sub("""        <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em' }}>{title}</div>""",
    """        <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em', textAlign: center ? 'center' : 'left' }}>{title}</div>""",
    'cimke kozepre')

sub("const APP_VERSION = 'v10.281';", "const APP_VERSION = 'v10.282';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — hofok-lap, "Ki iszik?" kozepen')
