#!/usr/bin/env python3
"""patch_9_125.py — ZeneGame: Deezer preview via allorigins.win CORS proxy, per-song cache in localStorage"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.124';" in content
content = content.replace("const APP_VERSION = 'v9.124';", "const APP_VERSION = 'v9.125';")

# ── 1. Replace corsproxy Spotify scraper with Deezer via allorigins.win ──
OLD_PREVIEW_BLOCK = """  // Spotify embed scraper: corsproxy.io → open.spotify.com/embed/track/{id}
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
          /"audioPreview"\\s*:\\s*\\{\\s*"url"\\s*:\\s*"(https:\\/\\/p\\.scdn\\.co\\/[^"]+)"/,
          /"preview_url"\\s*:\\s*"(https:\\/\\/p\\.scdn\\.co\\/[^"]+)"/,
          /(https:\\/\\/p\\.scdn\\.co\\/mp3-preview\\/[a-f0-9]+[^"\\\\s]*)/
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

NEW_DEEZER_BLOCK = """  // Deezer preview via allorigins.win CORS proxy
  // Deezer CDN URLs never expire, CORS-enabled, 30s MP3
  var _deezerMemCache = {};
  window.getZenePreviewUrl = function(spotifyId, artist, title) {
    // 1. Memory cache
    if (_deezerMemCache[spotifyId] !== undefined) return Promise.resolve(_deezerMemCache[spotifyId]);
    // 2. localStorage cache
    try {
      var lsKey = 'zdz_' + spotifyId;
      var cached = localStorage.getItem(lsKey);
      if (cached !== null) { _deezerMemCache[spotifyId] = cached || null; return Promise.resolve(cached || null); }
    } catch(e) {}
    // 3. Fetch from Deezer via allorigins.win
    var q = encodeURIComponent('artist:"' + artist + '" track:"' + title + '"');
    var deezerUrl = 'https://api.deezer.com/search?q=' + q + '&limit=3';
    var proxyUrl = 'https://api.allorigins.win/raw?url=' + encodeURIComponent(deezerUrl);
    return fetch(proxyUrl)
      .then(function(r) { return r.json(); })
      .then(function(d) {
        var items = d.data || [];
        var url = null;
        for (var i = 0; i < items.length; i++) {
          if (items[i].preview) { url = items[i].preview; break; }
        }
        _deezerMemCache[spotifyId] = url;
        try { localStorage.setItem('zdz_' + spotifyId, url || ''); } catch(e) {}
        return url;
      })
      .catch(function() { _deezerMemCache[spotifyId] = null; return null; });
  };"""

assert OLD_PREVIEW_BLOCK in content, "preview block not found"
content = content.replace(OLD_PREVIEW_BLOCK, NEW_DEEZER_BLOCK, 1)

# ── 2. Update ZeneGame useEffect to call getZenePreviewUrl with artist+title ──
OLD_GET_PREVIEW = "    window.getSpotifyPreviewUrl(song.spotifyId).then(url => {"
NEW_GET_PREVIEW = "    window.getZenePreviewUrl(song.spotifyId, song.artist, song.title).then(url => {"

assert OLD_GET_PREVIEW in content, "getSpotifyPreviewUrl call not found"
content = content.replace(OLD_GET_PREVIEW, NEW_GET_PREVIEW, 1)

# ── 3. Increase skip timeout: 5s for first fetch (uncached), 2.5s if cached ──
OLD_SKIP_TIMER = "    const skipTimer = setTimeout(skip, 2500);"
NEW_SKIP_TIMER = """    // Cached songs load instantly; uncached need up to 5s for network fetch
    var alreadyCached = false;
    try { alreadyCached = localStorage.getItem('zdz_' + song.spotifyId) !== null; } catch(e) {}
    const skipTimer = setTimeout(skip, alreadyCached ? 2500 : 5000);"""

assert OLD_SKIP_TIMER in content, "skip timer not found"
content = content.replace(OLD_SKIP_TIMER, NEW_SKIP_TIMER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.125 ready")
