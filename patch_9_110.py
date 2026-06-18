#!/usr/bin/env python3
"""patch_9_110.py — Spotify CC visszaállítva + egyszeri batch önellenőrzés"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.109';" in content
content = content.replace("const APP_VERSION = 'v9.109';", "const APP_VERSION = 'v9.110';")

# ── 1. iTunes → Spotify CC visszaállítása ────────────────────────
OLD_ITUNES = """  var _itunesCache = {};
  window.fetchItunesPreview = function(artist, title) {
    var key = artist + '|||' + title;
    if (_itunesCache[key] !== undefined) return Promise.resolve(_itunesCache[key]);
    var query = encodeURIComponent(artist + ' ' + title);
    var controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
    var timer = controller ? setTimeout(function() { controller.abort(); }, 7000) : null;
    var opts = controller ? { signal: controller.signal } : {};
    return fetch('https://itunes.apple.com/search?term=' + query + '&media=music&entity=song&limit=5&country=US', opts)
      .then(function(r) { if (timer) clearTimeout(timer); return r.json(); })
      .then(function(d) {
        var results = d.results || [];
        var preview = null;
        for (var i = 0; i < results.length; i++) {
          if (results[i].previewUrl) { preview = results[i].previewUrl; break; }
        }
        _itunesCache[key] = preview;
        return preview;
      })
      .catch(function() { if (timer) clearTimeout(timer); _itunesCache[key] = null; return null; });
  };"""

NEW_SPOTIFY_CC = """  var _ccToken = null, _ccExpiry = 0, _ccFetching = null;
  window.getSpotifyCCToken = function() {
    if (_ccToken && Date.now() < _ccExpiry) return Promise.resolve(_ccToken);
    if (_ccFetching) return _ccFetching;
    _ccFetching = fetch('https://accounts.spotify.com/api/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + btoa('466b1ac50ffb4a2a866dddbeab9bef80:9569e6631bd94cb9a155bc28aa49df08'),
      },
      body: 'grant_type=client_credentials',
    }).then(function(r) { return r.json(); }).then(function(d) {
      _ccToken = d.access_token;
      _ccExpiry = Date.now() + ((d.expires_in || 3600) - 60) * 1000;
      _ccFetching = null;
      return _ccToken;
    }).catch(function() { _ccFetching = null; return null; });
    return _ccFetching;
  };

  // Batch ellenőrzés: 50 track egyszerre
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

assert OLD_ITUNES in content, "iTunes block not found"
content = content.replace(OLD_ITUNES, NEW_SPOTIFY_CC, 1)

# ── 2. ZeneGame: batch önellenőrzés + csak working songs ─────────
OLD_ZENEGAME = """function ZeneGame({ gameIdx, challenger, onAdvance, onResult, gameMeta }) {
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

NEW_ZENEGAME = """function ZeneGame({ gameIdx, challenger, onAdvance, onResult, gameMeta }) {
  const selectedEra   = gameMeta?.zeneConfig?.era   || 'all';
  const selectedGenre = gameMeta?.zeneConfig?.genre || 'all';

  // Egyszeri batch ellenőrzés — melyik dalnak van Spotify preview?
  const [okIds, setOkIds] = React.useState(() => {
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
  }, []);

  const filteredSongs = React.useMemo(() => {
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

assert OLD_ZENEGAME in content, "ZeneGame top not found"
content = content.replace(OLD_ZENEGAME, NEW_ZENEGAME, 1)

# ── 3. ZeneGame: useEffect deps iTunes → Spotify ─────────────────
OLD_ITUNES_EFFECT = """    window.fetchItunesPreview(song.artist, song.title).then(url => {
      if (url) {
        setPreviewUrl(url);
        setLoading(false);
      } else {
        setLoading(false);
        setSkipped(true);
        if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); }
      }
    });

    window.fetchItunesPreview(nextSong.artist, nextSong.title); // prefetch next

    return () => { if (audioRef.current) audioRef.current.pause(); };
  }, [song.artist, song.title]);"""

NEW_SPOTIFY_EFFECT = """    window.getSpotifyCCToken().then(token => {
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
  }, [song.spotifyId]);"""

assert OLD_ITUNES_EFFECT in content, "iTunes effect not found"
content = content.replace(OLD_ITUNES_EFFECT, NEW_SPOTIFY_EFFECT, 1)

# ── 4. ZeneGame JSX: ellenőrzés képernyő ha okIds null ───────────
OLD_ZENE_RETURN = """  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:10 }}>"""

NEW_ZENE_RETURN = """  // Ellenőrzés képernyő
  if (okIds === null) {
    return (
      <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'20px 0' }}>
        <div style={{ fontSize:40 }}>🎵</div>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, textAlign:'center' }}>Zenék előkészítése...</div>
        <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>Egyszer szükséges — ellenőrzöm melyik dalnak van preview</div>
        <div style={{ width:'100%', height:8, borderRadius:8, background:T.surfaceMuted, overflow:'hidden' }}>
          <div style={{ height:'100%', borderRadius:8, background:T.mint, width: checkPct + '%', transition:'width .3s' }} />
        </div>
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:T.mint }}>{checkPct}%</div>
      </div>
    );
  }

  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:10 }}>"""

assert OLD_ZENE_RETURN in content, "ZeneGame return not found"
content = content.replace(OLD_ZENE_RETURN, NEW_ZENE_RETURN, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.110 ready")
