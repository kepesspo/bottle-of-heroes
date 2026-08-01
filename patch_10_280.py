#!/usr/bin/env python3
# v10.280 — Én még soha: a lap a Szerencsekerék formanyelvet kapja,
#           és a kapcsolo helyett a BUNTETES lepteto megy, 1-es plafonnal
#
# 1. A KAPCSOLO HELYETT LEPTETO (max 1)
#    "ne switch legyen hanem a buntetesnel hasznalt felulet csak annyi
#    valtoztatassal hogy csak 1 kortyot engedjen."
#    A `PlayerDrinkRow` megkap egy `max` propot: a `+` gomb a plafonon letiltott,
#    ugyanugy nezve, mint a `−` nullan. A 'toggle' mod kikerul — nem hasznalja
#    senki, es holt kodkent csak felretenne.
#
# 2. A LAP FORMANYELVE
#    A referencia a Szerencsekerek kepernyoje. Amit ott eltalaltunk:
#      * EGY nagy, kozepre igazitott hos-elem (a kerek), nem tobb reteg egymason
#      * folotte egy rovid, halk instrukcio-sor
#      * a metaadat NEM a hos-elemen belul zsufolodik
#      * lagy, egyszeru arnyek — nem arnyek az arnyekon
#    Ehhez kepest az "En meg soha" lapja harom elforgatott reteg volt egymas
#    hegyen-hatan, a metaadattal a lapon belul.
#
#    Most:
#      * a harom elforgatott hatso lap KIKERUL
#      * a fuszer-jelveny es a lapszam egy halk sorba kerul a lap FOLE
#      * a lap egyetlen tiszta feluletre egyszerusodik, 28-as lekerekitessel
#        (mint a tobbi hos-elem), es az ALLITAS a foszereplo: 23 px, kozepen
#      * fix magassag helyett a tartalomhoz igazodik, de van minimuma, hogy a
#        rovid es a hosszu allitas ne ugraljon
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─────────────────────────────────────────────────────────────────────────────
# 1. PlayerDrinkRow: `max` plafon, a 'toggle' mod kivezetve
# ─────────────────────────────────────────────────────────────────────────────
OLD_ROW = """function PlayerDrinkRow({ p, cnt, onAdd, onRemove, mode }) {
  const on = cnt > 0;
  const stepBtn = (extra) => ({ width:30, height:30, borderRadius:9, border:'none', flexShrink:0,
    fontFamily:T.font, fontSize:17, fontWeight:900, lineHeight:1, display:'grid', placeItems:'center', ...extra });
  return (
    <div onClick={mode === 'toggle' ? (e) => { if (on) onRemove(p.id); else { onAdd(p.id); if (window.bohFloat) window.bohFloat(e.currentTarget, '+1 🍺', T.coral); } } : undefined}
         style={{ flexShrink:0, height:DRINK_ROW_H, display:'flex', alignItems:'center', gap:10, padding:'7px 10px',
                  background: (mode === 'toggle' && on) ? T.coral + '1F' : T.surfaceMuted,
                  borderRadius:14, cursor: mode === 'toggle' ? 'pointer' : 'default', transition:'background .15s' }}>
      <PlayerAvatar player={p} size={34} />
      <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink,
                    overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
      {mode === 'toggle' ? (
        <div style={{ flexShrink:0, width:62, height:32, borderRadius:999, position:'relative',
                      background: on ? T.coral : `${T.inkMute}38`, transition:'background .15s' }}>
          <span style={{ position:'absolute', top:0, bottom:0, width:28, display:'grid', placeItems:'center',
                         fontFamily:T.font, fontSize:9, fontWeight:900, letterSpacing:'0.04em',
                         right:4, color:T.inkSoft, opacity: on ? 0 : 1 }}>NEM</span>
          <span style={{ position:'absolute', top:0, bottom:0, width:28, display:'grid', placeItems:'center',
                         fontFamily:T.font, fontSize:9, fontWeight:900, letterSpacing:'0.04em',
                         left:4, color:'#fff', opacity: on ? 1 : 0 }}>IGEN</span>
          <span style={{ position:'absolute', top:3, left: on ? 33 : 3, width:26, height:26, borderRadius:'50%',
                         background:'#fff', boxShadow:'0 1px 3px rgba(0,0,0,0.2)', transition:'left .15s' }} />
        </div>
      ) : (
        <div style={{ display:'flex', alignItems:'center', gap:6, flexShrink:0 }}>
          <button onClick={()=>onRemove(p.id)} disabled={!on}
            style={stepBtn({ background: on ? T.surface : 'transparent', color: on ? T.inkSoft : T.inkMute,
                             boxShadow: on ? T.shadowPill : 'none', cursor: on ? 'pointer' : 'default' })}>−</button>
          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, minWidth:44, textAlign:'center',
                         color: on ? T.coral : T.inkMute, fontVariantNumeric:'tabular-nums',
                         display:'inline-flex', alignItems:'center', justifyContent:'center', gap:3 }}>
            {on ? <React.Fragment>{cnt}<BohIcon name="beer" size={14} /></React.Fragment> : '–'}
          </span>
          <button onClick={(e)=>{ onAdd(p.id); if (window.bohFloat) window.bohFloat(e.currentTarget, `+${cnt+1} 🍺`, T.coral); }}
            style={stepBtn({ background: T.coral+'22', color:T.coral, cursor:'pointer' })}>+</button>
        </div>
      )}
    </div>
  );
}"""

NEW_ROW = """// `max`: felso plafon egy jatekosra. Az "En meg soha" igaz/hamis kerdes, ott
// `max={1}` — a `+` a plafonon ugyanugy letiltott, ahogy a `−` nullan. Igy a
// felulet SZO SZERINT a buntetesnel hasznalt, csak nem enged 1-nel tobbet.
function PlayerDrinkRow({ p, cnt, onAdd, onRemove, max }) {
  const on = cnt > 0;
  const tele = max != null && cnt >= max;
  const stepBtn = (extra) => ({ width:30, height:30, borderRadius:9, border:'none', flexShrink:0,
    fontFamily:T.font, fontSize:17, fontWeight:900, lineHeight:1, display:'grid', placeItems:'center', ...extra });
  return (
    <div style={{ flexShrink:0, height:DRINK_ROW_H, display:'flex', alignItems:'center', gap:10, padding:'7px 10px',
                  background: on ? T.coral + '16' : T.surfaceMuted, borderRadius:14, transition:'background .15s' }}>
      <PlayerAvatar player={p} size={34} />
      <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink,
                    overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
      <div style={{ display:'flex', alignItems:'center', gap:6, flexShrink:0 }}>
        <button onClick={()=>onRemove(p.id)} disabled={!on}
          style={stepBtn({ background: on ? T.surface : 'transparent', color: on ? T.inkSoft : T.inkMute,
                           boxShadow: on ? T.shadowPill : 'none', cursor: on ? 'pointer' : 'default' })}>−</button>
        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, minWidth:44, textAlign:'center',
                       color: on ? T.coral : T.inkMute, fontVariantNumeric:'tabular-nums',
                       display:'inline-flex', alignItems:'center', justifyContent:'center', gap:3 }}>
          {on ? <React.Fragment>{cnt}<BohIcon name="beer" size={14} /></React.Fragment> : '–'}
        </span>
        <button onClick={(e)=>{ if (tele) return; onAdd(p.id); if (window.bohFloat) window.bohFloat(e.currentTarget, `+${cnt+1} 🍺`, T.coral); }}
          disabled={tele}
          style={stepBtn({ background: tele ? 'transparent' : T.coral+'22', color: tele ? T.inkMute : T.coral,
                           cursor: tele ? 'default' : 'pointer' })}>+</button>
      </div>
    </div>
  );
}"""
sub(OLD_ROW, NEW_ROW, 'PlayerDrinkRow max')

sub("""// `mode`: 'stepper' (alap) vagy 'toggle'. A lista legfeljebb 5 sort mutat,
// onnantol gorget — igy a zaro gomb SOSEM csuszik a lathato resz ala. (Merve:
// 10 jatekosnal a regi valtozatban 940 px-nel volt, egy 874 px-es kepernyon.)
function DrinkDistributor({ players, onFinish, title, mode }) {""",
    """// `max`: felso plafon jatekosonkent (pl. En meg soha: 1). A lista legfeljebb
// 5 sort mutat, onnantol gorget — igy a zaro gomb SOSEM csuszik a lathato resz
// ala. (Merve: 10 jatekosnal a regi valtozatban 940 px-nel volt, 874-en.)
function DrinkDistributor({ players, onFinish, title, max }) {""",
    'DrinkDistributor max')

sub("""        {players.map(p => (
          <PlayerDrinkRow key={p.id} p={p} cnt={drinks[p.id]||0} onAdd={add} onRemove={remove} mode={mode} />
        ))}""",
    """        {players.map(p => (
          <PlayerDrinkRow key={p.id} p={p} cnt={drinks[p.id]||0} onAdd={add} onRemove={remove} max={max} />
        ))}""",
    'sor atadas')

sub("""        {total>0 ? (mode === 'toggle' ? `${fo} iszik · ${total} korty` : `${total} korty kiosztva`) : 'Senki sem iszik'}""",
    """        {total>0 ? (max === 1 ? `${fo} iszik · ${total} korty` : `${total} korty kiosztva`) : 'Senki sem iszik'}""",
    'gomb szoveg')

sub("""        <DrinkDistributor players={players||[]} onFinish={handleFinish} mode="toggle" title="Kire igaz?" />""",
    """        <DrinkDistributor players={players||[]} onFinish={handleFinish} max={1} title="Kire igaz?" />""",
    'sohanem max')

# ─────────────────────────────────────────────────────────────────────────────
# 2. A lap: egyetlen tiszta hos-elem, folotte halk metaadat-sor
# ─────────────────────────────────────────────────────────────────────────────
OLD_CARD = """      {/* Kártya */}
      {/* 62% -> 48%: a lista es a zaro gomb is elfer alatta gorgetes nelkul.
          A marginBottom a hatso lapok tulnyulasat fogja fel (bottom:-6 + forgatas). */}
      <div style={{ position:'relative', width:'100%', paddingTop:'48%', marginBottom:10 }}>
        <div style={{ position:'absolute', left:'3%', right:'3%', top:6, bottom:-6, background:backColors[gameIdx%backColors.length], borderRadius:18, transform:'rotate(-5deg)', transformOrigin:'center bottom' }} />
        <div style={{ position:'absolute', left:'2%', right:'2%', top:3, bottom:-3, background:backColors[(gameIdx+1)%backColors.length], borderRadius:18, transform:'rotate(4deg)', transformOrigin:'center bottom' }} />
        <div style={{ position:'absolute', inset:0, background:T.surface, borderRadius:18, boxShadow:'0 4px 20px rgba(0,0,0,0.12)', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'space-between', padding:'14px 16px 12px' }}>
          <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', width:'100%' }}>
            <div style={{ display:'flex', alignItems:'center', gap:5, background:`${lv.color}20`, borderRadius:999, padding:'4px 10px' }}>
              <span style={{ fontSize:12 }}>{lv.emoji}</span>
              <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:tierInk(lv.color), letterSpacing:'0.06em' }}>{lv.label}</span>
            </div>
            <span style={{ fontFamily:T.font, fontSize:11, fontWeight:600, color:T.inkSoft }}>
              <span style={{ fontWeight:800, color:T.ink }}>{String(cardNum).padStart(2,'0')}</span>/{total}
            </span>
          </div>
          <div style={{ textAlign:'center', padding:'8px 8px 4px' }}>
            <div style={{ fontFamily:T.font, fontSize:12, fontWeight:500, color:T.inkSoft, marginBottom:6 }}>{t('sohanemPrefix')}</div>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:19, color:T.ink, lineHeight:1.3 }}>{card.t}.</div>
          </div>
        </div>
      </div>"""

NEW_CARD = """      {/* ── A LAP — a Szerencsekerek formanyelve (v10.280) ──
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
sub(OLD_CARD, NEW_CARD, 'lap redesign')

# a backColors mar nem kell — csak a kivezetett hatso lapokhoz kellett
sub("""  const backColors = ['#5BA0DB','#E985B8','#F4C95A'];
""", "", 'backColors')

sub("const APP_VERSION = 'v10.279';", "const APP_VERSION = 'v10.280';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — lepteto max 1, es a lap egyetlen tiszta hos-elem')
