#!/usr/bin/env python3
"""v8.49: Kedvencek szekció a Games képernyőn (Busz, Beer Pong, Imposztor)"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. A játékok grid elé szúrjuk be a Kedvencek szekciót ────────────────────
OLD_GRID = """      <div style={{ flex:1, minHeight:0, overflowY:'auto', WebkitOverflowScrolling:'touch' }}>
        <div className="screen-wide screen-pad" style={{ paddingTop:14, paddingBottom:140 }}>
        <div className="grid-games">
          {visibleGames.map(g => {
            const isSelected = selectedGames.includes(g.id);
            const locked = isLocked(g.id);
            const dim = locked || g.comingSoon || (anySelected && !isSelected);
            return (
              <GameTile key={g.id} g={g} selected={isSelected} dim={dim} locked={locked || !!g.comingSoon}
                onClick={() => { if (!g.comingSoon) toggle(g.id); }} onInfo={() => setInfo(g.id)}
                onLongPress={g.id==='busz' ? ()=>{ if(!selectedGames.includes('busz')) toggle('busz'); setBuszSheet(true); } : g.id==='beerpong' ? ()=>{ if(!selectedGames.includes('beerpong')) toggle('beerpong'); setBeerpongSheet(true); } : g.id==='kisebb' ? ()=>{ if(!selectedGames.includes('kisebb')) toggle('kisebb'); setKisebbSheet(true); } : g.id==='collect' ? ()=>{ if(!selectedGames.includes('collect')) toggle('collect'); setCollectSheet(true); } : g.id==='ovfj' ? ()=>{ if(!selectedGames.includes('ovfj')) toggle('ovfj'); setOvfjSheet(true); } : undefined} />
            );
          })}
        </div>
        </div>
      </div>"""

NEW_GRID = """      <div style={{ flex:1, minHeight:0, overflowY:'auto', WebkitOverflowScrolling:'touch' }}>
        <div className="screen-wide screen-pad" style={{ paddingTop:14, paddingBottom:140 }}>

        {/* ── Kedvencek szekció ── */}
        {(() => {
          const FAVS = ['beerpong','busz','imposztor'];
          const favGames = FAVS.map(id => GAMES.find(g => g.id === id)).filter(Boolean);
          return (
            <div style={{ marginBottom:18 }}>
              <div style={{ display:'flex', alignItems:'center', gap:6, marginBottom:10 }}>
                <span style={{ fontSize:14 }}>⭐</span>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.12em' }}>Kedvencek</span>
              </div>
              <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
                {favGames.map(g => {
                  const isSelected = selectedGames.includes(g.id);
                  const locked = isLocked(g.id);
                  const dim = locked || (anySelected && !isSelected);
                  const longPress = g.id==='busz' ? ()=>{ if(!selectedGames.includes('busz')) toggle('busz'); setBuszSheet(true); }
                    : g.id==='beerpong' ? ()=>{ if(!selectedGames.includes('beerpong')) toggle('beerpong'); setBeerpongSheet(true); }
                    : undefined;
                  return (
                    <FavTile key={g.id} g={g} selected={isSelected} dim={dim} locked={locked}
                      onClick={() => toggle(g.id)} onInfo={() => setInfo(g.id)} onLongPress={longPress} />
                  );
                })}
              </div>
            </div>
          );
        })()}

        {/* ── Összes játék ── */}
        <div style={{ display:'flex', alignItems:'center', gap:6, marginBottom:10 }}>
          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.12em' }}>Összes játék</span>
        </div>
        <div className="grid-games">
          {visibleGames.map(g => {
            const isSelected = selectedGames.includes(g.id);
            const locked = isLocked(g.id);
            const dim = locked || g.comingSoon || (anySelected && !isSelected);
            return (
              <GameTile key={g.id} g={g} selected={isSelected} dim={dim} locked={locked || !!g.comingSoon}
                onClick={() => { if (!g.comingSoon) toggle(g.id); }} onInfo={() => setInfo(g.id)}
                onLongPress={g.id==='busz' ? ()=>{ if(!selectedGames.includes('busz')) toggle('busz'); setBuszSheet(true); } : g.id==='beerpong' ? ()=>{ if(!selectedGames.includes('beerpong')) toggle('beerpong'); setBeerpongSheet(true); } : g.id==='kisebb' ? ()=>{ if(!selectedGames.includes('kisebb')) toggle('kisebb'); setKisebbSheet(true); } : g.id==='collect' ? ()=>{ if(!selectedGames.includes('collect')) toggle('collect'); setCollectSheet(true); } : g.id==='ovfj' ? ()=>{ if(!selectedGames.includes('ovfj')) toggle('ovfj'); setOvfjSheet(true); } : undefined} />
            );
          })}
        </div>
        </div>
      </div>"""

assert OLD_GRID in content, "grid not found"
content = content.replace(OLD_GRID, NEW_GRID, 1)
print("✓ Kedvencek szekció hozzáadva")

# ── 2. FavTile komponens — vízszintes, banner-szerű kártya ───────────────────
OLD_GAMETILE = """function GameTile({ g, selected, dim, locked, onClick, onInfo, onLongPress }) {"""

NEW_FAVTILE = """function FavTile({ g, selected, dim, locked, onClick, onInfo, onLongPress }) {
  const diff = DIFFICULTY_META[g.difficulty];
  const pressRef = React.useRef(null);
  const startPress = () => { if (onLongPress) pressRef.current = setTimeout(onLongPress, 500); };
  const cancelPress = () => clearTimeout(pressRef.current);
  return (
    <div
      onMouseDown={startPress} onMouseUp={cancelPress} onMouseLeave={cancelPress}
      onTouchStart={startPress} onTouchEnd={cancelPress} onTouchCancel={cancelPress}
      onClick={onClick}
      style={{
        display:'flex', alignItems:'center', gap:14,
        background: selected ? T.mintSoft : T.surface,
        borderRadius:18, padding:'12px 14px',
        border: selected ? `2px solid ${T.mint}` : '2px solid transparent',
        boxShadow: selected ? `0 4px 16px ${T.mint}33` : T.shadow,
        cursor: locked ? 'default' : 'pointer',
        opacity: dim ? 0.45 : 1,
        transition:'all .15s',
        position:'relative', overflow:'hidden',
      }}>
      {/* Color accent bar */}
      <div style={{ position:'absolute', left:0, top:0, bottom:0, width:4, borderRadius:'18px 0 0 18px', background: selected ? T.mint : g.color || T.surfaceMuted }} />
      {/* Icon */}
      <div style={{ width:48, height:48, borderRadius:14, background: g.color ? g.color+'22' : T.surfaceMuted, display:'grid', placeItems:'center', flexShrink:0 }}>
        {g.img ? <img src={g.img} style={{ width:32, height:32, objectFit:'contain' }} /> : <span style={{ fontSize:24 }}>{g.emoji}</span>}
      </div>
      {/* Text */}
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color: selected ? T.mintDeep : T.ink, lineHeight:1.2 }}>{g.name}</div>
        <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2 }}>{g.desc?.slice(0,48)}…</div>
      </div>
      {/* Badges */}
      <div style={{ display:'flex', flexDirection:'column', alignItems:'flex-end', gap:4, flexShrink:0 }}>
        {selected && <div style={{ background:T.mint, borderRadius:999, width:22, height:22, display:'grid', placeItems:'center' }}><svg width="12" height="12" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/></svg></div>}
        {locked && !selected && <div style={{ fontSize:14 }}>🔒</div>}
        <button onClick={e => { e.stopPropagation(); onInfo && onInfo(); }} style={{ width:28, height:28, borderRadius:9, background:'rgba(26,42,74,0.07)', border:'none', cursor:'pointer', display:'grid', placeItems:'center', fontSize:14, color:T.inkSoft }}>ℹ</button>
      </div>
      {/* Long-press hint for busz/beerpong */}
      {onLongPress && <div style={{ position:'absolute', bottom:4, right:42, fontFamily:T.font, fontSize:9, color:T.inkMute, letterSpacing:'0.04em' }}>TARTSD A BEÁLLÍTÁSHOZ</div>}
    </div>
  );
}

function GameTile({ g, selected, dim, locked, onClick, onInfo, onLongPress }) {"""

assert OLD_GAMETILE in content, "GameTile not found"
content = content.replace(OLD_GAMETILE, NEW_FAVTILE, 1)
print("✓ FavTile komponens hozzáadva")

# ── 3. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.48';"
NEW_VER = "const APP_VERSION = 'v8.49';"
assert OLD_VER in content, "version not found"
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.49 saved")
