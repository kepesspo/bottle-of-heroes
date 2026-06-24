#!/usr/bin/env python3
"""
v9.585:
1. NetflixTile — logo/icon only (no banner image), consistent look
2. GamesScreen — view toggle (grid vs netflix), persisted in localStorage
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)

# ── 1. Version bump ──────────────────────────────────────────────────────────
assert html.count('v9.584') >= 1
html = html.replace('v9.584', 'v9.585', 1)

# ── 2. NetflixTile: replace banner img block with logo-only ──────────────────
OLD_COVER = '''        {g.banner ? (
          <img src={g.banner} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        ) : (
          <div style={{ width: 52, height: 52, display: 'grid', placeItems: 'center' }}>
            <GameImg g={g} size="full" />
          </div>
        )}
        {/* subtle color overlay */}
        <div style={{ position: 'absolute', inset: 0, background: g.color ? `${g.color}10` : 'transparent' }} />'''

NEW_COVER = '''        <div style={{ width: 54, height: 54, display: 'grid', placeItems: 'center' }}>
          <GameImg g={g} size="full" />
        </div>
        {/* subtle color overlay */}
        <div style={{ position: 'absolute', inset: 0, background: g.color ? `${g.color}10` : 'transparent' }} />'''

assert html.count(OLD_COVER) == 1, f"cover block not found: {html.count(OLD_COVER)}"
html = html.replace(OLD_COVER, NEW_COVER, 1)

# ── 3. Add viewMode state to GamesScreen ────────────────────────────────────
OLD_STATE = "  const [collapsedSections, setCollapsedSections] = useState({});"
NEW_STATE = """  const [collapsedSections, setCollapsedSections] = useState({});
  const [viewMode, setViewMode] = useState(() => localStorage.getItem('boh_games_view') || 'netflix');
  const toggleViewMode = () => setViewMode(m => {
    const next = m === 'netflix' ? 'grid' : 'netflix';
    localStorage.setItem('boh_games_view', next);
    return next;
  });"""
assert html.count(OLD_STATE) == 1
html = html.replace(OLD_STATE, NEW_STATE, 1)

# ── 4. Add view toggle button to AppBar right slot ───────────────────────────
OLD_APPBAR = """      <AppBar title={t('games')} onBack={() => go('players')}
        right={
          <div style={{ display:'flex', gap:6, padding:4, background:T.mintSoft, borderRadius:999 }}>
            <div style={{ width:34, height:34, display:'grid', placeItems:'center', color:T.mintDeep }}>{Icon.users(T.mintDeep)}</div>
            <div style={{ width:34, height:34, borderRadius:999, background:T.mint, display:'grid', placeItems:'center' }}>{Icon.controller('#fff')}</div>
          </div>
        }
      />"""

NEW_APPBAR = """      <AppBar title={t('games')} onBack={() => go('players')}
        right={
          <div style={{ display:'flex', gap:6, alignItems:'center' }}>
            {/* View mode toggle */}
            <button onClick={toggleViewMode} style={{
              width:36, height:36, borderRadius:10, border:'none', cursor:'pointer',
              background: T.inkMute+'18', display:'grid', placeItems:'center',
              color: T.inkSoft, transition:'all .15s',
            }} title={viewMode === 'netflix' ? 'Rácsos nézet' : 'Netflix nézet'}>
              {viewMode === 'netflix' ? (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={T.inkSoft} strokeWidth="2" strokeLinecap="round">
                  <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
                  <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
                </svg>
              ) : (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={T.inkSoft} strokeWidth="2" strokeLinecap="round">
                  <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
                  <circle cx="3" cy="6" r="1" fill={T.inkSoft}/><circle cx="3" cy="12" r="1" fill={T.inkSoft}/><circle cx="3" cy="18" r="1" fill={T.inkSoft}/>
                </svg>
              )}
            </button>
            <div style={{ display:'flex', gap:6, padding:4, background:T.mintSoft, borderRadius:999 }}>
              <div style={{ width:34, height:34, display:'grid', placeItems:'center', color:T.mintDeep }}>{Icon.users(T.mintDeep)}</div>
              <div style={{ width:34, height:34, borderRadius:999, background:T.mint, display:'grid', placeItems:'center' }}>{Icon.controller('#fff')}</div>
            </div>
          </div>
        }
      />"""

assert html.count(OLD_APPBAR) == 1, f"appbar not found"
html = html.replace(OLD_APPBAR, NEW_APPBAR, 1)

# ── 5. Make category rendering conditional on viewMode ───────────────────────
OLD_NETFLIX_SECTION = '''              {/* Játékok — Netflix horizontal scroll */}
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

NEW_CONDITIONAL_SECTION = '''              {/* Játékok — viewMode alapján */}
              {!isCollapsed && viewMode === 'netflix' && (
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
              )}
              {!isCollapsed && viewMode === 'grid' && (
                <div className="grid-games" style={{ marginBottom: 4 }}>
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

assert html.count(OLD_NETFLIX_SECTION) == 1, f"netflix section not found"
html = html.replace(OLD_NETFLIX_SECTION, NEW_CONDITIONAL_SECTION, 1)

assert len(html) != original_len
print(f"Done. {len(html) - original_len:+d} chars")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written.")
