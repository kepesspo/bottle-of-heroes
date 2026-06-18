#!/usr/bin/env python3
"""patch_9_109.py — iTunes country=US, timeout, jobb UX skip esetén"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.108';" in content
content = content.replace("const APP_VERSION = 'v9.108';", "const APP_VERSION = 'v9.109';")

# ── 1. iTunes: country=US, AbortController timeout ───────────────
OLD_ITUNES_FETCH = """  var _itunesCache = {};
  window.fetchItunesPreview = function(artist, title) {
    var key = artist + '|||' + title;
    if (_itunesCache[key] !== undefined) return Promise.resolve(_itunesCache[key]);
    var query = encodeURIComponent(artist + ' ' + title);
    return fetch('https://itunes.apple.com/search?term=' + query + '&media=music&entity=song&limit=3&country=HU')
      .then(function(r) { return r.json(); })
      .then(function(d) {
        var results = d.results || [];
        var preview = null;
        for (var i = 0; i < results.length; i++) {
          if (results[i].previewUrl) { preview = results[i].previewUrl; break; }
        }
        _itunesCache[key] = preview;
        return preview;
      })
      .catch(function() { _itunesCache[key] = null; return null; });
  };"""

NEW_ITUNES_FETCH = """  var _itunesCache = {};
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

assert OLD_ITUNES_FETCH in content
content = content.replace(OLD_ITUNES_FETCH, NEW_ITUNES_FETCH, 1)

# ── 2. ZeneGame: skip state helyett loading → skipped UX ─────────
# Add 'skipped' state, show message + auto-advance after 1.5s
OLD_ZENE_STATES = """  const [playing, setPlaying] = React.useState(false);
  const [revealed, setRevealed] = React.useState(false);
  const [previewUrl, setPreviewUrl] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const audioRef    = React.useRef(null);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPlaying(false);
    setRevealed(false);
    setLoading(true);
    setPreviewUrl(null);
    advancedRef.current = false;
    if (audioRef.current) { audioRef.current.pause(); audioRef.current.src = ''; }

    window.fetchItunesPreview(song.artist, song.title).then(url => {
      if (url) {
        setPreviewUrl(url);
        setLoading(false);
      } else {
        // No preview → auto-skip silently
        if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); }
      }
    });

    window.fetchItunesPreview(nextSong.artist, nextSong.title); // prefetch next

    return () => { if (audioRef.current) audioRef.current.pause(); };
  }, [song.artist, song.title]);"""

NEW_ZENE_STATES = """  const [playing, setPlaying] = React.useState(false);
  const [revealed, setRevealed] = React.useState(false);
  const [previewUrl, setPreviewUrl] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [skipped, setSkipped] = React.useState(false);
  const audioRef    = React.useRef(null);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPlaying(false);
    setRevealed(false);
    setLoading(true);
    setSkipped(false);
    setPreviewUrl(null);
    advancedRef.current = false;
    if (audioRef.current) { audioRef.current.pause(); audioRef.current.src = ''; }

    window.fetchItunesPreview(song.artist, song.title).then(url => {
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

assert OLD_ZENE_STATES in content
content = content.replace(OLD_ZENE_STATES, NEW_ZENE_STATES, 1)

# ── 3. ZeneGame JSX: show skipped message ────────────────────────
OLD_LOADING_UI = """      {previewUrl && (
        <audio ref={audioRef} src={previewUrl}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => setPlaying(false)} />
      )}

      {/* Vinyl */}"""

NEW_LOADING_UI = """      {previewUrl && (
        <audio ref={audioRef} src={previewUrl}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => setPlaying(false)} />
      )}

      {/* Vinyl */}"""

# (vinyl unchanged, but update buttons section)

OLD_BUTTONS = """      {/* Buttons */}
      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8 }}>
        {loading ? (
          <div style={{ width:'100%', padding:'14px 0', borderRadius:16, display:'flex', alignItems:'center', justifyContent:'center' }}>
            <span style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>⏳ Betöltés...</span>
          </div>
        ) : !playing ? ("""

NEW_BUTTONS = """      {/* Buttons */}
      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8 }}>
        {loading ? (
          <div style={{ width:'100%', padding:'14px 0', borderRadius:16, display:'flex', alignItems:'center', justifyContent:'center' }}>
            <span style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>⏳ Betöltés...</span>
          </div>
        ) : skipped ? (
          <div style={{ width:'100%', padding:'16px', borderRadius:16, background:T.surfaceMuted, display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
            <span style={{ fontSize:18 }}>⏭</span>
            <span style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>Nincs preview — kihagyva. Nyomj Kövi-t!</span>
          </div>
        ) : !playing ? ("""

assert OLD_BUTTONS in content
content = content.replace(OLD_BUTTONS, NEW_BUTTONS, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.109 ready")
