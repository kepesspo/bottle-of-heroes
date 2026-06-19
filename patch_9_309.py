#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Animated empty state keyframe
old_kf = "    @keyframes nextBounce  {"
new_kf = """    @keyframes floatBob   { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
    @keyframes waveHand   { 0%,100%{transform:rotate(0deg)} 20%{transform:rotate(-20deg)} 40%{transform:rotate(20deg)} 60%{transform:rotate(-15deg)} 80%{transform:rotate(15deg)} }
    @keyframes tooltipIn  { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
    @keyframes nextBounce  {"""
assert old_kf in html, "FAIL: keyframes anchor"
html = html.replace(old_kf, new_kf, 1)

# ── 2. Animated empty state — players.length===0 esetén az add gomb helyett
old_grid = """        <div className="grid-players">
          {players.map((p, i) =>
            <PlayerCard key={p.id} p={p} index={i} onEdit={() => setEditing(p.id)} onRemove={() => removePlayer(p.id)} badge={getBadge(p)} />
          )}
          <button onClick={addPlayer} style={{
            aspectRatio:'1/1.18', minHeight:120,
            border:`2.5px dashed ${T.mint}`, borderRadius:16, background:T.surfaceMuted,
            display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center',
            gap:8, cursor:'pointer', color:T.mint, padding:6,
          }}>
            <div style={{ width:44, height:44, borderRadius:999, border:`2.5px solid ${T.mint}`, display:'grid', placeItems:'center' }}>{Icon.plus(T.mint)}</div>
            <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.mint, textAlign:'center' }}>{players.length+1}{t('addPlayer')}</div>
          </button>
        </div>"""

new_grid = """        {players.length === 0 ? (
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:'32px 16px 16px', gap:16 }} onClick={addPlayer}>
            <div style={{ position:'relative', width:120, height:120 }}>
              {/* Bouncing bottle */}
              <div style={{ animation:'floatBob 2.2s ease-in-out infinite', transformOrigin:'bottom center' }}>
                <svg width="120" height="120" viewBox="0 0 120 120">
                  <ellipse cx="60" cy="108" rx="28" ry="7" fill={T.mintSoft} opacity="0.6" />
                  <rect x="48" y="30" width="24" height="62" rx="12" fill={T.mint} />
                  <rect x="51" y="16" width="18" height="18" rx="5" fill={T.mintDeep} />
                  <rect x="53" y="12" width="14" height="8" rx="3" fill={T.mintDeep} />
                  <ellipse cx="60" cy="30" rx="12" ry="4" fill={T.mintDeep} />
                  <ellipse cx="54" cy="56" rx="5" ry="8" fill="rgba(255,255,255,0.18)" />
                </svg>
              </div>
              {/* Waving hand */}
              <div style={{ position:'absolute', right:4, top:18, fontSize:32, animation:'waveHand 1.8s ease-in-out infinite', transformOrigin:'bottom center' }}>👋</div>
            </div>
            <div style={{ textAlign:'center' }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, marginBottom:4 }}>Nincs még játékos!</div>
              <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft }}>Koppints ide és add hozzá az első játékost</div>
            </div>
            <div style={{ display:'flex', alignItems:'center', gap:8, background:T.mint, borderRadius:999, padding:'12px 24px', boxShadow:`0 4px 16px ${T.mint}55` }}>
              {Icon.plus('#fff')}
              <span style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:'#fff' }}>Játékos hozzáadása</span>
            </div>
          </div>
        ) : (
        <div className="grid-players">
          {players.map((p, i) =>
            <PlayerCard key={p.id} p={p} index={i} onEdit={() => setEditing(p.id)} onRemove={() => removePlayer(p.id)} badge={getBadge(p)} />
          )}
          <button onClick={addPlayer} style={{
            aspectRatio:'1/1.18', minHeight:120,
            border:`2.5px dashed ${T.mint}`, borderRadius:16, background:T.surfaceMuted,
            display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center',
            gap:8, cursor:'pointer', color:T.mint, padding:6,
          }}>
            <div style={{ width:44, height:44, borderRadius:999, border:`2.5px solid ${T.mint}`, display:'grid', placeItems:'center' }}>{Icon.plus(T.mint)}</div>
            <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.mint, textAlign:'center' }}>{players.length+1}{t('addPlayer')}</div>
          </button>
        </div>
        )}"""

assert old_grid in html, "FAIL: grid-players empty state"
html = html.replace(old_grid, new_grid, 1)

# ── 3. Tooltip — MENÜ gomb mellé, első megnyitáskor "← húzd le a bezáráshoz"
# Tooltip state a PlayScreen-ben: localStorage alapú, egyszer mutatja
old_showmenu_state = "  const [showMenu, setShowMenu] = useState(false);"
new_showmenu_state = """  const [showMenu, setShowMenu] = useState(false);
  const [showSwipeHint, setShowSwipeHint] = React.useState(() => {
    try { return !localStorage.getItem('boh_swipe_hint_seen'); } catch(e) { return true; }
  });"""
assert old_showmenu_state in html, "FAIL: showMenu state"
html = html.replace(old_showmenu_state, new_showmenu_state, 1)

# Tooltip megjelenítése SheetOverlay-en belül, a handle bar fölött
old_sheet_open = "          <SheetOverlay onClose={() => setShowMenu(false)}>"
new_sheet_open = """          <SheetOverlay onClose={() => setShowMenu(false)}>
            {showSwipeHint && (() => {
              setTimeout(() => {
                try { localStorage.setItem('boh_swipe_hint_seen','1'); } catch(e) {}
                setShowSwipeHint(false);
              }, 3000);
              return (
                <div style={{ display:'flex', justifyContent:'center', padding:'6px 0 2px', animation:'tooltipIn .4s ease-out' }}>
                  <div style={{ background:T.inkMute, borderRadius:999, padding:'5px 14px', display:'flex', alignItems:'center', gap:6 }}>
                    <span style={{ fontSize:13 }}>👇</span>
                    <span style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:'#fff' }}>Húzd le a bezáráshoz</span>
                  </div>
                </div>
              );
            })()}"""
assert old_sheet_open in html, "FAIL: SheetOverlay open"
html = html.replace(old_sheet_open, new_sheet_open, 1)

html = html.replace("const APP_VERSION = 'v9.308';", "const APP_VERSION = 'v9.309';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.309 — Animated empty state (játékos lista), Tooltip (MENÜ első megnyitáskor)")
