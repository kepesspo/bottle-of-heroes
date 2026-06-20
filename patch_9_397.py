#!/usr/bin/env python3
"""v9.397 — Szűrő gombok téma-tudatos + FavTile info gomb eltávolítva"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Szűrő sheet gombok: #fff → T.surface ──────────────────────────────────
old_filter = """                  <button key={opt.key} onClick={() => toggleFilter(opt.key)} style={{
                    display:'flex', alignItems:'center', gap:12, padding:'13px 14px',
                    borderRadius:15, cursor:'pointer', border: on?'1.5px solid '+T.mint:'1.5px solid rgba(26,42,74,0.10)',
                    background: on?T.mintSoft:'#fff', width:'100%', textAlign:'left',
                  }}>"""

new_filter = """                  <button key={opt.key} onClick={() => toggleFilter(opt.key)} style={{
                    display:'flex', alignItems:'center', gap:12, padding:'13px 14px',
                    borderRadius:15, cursor:'pointer', border: on?'1.5px solid '+T.mint:'1.5px solid '+T.inkMute+'28',
                    background: on?T.mintSoft:T.surface, width:'100%', textAlign:'left',
                  }}>"""

assert old_filter in html, "FAIL: filter btns"
html = html.replace(old_filter, new_filter, 1)

# ── 2. FavTile: info gomb eltávolítása ───────────────────────────────────────
old_info_btn = """        {locked && !selected && <div style={{ fontSize:14 }}>🔒</div>}
        <button onClick={e => { e.stopPropagation(); onInfo && onInfo(); }} style={{ width:40, height:40, borderRadius:12, background:'rgba(26,42,74,0.07)', border:'none', cursor:'pointer', display:'grid', placeItems:'center', fontSize:15, color:T.inkSoft }}>ℹ</button>
      </div>
      {/* Long-press hint for busz/beerpong */}
      {onLongPress && <div style={{ position:'absolute', bottom:4, right:42, fontFamily:T.font, fontSize:11, color:T.inkMute, letterSpacing:'0.04em' }}>TARTSD A BEÁLLÍTÁSHOZ</div>}"""

new_info_btn = """        {locked && !selected && <div style={{ fontSize:14 }}>🔒</div>}
      </div>
      {/* Long-press hint for busz/beerpong */}
      {onLongPress && <div style={{ position:'absolute', bottom:4, right:6, fontFamily:T.font, fontSize:11, color:T.inkMute, letterSpacing:'0.04em' }}>TARTSD A BEÁLLÍTÁSHOZ</div>}"""

assert old_info_btn in html, "FAIL: fav info btn"
html = html.replace(old_info_btn, new_info_btn, 1)

html = html.replace("const APP_VERSION = 'v9.396';", "const APP_VERSION = 'v9.397';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.397 — Szűrő gombok javítva + FavTile info gomb eltávolítva")
