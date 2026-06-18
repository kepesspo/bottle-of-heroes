#!/usr/bin/env python3
"""patch_9_108.py — Switch from Spotify preview_url to iTunes Search API for previews"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.107';" in content
content = content.replace("const APP_VERSION = 'v9.107';", "const APP_VERSION = 'v9.108';")

# ── 1. Replace Spotify CC token + fetchSpotifyPreview with iTunes fetch ──
OLD_SPOTIFY_CC = """  // Client Credentials token (for preview URL lookup — no user login needed)
  var _ccToken = null;
  var _ccExpiry = 0;
  var _ccFetching = null;
  window.getSpotifyCCToken = function() {
    if (_ccToken && Date.now() < _ccExpiry) return Promise.resolve(_ccToken);
    if (_ccFetching) return _ccFetching;
    _ccFetching = fetch('https://accounts.spotify.com/api/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + btoa(CLIENT_ID + ':9569e6631bd94cb9a155bc28aa49df08'),
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

  var _previewCache = {};
  window.fetchSpotifyPreview = function(trackId) {
    if (_previewCache[trackId] !== undefined) return Promise.resolve(_previewCache[trackId]);
    return window.getSpotifyCCToken().then(function(token) {
      if (!token) { _previewCache[trackId] = null; return null; }
      return fetch('https://api.spotify.com/v1/tracks/' + trackId + '?market=HU', {
        headers: { 'Authorization': 'Bearer ' + token }
      }).then(function(r) { return r.json(); }).then(function(d) {
        _previewCache[trackId] = d.preview_url || null;
        return _previewCache[trackId];
      });
    }).catch(function() { _previewCache[trackId] = null; return null; });
  };

  // Prefetch next songs in background
  window.prefetchSpotifyPreviews = function(ids) {
    ids.forEach(function(id) { window.fetchSpotifyPreview(id); });
  };"""

NEW_ITUNES = """  // iTunes Search API — ingyenes, nincs auth, CORS-friendly, 30mp M4A preview
  var _itunesCache = {};
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

assert OLD_SPOTIFY_CC in content, "Spotify CC block not found"
content = content.replace(OLD_SPOTIFY_CC, NEW_ITUNES, 1)

# ── 2. Update ZeneGame to use iTunes instead of Spotify ──────────
OLD_ZENE_EFFECT = """    window.fetchSpotifyPreview(song.spotifyId).then(url => {
      if (url) {
        setPreviewUrl(url);
        setLoading(false);
      } else {
        // No preview → auto-skip silently
        if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); }
      }
    });

    window.fetchSpotifyPreview(nextSong.spotifyId); // prefetch next"""

NEW_ZENE_EFFECT = """    window.fetchItunesPreview(song.artist, song.title).then(url => {
      if (url) {
        setPreviewUrl(url);
        setLoading(false);
      } else {
        // No preview → auto-skip silently
        if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); }
      }
    });

    window.fetchItunesPreview(nextSong.artist, nextSong.title); // prefetch next"""

assert OLD_ZENE_EFFECT in content, "ZeneGame effect not found"
content = content.replace(OLD_ZENE_EFFECT, NEW_ZENE_EFFECT, 1)

# ── 3. Update useEffect dependency from spotifyId to artist+title ─
OLD_DEP = "  }, [song.spotifyId]);"
NEW_DEP = "  }, [song.artist, song.title]);"
assert OLD_DEP in content, "useEffect dep not found"
content = content.replace(OLD_DEP, NEW_DEP, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.108 ready (iTunes previews)")
