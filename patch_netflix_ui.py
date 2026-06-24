#!/usr/bin/env python3
"""
v9.584 — Visual overhaul:
D) Netflix-style horizontal scroll game cards (NetflixTile)
A+B) Theme picker: color swatch preview strips instead of emoji
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)

# ── 1. Version bump ──────────────────────────────────────────────────────────
assert html.count('v9.583') >= 1
html = html.replace('v9.583', 'v9.584', 1)

# ── 2. NetflixTile component — insert after GameTile ends ────────────────────
NETFLIX_TILE = '''
function NetflixTile({ g, selected, dim, locked, onClick, onInfo, onLongPress }) {
  const diff = DIFFICULTY_META[g.difficulty] || { tone: '#aaa' };
  const diffDots = g.difficulty === 'könnyű' ? 1 : g.difficulty === 'közepes' ? 2 : 3;
  const [bouncing, setBouncing] = React.useState(false);
  const prevSel = React.useRef(selected);
  React.useEffect(() => {
    if (selected && !prevSel.current) { setBouncing(true); setTimeout(() => setBouncing(false), 400); }
    prevSel.current = selected;
  }, [selected]);
  const pressRef = React.useRef(null);
  const startPress = () => { if (onLongPress) pressRef.current = setTimeout(onLongPress, 500); };
  const cancelPress = () => clearTimeout(pressRef.current);
  return (
    <div
      onClick={onClick}
      onTouchStart={startPress} onTouchEnd={cancelPress} onTouchCancel={cancelPress}
      onMouseDown={startPress} onMouseUp={cancelPress} onMouseLeave={cancelPress}
      style={{
        width: 132, flexShrink: 0,
        borderRadius: 18,
        background: T.surface,
        border: selected ? `2.5px solid ${T.mint}` : `2px solid ${T.inkMute}18`,
        boxShadow: selected ? `0 6px 22px ${T.mint}44` : T.shadow,
        cursor: locked ? 'not-allowed' : 'pointer',
        opacity: dim ? 0.42 : 1,
        transition: 'all .15s',
        overflow: 'hidden',
        position: 'relative',
        animation: bouncing ? 'bounceSelect 0.4s ease' : 'none',
        userSelect: 'none', WebkitUserSelect: 'none', WebkitTouchCallout: 'none',
      }}
    >
      {/* Cover area */}
      <div style={{
        height: 96,
        background: g.color ? `${g.color}28` : T.surfaceMuted,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        position: 'relative', overflow: 'hidden',
      }}>
        {g.banner ? (
          <img src={g.banner} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        ) : (
          <div style={{ width: 52, height: 52, display: 'grid', placeItems: 'center' }}>
            <GameImg g={g} size="full" />
          </div>
        )}
        {/* subtle color overlay */}
        <div style={{ position: 'absolute', inset: 0, background: g.color ? `${g.color}10` : 'transparent' }} />
        {/* Selected checkmark */}
        {selected && (
          <div style={{
            position: 'absolute', top: 7, right: 7,
            width: 22, height: 22, borderRadius: '50%',
            background: T.mint, display: 'grid', placeItems: 'center',
            boxShadow: `0 2px 8px ${T.mint}66`,
          }}>
            <svg width="11" height="11" viewBox="0 0 24 24">
              <path d="M5 13l4 4L19 7" stroke="#fff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        )}
        {/* Lock icon */}
        {locked && !selected && (
          <div style={{ position: 'absolute', top: 7, right: 7, fontSize: 14, lineHeight: 1 }}>🔒</div>
        )}
        {/* Info button */}
        <button onClick={e => { e.stopPropagation(); onInfo(); }} style={{
          position: 'absolute', top: 6, left: 6,
          width: 26, height: 26, borderRadius: '50%',
          background: 'rgba(255,255,255,0.82)', border: 'none', cursor: 'pointer',
          display: 'grid', placeItems: 'center', padding: 0,
          backdropFilter: 'blur(4px)',
          boxShadow: '0 1px 4px rgba(0,0,0,0.15)',
        }}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="9" stroke={T.inkSoft} strokeWidth="2"/>
            <path d="M12 11v6M12 8v.01" stroke={T.inkSoft} strokeWidth="2.5" strokeLinecap="round"/>
          </svg>
        </button>
        {/* Config pencil button */}
        {onLongPress && (
          <button onClick={e => { e.stopPropagation(); onLongPress(); }} style={{
            position: 'absolute', bottom: 6, right: 6,
            width: 26, height: 26, borderRadius: '50%',
            background: T.purple, border: 'none', cursor: 'pointer',
            display: 'grid', placeItems: 'center', padding: 0,
            boxShadow: '0 2px 8px rgba(124,58,237,0.4)',
          }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
              <path d="M4 20h4l10.5-10.5-4-4L4 16v4z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/>
              <path d="M14.5 5.5l4 4" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        )}
        {/* Coming Soon badge */}
        {g.comingSoon && (
          <div style={{
            position: 'absolute', bottom: 0, left: 0, right: 0,
            padding: '4px 8px', textAlign: 'center',
            background: 'rgba(14,14,24,0.75)', backdropFilter: 'blur(4px)',
            fontFamily: T.font, fontWeight: 900, fontSize: 8, color: '#A78BFA',
            letterSpacing: '0.14em',
          }}>COMING SOON</div>
        )}
        {/* DNR badge */}
        {!g.comingSoon && (g.id === 'busz' || g.dnr) && (
          <div style={{
            position: 'absolute', bottom: 0, left: 0, right: 0,
            padding: '4px 8px', textAlign: 'center',
            background: 'rgba(14,14,24,0.72)', backdropFilter: 'blur(4px)',
            fontFamily: T.font, fontWeight: 900, fontSize: 8, color: '#FFD23F',
            letterSpacing: '0.12em',
          }}>★ DNR</div>
        )}
      </div>
      {/* Info strip */}
      <div style={{ padding: '9px 10px 11px' }}>
        <div style={{
          fontFamily: T.font, fontWeight: 800, fontSize: 12.5, color: T.ink,
          lineHeight: 1.2, marginBottom: 6,
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
        }}>{tg(g, 'name')}</div>
        <div style={{ display: 'flex', gap: 3 }}>
          {[1,2,3].map(n => (
            <div key={n} style={{
              width: 6, height: 6, borderRadius: '50%',
              background: n <= diffDots ? diff.tone : `${diff.tone}28`,
            }} />
          ))}
        </div>
      </div>
    </div>
  );
}
'''

# Insert after GameTile function ends — look for the function that comes after
AFTER_GAMETILE = '''function FavTile({ g, selected, dim, locked, onClick, onInfo, onLongPress }) {'''
assert html.count(AFTER_GAMETILE) == 1
html = html.replace(AFTER_GAMETILE, NETFLIX_TILE + '\n' + AFTER_GAMETILE, 1)

# ── 3. Replace category grid with horizontal scroll of NetflixTile ────────────
OLD_GRID = '''              {/* Játékok grid */}
              {!isCollapsed && (
                <div className="grid-games">
                  {sectionGames.map(g => {
                    const isSelected = selectedGames.includes(g.id);
                    const locked = isLocked(g.id);
                    const dim = locked || g.comingSoon || (anySelected && !isSelected);
                    return (
                      <GameTile key={g.id} g={g} selected={isSelected} dim={dim} locked={locked || !!g.comingSoon}
                        onClick={() => { if (!g.comingSoon) toggle(g.id); }} onInfo={() => setInfo(g.id)}
                        onLongPress={g.id==='busz' ? ()=>{ if(!selectedGames.includes('busz')) toggle('busz'); setBuszSheet(true); } : g.id==='beerpong' ? ()=>{ if(!selectedGames.includes('beerpong')) toggle('beerpong'); setBeerpongSheet(true); } : g.id==='kisebb' ? ()=>{ if(!selectedGames.includes('kisebb')) toggle('kisebb'); setKisebbSheet(true); } : g.id==='collect' ? ()=>{ if(!selectedGames.includes('collect')) toggle('collect'); setCollectSheet(true); } : g.id==='ovfj' ? ()=>{ if(!selectedGames.includes('ovfj')) toggle('ovfj'); setOvfjSheet(true); } : g.id==='zene' ? ()=>{ if(!selectedGames.includes('zene')) toggle('zene'); setZeneSheet(true); } : undefined} />
                    );
                  })}
                </div>
              )}'''

NEW_GRID = '''              {/* Játékok — Netflix horizontal scroll */}
              {!isCollapsed && (
                <div style={{ position: 'relative' }}>
                  <div style={{
                    display: 'flex', gap: 10, overflowX: 'auto', WebkitOverflowScrolling: 'touch',
                    paddingBottom: 10, paddingTop: 4,
                    paddingLeft: 16, paddingRight: 32,
                    marginLeft: -16, marginRight: -16,
                    scrollbarWidth: 'none', msOverflowStyle: 'none',
                  }}>
                    {sectionGames.map(g => {
                      const isSelected = selectedGames.includes(g.id);
                      const locked = isLocked(g.id);
                      const dim = locked || g.comingSoon || (anySelected && !isSelected);
                      return (
                        <NetflixTile key={g.id} g={g} selected={isSelected} dim={dim} locked={locked || !!g.comingSoon}
                          onClick={() => { if (!g.comingSoon) toggle(g.id); }} onInfo={() => setInfo(g.id)}
                          onLongPress={g.id==='busz' ? ()=>{ if(!selectedGames.includes('busz')) toggle('busz'); setBuszSheet(true); } : g.id==='beerpong' ? ()=>{ if(!selectedGames.includes('beerpong')) toggle('beerpong'); setBeerpongSheet(true); } : g.id==='kisebb' ? ()=>{ if(!selectedGames.includes('kisebb')) toggle('kisebb'); setKisebbSheet(true); } : g.id==='collect' ? ()=>{ if(!selectedGames.includes('collect')) toggle('collect'); setCollectSheet(true); } : g.id==='ovfj' ? ()=>{ if(!selectedGames.includes('ovfj')) toggle('ovfj'); setOvfjSheet(true); } : g.id==='zene' ? ()=>{ if(!selectedGames.includes('zene')) toggle('zene'); setZeneSheet(true); } : undefined} />
                      );
                    })}
                  </div>
                  <div style={{ position: 'absolute', top: 0, right: -16, bottom: 10, width: 40,
                    background: `linear-gradient(to right, transparent, ${T.bg})`, pointerEvents: 'none' }} />
                </div>
              )}'''

assert html.count(OLD_GRID) == 1, f"grid section not found: {html.count(OLD_GRID)}"
html = html.replace(OLD_GRID, NEW_GRID, 1)

# ── 4. Theme picker: color swatch strips ─────────────────────────────────────
OLD_THEME_LIGHT = '''              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:8 }}>☀️ Világos témák</div>
              <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8, marginBottom:16 }}>
                {[
                  ['warm','☀️','Meleg'],['peach','🍑','Peach'],['lemon','🍋','Citrom'],['ice','🩵','Ice'],['jade','🪴','Jade'],
                ].map(([key, icon, label]) => (
                  <button key={key} onClick={() => { setTheme && setTheme(key); }} style={{ padding:'10px 4px', borderRadius:14, border: currentTheme===key ? `2px solid ${T.mint}` : `2px solid transparent`, background: currentTheme===key ? T.mintSoft : T.surfaceMuted, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
                    <span style={{ fontSize:20 }}>{icon}</span>
                    <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color: currentTheme===key ? T.mintDeep : T.inkSoft }}>{label}</span>
                  </button>
                ))}
              </div>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:8 }}>🌙 Sötét témák</div>
              <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:8, marginBottom:24 }}>
                {[
                  ['dark','🌙','Sötét'],['slate','🪨','Kő'],['midnight','🔮','Midnight'],
                ].map(([key, icon, label]) => (
                  <button key={key} onClick={() => { setTheme && setTheme(key); }} style={{ padding:'10px 4px', borderRadius:14, border: currentTheme===key ? `2px solid ${T.mint}` : `2px solid transparent`, background: currentTheme===key ? T.mintSoft : T.surfaceMuted, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
                    <span style={{ fontSize:20 }}>{icon}</span>
                    <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color: currentTheme===key ? T.mintDeep : T.inkSoft }}>{label}</span>
                  </button>
                ))}
              </div>'''

NEW_THEME_PICKER = '''              {/* Theme picker — color swatch strips */}
              {(() => {
                const THEME_DEFS = [
                  { key:'warm',     label:'Meleg',    bg:'#F4C57E', accent:'#4FC2A0', surface:'#FFFFFF' },
                  { key:'peach',    label:'Barack',   bg:'#FFE8D8', accent:'#E06030', surface:'#FFFFFF' },
                  { key:'lemon',    label:'Citrom',   bg:'#F8F8D8', accent:'#808010', surface:'#FFFFFF' },
                  { key:'ice',      label:'Ice',      bg:'#E8F4FF', accent:'#2070C0', surface:'#FFFFFF' },
                  { key:'jade',     label:'Jade',     bg:'#B8E8C8', accent:'#20A060', surface:'#FFFFFF' },
                  { key:'dark',     label:'Sötét',    bg:'#2C3554', accent:'#4FC2A0', surface:'#3D4870' },
                  { key:'slate',    label:'Kő',       bg:'#1E2A38', accent:'#40C8A0', surface:'#2E3E50' },
                  { key:'midnight', label:'Éjfél',    bg:'#28204A', accent:'#9070F8', surface:'#3C2E60' },
                ];
                const ThemeBtn = ({ def }) => {
                  const active = currentTheme === def.key;
                  return (
                    <button onClick={() => setTheme && setTheme(def.key)} style={{
                      padding: 0, borderRadius: 14, cursor: 'pointer', overflow: 'hidden',
                      border: active ? `2.5px solid ${T.mint}` : `2px solid ${T.inkMute}22`,
                      boxShadow: active ? `0 3px 12px ${T.mint}55` : T.shadow,
                      background: 'transparent', transition: 'all .15s',
                      display: 'flex', flexDirection: 'column',
                    }}>
                      {/* Color strip */}
                      <div style={{ height: 36, background: def.bg, position: 'relative', overflow: 'hidden' }}>
                        {/* mini surface card */}
                        <div style={{
                          position: 'absolute', bottom: 4, left: 6, right: 6, height: 14,
                          background: def.surface, borderRadius: 4, opacity: 0.9,
                        }} />
                        {/* accent dot */}
                        <div style={{
                          position: 'absolute', top: 5, right: 7,
                          width: 8, height: 8, borderRadius: '50%', background: def.accent,
                        }} />
                      </div>
                      {/* Label */}
                      <div style={{
                        padding: '5px 4px 6px', background: active ? T.mintSoft : T.surfaceMuted,
                        fontFamily: T.font, fontWeight: 700, fontSize: 11,
                        color: active ? T.mintDeep : T.inkSoft, textAlign: 'center',
                      }}>{def.label}</div>
                    </button>
                  );
                };
                const lightThemes = THEME_DEFS.filter(d => !['dark','slate','midnight'].includes(d.key));
                const darkThemes  = THEME_DEFS.filter(d =>  ['dark','slate','midnight'].includes(d.key));
                return (
                  <>
                    <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:8 }}>☀️ Világos témák</div>
                    <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8, marginBottom:16 }}>
                      {lightThemes.map(def => <ThemeBtn key={def.key} def={def} />)}
                    </div>
                    <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:8 }}>🌙 Sötét témák</div>
                    <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:8, marginBottom:24 }}>
                      {darkThemes.map(def => <ThemeBtn key={def.key} def={def} />)}
                    </div>
                  </>
                );
              })()}'''

assert html.count(OLD_THEME_LIGHT) == 1, f"theme picker not found: {html.count(OLD_THEME_LIGHT)}"
html = html.replace(OLD_THEME_LIGHT, NEW_THEME_PICKER, 1)

# ── 5. Hide scrollbar for Netflix scroll (CSS) ────────────────────────────────
OLD_CSS = '    .bottombar-shell { padding:14px 0 max(14px, env(safe-area-inset-bottom)); }'
NEW_CSS = '''    .bottombar-shell { padding:14px 0 max(14px, env(safe-area-inset-bottom)); }
    .netflix-scroll::-webkit-scrollbar { display:none; }'''
assert html.count(OLD_CSS) == 1, f"css anchor not found: {html.count(OLD_CSS)}"
html = html.replace(OLD_CSS, NEW_CSS, 1)

assert len(html) > original_len
print(f"Done. {len(html) - original_len:+d} chars")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written.")
