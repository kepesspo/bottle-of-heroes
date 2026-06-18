#!/usr/bin/env python3
"""patch_9_112.py — Batch check stores preview URLs directly, no API call during gameplay"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.111';" in content
content = content.replace("const APP_VERSION = 'v9.111';", "const APP_VERSION = 'v9.112';")

# ── 1. checkZeneBatch: return {id: previewUrl} instead of {id: bool} ──
OLD_CHECK_BATCH = """  // Batch ellenőrzés: 50 track egyszerre
  window.checkZeneBatch = function(ids) {
    return window.getSpotifyCCToken().then(function(token) {
      if (!token) return {};
      return fetch('https://api.spotify.com/v1/tracks?ids=' + ids.join(',') + '&market=US', {
        headers: { 'Authorization': 'Bearer ' + token }
      }).then(function(r) { return r.json(); }).then(function(d) {
        var result = {};
        (d.tracks || []).forEach(function(track, i) {
          result[ids[i]] = !!(track && track.preview_url);
        });
        return result;
      });
    }).catch(function() { return {}; });
  };"""

NEW_CHECK_BATCH = """  // Batch ellenőrzés: 50 track egyszerre — visszaadja {id: previewUrl}
  window.checkZeneBatch = function(ids) {
    return window.getSpotifyCCToken().then(function(token) {
      if (!token) return {};
      return fetch('https://api.spotify.com/v1/tracks?ids=' + ids.join(',') + '&market=US', {
        headers: { 'Authorization': 'Bearer ' + token }
      }).then(function(r) { return r.json(); }).then(function(d) {
        var result = {};
        (d.tracks || []).forEach(function(track, i) {
          if (track && track.preview_url) result[ids[i]] = track.preview_url;
        });
        return result;
      });
    }).catch(function() { return {}; });
  };"""

assert OLD_CHECK_BATCH in content, "checkZeneBatch not found"
content = content.replace(OLD_CHECK_BATCH, NEW_CHECK_BATCH, 1)

# ── 2. ZeneGame: store previewUrls map, load from localStorage ───
OLD_OKIDS_STATE = """  const [okIds, setOkIds] = React.useState(() => {
    try {
      const s = localStorage.getItem('zene_ok_ids_v2');
      return s ? new Set(JSON.parse(s)) : null;
    } catch(e) { return null; }
  });
  const [checkPct, setCheckPct] = React.useState(0);

  React.useEffect(() => {
    if (okIds !== null) return;
    const allIds = ZENE_SONGS.map(s => s.spotifyId);
    const BATCH = 50;
    const working = [];
    let i = 0;
    const next = () => {
      if (i >= allIds.length) {
        try { localStorage.setItem('zene_ok_ids_v2', JSON.stringify(working)); } catch(e) {}
        setOkIds(new Set(working));
        return;
      }
      setCheckPct(Math.round(i / allIds.length * 100));
      window.checkZeneBatch(allIds.slice(i, i + BATCH)).then(res => {
        Object.keys(res).forEach(id => { if (res[id]) working.push(id); });
        i += BATCH;
        setTimeout(next, 150);
      });
    };
    next();
  }, []);"""

NEW_OKIDS_STATE = """  // previewUrls: {spotifyId -> previewUrl} — localStorage-ból töltve
  const [previewMap, setPreviewMap] = React.useState(() => {
    try {
      const s = localStorage.getItem('zene_preview_map_v1');
      return s ? JSON.parse(s) : null;
    } catch(e) { return null; }
  });
  const [checkPct, setCheckPct] = React.useState(0);

  React.useEffect(() => {
    if (previewMap !== null) return;
    const allIds = ZENE_SONGS.map(s => s.spotifyId);
    const BATCH = 50;
    const map = {};
    let i = 0;
    const next = () => {
      if (i >= allIds.length) {
        try { localStorage.setItem('zene_preview_map_v1', JSON.stringify(map)); } catch(e) {}
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
  }, []);"""

assert OLD_OKIDS_STATE in content, "okIds state not found"
content = content.replace(OLD_OKIDS_STATE, NEW_OKIDS_STATE, 1)

# ── 3. filteredSongs: use previewMap instead of okIds Set ────────
OLD_FILTERED = """  const filteredSongs = React.useMemo(() => {
    if (!okIds) return [];
    let songs = ZENE_SONGS.filter(s => okIds.has(s.spotifyId));
    if (selectedEra !== 'all') songs = songs.filter(s => s.era === selectedEra);
    if (selectedGenre !== 'all') songs = songs.filter(s => s.genre === selectedGenre);
    if (songs.length === 0) songs = ZENE_SONGS.filter(s => okIds.has(s.spotifyId));
    const a = [...songs];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }, [okIds, selectedEra, selectedGenre]);"""

NEW_FILTERED = """  const filteredSongs = React.useMemo(() => {
    if (!previewMap) return [];
    let songs = ZENE_SONGS.filter(s => previewMap[s.spotifyId]);
    if (selectedEra !== 'all') songs = songs.filter(s => s.era === selectedEra);
    if (selectedGenre !== 'all') songs = songs.filter(s => s.genre === selectedGenre);
    if (songs.length === 0) songs = ZENE_SONGS.filter(s => previewMap[s.spotifyId]);
    const a = [...songs];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }, [previewMap, selectedEra, selectedGenre]);"""

assert OLD_FILTERED in content, "filteredSongs not found"
content = content.replace(OLD_FILTERED, NEW_FILTERED, 1)

# ── 4. ZeneGame useEffect: use previewMap[song.spotifyId] directly ──
OLD_SPOTIFY_EFFECT = """  React.useEffect(() => {
    if (!song) return;
    setPlaying(false);
    setRevealed(false);
    setLoading(true);
    setSkipped(false);
    setPreviewUrl(null);
    advancedRef.current = false;
    if (audioRef.current) { audioRef.current.pause(); audioRef.current.src = ''; }

    window.getSpotifyCCToken().then(token => {
      if (!token) { setLoading(false); setSkipped(true); if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); } return; }
      fetch('https://api.spotify.com/v1/tracks/' + song.spotifyId + '?market=US', {
        headers: { 'Authorization': 'Bearer ' + token }
      }).then(r => r.json()).then(d => {
        const url = d.preview_url || null;
        if (url) { setPreviewUrl(url); setLoading(false); }
        else { setLoading(false); setSkipped(true); if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); } }
      }).catch(() => { setLoading(false); setSkipped(true); if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); } });
    });

    return () => { if (audioRef.current) audioRef.current.pause(); };
  }, [song?.spotifyId]);"""

NEW_DIRECT_EFFECT = """  React.useEffect(() => {
    if (!song || !previewMap) return;
    setPlaying(false);
    setRevealed(false);
    setSkipped(false);
    advancedRef.current = false;
    if (audioRef.current) { audioRef.current.pause(); audioRef.current.src = ''; }

    // URL már a previewMap-ben van — nincs szükség API hívásra
    const url = previewMap[song.spotifyId] || null;
    if (url) {
      setPreviewUrl(url);
      setLoading(false);
    } else {
      setPreviewUrl(null);
      setLoading(false);
      setSkipped(true);
      if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); }
    }

    return () => { if (audioRef.current) audioRef.current.pause(); };
  }, [song?.spotifyId]);"""

assert OLD_SPOTIFY_EFFECT in content, "Spotify effect not found"
content = content.replace(OLD_SPOTIFY_EFFECT, NEW_DIRECT_EFFECT, 1)

# ── 5. Check screen: use previewMap instead of okIds ─────────────
OLD_CHECK_SCREEN = "  if (okIds === null) {"
NEW_CHECK_SCREEN = "  if (previewMap === null) {"

assert OLD_CHECK_SCREEN in content
content = content.replace(OLD_CHECK_SCREEN, NEW_CHECK_SCREEN, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.112 ready")
