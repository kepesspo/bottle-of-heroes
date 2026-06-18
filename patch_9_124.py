#!/usr/bin/env python3
"""patch_9_124.py — ZeneGame: fetch preview URL from Spotify embed page via CORS proxy,
use own <audio> element + MediaSession metadata hiding (shows ??? instead of song name)"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.123';" in content
content = content.replace("const APP_VERSION = 'v9.123';", "const APP_VERSION = 'v9.124';")

# ── 1. Replace iTunes + Spotify CC block with corsproxy → Spotify embed scraper ──
OLD_ITUNES_BLOCK = """  // iTunes Search API — ingyenes, nincs auth, CORS-friendly, 30mp AAC preview
  // Spotify eltávolította a preview_url-t 2023 végén, ezért iTunes-ra váltunk
  window.fetchItunesPreviewBySpotifyId = function(spotifyId, artist, title) {
    var query = encodeURIComponent(artist + ' ' + title);
    return fetch('https://itunes.apple.com/search?term=' + query + '&media=music&entity=song&limit=5&country=US')
      .then(function(r) { return r.json(); })
      .then(function(d) {
        var results = d.results || [];
        for (var i = 0; i < results.length; i++) {
          if (results[i].previewUrl) return { id: spotifyId, url: results[i].previewUrl };
        }
        return null;
      })
      .catch(function() { return null; });
  };

  // Párhuzamos iTunes ellenőrzés: 5 egyszerre
  window.checkZeneBatch = function(songs) {
    // songs: [{spotifyId, artist, title}, ...]
    var results = {};
    var promises = songs.map(function(s) {
      return window.fetchItunesPreviewBySpotifyId(s.spotifyId, s.artist, s.title)
        .then(function(r) { if (r) results[r.id] = r.url; });
    });
    return Promise.all(promises).then(function() { return results; });
  };

  // Keep getSpotifyCCToken for potential other uses
  var _ccToken = null, _ccExpiry = 0, _ccFetching = null;
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
  };"""

NEW_PREVIEW_BLOCK = """  // Spotify embed scraper: corsproxy.io → open.spotify.com/embed/track/{id}
  // Extracts p.scdn.co preview URL from the embed page HTML
  var _previewCache = {};
  window.getSpotifyPreviewUrl = function(spotifyId) {
    if (_previewCache[spotifyId] !== undefined) return Promise.resolve(_previewCache[spotifyId]);
    var embedUrl = 'https://open.spotify.com/embed/track/' + spotifyId;
    var proxyUrl = 'https://corsproxy.io/?' + encodeURIComponent(embedUrl);
    return fetch(proxyUrl, { signal: AbortSignal.timeout ? AbortSignal.timeout(8000) : undefined })
      .then(function(r) { return r.text(); })
      .then(function(html) {
        var patterns = [
          /"audioPreview"\s*:\s*\{\s*"url"\s*:\s*"(https:\/\/p\.scdn\.co\/[^"]+)"/,
          /"preview_url"\s*:\s*"(https:\/\/p\.scdn\.co\/[^"]+)"/,
          /(https:\/\/p\.scdn\.co\/mp3-preview\/[a-f0-9]+[^"\\s]*)/
        ];
        for (var i = 0; i < patterns.length; i++) {
          var m = html.match(patterns[i]);
          if (m) { _previewCache[spotifyId] = m[1]; return m[1]; }
        }
        _previewCache[spotifyId] = null;
        return null;
      })
      .catch(function() { _previewCache[spotifyId] = null; return null; });
  };"""

assert OLD_ITUNES_BLOCK in content, "iTunes block not found"
content = content.replace(OLD_ITUNES_BLOCK, NEW_PREVIEW_BLOCK, 1)

# ── 2. Replace entire ZeneGame with audio-element based version ──
# Replace the IFrame-based states + effect with audio-based ones

OLD_AUDIO_STATES = """  const [playing, setPlaying] = React.useState(false);
  const [revealed, setRevealed] = React.useState(false);
  const [embedReady, setEmbedReady] = React.useState(false);
  const embedRef     = React.useRef(null);
  const controllerRef = React.useRef(null);
  const advancedRef  = React.useRef(false);

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
    const skipTimer = setTimeout(() => {
      if (!advancedRef.current) {
        advancedRef.current = true;
        onAdvance && onAdvance({}, {});
        setTimeout(() => { onCommit && onCommit(); }, 50);
      }
    }, 2500);
    const create = () => {
      if (!window._spotifyIFrameAPI || !embedRef.current) return;
      window._spotifyIFrameAPI.createController(embedRef.current, { uri, width: 300, height: 80 }, (ctrl) => {
        controllerRef.current = ctrl;
        ctrl.addListener('ready', () => { clearTimeout(skipTimer); setEmbedReady(true); });
        ctrl.addListener('playback_update', (e) => {
          setPlaying(!e.data.isPaused && e.data.position > 0);
        });
      });
    };
    if (window._spotifyIFrameAPI) { create(); }
    else {
      const prev = window.onSpotifyIframeApiReady;
      window.onSpotifyIframeApiReady = (api) => { window._spotifyIFrameAPI = api; if (prev) prev(api); create(); };
    }
    return () => { clearTimeout(skipTimer); if (controllerRef.current) { try { controllerRef.current.pause(); } catch(e) {} } };
  }, [song?.spotifyId]);

  const handlePlay = () => {
    if (!controllerRef.current) return;
    try { controllerRef.current.seek(((song?.start) || 0) * 1000); controllerRef.current.play(); } catch(e) {}
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

    const skip = () => {
      if (!advancedRef.current) {
        advancedRef.current = true;
        onAdvance && onAdvance({}, {});
        setTimeout(() => { onCommit && onCommit(); }, 50);
      }
    };
    const skipTimer = setTimeout(skip, 2500);

    window.getSpotifyPreviewUrl(song.spotifyId).then(url => {
      clearTimeout(skipTimer);
      if (url) {
        setPreviewUrl(url);
        setLoading(false);
        // Hide song info from OS media controls
        if (navigator.mediaSession) {
          navigator.mediaSession.metadata = new MediaMetadata({
            title: '🎵 Melyik szám ez?',
            artist: '???',
            album: 'Bottle of Heroes'
          });
        }
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

assert OLD_AUDIO_STATES in content, "audio states not found"
content = content.replace(OLD_AUDIO_STATES, NEW_AUDIO_STATES, 1)

# ── 3. Fix handleResult: controllerRef → audioRef ──
OLD_HANDLE_RESULT = "    if (controllerRef.current) { try { controllerRef.current.pause(); } catch(e) {} }"
NEW_HANDLE_RESULT = "    if (audioRef.current) audioRef.current.pause();"

assert OLD_HANDLE_RESULT in content, "handleResult not found"
content = content.replace(OLD_HANDLE_RESULT, NEW_HANDLE_RESULT, 1)

# ── 4. Replace embed div + buttons with audio element ──
OLD_EMBED_DIV = """      {/* Spotify Embed IFrame — invisible, audio only, IFrame API controls it */}
      <div ref={embedRef} style={{ position:'fixed', left:'-9999px', top:'-9999px', width:300, height:80 }} />

      {/* Vinyl */}"""

NEW_AUDIO_EL = """      {previewUrl && (
        <audio ref={audioRef} src={previewUrl}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => setPlaying(false)} />
      )}

      {/* Vinyl */}"""

assert OLD_EMBED_DIV in content, "embed div not found"
content = content.replace(OLD_EMBED_DIV, NEW_AUDIO_EL, 1)

# ── 5. Fix buttons: embedReady → !loading ──
OLD_EMBED_READY_BTN = "        {!embedReady ? ("
NEW_LOADING_BTN = "        {loading ? ("

assert OLD_EMBED_READY_BTN in content, "embedReady button not found"
content = content.replace(OLD_EMBED_READY_BTN, NEW_LOADING_BTN, 1)

OLD_EMBED_READY_REVEAL = "        {embedReady && (!revealed"
NEW_LOADING_REVEAL = "        {!loading && (!revealed"

assert OLD_EMBED_READY_REVEAL in content, "embedReady reveal not found"
content = content.replace(OLD_EMBED_READY_REVEAL, NEW_LOADING_REVEAL, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.124 ready")
