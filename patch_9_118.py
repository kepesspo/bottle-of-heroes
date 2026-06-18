#!/usr/bin/env python3
"""patch_9_118.py — iTunes raw debug: show full response for first song"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.117';" in content
content = content.replace("const APP_VERSION = 'v9.117';", "const APP_VERSION = 'v9.118';")

# Replace the iTunes batch call with a focused single-song debug first
OLD_BATCH_CALL = """    // iTunes alapú ellenőrzés: 5 párhuzamos kérés egyszerre
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
    next();"""

NEW_BATCH_CALL = """    // iTunes debug: először egyetlen dal keresése raw válasszal
    const allSongs = ZENE_SONGS.map(s => ({ spotifyId: s.spotifyId, artist: s.artist, title: s.title }));
    const testSong = allSongs[0];
    const testQuery = encodeURIComponent(testSong.artist + ' ' + testSong.title);
    const testUrl = 'https://itunes.apple.com/search?term=' + testQuery + '&media=music&entity=song&limit=3&country=US';
    log('🎵 Teszt: ' + testSong.artist + ' — ' + testSong.title);
    log('🔗 URL: ' + testUrl.substring(0, 80));
    fetch(testUrl)
      .then(function(r) {
        log('📡 HTTP: ' + r.status + ' ' + r.statusText);
        return r.json();
      })
      .then(function(d) {
        log('📦 resultCount: ' + (d.resultCount || 0));
        var results = d.results || [];
        if (results.length === 0) {
          log('❌ Nincs találat!');
        } else {
          results.forEach(function(r, idx) {
            log('[' + idx + '] ' + (r.artistName||'?') + ' — ' + (r.trackName||'?'));
            log('    previewUrl: ' + (r.previewUrl ? '✅ ' + r.previewUrl.substring(0,50) : '❌ null/undefined'));
          });
        }
        // Now test with "Bohemian Rhapsody" as known control
        return fetch('https://itunes.apple.com/search?term=Bohemian+Rhapsody+Queen&media=music&entity=song&limit=2&country=US');
      })
      .then(function(r2) { return r2.json(); })
      .then(function(d2) {
        log('--- Bohemian Rhapsody kontroll ---');
        (d2.results||[]).forEach(function(r, idx) {
          log('[' + idx + '] previewUrl: ' + (r.previewUrl ? '✅ ' + r.previewUrl.substring(0,50) : '❌ null'));
        });
        log('✅ Debug kész. Teljes ellenőrzés indul...');
        // Full batch
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
            if (found > 0) log('  ✅ ' + i + ': ' + found + ' preview');
            Object.assign(map, res);
            i += CONCURRENT;
            setTimeout(next, 200);
          });
        };
        next();
      })
      .catch(function(e) {
        log('❌ HIBA: ' + e.message + ' (CORS blokk?)');
        setPreviewMap({});
      });"""

assert OLD_BATCH_CALL in content, "batch call not found"
content = content.replace(OLD_BATCH_CALL, NEW_BATCH_CALL, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.118 ready")
