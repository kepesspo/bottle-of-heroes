# v10.477 — DNR Bingó: választható kártya-kinézet (admin): „Ikonos" (a mostani, alap) ·
# „Nagy szöveg" · „Kaparós". A két új: NINCS ikon, a szöveg a mezőhöz méretezve nagy, és a
# korty-szám REJTETT — csak kipipáláskor derül ki (az X helyén).
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.476';", "const APP_VERSION = 'v10.477';")

rep("""// v10.475: ki léphet be a Bingóba""",
"""// v10.477: a kártya kinézete — 'icon' (alap, hiányzó mező is) · 'text' · 'scratch'
const BINGO_STYLES = [
  { id:'icon',    label:'Ikonos' },
  { id:'text',    label:'Nagy szöveg' },
  { id:'scratch', label:'Kaparós' },
];
function bingoStyleOf(cfg) {
  const v = cfg && cfg.bingoCardStyle;
  return (v === 'text' || v === 'scratch') ? v : 'icon';
}
// Ikon nélküli mező betűmérete: a LEGHOSSZABB szó férjen ki egy sorba (a szótörés csúnya).
// A Nunito 800 átlagos betűszélessége ~0,56 em; a hasznos szélesség 5×5-ön ~58, 4×4-en ~78 px.
function bingoTextFont(t, s) {
  const w = Math.max(1, ...String(t || '').split(/\\s+/).map(x => x.length));
  const room = s === 4 ? 78 : 58, cap = s === 4 ? 17 : 13.5;
  return Math.max(7, Math.min(cap, Math.floor(room / (0.56 * w) * 10) / 10));
}
// Kaparós: a felfedett mező színe a TÉTET mondja (fix, nem témafüggő — mint a nehézség-színek)
const BINGO_K_TONES = { 1: '#2E9E76', 2: '#E8961E', 3: '#E0533F' };
// v10.475: ki léphet be a Bingóba""")

# ── admin ──
rep("""  const [whoMode, setWhoMode] = React.useState('both'); // v10.475: ki léphet be""",
    """  const [whoMode, setWhoMode] = React.useState('both'); // v10.475: ki léphet be
  const [cardStyle, setCardStyle] = React.useState('icon'); // v10.477: kártya-kinézet
  const [styleMsg, setStyleMsg] = React.useState('');""")
rep("""      setWhoMode(bingoWhoOf(c));""", """      setWhoMode(bingoWhoOf(c));
      setCardStyle(bingoStyleOf(c));""")
rep("""bingoRound: round, bingoWho: whoMode, tippTitle:""", """bingoRound: round, bingoWho: whoMode, bingoCardStyle: cardStyle, tippTitle:""")
rep("""          {/* v10.473: szettek — egy koppintás, és mindenki az új szett tiszta kártyáját kapja */}""",
"""          {/* v10.477: kártya-kinézet — AZONNAL ment (merge) */}
          <div data-bingo-stylebox style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
            {lbl('Kártya kinézete')}
            <div style={{ display:'flex', gap:6, background:T.bg, borderRadius:12, padding:4 }}>
              {BINGO_STYLES.map(m => {
                const on = m.id === cardStyle;
                return <button key={m.id} type="button" data-bingo-style={m.id} aria-pressed={on} onClick={() => {
                  if (on) return;
                  const prev = cardStyle; setCardStyle(m.id); setStyleMsg('mentés…');
                  if (typeof firebase === 'undefined') { setStyleMsg(''); return; }
                  firebase.firestore().collection('config').doc('bingoConfig').set({ bingoCardStyle: m.id }, { merge: true })
                    .then(() => setStyleMsg('mentve'))
                    .catch(e => { setCardStyle(prev); setStyleMsg('nem sikerült menteni' + (e && e.code ? ` (${e.code})` : '')); });
                }} style={{ flex:1, minWidth:0, height:38, borderRadius:9, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:12.5, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis',
                  background: on ? T.surface : 'transparent', color: on ? T.ink : T.inkSoft, boxShadow: on ? T.shadow : 'none' }}>{m.label}</button>;
              })}
            </div>
            <div style={{ fontFamily:T.font, fontSize:11.5, color:T.inkSoft, marginTop:7, lineHeight:1.4 }}>
              {cardStyle === 'text' ? 'Ikon nélkül, nagy betűvel. A korty-szám rejtett — kipipáláskor derül ki.'
                : cardStyle === 'scratch' ? 'Ikon nélkül, nagy betűvel. Kipipáláskor a mező a tét színére vált (zöld 1 · narancs 2 · piros 3), és kiírja a kortyot.'
                : 'Ikon + felirat, a korty a sarokban mindig látszik.'}{styleMsg ? ` · ${styleMsg}` : ''}
            </div>
          </div>
          {/* v10.473: szettek — egy koppintás, és mindenki az új szett tiszta kártyáját kapja */}""")

# ── képernyő ──
rep("""  const whoMode = bingoWhoOf(cfg);""", """  const whoMode = bingoWhoOf(cfg);
  const cardStyle = bingoStyleOf(cfg);   // v10.477""")

old_cell = """                  <button key={c} data-bingo={c} onClick={() => toggle(c)} style={{ position:'relative', aspectRatio:'1', border:'none', borderRadius:12, cursor: free ? 'default' : 'pointer', background: free ? (T.yellow || '#F4C95A') : on ? T.mint : T.surface, boxShadow: on ? 'none' : T.shadowPill, padding:3, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:2, overflow:'hidden', WebkitTapHighlightColor:'transparent' }}>
                    <span style={{ fontSize: grid.s === 4 ? 20 : 15, lineHeight:1, opacity: on && !free ? 0.3 : 1 }}>{free ? bingoCenter.e : item.e}</span>"""
new_cell = """                // v10.477: ikon nélküli kinézetek — a szám a kipipálásig rejtett
                  if (cardStyle !== 'icon') {
                    const k = free ? 0 : bingoK(item), txt = free ? bingoCenter.t : item.t;
                    const bg = free ? (T.yellow || '#F4C95A') : !on ? T.surface : cardStyle === 'scratch' ? BINGO_K_TONES[k] : T.mint;
                    return (
                      <button key={c} data-bingo={c} data-bingo-cellstyle={cardStyle} onClick={() => toggle(c)} style={{ position:'relative', aspectRatio:'1', border:'none', borderRadius:12, cursor: free ? 'default' : 'pointer', background: bg, boxShadow: on && !free ? 'none' : T.shadowPill, padding:3, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', overflow:'hidden', WebkitTapHighlightColor:'transparent', transition:'background .25s' }}>
                        {(!on || free) ? (
                          <span style={{ fontFamily:T.font, fontWeight:900, fontSize: bingoTextFont(txt, grid.s), lineHeight:1.08, textAlign:'center', color: free ? '#1A2A4A' : T.ink, wordBreak:'break-word' }}>{txt}</span>
                        ) : (
                          <React.Fragment>
                            <span data-bingo-reveal={k} style={{ fontFamily:T.font, fontWeight:900, fontSize: grid.s === 4 ? 40 : 30, lineHeight:0.95, color:'#fff', textShadow:'0 2px 6px rgba(0,0,0,0.18)', animation:'bingoPop .35s cubic-bezier(.2,1.6,.4,1)' }}>{cardStyle === 'scratch' ? k : '+' + k}</span>
                            <span style={{ fontFamily:T.font, fontWeight:900, fontSize: grid.s === 4 ? 10.5 : 8, lineHeight:1.1, color:'rgba(255,255,255,0.92)', textTransform:'uppercase', letterSpacing:'0.04em', marginTop:2 }}>{cardStyle === 'scratch' ? 'korty' : '🍺'}</span>
                            <span style={{ position:'absolute', left:3, right:3, bottom:3, fontFamily:T.font, fontWeight:800, fontSize: grid.s === 4 ? 8.5 : 6.6, lineHeight:1.05, color:'rgba(255,255,255,0.72)', textAlign:'center', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{txt}</span>
                          </React.Fragment>
                        )}
                      </button>
                    );
                  }
                  return (
                  <button key={c} data-bingo={c} onClick={() => toggle(c)} style={{ position:'relative', aspectRatio:'1', border:'none', borderRadius:12, cursor: free ? 'default' : 'pointer', background: free ? (T.yellow || '#F4C95A') : on ? T.mint : T.surface, boxShadow: on ? 'none' : T.shadowPill, padding:3, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:2, overflow:'hidden', WebkitTapHighlightColor:'transparent' }}>
                    <span style={{ fontSize: grid.s === 4 ? 20 : 15, lineHeight:1, opacity: on && !free ? 0.3 : 1 }}>{free ? bingoCenter.e : item.e}</span>"""
rep(old_cell, new_cell)
# a régi ág `return (` nyitását a fenti `return (` váltja ki — a régi nyitót ki kell venni
rep("""                const on = free || myMarks.has(c);
                return (
                // v10.477""", """                const on = free || myMarks.has(c);
                // v10.477""")
rep("""                    {on && !free && <span style={{ position:'absolute', inset:0, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:30, color:'#fff', textShadow:'0 2px 6px rgba(0,0,0,0.25)' }}>✕</span>}
                  </button>
                );""", """                    {on && !free && <span style={{ position:'absolute', inset:0, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:30, color:'#fff', textShadow:'0 2px 6px rgba(0,0,0,0.25)' }}>✕</span>}
                  </button>
                  );""")
rep("""Koppints a mezőre, ha megtörtént / elhangzott, és idd meg a sarkában álló kortyot (🍺1–3).""",
    """{cardStyle === 'icon' ? 'Koppints a mezőre, ha megtörtént / elhangzott, és idd meg a sarkában álló kortyot (🍺1–3).' : 'Koppints a mezőre, ha elhangzott — csak akkor derül ki, hány kortyot iszol (1–3).'}""")
i = s.index('@keyframes')
s = s[:i] + "@keyframes bingoPop { 0% { transform: scale(0.3); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }\n    " + s[i:]
open(P, 'w', encoding='utf-8').write(s)
print('OK')
