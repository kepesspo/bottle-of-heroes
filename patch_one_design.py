#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# EGY DIZÁJN (v9.958):
#  - Playful mód megszűnik: _appDesign fixen 'classic', a playful ágak alvó kóddá válnak
#  - Téma shadow token: kis kemény offset ("3D") minden témában → app-szerte egységes
#  - BohIcon B-szelídítés: ~30%-kal vékonyabb kontúr, lágyabb tónusok, 1.15× méret
#  - Home: bal felső köszöntés + playful elrendezés kontúr nélkül, 3D offsetekkel
#  - Játékosok: kártyák pici döntéssel + 3D, korall × törlés
#  - Játékok: elrendezés/méret változatlan, kártyák 3D árnyékkal, mint kiválasztás
import io, re

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:90])
    src = src.replace(old, new)

# ── 1) Téma shadow tokenek: kemény 3px offset + ambient ──
def shadow_sub(m):
    c1, a1, c2, a2 = m.group(1), float(m.group(2)), m.group(3), float(m.group(4))
    if a2 >= 0.15:  # sötét témák: erősebb árnyék marad
        return "shadow: '0 3px 0 rgba(%s,0.30), 0 8px 20px rgba(%s,0.30)'" % (c1, c2)
    return "shadow: '0 3px 0 rgba(%s,0.10), 0 8px 20px rgba(%s,0.08)'" % (c1, c2)
new_src, n = re.subn(r"shadow: '0 2px 0 rgba\(([^)]+),([\d.]+)\), 0 6px 20px rgba\(([^)]+),([\d.]+)\)'", shadow_sub, src)
assert 7 <= n <= 10, 'theme shadows: expected 7-10, got %d' % n
src = new_src

# ── 2) BohIcon szelídítés ──
rep("  const I = '#1A2A4A', M = '#3DA888', C = '#E8604C', G = '#EDD17A', W = '#fff', CR = '#F7EFD8';",
    "  const I = '#3A4A68', M = '#67BCA4', C = '#EE9480', G = '#F0DFA6', W = '#fff', CR = '#FAF4E4';")
rep("""  // Globális méret-szorzó: a megadott méretnél ~32%-kal nagyobbra renderelünk,
  // hogy az ikonok vizuálisan az emojikhoz hasonló súlyúak legyenek.
  size = Math.round(size * 1.32);""",
"""  // Globális méret-szorzó: enyhén nagyobbra renderelünk az emoji-súlyhoz,
  // a B (szelídített) készlet kisebb, mint a korábbi matrica-look volt.
  size = Math.round(size * 1.15);""")
rep("      <rect x=\"6\" y=\"15\" width=\"36\" height=\"20\" rx=\"10\" fill=\"#7C5CC4\" stroke={I} strokeWidth=\"3.8\"/>",
    "      <rect x=\"6\" y=\"15\" width=\"36\" height=\"20\" rx=\"10\" fill=\"#9B82D4\" stroke={I} strokeWidth=\"3.8\"/>")
# kontúrvastagság ×0.7 CSAK a BohIcon törzsében
i0 = src.index('function BohIcon({ name, size = 20, style })')
i1 = src.index('function BohText', i0)
body = src[i0:i1]
body2, nsw = re.subn(r'strokeWidth="([\d.]+)"', lambda m: 'strokeWidth="%s"' % round(float(m.group(1)) * 0.7, 2), body)
assert nsw > 80, 'strokeWidth count too low: %d' % nsw
src = src[:i0] + body2 + src[i1:]

# ── 3) Egy dizájn: playful mód kikapcsolva ──
rep("let _appDesign = (() => { try { return localStorage.getItem('boh_home_design') === 'playful' ? 'playful' : 'classic'; } catch(e) { return 'classic'; } })();",
    "let _appDesign = 'classic'; // Egy dizájn — a playful mód megszűnt, minden felület a közös stílust használja")
rep("""function _setAppDesign(d) {
  const v = d === 'playful' ? 'playful' : 'classic';""",
"""function _setAppDesign(d) {
  const v = 'classic'; // egy dizájn — a playful érték már nem kapcsol át semmit""")

# ── 4) Home egységesítés ──
# 4a) konfetti szórás mindig
rep("""      {isPlayful && (
        <div style={{ position:'absolute', inset:0, overflow:'hidden', pointerEvents:'none', zIndex:0 }}>""",
"""      {(
        <div style={{ position:'absolute', inset:0, overflow:'hidden', pointerEvents:'none', zIndex:0 }}>""")
# 4b) logó egységes méret
rep("<Logo size={isPlayful ? 130 : 148} />", "<Logo size={142} />")
# 4c) cím egy változat
rep("""            {isPlayful ? (
              <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:26, lineHeight:1, letterSpacing:'0.04em', color:T.ink, textTransform:'uppercase', whiteSpace:'nowrap' }}>
                Bottle of <span style={{ color:T.coral }}>Heroes</span>
              </div>
            ) : (
              <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:28, lineHeight:1, letterSpacing:'0.05em', color:T.ink, textTransform:'uppercase', whiteSpace:'nowrap' }}>
                Bottle of Heroes
              </div>
            )}""",
"""            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:28, lineHeight:1, letterSpacing:'0.05em', color:T.ink, textTransform:'uppercase', whiteSpace:'nowrap' }}>
              Bottle of Heroes
            </div>""")
# 4d) bal felső: mindig köszöntés (verzió a dátum-sorban)
rep("""          {isPlayful && (
            <div style={{ pointerEvents:'auto' }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:19, color:T.ink, letterSpacing:'-0.01em', lineHeight:1.05, whiteSpace:'nowrap' }}>👋 {greetHi}</div>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkSoft, marginTop:2 }}>{greetSub}</div>
            </div>
          )}
          {!isPlayful && (
          <div style={{ display:'inline-flex', alignItems:'center', gap:6, padding:'5px 12px', background:T.surface, borderRadius:999, boxShadow:T.shadow, fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkSoft, letterSpacing:'0.08em', textTransform:'uppercase', whiteSpace:'nowrap', pointerEvents:'auto' }}>
            <span style={{ width:6, height:6, borderRadius:'50%', background:T.mint, flexShrink:0 }} />
            {APP_VERSION}
          </div>
          )}""",
"""          <div style={{ pointerEvents:'auto' }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:19, color:T.ink, letterSpacing:'-0.01em', lineHeight:1.05, whiteSpace:'nowrap' }}>👋 {greetHi}</div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkSoft, marginTop:2 }}>{greetSub}</div>
          </div>""")
# 4e) akciógombok: playful elrendezés kontúr nélkül, 3D offsetekkel
rep("""          {isPlayful ? (
          <div style={{ display:'flex', flexDirection:'column', gap:14, width:'100%' }}>
            <button onClick={onStartGame || (() => go('players'))} style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:12, border:`2.5px solid ${T.ink}`, background:T.mint, borderRadius:22, padding:'18px', cursor:'pointer', boxShadow:`0 6px 0 ${T.ink}`, transform:'rotate(-1deg)', WebkitTapHighlightColor:'transparent' }}>
              <BohIcon name="play" size={26} />
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:'#fff' }}>{t('play')}</span>
            </button>
            <div style={{ display:'flex', gap:12 }}>
              <button onClick={() => go('observer')} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:5, border:`2.5px solid ${T.ink}`, background:T.surface, borderRadius:18, padding:'14px 8px', cursor:'pointer', boxShadow:`0 5px 0 ${T.coral}`, transform:'rotate(1.2deg)', textAlign:'center', WebkitTapHighlightColor:'transparent' }}>
                <BohIcon name="enter" size={20} />
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.coral }}>{t('join')}</span>
                <span style={{ fontFamily:T.font, fontWeight:700, fontSize:9.5, color:T.inkSoft }}>{t('enterCode')}</span>
              </button>
              <button onClick={onQuickGame} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:5, border:`2.5px solid ${T.ink}`, background:T.surface, borderRadius:18, padding:'14px 8px', cursor:'pointer', boxShadow:`0 5px 0 ${T.yellow || T.mint}`, transform:'rotate(-1.2deg)', textAlign:'center', WebkitTapHighlightColor:'transparent' }}>
                <BohIcon name="bolt" size={20} />
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.mint }}>Quick Game</span>
                <span style={{ fontFamily:T.font, fontWeight:700, fontSize:9.5, color:T.inkSoft }}>{t('quickGameSub')}</span>
              </button>
            </div>
          </div>
          ) : (
          <div style={{ display:'flex', gap:12, width:'100%' }}>
            <button onClick={onStartGame || (() => go('players'))} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:14, padding:'24px 12px 20px', border:'none', background:T.mint, borderRadius:20, cursor:'pointer', boxShadow:`0 6px 24px ${T.mint}55` }}>
              <div style={{ width:64, height:64, borderRadius:'50%', background:'rgba(255,255,255,0.25)', display:'grid', placeItems:'center' }}>
                <BohIcon name="play" size={32} />
              </div>
              <div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:'#fff', letterSpacing:'-0.01em' }}>{t('play')}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.75)', marginTop:3 }}>{t('newRound')}</div>
              </div>
            </button>
            <div style={{ flex:1, display:'flex', flexDirection:'column', gap:12, alignSelf:'stretch' }}>
              <button onClick={() => go('observer')} style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', gap:10, padding:'0 12px', border:'none', background:T.surface, borderRadius:20, cursor:'pointer', boxShadow:T.shadow }}>
                <div style={{ width:36, height:36, borderRadius:'50%', background:`${T.coral}18`, display:'grid', placeItems:'center', flexShrink:0 }}>
                  <BohIcon name="enter" size={19} />
                </div>
                <div style={{ textAlign:'left' }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.coral, letterSpacing:'-0.01em' }}>{t('join')}</div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>{t('enterCode')}</div>
                </div>
              </button>
              <button onClick={onQuickGame} style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', gap:10, padding:'0 12px', border:'none', background:T.surface, borderRadius:20, cursor:'pointer', boxShadow:T.shadow }}>
                <div style={{ width:36, height:36, borderRadius:'50%', background:T.mintSoft, display:'grid', placeItems:'center', flexShrink:0 }}>
                  <BohIcon name="bolt" size={17} />
                </div>
                <div style={{ textAlign:'left' }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.mint, letterSpacing:'-0.01em' }}>Quick Game</div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>{t('quickGameSub')}</div>
                </div>
              </button>
            </div>

          </div>
          )}""",
"""          <div style={{ display:'flex', flexDirection:'column', gap:14, width:'100%' }}>
            <button onClick={onStartGame || (() => go('players'))} style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:12, border:'none', background:T.mint, borderRadius:22, padding:'18px', cursor:'pointer', boxShadow:`0 4px 0 ${T.mintDeep || T.mint}88, 0 10px 26px ${T.mint}55`, transform:'rotate(-0.7deg)', WebkitTapHighlightColor:'transparent' }}>
              <BohIcon name="play" size={26} />
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:'#fff' }}>{t('play')}</span>
            </button>
            <div style={{ display:'flex', gap:12 }}>
              <button onClick={() => go('observer')} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:5, border:'none', background:T.surface, borderRadius:18, padding:'14px 8px', cursor:'pointer', boxShadow:`0 3px 0 ${T.coral}66, 0 8px 20px ${T.ink}12`, transform:'rotate(0.9deg)', textAlign:'center', WebkitTapHighlightColor:'transparent' }}>
                <BohIcon name="enter" size={20} />
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.coral }}>{t('join')}</span>
                <span style={{ fontFamily:T.font, fontWeight:700, fontSize:9.5, color:T.inkSoft }}>{t('enterCode')}</span>
              </button>
              <button onClick={onQuickGame} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:5, border:'none', background:T.surface, borderRadius:18, padding:'14px 8px', cursor:'pointer', boxShadow:`0 3px 0 ${T.yellow || T.mint}88, 0 8px 20px ${T.ink}12`, transform:'rotate(-0.9deg)', textAlign:'center', WebkitTapHighlightColor:'transparent' }}>
                <BohIcon name="bolt" size={20} />
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.mint }}>Quick Game</span>
                <span style={{ fontFamily:T.font, fontWeight:700, fontSize:9.5, color:T.inkSoft }}>{t('quickGameSub')}</span>
              </button>
            </div>
          </div>""")
# 4f) dokk kártyák egységesen
rep("border: isPlayful ? `2.5px solid ${T.ink}` : 'none', boxShadow: isPlayful ? `0 4px 0 ${T.ink}` : T.shadow, WebkitTapHighlightColor:'transparent' }}>\n              <img src=\"assets/dnr_events_icon.png\"",
    "border:'none', boxShadow:T.shadow, WebkitTapHighlightColor:'transparent' }}>\n              <img src=\"assets/dnr_events_icon.png\"")
rep("border: isPlayful ? `2.5px solid ${T.ink}` : 'none', boxShadow: isPlayful ? `0 4px 0 ${T.ink}` : T.shadow, WebkitTapHighlightColor:'transparent' }}>\n              <img src=\"assets/dnr_box_icon.png\"",
    "border:'none', boxShadow:T.shadow, WebkitTapHighlightColor:'transparent' }}>\n              <img src=\"assets/dnr_box_icon.png\"")

# ── 5) PlayerCard: pici döntés + 3D + korall × ──
rep("""function PlayerCard({ p, onEdit, onRemove, index, badge, playful }) {
  const tilt = playful ? [-1.5,1.2,-1,1.4,-1.2,1.5][(index||0)%6] : 0;
  return (
    <div onClick={onEdit} style={{
      position:'relative', background:T.surface, borderRadius:16,
      padding:'10px 8px 10px',
      boxShadow: playful ? `0 5px 0 ${T.ink}` : T.shadow,
      border: playful ? `2.5px solid ${T.ink}` : 'none',
      transform: playful ? `rotate(${tilt}deg)` : 'none',""",
"""function PlayerCard({ p, onEdit, onRemove, index, badge, playful }) {
  const tilt = [-0.8, 0.8, -0.6, 0.9, -0.9, 0.7][(index||0)%6];
  return (
    <div onClick={onEdit} style={{
      position:'relative', background:T.surface, borderRadius:16,
      padding:'10px 8px 10px',
      boxShadow: T.shadow,
      border: 'none',
      transform: `rotate(${tilt}deg)`,""")
rep("""      <button onClick={e => { e.stopPropagation(); onRemove(); }} style={{
        position:'absolute', top:-5, right:-5, width:28, height:28,
        borderRadius:'50%', background:T.surface, color:T.inkSoft,
        border:'1.5px solid rgba(20,30,50,0.12)',
        boxShadow:'0 1px 4px rgba(0,0,0,0.15)',
        cursor:'pointer', display:'grid', placeItems:'center', padding:0,
      }}>{Icon.close(T.inkSoft)}</button>""",
"""      <button onClick={e => { e.stopPropagation(); onRemove(); }} style={{
        position:'absolute', top:-7, right:-7, width:28, height:28,
        borderRadius:'50%', background:'transparent', border:'none',
        cursor:'pointer', display:'grid', placeItems:'center', padding:0,
      }}><BohIcon name="cross" size={20} /></button>""")
rep("      <div style={{ width:56, height:56, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0, border: playful ? `2.5px solid ${T.ink}` : 'none', boxSizing:'border-box' }}>",
    "      <div style={{ width:56, height:56, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0, border:'none', boxSizing:'border-box' }}>")

# ── 6) NetflixTile (játék kártya): méret marad, 3D árnyék, egyenes rács ──
rep("""        border: selected ? `2.5px solid ${T.mint}` : (isPlayful ? `2.5px solid ${T.ink}` : `2px solid ${T.inkMute}18`),
        boxShadow: isPlayful ? (selected ? `0 4px 0 ${T.mint}` : `0 4px 0 ${T.ink}`) : (selected ? `0 6px 22px ${T.mint}44` : T.shadow),""",
"""        border: selected ? `2.5px solid ${T.mint}` : `2px solid ${T.inkMute}18`,
        boxShadow: selected ? `0 4px 0 ${T.mint}66, 0 8px 20px ${T.mint}33` : T.shadow,""")
rep("        transform: isPlayful && !bouncing ? `rotate(${tilt}deg)` : 'none',\n", "")

# ── 7) Chip: kontúr ki, 3D árnyék be ──
rep("""      minHeight:44, padding:'0 6px', background:bg, color:fg, border: isPlayful ? `2px solid ${T.ink}` : 'none',
      borderRadius:14, boxShadow: isPlayful ? `0 3px 0 ${T.ink}` : (tone==='purple' ? '0 4px 14px rgba(124,58,237,0.3)' : isFilter && active ? `0 4px 14px ${T.mint}55` : 'none'),""",
"""      minHeight:44, padding:'0 6px', background:bg, color:fg, border:'none',
      borderRadius:14, boxShadow: tone==='purple' ? '0 3px 0 rgba(124,92,196,0.4), 0 6px 16px rgba(124,58,237,0.25)' : isFilter && active ? `0 3px 0 ${T.mint}66, 0 6px 16px ${T.mint}40` : T.shadow,""")

# ── 8) Verziobump ──
rep("const APP_VERSION = 'v9.957';", "const APP_VERSION = 'v9.958';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — one design applied')
