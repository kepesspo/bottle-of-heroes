#!/usr/bin/env python3
"""patch_9_131.py — ZeneGame: Deezer JSONP (no CORS proxy needed) + localStorage cache"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.130';" in content
content = content.replace("const APP_VERSION = 'v9.130';", "const APP_VERSION = 'v9.131';")

# ── 1. Replace IFrame comment with Deezer JSONP fetcher ──
OLD_COMMENT = """  // Spotify IFrame API used for ZeneGame audio (see onSpotifyIframeApiReady above)"""

NEW_DEEZER_JSONP = """  // Deezer JSONP — no CORS proxy needed, works in any browser
  var _dzCache = {};
  window.getZenePreviewUrl = function(spotifyId, artist, title) {
    if (_dzCache[spotifyId] !== undefined) return Promise.resolve(_dzCache[spotifyId]);
    try {
      var ls = localStorage.getItem('zdz_' + spotifyId);
      if (ls !== null) { _dzCache[spotifyId] = ls || null; return Promise.resolve(ls || null); }
    } catch(e) {}
    return new Promise(function(resolve) {
      var cbName = '_dzcb_' + spotifyId.replace(/[^a-z0-9]/gi, '_');
      var q = encodeURIComponent('artist:"' + artist + '" track:"' + title + '"');
      var url = 'https://api.deezer.com/search?q=' + q + '&limit=5&output=jsonp&callback=' + cbName;
      var done = false;
      var timer = setTimeout(function() {
        if (!done) { done = true; delete window[cbName]; if (sc.parentNode) sc.parentNode.removeChild(sc); _dzCache[spotifyId] = null; resolve(null); }
      }, 6000);
      window[cbName] = function(data) {
        if (done) return; done = true; clearTimeout(timer);
        delete window[cbName]; if (sc.parentNode) sc.parentNode.removeChild(sc);
        var items = (data && data.data) ? data.data : [];
        var previewUrl = null;
        for (var i = 0; i < items.length; i++) { if (items[i].preview) { previewUrl = items[i].preview; break; } }
        _dzCache[spotifyId] = previewUrl;
        try { localStorage.setItem('zdz_' + spotifyId, previewUrl || ''); } catch(e) {}
        resolve(previewUrl);
      };
      var sc = document.createElement('script');
      sc.src = url;
      sc.onerror = function() {
        if (!done) { done = true; clearTimeout(timer); delete window[cbName]; _dzCache[spotifyId] = null; resolve(null); }
      };
      document.head.appendChild(sc);
    });
  };"""

assert OLD_COMMENT in content, "comment not found"
content = content.replace(OLD_COMMENT, NEW_DEEZER_JSONP, 1)

# ── 2. Replace IFrame-based ZeneGame states+effect with audio element + Deezer ──
OLD_IFRAME_STATES = """  const [playing, setPlaying] = React.useState(false);
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

    const skipAndBlacklist = () => {
      // Blacklist this song globally (Firestore + localStorage)
      window.markZeneBad && window.markZeneBad(song.spotifyId);
      if (!advancedRef.current) {
        advancedRef.current = true;
        onAdvance && onAdvance({}, {});
        setTimeout(() => { onCommit && onCommit(); }, 50);
      }
    };
    const skipTimer = setTimeout(skipAndBlacklist, 4000);

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

NEW_AUDIO_STATES = """  const [playing, setPlaying] = React.useState(false);
  const [revealed, setRevealed] = React.useState(false);
  const [previewUrl, setPreviewUrl] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const audioRef    = React.useRef(null);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    if (!song) return;
    setPlaying(false);
    setRevealed(false);
    setLoading(true);
    setPreviewUrl(null);
    advancedRef.current = false;
    if (audioRef.current) { audioRef.current.pause(); audioRef.current.src = ''; }

    const skipAndBlacklist = () => {
      window.markZeneBad && window.markZeneBad(song.spotifyId);
      if (!advancedRef.current) {
        advancedRef.current = true;
        onAdvance && onAdvance({}, {});
        setTimeout(() => { onCommit && onCommit(); }, 50);
      }
    };

    // Use cached entry: if already known bad, skip instantly
    var knownBad = false;
    try { knownBad = !!localStorage.getItem('znobad_' + song.spotifyId); } catch(e) {}
    if (knownBad || (window._zeneBadIds && window._zeneBadIds.has(song.spotifyId))) {
      skipAndBlacklist();
      return;
    }

    var isCached = false;
    try { isCached = localStorage.getItem('zdz_' + song.spotifyId) !== null; } catch(e) {}
    const skipTimer = setTimeout(skipAndBlacklist, isCached ? 3000 : 7000);

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
      } else {
        skipAndBlacklist();
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

assert OLD_IFRAME_STATES in content, "iframe states not found"
content = content.replace(OLD_IFRAME_STATES, NEW_AUDIO_STATES, 1)

# ── 3. Fix handleResult: controllerRef → audioRef ──
OLD_RESULT_PAUSE = "    if (controllerRef.current) { try { controllerRef.current.pause(); } catch(e) {} }"
NEW_RESULT_PAUSE = "    if (audioRef.current) audioRef.current.pause();"

assert OLD_RESULT_PAUSE in content, "result pause not found"
content = content.replace(OLD_RESULT_PAUSE, NEW_RESULT_PAUSE, 1)

# ── 4. Replace 0x0 embed div with audio element ──
OLD_EMBED_JSX = """      {/* Spotify embed — clipped to 0x0, IFrame API controls audio only */}
      <div style={{ position:'absolute', width:0, height:0, overflow:'hidden', top:0, left:0 }}>
        <div ref={embedRef} />
      </div>

      {/* Vinyl */}"""

NEW_AUDIO_JSX = """      {previewUrl && (
        <audio ref={audioRef} src={previewUrl}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => setPlaying(false)} />
      )}

      {/* Vinyl */}"""

assert OLD_EMBED_JSX in content, "embed JSX not found"
content = content.replace(OLD_EMBED_JSX, NEW_AUDIO_JSX, 1)

# ── 5. Fix buttons: !embedReady → loading ──
OLD_BTN = "        {!embedReady ? ("
NEW_BTN = "        {loading ? ("
assert OLD_BTN in content, "btn not found"
content = content.replace(OLD_BTN, NEW_BTN, 1)

OLD_REVEAL = "        {embedReady && (!revealed"
NEW_REVEAL = "        {!loading && (!revealed"
assert OLD_REVEAL in content, "reveal not found"
content = content.replace(OLD_REVEAL, NEW_REVEAL, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.131 ready")
