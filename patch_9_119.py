#!/usr/bin/env python3
"""patch_9_119.py — ZeneGame: use Spotify IFrame Embed API instead of audio element + preview_url"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.118';" in content
content = content.replace("const APP_VERSION = 'v9.118';", "const APP_VERSION = 'v9.119';")

# ── 1. Remove the whole previewMap / batch check machinery and replace ZeneGame ──
# Find ZeneGame start and replace the entire component

OLD_ZENEGAME_OPEN = """function ZeneGame({ gameIdx, challenger, onAdvance, onResult, gameMeta }) {
  const selectedEra   = gameMeta?.zeneConfig?.era   || 'all';
  const selectedGenre = gameMeta?.zeneConfig?.genre || 'all';

  // Egyszeri batch ellenőrzés — melyik dalnak van Spotify preview?
  // previewUrls: {spotifyId -> previewUrl} — localStorage-ból töltve
  const [previewMap, setPreviewMap] = React.useState(() => {
    try {
      const s = localStorage.getItem('zene_preview_map_v2');
      return s ? JSON.parse(s) : null;
    } catch(e) { return null; }
  });
  const [checkPct, setCheckPct] = React.useState(0);
  const [showDebug, setShowDebug] = React.useState(false);
  const [debugLog, setDebugLog] = React.useState([]);"""

NEW_ZENEGAME_OPEN = """function ZeneGame({ gameIdx, challenger, onAdvance, onResult, gameMeta }) {
  const selectedEra   = gameMeta?.zeneConfig?.era   || 'all';
  const selectedGenre = gameMeta?.zeneConfig?.genre || 'all';"""

assert OLD_ZENEGAME_OPEN in content, "ZeneGame open not found"
content = content.replace(OLD_ZENEGAME_OPEN, NEW_ZENEGAME_OPEN, 1)

# ── 2. Remove the entire batch check useEffect (large block) ──
OLD_BATCH_EFFECT_FULL = """  React.useEffect(() => {
    if (previewMap !== null) return;
    const logs = [];
    const log = (msg) => { logs.push(msg); setDebugLog([...logs]); };
    const allIds = ZENE_SONGS.map(s => s.spotifyId); // used for length only
    const BATCH = 50;
    const map = {};
    let i = 0;

    // Step 1: get token and log result
    window.getSpotifyCCToken().then(token => {
      if (!token) {
        log('❌ Token: SIKERTELEN (null visszatérés)');
        setPreviewMap({});
        return;
      }
      log('✅ Token megérkezett: ' + token.substring(0, 20) + '...');

      // Step 2: test first batch raw
      const firstBatch = allIds.slice(0, 3);
      log('🔍 Teszt kérés: ' + firstBatch.join(', '));

      // Try with no market
      fetch('https://api.spotify.com/v1/tracks?ids=' + firstBatch.join(','), {
        headers: { 'Authorization': 'Bearer ' + token }
      }).then(r => {
        log('📡 HTTP státusz: ' + r.status);
        return r.json();
      }).then(d => {
        if (d.error) { log('❌ API hiba: ' + JSON.stringify(d.error)); }
        const tracks = d.tracks || [];
        log('📦 Visszaérkezett ' + tracks.length + ' track');
        tracks.forEach((t, idx) => {
          if (t) {
            log('  [' + idx + '] ' + (t.name||'?') + ' — preview_url: ' + (t.preview_url ? '✅ ' + t.preview_url.substring(0,40) : '❌ null'));
          } else {
            log('  [' + idx + '] null track');
          }
        });

        // Try same with market=HU
        fetch('https://api.spotify.com/v1/tracks?ids=' + firstBatch.join(',') + '&market=HU', {
          headers: { 'Authorization': 'Bearer ' + token }
        }).then(r2 => r2.json()).then(d2 => {
          const t2 = d2.tracks || [];
          log('--- market=HU ---');
          t2.forEach((t, idx) => {
            if (t) log('  [' + idx + '] preview_url: ' + (t.preview_url ? '✅ ' + t.preview_url.substring(0,40) : '❌ null'));
          });

          // Try market=GB
          fetch('https://api.spotify.com/v1/tracks?ids=' + firstBatch.join(',') + '&market=GB', {
            headers: { 'Authorization': 'Bearer ' + token }
          }).then(r3 => r3.json()).then(d3 => {
            const t3 = d3.tracks || [];
            log('--- market=GB ---');
            t3.forEach((t, idx) => {
              if (t) log('  [' + idx + '] preview_url: ' + (t.preview_url ? '✅ ' + t.preview_url.substring(0,40) : '❌ null'));
            });
            log('✅ Debug kész. Batch ellenőrzés indul...');

            // Now run full batch
            const next = () => {
              if (i >= allIds.length) {
                log('🏁 Kész: ' + Object.keys(map).length + ' preview URL összesen');
                if (Object.keys(map).length === 0) {
                  try { localStorage.removeItem('zene_preview_map_v1'); } catch(e) {}
                } else {
                  try { localStorage.setItem('zene_preview_map_v1', JSON.stringify(map)); } catch(e) {}
                }
                setPreviewMap(map);
                return;
              }
              setCheckPct(Math.round(i / allIds.length * 100));
              window.checkZeneBatch(allIds.slice(i, i + BATCH)).then(res => {
                Object.assign(map, res);
                i += BATCH;
                setTimeout(next, 150);
              });
            };
            next();
          });
        });
      }).catch(e => {
        log('❌ Fetch hiba: ' + e.message);
        setPreviewMap({});
      });
    });
  }, []);"""

assert OLD_BATCH_EFFECT_FULL in content, "batch effect not found"
content = content.replace(OLD_BATCH_EFFECT_FULL, "", 1)

# ── 3. Replace previewMapEmpty + filteredSongs ──
OLD_FILTERED = """  const previewMapEmpty = previewMap !== null && Object.keys(previewMap).length === 0;
  const filteredSongs = React.useMemo(() => {
    if (!previewMap) return [];
    // If map has data, only use songs with preview; if empty fallback to all songs
    const hasPreviews = Object.keys(previewMap).length > 0;
    let base = hasPreviews ? ZENE_SONGS.filter(s => previewMap[s.spotifyId]) : ZENE_SONGS;
    let songs = [...base];
    if (selectedEra !== 'all') songs = songs.filter(s => s.era === selectedEra);
    if (selectedGenre !== 'all') songs = songs.filter(s => s.genre === selectedGenre);
    if (songs.length === 0) songs = [...base];
    const a = [...songs];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }, [previewMap, selectedEra, selectedGenre]);"""

NEW_FILTERED = """  const filteredSongs = React.useMemo(() => {
    let songs = [...ZENE_SONGS];
    if (selectedEra !== 'all') songs = songs.filter(s => s.era === selectedEra);
    if (selectedGenre !== 'all') songs = songs.filter(s => s.genre === selectedGenre);
    if (songs.length === 0) songs = [...ZENE_SONGS];
    for (let i = songs.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [songs[i], songs[j]] = [songs[j], songs[i]];
    }
    return songs;
  }, [selectedEra, selectedGenre]);"""

assert OLD_FILTERED in content, "filteredSongs not found"
content = content.replace(OLD_FILTERED, NEW_FILTERED, 1)

# ── 4. Replace audio states + useEffect with Spotify IFrame approach ──
OLD_AUDIO_STATES = """  const [playing, setPlaying] = React.useState(false);
  const [revealed, setRevealed] = React.useState(false);
  const [previewUrl, setPreviewUrl] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [skipped, setSkipped] = React.useState(false);
  const audioRef    = React.useRef(null);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    if (!song || !previewMap) return;
    setPlaying(false);
    setRevealed(false);
    setLoading(true);
    setSkipped(false);
    setPreviewUrl(null);
    advancedRef.current = false;
    if (audioRef.current) { audioRef.current.pause(); audioRef.current.src = ''; }

    const url = previewMap[song.spotifyId] || null;
    if (url) {
      setPreviewUrl(url);
      setLoading(false);
    } else {
      // No cached URL — try Spotify API directly
      window.getSpotifyCCToken().then(token => {
        if (!token) { setLoading(false); setSkipped(true); if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); } return; }
        fetch('https://api.spotify.com/v1/tracks/' + song.spotifyId, {
          headers: { 'Authorization': 'Bearer ' + token }
        }).then(r => r.json()).then(d => {
          const u = d.preview_url || null;
          if (u) { setPreviewUrl(u); setLoading(false); }
          else { setLoading(false); setSkipped(true); if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); } }
        }).catch(() => { setLoading(false); setSkipped(true); if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); } });
      });
    }

    return () => { if (audioRef.current) audioRef.current.pause(); };
  }, [song?.spotifyId, previewMap]);"""

NEW_AUDIO_STATES = """  const [playing, setPlaying] = React.useState(false);
  const [revealed, setRevealed] = React.useState(false);
  const [embedReady, setEmbedReady] = React.useState(false);
  const embedRef     = React.useRef(null);   // DOM div for iframe
  const controllerRef = React.useRef(null);  // Spotify EmbedController
  const advancedRef  = React.useRef(false);

  // Create/update Spotify embed controller when song changes
  React.useEffect(() => {
    if (!song) return;
    setPlaying(false);
    setRevealed(false);
    setEmbedReady(false);
    advancedRef.current = false;
    if (controllerRef.current) {
      try { controllerRef.current.destroy(); } catch(e) {}
      controllerRef.current = null;
    }

    const uri = 'spotify:track:' + song.spotifyId;
    const createController = () => {
      if (!window._spotifyIFrameAPI || !embedRef.current) return;
      window._spotifyIFrameAPI.createController(embedRef.current, {
        uri,
        width: '100%',
        height: '80',
      }, (controller) => {
        controllerRef.current = controller;
        controller.addListener('ready', () => setEmbedReady(true));
        controller.addListener('playback_update', (e) => {
          setPlaying(!e.data.isPaused && e.data.position > 0);
        });
      });
    };

    if (window._spotifyIFrameAPI) {
      createController();
    } else {
      // Wait for IFrame API to load
      const orig = window.onSpotifyIframeApiReady;
      window.onSpotifyIframeApiReady = (IFrameAPI) => {
        window._spotifyIFrameAPI = IFrameAPI;
        if (orig) orig(IFrameAPI);
        createController();
      };
    }

    return () => {
      if (controllerRef.current) {
        try { controllerRef.current.pause(); } catch(e) {}
      }
    };
  }, [song?.spotifyId]);"""

assert OLD_AUDIO_STATES in content, "audio states not found"
content = content.replace(OLD_AUDIO_STATES, NEW_AUDIO_STATES, 1)

# ── 5. Replace handlePlay / handleStop ──
OLD_HANDLE_PLAY = """  const handlePlay = () => {
    if (!audioRef.current || !previewUrl || !song) return;
    audioRef.current.currentTime = song.start || 0;
    audioRef.current.play().catch(() => {});
  };
  const handleStop = () => {
    if (!audioRef.current) return;
    audioRef.current.pause();
    setPlaying(false);
  };"""

NEW_HANDLE_PLAY = """  const handlePlay = () => {
    if (!controllerRef.current) return;
    try {
      controllerRef.current.seek(((song?.start) || 0) * 1000);
      controllerRef.current.play();
    } catch(e) {}
  };
  const handleStop = () => {
    if (!controllerRef.current) return;
    try { controllerRef.current.pause(); } catch(e) {}
    setPlaying(false);
  };"""

assert OLD_HANDLE_PLAY in content, "handlePlay not found"
content = content.replace(OLD_HANDLE_PLAY, NEW_HANDLE_PLAY, 1)

# ── 6. Remove audio element from JSX, add embedRef div, fix loading/buttons ──
OLD_AUDIO_JSX = """      {previewUrl && (
        <audio ref={audioRef} src={previewUrl}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => setPlaying(false)} />
      )}

      {/* Vinyl */}"""

NEW_AUDIO_JSX = """      {/* Spotify Embed (hidden div, IFrame API uses it) */}
      <div ref={embedRef} style={{ width:'100%', marginBottom: embedReady ? 4 : 0 }} />

      {/* Vinyl */}"""

assert OLD_AUDIO_JSX in content, "audio JSX not found"
content = content.replace(OLD_AUDIO_JSX, NEW_AUDIO_JSX, 1)

# ── 7. Fix the buttons section: loading→embedReady, remove previewUrl refs ──
OLD_BUTTONS_LOADING = """        {loading ? (
          <div style={{ width:'100%', padding:'14px 0', borderRadius:16, display:'flex', alignItems:'center', justifyContent:'center' }}>
            <span style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>⏳ Betöltés...</span>
          </div>
        ) : skipped ? (
          <div style={{ width:'100%', padding:'16px', borderRadius:16, background:T.surfaceMuted, display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
            <span style={{ fontSize:18 }}>⏭</span>
            <span style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>Nincs preview — kihagyva. Nyomj Kövi-t!</span>
          </div>
        ) : !playing ? ("""

NEW_BUTTONS_LOADING = """        {!embedReady ? (
          <div style={{ width:'100%', padding:'14px 0', borderRadius:16, display:'flex', alignItems:'center', justifyContent:'center' }}>
            <span style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>⏳ Betöltés...</span>
          </div>
        ) : !playing ? ("""

assert OLD_BUTTONS_LOADING in content, "buttons loading not found"
content = content.replace(OLD_BUTTONS_LOADING, NEW_BUTTONS_LOADING, 1)

# ── 8. Remove check screen (no longer needed — no batch check) ──
OLD_DEBUG_OVERLAY = """  // Debug overlay
  if (showDebug && previewMap !== null) {
    const entries = Object.entries(previewMap);
    return (
      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8, padding:'12px 0' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink }}>
          🔍 Debug: {entries.length} dal / {ZENE_SONGS.length} kapott preview URL-t
        </div>
        <button onClick={() => setShowDebug(false)} style={{
          padding:'8px 16px', borderRadius:10, border:'none', background:T.mint, color:'#fff',
          fontFamily:T.font, fontWeight:700, fontSize:13, cursor:'pointer', alignSelf:'flex-start'
        }}>← Vissza a játékhoz</button>
        <div style={{ width:'100%', height:1, background:T.surfaceMuted, margin:'4px 0' }} />
        {entries.length === 0 ? (
          <div style={{ fontFamily:T.font, fontSize:14, color:'#c0392b', fontWeight:700 }}>
            ⚠️ Egyetlen dalnál sem érkezett vissza preview_url a Spotify API-tól!
          </div>
        ) : (
          <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
            {entries.map(([id, url]) => {
              const song = ZENE_SONGS.find(s => s.spotifyId === id);
              return (
                <div key={id} style={{ background:T.surfaceMuted, borderRadius:8, padding:'8px 10px' }}>
                  <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink }}>
                    {song ? song.artist + ' — ' + song.title : id}
                  </div>
                  <div style={{ fontFamily:'monospace', fontSize:10, color:T.inkSoft, wordBreak:'break-all', marginTop:2 }}>
                    {url}
                  </div>
                  <audio controls src={url} style={{ width:'100%', marginTop:4, height:28 }} />
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  }

  // Ellenőrzés képernyő
  if (previewMap === null) { // check screen
    return (
      <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'20px 0' }}>
        <div style={{ fontSize:40 }}>🎵</div>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, textAlign:'center' }}>Zenék előkészítése...</div>
        <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>Egyszer szükséges — ellenőrzöm melyik dalnak van preview</div>
        <div style={{ width:'100%', height:8, borderRadius:8, background:T.surfaceMuted, overflow:'hidden' }}>
          <div style={{ height:'100%', borderRadius:8, background:T.mint, width: checkPct + '%', transition:'width .3s' }} />
        </div>
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:T.mint }}>{checkPct}%</div>
        {checkPct === 100 && (
          <button onClick={() => setShowDebug(true)} style={{
            padding:'10px 20px', borderRadius:12, border:'none', background:'#1B2340', color:'#fff',
            fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer'
          }}>🔍 Debug: previewMap megtekintése</button>
        )}
        {debugLog.length > 0 && (
          <div style={{ width:'100%', background:'#0d1117', borderRadius:10, padding:'10px 12px', maxHeight:300, overflowY:'auto' }}>
            {debugLog.map((line, i) => (
              <div key={i} style={{ fontFamily:'monospace', fontSize:11, color:'#58a6ff', marginBottom:2 }}>{line}</div>
            ))}
          </div>
        )}
      </div>
    );
  }"""

assert OLD_DEBUG_OVERLAY in content, "debug overlay not found"
content = content.replace(OLD_DEBUG_OVERLAY, "", 1)

# ── 9. Remove debug button from game render ──
OLD_DEBUG_BTN = """      {previewMap && <button onClick={() => setShowDebug(true)} style={{
        alignSelf:'flex-end', padding:'4px 10px', borderRadius:8, border:'1px solid ' + T.surfaceMuted,
        background:'transparent', fontFamily:T.font, fontSize:10, color:T.inkSoft, cursor:'pointer'
      }}>🔍 {Object.keys(previewMap).length} preview</button>}"""

assert OLD_DEBUG_BTN in content, "debug button not found"
content = content.replace(OLD_DEBUG_BTN, "", 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.119 ready")
