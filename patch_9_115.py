#!/usr/bin/env python3
"""patch_9_115.py — Add debug overlay: show previewMap result after batch check"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.114';" in content
content = content.replace("const APP_VERSION = 'v9.114';", "const APP_VERSION = 'v9.115';")

# ── 1. Add showDebug state after checkPct ──
OLD_CHECK_PCT = "  const [checkPct, setCheckPct] = React.useState(0);"
NEW_CHECK_PCT = """  const [checkPct, setCheckPct] = React.useState(0);
  const [showDebug, setShowDebug] = React.useState(false);"""

assert OLD_CHECK_PCT in content
content = content.replace(OLD_CHECK_PCT, NEW_CHECK_PCT, 1)

# ── 2. Replace check screen with debug-capable version ──
OLD_CHECK_SCREEN = """  // Ellenőrzés képernyő
  if (previewMap === null) { // check screen
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
    );"""

NEW_CHECK_SCREEN = """  // Debug overlay
  if (showDebug && previewMap !== null) {
    const entries = Object.entries(previewMap);
    return (
      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8, padding:'12px 0' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink }}>
          🔍 Debug: {entries.length} dal / {ZENE_SONGS.length} kapott preview URL-t
        </div>
        <button onClick={() => setShowDebug(false)} style={{
          padding:'8px 16px', borderRadius:10, border:'none', background:T.mint, color:'#fff',
          fontFamily:T.font, fontWeight:700, fontSize:13, cursor:'pointer', alignSelf:'flex-start'
        }}>← Vissza a játékhoz</button>
        <div style={{ width:'100%', height:1, background:T.surfaceMuted, margin:'4px 0' }} />
        {entries.length === 0 ? (
          <div style={{ fontFamily:T.font, fontSize:14, color:'#c0392b', fontWeight:700 }}>
            ⚠️ Egyetlen dalnál sem érkezett vissza preview_url a Spotify API-tól!
          </div>
        ) : (
          <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
            {entries.map(([id, url]) => {
              const song = ZENE_SONGS.find(s => s.spotifyId === id);
              return (
                <div key={id} style={{ background:T.surfaceMuted, borderRadius:8, padding:'8px 10px' }}>
                  <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink }}>
                    {song ? song.artist + ' — ' + song.title : id}
                  </div>
                  <div style={{ fontFamily:'monospace', fontSize:10, color:T.inkSoft, wordBreak:'break-all', marginTop:2 }}>
                    {url}
                  </div>
                  <audio controls src={url} style={{ width:'100%', marginTop:4, height:28 }} />
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  }

  // Ellenőrzés képernyő
  if (previewMap === null) { // check screen
    return (
      <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'20px 0' }}>
        <div style={{ fontSize:40 }}>🎵</div>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, textAlign:'center' }}>Zenék előkészítése...</div>
        <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>Egyszer szükséges — ellenőrzöm melyik dalnak van preview</div>
        <div style={{ width:'100%', height:8, borderRadius:8, background:T.surfaceMuted, overflow:'hidden' }}>
          <div style={{ height:'100%', borderRadius:8, background:T.mint, width: checkPct + '%', transition:'width .3s' }} />
        </div>
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:T.mint }}>{checkPct}%</div>
        {checkPct === 100 && (
          <button onClick={() => setShowDebug(true)} style={{
            padding:'10px 20px', borderRadius:12, border:'none', background:'#1B2340', color:'#fff',
            fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer'
          }}>🔍 Debug: previewMap megtekintése</button>
        )}
      </div>
    );"""

assert OLD_CHECK_SCREEN in content, "check screen not found"
content = content.replace(OLD_CHECK_SCREEN, NEW_CHECK_SCREEN, 1)

# ── 3. After game renders, add a small debug button in corner ──
OLD_GAME_RETURN = """  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:10 }}>"""

NEW_GAME_RETURN = """  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:10 }}>
      {previewMap && <button onClick={() => setShowDebug(true)} style={{
        alignSelf:'flex-end', padding:'4px 10px', borderRadius:8, border:'1px solid ' + T.surfaceMuted,
        background:'transparent', fontFamily:T.font, fontSize:10, color:T.inkSoft, cursor:'pointer'
      }}>🔍 {Object.keys(previewMap).length} preview</button>}"""

assert OLD_GAME_RETURN in content, "game return not found"
content = content.replace(OLD_GAME_RETURN, NEW_GAME_RETURN, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.115 ready")
