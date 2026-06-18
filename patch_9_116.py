#!/usr/bin/env python3
"""patch_9_116.py — Deep debug: show token status + raw API response for first batch"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.115';" in content
content = content.replace("const APP_VERSION = 'v9.115';", "const APP_VERSION = 'v9.116';")

# ── 1. Add debugLog state ──
OLD_SHOW_DEBUG = "  const [showDebug, setShowDebug] = React.useState(false);"
NEW_SHOW_DEBUG = """  const [showDebug, setShowDebug] = React.useState(false);
  const [debugLog, setDebugLog] = React.useState([]);"""

assert OLD_SHOW_DEBUG in content
content = content.replace(OLD_SHOW_DEBUG, NEW_SHOW_DEBUG, 1)

# ── 2. Replace batch effect with detailed debug version ──
OLD_BATCH_EFFECT = """  React.useEffect(() => {
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

NEW_BATCH_EFFECT = """  React.useEffect(() => {
    if (previewMap !== null) return;
    const logs = [];
    const log = (msg) => { logs.push(msg); setDebugLog([...logs]); };
    const allIds = ZENE_SONGS.map(s => s.spotifyId);
    const BATCH = 50;
    const map = {};
    let i = 0;

    // Step 1: get token and log result
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

assert OLD_BATCH_EFFECT in content, "batch effect not found"
content = content.replace(OLD_BATCH_EFFECT, NEW_BATCH_EFFECT, 1)

# ── 3. Show debugLog on check screen ──
OLD_CHECK_PCT_BAR = """        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:T.mint }}>{checkPct}%</div>
        {checkPct === 100 && (
          <button onClick={() => setShowDebug(true)} style={{
            padding:'10px 20px', borderRadius:12, border:'none', background:'#1B2340', color:'#fff',
            fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer'
          }}>🔍 Debug: previewMap megtekintése</button>
        )}"""

NEW_CHECK_PCT_BAR = """        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:T.mint }}>{checkPct}%</div>
        {checkPct === 100 && (
          <button onClick={() => setShowDebug(true)} style={{
            padding:'10px 20px', borderRadius:12, border:'none', background:'#1B2340', color:'#fff',
            fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer'
          }}>🔍 Debug: previewMap megtekintése</button>
        )}
        {debugLog.length > 0 && (
          <div style={{ width:'100%', background:'#0d1117', borderRadius:10, padding:'10px 12px', maxHeight:300, overflowY:'auto' }}>
            {debugLog.map((line, i) => (
              <div key={i} style={{ fontFamily:'monospace', fontSize:11, color:'#58a6ff', marginBottom:2 }}>{line}</div>
            ))}
          </div>
        )}"""

assert OLD_CHECK_PCT_BAR in content, "check pct bar not found"
content = content.replace(OLD_CHECK_PCT_BAR, NEW_CHECK_PCT_BAR, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.116 ready")
