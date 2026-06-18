#!/usr/bin/env python3
"""patch_9_107.py — ZeneGame: move era/genre settings to long-tap card sheet"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.106';" in content
content = content.replace("const APP_VERSION = 'v9.106';", "const APP_VERSION = 'v9.107';")

# ── 1. Add ZeneConfigSheet before ZeneGame ───────────────────────
OLD_ZENE_FUNC_START = "function ZeneGame({ gameIdx, challenger, onAdvance, onResult }) {"

NEW_ZENE_CONFIG_SHEET = """function ZeneConfigSheet({ config, setConfig, onClose }) {
  const era   = config.era   || 'all';
  const genre = config.genre || 'all';
  const ERA_OPTIONS = [
    { v:'all',     label:'Minden korszak' },
    { v:'classic', label:'Klasszikusok (pre-2000)' },
    { v:'2000s',   label:'2000-es évek' },
    { v:'2010s',   label:'2010-es évek' },
    { v:'2020s',   label:'2020-as évek' },
  ];
  const GENRE_OPTIONS = [
    { v:'all',        label:'Minden stílus' },
    { v:'pop',        label:'Pop' },
    { v:'rnb',        label:'R&B / Hip-hop' },
    { v:'hiphop',     label:'Hip-hop' },
    { v:'rock',       label:'Rock' },
    { v:'electronic', label:'Electronic' },
    { v:'indie',      label:'Indie' },
  ];
  const chip = (active) => ({
    flex:1, padding:'10px 0', borderRadius:12, border:'none', cursor:'pointer',
    fontFamily:T.font, fontWeight:700, fontSize:13,
    background: active ? T.mint : T.surfaceMuted,
    color: active ? '#fff' : T.ink,
  });
  return (
    <SheetOverlay onClose={onClose}>
      <div style={{padding:'4px 20px 32px'}}>
        <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:18,color:T.ink,marginBottom:4,letterSpacing:T.letterDisplay}}>🎵 Zenefelismerés beállítások</div>
        <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,marginBottom:18}}>Szűrd a zenéket korszak és stílus szerint</div>

        <div style={{borderTop:`1px solid ${T.surfaceMuted}`,paddingTop:14,marginBottom:4}}>
          <div style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:14,color:T.ink,marginBottom:10}}>Korszak</div>
          <div style={{display:'flex',flexDirection:'column',gap:8}}>
            {ERA_OPTIONS.map(o => (
              <button key={o.v} onClick={()=>setConfig(c=>({...c,era:o.v}))} style={{
                width:'100%', padding:'11px 14px', borderRadius:12, border: era===o.v?`1.5px solid ${T.mint}`:'1.5px solid rgba(26,42,74,0.10)',
                background: era===o.v?T.mintSoft:'#fff', cursor:'pointer',
                fontFamily:T.font, fontWeight: era===o.v?700:500, fontSize:14,
                color: era===o.v?T.mintDeep:T.ink, textAlign:'left',
              }}>{o.label}</button>
            ))}
          </div>
        </div>

        <div style={{borderTop:`1px solid ${T.surfaceMuted}`,paddingTop:14,marginTop:14,marginBottom:4}}>
          <div style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:14,color:T.ink,marginBottom:10}}>Stílus</div>
          <div style={{display:'flex',flexDirection:'column',gap:8}}>
            {GENRE_OPTIONS.map(o => (
              <button key={o.v} onClick={()=>setConfig(c=>({...c,genre:o.v}))} style={{
                width:'100%', padding:'11px 14px', borderRadius:12, border: genre===o.v?`1.5px solid ${T.mint}`:'1.5px solid rgba(26,42,74,0.10)',
                background: genre===o.v?T.mintSoft:'#fff', cursor:'pointer',
                fontFamily:T.font, fontWeight: genre===o.v?700:500, fontSize:14,
                color: genre===o.v?T.mintDeep:T.ink, textAlign:'left',
              }}>{o.label}</button>
            ))}
          </div>
        </div>

        <PrimaryButton onClick={onClose} style={{marginTop:16}}>Kész</PrimaryButton>
      </div>
    </SheetOverlay>
  );
}

"""

assert OLD_ZENE_FUNC_START in content
content = content.replace(OLD_ZENE_FUNC_START, NEW_ZENE_CONFIG_SHEET + OLD_ZENE_FUNC_START, 1)

# ── 2. Update ZeneGame signature + remove filter UI ──────────────
OLD_ZENE_GAME = """function ZeneGame({ gameIdx, challenger, onAdvance, onResult }) {
  const [selectedEra, setSelectedEra] = React.useState(() => {
    try { return localStorage.getItem('zene_era') || 'all'; } catch(e) { return 'all'; }
  });
  const [selectedGenre, setSelectedGenre] = React.useState(() => {
    try { return localStorage.getItem('zene_genre') || 'all'; } catch(e) { return 'all'; }
  });

  const filteredSongs = React.useMemo(() => {
    let songs = ZENE_SONGS;
    if (selectedEra !== 'all') songs = songs.filter(s => s.era === selectedEra);
    if (selectedGenre !== 'all') songs = songs.filter(s => s.genre === selectedGenre);
    if (songs.length === 0) songs = ZENE_SONGS;
    const a = [...songs];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }, [selectedEra, selectedGenre]);"""

NEW_ZENE_GAME_TOP = """function ZeneGame({ gameIdx, challenger, onAdvance, onResult, gameMeta }) {
  const selectedEra   = gameMeta?.zeneConfig?.era   || 'all';
  const selectedGenre = gameMeta?.zeneConfig?.genre || 'all';

  const filteredSongs = React.useMemo(() => {
    let songs = ZENE_SONGS;
    if (selectedEra !== 'all') songs = songs.filter(s => s.era === selectedEra);
    if (selectedGenre !== 'all') songs = songs.filter(s => s.genre === selectedGenre);
    if (songs.length === 0) songs = ZENE_SONGS;
    const a = [...songs];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }, [selectedEra, selectedGenre]);"""

assert OLD_ZENE_GAME in content
content = content.replace(OLD_ZENE_GAME, NEW_ZENE_GAME_TOP, 1)

# ── 3. Remove saveEra/saveGenre/chip/ERA_OPTIONS/GENRE_OPTIONS from ZeneGame ──
OLD_ZENE_HELPERS = """  const saveEra   = v => { setSelectedEra(v);   try { localStorage.setItem('zene_era',   v); } catch(e){} };
  const saveGenre = v => { setSelectedGenre(v); try { localStorage.setItem('zene_genre', v); } catch(e){} };

  const ERA_OPTIONS = [
    { v:'all',     label:'Minden' },
    { v:'classic', label:'Klassz.' },
    { v:'2000s',   label:'2000-es' },
    { v:'2010s',   label:'2010-es' },
    { v:'2020s',   label:'2020-as' },
  ];
  const GENRE_OPTIONS = [
    { v:'all',        label:'Minden' },
    { v:'pop',        label:'Pop' },
    { v:'rnb',        label:'R&B' },
    { v:'hiphop',     label:'Hip-hop' },
    { v:'rock',       label:'Rock' },
    { v:'electronic', label:'Electronic' },
    { v:'indie',      label:'Indie' },
  ];

  const chip = (active) => ({
    padding:'5px 11px', borderRadius:999, border:'none', cursor:'pointer',
    fontFamily:T.font, fontWeight:700, fontSize:11,
    background: active ? T.mint : T.surfaceMuted,
    color: active ? '#fff' : T.inkSoft,
    whiteSpace:'nowrap', flexShrink:0, transition:'background .15s',
  });

  return ("""

NEW_ZENE_HELPERS = """  return ("""

assert OLD_ZENE_HELPERS in content
content = content.replace(OLD_ZENE_HELPERS, NEW_ZENE_HELPERS, 1)

# ── 4. Remove filter chip rows from ZeneGame JSX ─────────────────
OLD_FILTER_UI = """      {/* Filter chips */}
      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:5 }}>
        <div style={{ overflowX:'auto', display:'flex', gap:5, paddingBottom:1, WebkitOverflowScrolling:'touch' }}>
          {ERA_OPTIONS.map(o => <button key={o.v} onClick={() => saveEra(o.v)} style={chip(selectedEra===o.v)}>{o.label}</button>)}
        </div>
        <div style={{ overflowX:'auto', display:'flex', gap:5, paddingBottom:1, WebkitOverflowScrolling:'touch' }}>
          {GENRE_OPTIONS.map(o => <button key={o.v} onClick={() => saveGenre(o.v)} style={chip(selectedGenre===o.v)}>{o.label}</button>)}
        </div>
      </div>

      {previewUrl && ("""

NEW_FILTER_UI = """      {previewUrl && ("""

assert OLD_FILTER_UI in content
content = content.replace(OLD_FILTER_UI, NEW_FILTER_UI, 1)

# ── 5. Pass gameMeta to ZeneGame in GameContent ───────────────────
OLD_GAME_CONTENT_ZENE = "  if (gameId === 'zene') return <ZeneGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;"
NEW_GAME_CONTENT_ZENE = "  if (gameId === 'zene') return <ZeneGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} />;"

assert OLD_GAME_CONTENT_ZENE in content
content = content.replace(OLD_GAME_CONTENT_ZENE, NEW_GAME_CONTENT_ZENE, 1)

# ── 6. Add zeneSheet state and zeneConfig in GamesScreen ──────────
OLD_GAMESSCREEN_STATE = """  const [ovfjSheet, setOvfjSheet] = useState(false);
  const [filterSheet, setFilterSheet] = useState(false);"""

NEW_GAMESSCREEN_STATE = """  const [ovfjSheet, setOvfjSheet] = useState(false);
  const [zeneSheet, setZeneSheet] = useState(false);
  const [filterSheet, setFilterSheet] = useState(false);"""

assert OLD_GAMESSCREEN_STATE in content
content = content.replace(OLD_GAMESSCREEN_STATE, NEW_GAMESSCREEN_STATE, 1)

# ── 7. Add zeneConfig accessor in GamesScreen ────────────────────
OLD_GAMESSCREEN_CONFIG = """  const beerpongConfig = gameMeta?.beerpongConfig || {};
  const setBeerpongConfig = cfg => setGameMeta(m => ({...m, beerpongConfig: typeof cfg === 'function' ? cfg(m?.beerpongConfig||{}) : cfg}));"""

NEW_GAMESSCREEN_CONFIG = """  const beerpongConfig = gameMeta?.beerpongConfig || {};
  const setBeerpongConfig = cfg => setGameMeta(m => ({...m, beerpongConfig: typeof cfg === 'function' ? cfg(m?.beerpongConfig||{}) : cfg}));
  const zeneConfig = gameMeta?.zeneConfig || {};
  const setZeneConfig = cfg => setGameMeta(m => ({...m, zeneConfig: typeof cfg === 'function' ? cfg(m?.zeneConfig||{}) : cfg}));"""

assert OLD_GAMESSCREEN_CONFIG in content
content = content.replace(OLD_GAMESSCREEN_CONFIG, NEW_GAMESSCREEN_CONFIG, 1)

# ── 8. Add zene to FavTile long-press handlers ────────────────────
OLD_FAV_LONGPRESS = """                  const longPress = g.id==='busz' ? ()=>{ if(!selectedGames.includes('busz')) toggle('busz'); setBuszSheet(true); }
                    : g.id==='beerpong' ? ()=>{ if(!selectedGames.includes('beerpong')) toggle('beerpong'); setBeerpongSheet(true); }
                    : undefined;"""

NEW_FAV_LONGPRESS = """                  const longPress = g.id==='busz' ? ()=>{ if(!selectedGames.includes('busz')) toggle('busz'); setBuszSheet(true); }
                    : g.id==='beerpong' ? ()=>{ if(!selectedGames.includes('beerpong')) toggle('beerpong'); setBeerpongSheet(true); }
                    : g.id==='zene' ? ()=>{ if(!selectedGames.includes('zene')) toggle('zene'); setZeneSheet(true); }
                    : undefined;"""

assert OLD_FAV_LONGPRESS in content
content = content.replace(OLD_FAV_LONGPRESS, NEW_FAV_LONGPRESS, 1)

# ── 9. Add zene to GameTile long-press handlers ───────────────────
OLD_TILE_LONGPRESS = "g.id==='ovfj' ? ()=>{ if(!selectedGames.includes('ovfj')) toggle('ovfj'); setOvfjSheet(true); } : undefined}"
NEW_TILE_LONGPRESS = "g.id==='ovfj' ? ()=>{ if(!selectedGames.includes('ovfj')) toggle('ovfj'); setOvfjSheet(true); } : g.id==='zene' ? ()=>{ if(!selectedGames.includes('zene')) toggle('zene'); setZeneSheet(true); } : undefined}"

assert OLD_TILE_LONGPRESS in content
content = content.replace(OLD_TILE_LONGPRESS, NEW_TILE_LONGPRESS, 1)

# ── 10. Add ZeneConfigSheet rendering in GamesScreen ─────────────
OLD_SHEET_RENDER = "      {ovfjSheet && <OVFJConfigSheet config={ovfjConfig} setConfig={setOvfjConfig} onClose={() => setOvfjSheet(false)} />}"
NEW_SHEET_RENDER = """      {ovfjSheet && <OVFJConfigSheet config={ovfjConfig} setConfig={setOvfjConfig} onClose={() => setOvfjSheet(false)} />}
      {zeneSheet && <ZeneConfigSheet config={zeneConfig} setConfig={setZeneConfig} onClose={() => setZeneSheet(false)} />}"""

assert OLD_SHEET_RENDER in content
content = content.replace(OLD_SHEET_RENDER, NEW_SHEET_RENDER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.107 ready")
