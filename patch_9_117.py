#!/usr/bin/env python3
"""patch_9_117.py — Switch to iTunes Search API for previews (Spotify removed preview_url globally)"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.116';" in content
content = content.replace("const APP_VERSION = 'v9.116';", "const APP_VERSION = 'v9.117';")

# ── 1. Replace checkZeneBatch with iTunes-based checker ──
OLD_CC_BLOCK = """  // iTunes Search API — ingyenes, nincs auth, CORS-friendly, 30mp M4A preview
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
  };

  // Batch ellenőrzés: 50 track egyszerre — visszaadja {id: previewUrl}
  window.checkZeneBatch = function(ids) {
    return window.getSpotifyCCToken().then(function(token) {
      if (!token) return {};
      return fetch('https://api.spotify.com/v1/tracks?ids=' + ids.join(','), {
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

NEW_ITUNES_BLOCK = """  // iTunes Search API — ingyenes, nincs auth, CORS-friendly, 30mp AAC preview
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

assert OLD_CC_BLOCK in content, "CC block not found"
content = content.replace(OLD_CC_BLOCK, NEW_ITUNES_BLOCK, 1)

# ── 2. Update batch effect: pass {spotifyId, artist, title} objects, use new localStorage key ──
OLD_BATCH_CALL = """    // Step 1: get token and log result
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

NEW_BATCH_CALL = """    // iTunes alapú ellenőrzés: 5 párhuzamos kérés egyszerre
    log('🎵 iTunes Search API ellenőrzés indul (' + allIds.length + ' dal)...');
    const allSongs = ZENE_SONGS.map(s => ({ spotifyId: s.spotifyId, artist: s.artist, title: s.title }));
    const CONCURRENT = 5;
    const next = () => {
      if (i >= allSongs.length) {
        log('🏁 Kész: ' + Object.keys(map).length + ' / ' + allSongs.length + ' dalnak van iTunes preview');
        if (Object.keys(map).length === 0) {
          try { localStorage.removeItem('zene_preview_map_v2'); } catch(e) {}
        } else {
          try { localStorage.setItem('zene_preview_map_v2', JSON.stringify(map)); } catch(e) {}
        }
        setPreviewMap(map);
        return;
      }
      setCheckPct(Math.round(i / allSongs.length * 100));
      const batch = allSongs.slice(i, i + CONCURRENT);
      window.checkZeneBatch(batch).then(res => {
        const found = Object.keys(res).length;
        if (found > 0) log('  ✅ ' + i + '-' + (i+CONCURRENT) + ': ' + found + ' preview');
        Object.assign(map, res);
        i += CONCURRENT;
        setTimeout(next, 200);
      });
    };
    next();
  }, []);"""

assert OLD_BATCH_CALL in content, "batch call not found"
content = content.replace(OLD_BATCH_CALL, NEW_BATCH_CALL, 1)

# ── 3. Update localStorage key in useState init ──
OLD_LS_KEY = "      const s = localStorage.getItem('zene_preview_map_v1');"
NEW_LS_KEY = "      const s = localStorage.getItem('zene_preview_map_v2');"

assert OLD_LS_KEY in content, "localStorage key not found"
content = content.replace(OLD_LS_KEY, NEW_LS_KEY, 1)

# ── 4. Update allIds variable name (now we use allSongs) ──
OLD_ALL_IDS = "    const allIds = ZENE_SONGS.map(s => s.spotifyId);"
NEW_ALL_IDS = "    const allIds = ZENE_SONGS.map(s => s.spotifyId); // used for length only"

assert OLD_ALL_IDS in content, "allIds not found"
content = content.replace(OLD_ALL_IDS, NEW_ALL_IDS, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.117 ready")
