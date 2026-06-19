#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. StatsScreen scroll fix — revert wrapper, restore flex:1 overflowY
old1 = """      <div style={{ flex:1, position:'relative' }}>
        <div style={{ position:'absolute', bottom:0, left:0, right:0, height:80, background:`linear-gradient(to bottom, transparent, ${T.bg})`, pointerEvents:'none', zIndex:2 }} />
        <div style={{ height:'100%', overflowY:'auto', padding:'12px 16px 40px' }}>"""
new1 = """      <div style={{ flex:1, position:'relative' }}>
        <div style={{ position:'absolute', bottom:0, left:0, right:0, height:80, background:`linear-gradient(to bottom, transparent, ${T.bg})`, pointerEvents:'none', zIndex:2 }} />
        <div style={{ position:'absolute', inset:0, overflowY:'auto', padding:'12px 16px 40px' }}>"""
assert old1 in html, "FAIL: StatsScreen scroll"
html = html.replace(old1, new1, 1)

# Fix the extra closing div we added
old1b = """      </div>
      </div>{/* StatsScreen scroll wrapper */}
    </div>
  );
}

function HomeScreen"""
new1b = """      </div>
      </div>
    </div>
  );
}

function HomeScreen"""
assert old1b in html, "FAIL: StatsScreen close"
html = html.replace(old1b, new1b, 1)

# ── 2. PlayScreen menü — távolítsuk el a fade-et
old2 = """              <div style={{ position:'absolute', bottom:0, left:0, right:0, height:56, background:`linear-gradient(to bottom, transparent, ${T.surface})`, pointerEvents:'none', zIndex:3 }} />
            </div>{/* end tab contents wrapper */}"""
new2 = """            </div>{/* end tab contents wrapper */}"""
assert old2 in html, "FAIL: PlayScreen menu fade"
html = html.replace(old2, new2, 1)

# ── 3. SorrendTab sorok — LeaderRow stílusú, nyilak egymás mellett
old3 = """      {localOrder.map((p,i) => (
        <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 12px', borderRadius:14, background:T.bgSoft }}>
          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.inkMute, minWidth:20, textAlign:'center' }}>{i+1}</span>
          <div style={{ width:36, height:36, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, color:'#fff', flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>
          <div style={{ flex:1, fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>{p.name}</div>
          <div style={{ display:'flex', flexDirection:'column', gap:4 }}>
            <button
              onPointerDown={e => { e.stopPropagation(); moveUp(i); }}
              disabled={i===0}
              style={{ width:36, height:32, border:'none', borderRadius:8, background: i===0 ? T.surfaceMuted : T.surface, color: i===0 ? T.inkMute : T.ink, fontSize:16, cursor: i===0 ? 'default' : 'pointer', display:'grid', placeItems:'center', boxShadow: i===0 ? 'none' : '0 1px 4px rgba(0,0,0,0.15)', WebkitTapHighlightColor:'transparent' }}>▲</button>
            <button
              onPointerDown={e => { e.stopPropagation(); moveDown(i); }}
              disabled={i===localOrder.length-1}
              style={{ width:36, height:32, border:'none', borderRadius:8, background: i===localOrder.length-1 ? T.surfaceMuted : T.surface, color: i===localOrder.length-1 ? T.inkMute : T.ink, fontSize:16, cursor: i===localOrder.length-1 ? 'default' : 'pointer', display:'grid', placeItems:'center', boxShadow: i===localOrder.length-1 ? 'none' : '0 1px 4px rgba(0,0,0,0.15)', WebkitTapHighlightColor:'transparent' }}>▼</button>
          </div>
        </div>
      ))}"""
new3 = """      {localOrder.map((p,i) => (
        <div key={p.id} style={{ background:T.surface, borderRadius:14, boxShadow:T.shadow, padding:'10px 14px', display:'flex', alignItems:'center', gap:12, position:'relative', overflow:'hidden' }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:T.inkSoft, minWidth:22 }}>{i+1}</div>
          <div style={{ width:36, height:36, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', color:'#fff', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>
          <div style={{ flex:1, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:15, color:T.ink }}>{p.name}</div>
          <div style={{ display:'flex', gap:4 }}>
            <button
              onPointerDown={e => { e.stopPropagation(); moveUp(i); }}
              disabled={i===0}
              style={{ width:34, height:34, border:'none', borderRadius:8, background: i===0 ? T.surfaceMuted : T.bgSoft, color: i===0 ? T.inkMute : T.ink, fontSize:16, cursor: i===0 ? 'default' : 'pointer', display:'grid', placeItems:'center', WebkitTapHighlightColor:'transparent' }}>▲</button>
            <button
              onPointerDown={e => { e.stopPropagation(); moveDown(i); }}
              disabled={i===localOrder.length-1}
              style={{ width:34, height:34, border:'none', borderRadius:8, background: i===localOrder.length-1 ? T.surfaceMuted : T.bgSoft, color: i===localOrder.length-1 ? T.inkMute : T.ink, fontSize:16, cursor: i===localOrder.length-1 ? 'default' : 'pointer', display:'grid', placeItems:'center', WebkitTapHighlightColor:'transparent' }}>▼</button>
          </div>
        </div>
      ))}"""
assert old3 in html, "FAIL: SorrendTab rows"
html = html.replace(old3, new3, 1)

html = html.replace("const APP_VERSION = 'v9.295';", "const APP_VERSION = 'v9.296';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.296 — StatsScreen scroll fix, PlayScreen fade eltávolítva, SorrendTab LeaderRow stílus + vízszintes nyilak")
