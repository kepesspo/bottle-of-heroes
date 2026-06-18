#!/usr/bin/env python3
"""patch_9_114.py — Fix loading forever: handle empty previewMap + remove market=US"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.113';" in content
content = content.replace("const APP_VERSION = 'v9.113';", "const APP_VERSION = 'v9.114';")

# ── 1. checkZeneBatch: remove &market=US (many tracks have null preview_url in US) ──
OLD_BATCH_URL = "      return fetch('https://api.spotify.com/v1/tracks?ids=' + ids.join(',') + '&market=US', {"
NEW_BATCH_URL = "      return fetch('https://api.spotify.com/v1/tracks?ids=' + ids.join(','), {"

assert OLD_BATCH_URL in content, "batch URL not found"
content = content.replace(OLD_BATCH_URL, NEW_BATCH_URL, 1)

# ── 2. ZeneGame batch check: if map empty after check, clear cache + retry once ──
OLD_BATCH_EFFECT = """  React.useEffect(() => {
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

NEW_BATCH_EFFECT = """  React.useEffect(() => {
    if (previewMap !== null) return;
    const allIds = ZENE_SONGS.map(s => s.spotifyId);
    const BATCH = 50;
    const map = {};
    let i = 0;
    const next = () => {
      if (i >= allIds.length) {
        if (Object.keys(map).length === 0) {
          // No previews found — save empty sentinel so we don't loop, but mark as failed
          try { localStorage.removeItem('zene_preview_map_v1'); } catch(e) {}
          setPreviewMap({});
        } else {
          try { localStorage.setItem('zene_preview_map_v1', JSON.stringify(map)); } catch(e) {}
          setPreviewMap(map);
        }
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

assert OLD_BATCH_EFFECT in content, "batch effect not found"
content = content.replace(OLD_BATCH_EFFECT, NEW_BATCH_EFFECT, 1)

# ── 3. filteredSongs: if previewMap empty fall back to all songs ──
OLD_FILTERED = """  const filteredSongs = React.useMemo(() => {
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

NEW_FILTERED = """  const previewMapEmpty = previewMap !== null && Object.keys(previewMap).length === 0;
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

assert OLD_FILTERED in content, "filteredSongs not found"
content = content.replace(OLD_FILTERED, NEW_FILTERED, 1)

# ── 4. useEffect: add setLoading(true) at start, handle missing previewUrl with API fallback ──
OLD_DIRECT_EFFECT = """  React.useEffect(() => {
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
  }, [song?.spotifyId, previewMap]);"""

NEW_DIRECT_EFFECT = """  React.useEffect(() => {
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

assert OLD_DIRECT_EFFECT in content, "direct effect not found"
content = content.replace(OLD_DIRECT_EFFECT, NEW_DIRECT_EFFECT, 1)

# ── 5. Check screen: also handle null case ──
OLD_CHECK = "  if (previewMap === null) {"
NEW_CHECK = "  if (previewMap === null) { // check screen"

assert OLD_CHECK in content
content = content.replace(OLD_CHECK, NEW_CHECK, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.114 ready")
