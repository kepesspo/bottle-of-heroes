#!/usr/bin/env python3
"""patch_9_128.py — Back to Spotify IFrame API (reliable), properly hidden in 0x0 clip container"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.127';" in content
content = content.replace("const APP_VERSION = 'v9.127';", "const APP_VERSION = 'v9.128';")

# ── 1. Remove Deezer/proxy block, restore IFrame-based audio ──
OLD_DEEZER_BLOCK = """  // Deezer preview — tries multiple CORS proxies in order
  var _deezerMemCache = {};
  var ZENE_PROXIES = [
    function(url) { return 'https://api.allorigins.win/raw?url=' + encodeURIComponent(url); },
    function(url) { return 'https://corsproxy.io/?' + encodeURIComponent(url); },
    function(url) { return 'https://proxy.cors.sh/' + url; },
  ];
  window.getZenePreviewUrl = function(spotifyId, artist, title) {
    if (_deezerMemCache[spotifyId] !== undefined) return Promise.resolve(_deezerMemCache[spotifyId]);
    try {
      var cached = localStorage.getItem('zdz_' + spotifyId);
      if (cached !== null) { _deezerMemCache[spotifyId] = cached || null; return Promise.resolve(cached || null); }
    } catch(e) {}
    var q = encodeURIComponent('artist:"' + artist + '" track:"' + title + '"');
    var deezerUrl = 'https://api.deezer.com/search?q=' + q + '&limit=3';

    // Try proxies in sequence until one works
    var tryProxy = function(idx) {
      if (idx >= ZENE_PROXIES.length) { _deezerMemCache[spotifyId] = null; return Promise.resolve(null); }
      return fetch(ZENE_PROXIES[idx](deezerUrl))
        .then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function(d) {
          var items = d.data || [];
          var url = null;
          for (var i = 0; i < items.length; i++) {
            if (items[i].preview) { url = items[i].preview; break; }
          }
          if (!url) throw new Error('no preview');
          _deezerMemCache[spotifyId] = url;
          try { localStorage.setItem('zdz_' + spotifyId, url); } catch(e) {}
          return url;
        })
        .catch(function() { return tryProxy(idx + 1); });
    };
    return tryProxy(0);
  };

  // Quick connectivity test — called from ZeneGame on mount
  window.testZeneProxy = function() {
    var url = 'https://api.deezer.com/search?q=Queen+Bohemian+Rhapsody&limit=1';
    var results = [];
    var tests = ZENE_PROXIES.map(function(proxy, i) {
      var start = Date.now();
      return fetch(proxy(url))
        .then(function(r) { return r.json(); })
        .then(function(d) {
          var preview = (d.data && d.data[0]) ? d.data[0].preview : null;
          results.push({ proxy: i, ok: !!preview, ms: Date.now()-start, url: preview ? preview.substring(0,40) : 'null' });
        })
        .catch(function(e) { results.push({ proxy: i, ok: false, ms: Date.now()-start, err: e.message }); });
    });
    return Promise.all(tests).then(function() { return results; });
  };"""

NEW_EMPTY = """  // Spotify IFrame API used for ZeneGame audio (see onSpotifyIframeApiReady above)"""

assert OLD_DEEZER_BLOCK in content, "deezer block not found"
content = content.replace(OLD_DEEZER_BLOCK, NEW_EMPTY, 1)

# ── 2. Replace audio-element ZeneGame states+effect with IFrame API version ──
OLD_AUDIO_STATES = """  const [playing, setPlaying] = React.useState(false);
  const [revealed, setRevealed] = React.useState(false);
  const [previewUrl, setPreviewUrl] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [debugLines, setDebugLines] = React.useState(null);
  const audioRef    = React.useRef(null);
  const advancedRef = React.useRef(false);

  // Prefetch next N songs in background so they load instantly when reached
  const prefetchAhead = React.useCallback((currentSong) => {
    if (!currentSong) return;
    const idx = filteredSongs.findIndex(s => s.spotifyId === currentSong.spotifyId);
    for (let i = 1; i <= 4; i++) {
      const next = filteredSongs[(idx + i) % filteredSongs.length];
      if (next) {
        try {
          if (localStorage.getItem('zdz_' + next.spotifyId) === null) {
            window.getZenePreviewUrl(next.spotifyId, next.artist, next.title);
          }
        } catch(e) {
          window.getZenePreviewUrl(next.spotifyId, next.artist, next.title);
        }
      }
    }
  }, [filteredSongs]);

  React.useEffect(() => {
    if (!song) return;
    setPlaying(false);
    setRevealed(false);
    setLoading(true);
    setPreviewUrl(null);
    advancedRef.current = false;
    if (audioRef.current) { audioRef.current.pause(); audioRef.current.src = ''; }

    const skip = () => {
      if (!advancedRef.current) {
        advancedRef.current = true;
        onAdvance && onAdvance({}, {});
        setTimeout(() => { onCommit && onCommit(); }, 50);
      }
    };
    var alreadyCached = false;
    try { alreadyCached = localStorage.getItem('zdz_' + song.spotifyId) !== null; } catch(e) {}
    const skipTimer = setTimeout(skip, alreadyCached ? 2500 : 8000);

    window.getZenePreviewUrl(song.spotifyId, song.artist, song.title).then(url => {
      clearTimeout(skipTimer);
      if (url) {
        setPreviewUrl(url);
        setLoading(false);
        if (navigator.mediaSession) {
          navigator.mediaSession.metadata = new MediaMetadata({
            title: '🎵 Melyik szám ez?', artist: '???', album: 'Bottle of Heroes'
          });
        }
        // Prefetch next songs in background
        prefetchAhead(song);
      } else {
        skip();
      }
    });

    return () => {
      clearTimeout(skipTimer);
      if (audioRef.current) audioRef.current.pause();
    };
  }, [song?.spotifyId]);

  const handlePlay = () => {
    if (!audioRef.current || !previewUrl || !song) return;
    audioRef.current.currentTime = song.start || 0;
    audioRef.current.play().catch(() => {});
  };
  const handleStop = () => {
    if (!audioRef.current) return;
    audioRef.current.pause();
    setPlaying(false);
  };"""

NEW_IFRAME_STATES = """  const [playing, setPlaying] = React.useState(false);
  const [revealed, setRevealed] = React.useState(false);
  const [embedReady, setEmbedReady] = React.useState(false);
  const embedRef      = React.useRef(null);
  const controllerRef = React.useRef(null);
  const advancedRef   = React.useRef(false);

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

    const skip = () => {
      if (!advancedRef.current) {
        advancedRef.current = true;
        onAdvance && onAdvance({}, {});
        setTimeout(() => { onCommit && onCommit(); }, 50);
      }
    };
    const skipTimer = setTimeout(skip, 5000);

    const create = () => {
      if (!window._spotifyIFrameAPI || !embedRef.current) return;
      window._spotifyIFrameAPI.createController(
        embedRef.current,
        { uri: 'spotify:track:' + song.spotifyId, width: 300, height: 80 },
        (ctrl) => {
          controllerRef.current = ctrl;
          ctrl.addListener('ready', () => { clearTimeout(skipTimer); setEmbedReady(true); });
          ctrl.addListener('playback_update', (e) => {
            setPlaying(!e.data.isPaused && e.data.position > 0);
          });
        }
      );
    };

    if (window._spotifyIFrameAPI) { create(); }
    else {
      const prev = window.onSpotifyIframeApiReady;
      window.onSpotifyIframeApiReady = (api) => {
        window._spotifyIFrameAPI = api;
        if (prev) prev(api);
        create();
      };
    }

    return () => {
      clearTimeout(skipTimer);
      if (controllerRef.current) { try { controllerRef.current.pause(); } catch(e) {} }
    };
  }, [song?.spotifyId]);

  const handlePlay = () => {
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

assert OLD_AUDIO_STATES in content, "audio states not found"
content = content.replace(OLD_AUDIO_STATES, NEW_IFRAME_STATES, 1)

# ── 3. Fix handleResult ──
OLD_RESULT_PAUSE = "    if (audioRef.current) audioRef.current.pause();"
NEW_RESULT_PAUSE = "    if (controllerRef.current) { try { controllerRef.current.pause(); } catch(e) {} }"

assert OLD_RESULT_PAUSE in content, "result pause not found"
content = content.replace(OLD_RESULT_PAUSE, NEW_RESULT_PAUSE, 1)

# ── 4. Replace audio element JSX with clipped embed div ──
OLD_AUDIO_JSX = """      {previewUrl && (
        <audio ref={audioRef} src={previewUrl}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => setPlaying(false)} />
      )}

      {/* Vinyl */}"""

NEW_IFRAME_JSX = """      {/* Spotify embed — clipped to 0x0, IFrame API controls audio only */}
      <div style={{ position:'absolute', width:0, height:0, overflow:'hidden', top:0, left:0 }}>
        <div ref={embedRef} />
      </div>

      {/* Vinyl */}"""

assert OLD_AUDIO_JSX in content, "audio JSX not found"
content = content.replace(OLD_AUDIO_JSX, NEW_IFRAME_JSX, 1)

# ── 5. Fix buttons: loading → !embedReady, reveal ──
OLD_LOADING_BTN = "        {loading ? ("
NEW_READY_BTN   = "        {!embedReady ? ("

assert OLD_LOADING_BTN in content, "loading btn not found"
content = content.replace(OLD_LOADING_BTN, NEW_READY_BTN, 1)

OLD_LOADING_REVEAL = "        {!loading && (!revealed"
NEW_READY_REVEAL   = "        {embedReady && (!revealed"

assert OLD_LOADING_REVEAL in content, "loading reveal not found"
content = content.replace(OLD_LOADING_REVEAL, NEW_READY_REVEAL, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.128 ready")
