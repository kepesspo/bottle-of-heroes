#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. LeaderRow: add egység after drinks count (for Állás tab)
old = """      {showScores && <div style={{ position:'relative', display:'flex', alignItems:'center', gap:4, color:T.coral }}>{Icon.beer(T.coral)}<div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, fontVariantNumeric:'tabular-nums', color:T.ink }}>{p.drinks}</div></div>}"""
new = """      {showScores && <div style={{ position:'relative', display:'flex', alignItems:'center', gap:6, color:T.coral }}>
        {Icon.beer(T.coral)}
        <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, fontVariantNumeric:'tabular-nums', color:T.ink }}>{p.drinks}</div>
        {p.drinks > 0 && <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkMute, lineHeight:1 }}>~{(p.drinks*0.2).toFixed(1)}e</div>}
      </div>}"""
assert old in html, "FAIL: LeaderRow drinks"
html = html.replace(old, new, 1)

# ── 2. EndScreen: add ital egység szekció after Full leaderboard
old = """        {/* Full leaderboard */}
        <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
          {sorted.map((p,i) => <LeaderRow key={p.id} p={p} rank={i+1} maxScore={maxScore} />)}
        </div>
      </div>"""
new = """        {/* Full leaderboard */}
        <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
          {sorted.map((p,i) => <LeaderRow key={p.id} p={p} rank={i+1} maxScore={maxScore} />)}
        </div>

        {/* Ital egység kalkulátor */}
        {players.some(p => p.drinks > 0) && (
          <div style={{ background:T.surface, borderRadius:16, boxShadow:T.shadow, overflow:'hidden' }}>
            <div style={{ height:4, background:T.coral }} />
            <div style={{ padding:'14px 16px', display:'flex', flexDirection:'column', gap:10 }}>
              <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                <span style={{ fontSize:18 }}>🍺</span>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Becsült alkohol egységek</div>
              </div>
              {[...players].sort((a,b)=>b.drinks-a.drinks).map(p => {
                const units = +(p.drinks * 0.2).toFixed(1);
                const barPct = Math.min(100, (p.drinks / Math.max(1, ...players.map(x=>x.drinks))) * 100);
                const color = units < 2 ? T.mint : units < 4 ? T.yellow : T.coral;
                return (
                  <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10 }}>
                    <div style={{ width:28, height:28, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', flexShrink:0 }}>{p.name.charAt(0).toUpperCase()}</div>
                    <div style={{ flex:1, minWidth:0 }}>
                      <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink, marginBottom:3 }}>{p.name}</div>
                      <div style={{ height:6, borderRadius:3, background:T.surfaceMuted, overflow:'hidden' }}>
                        <div style={{ height:'100%', width:`${barPct}%`, background:color, borderRadius:3, transition:'width .6s cubic-bezier(.2,.9,.3,1)' }} />
                      </div>
                    </div>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color, flexShrink:0 }}>~{units}e</div>
                  </div>
                );
              })}
              <div style={{ marginTop:4, padding:'10px 12px', background:`${T.coral}12`, borderRadius:10, borderLeft:`3px solid ${T.coral}` }}>
                <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, lineHeight:1.55 }}>
                  ⚠️ <strong style={{ color:T.ink }}>Csak becslés.</strong> 1 korty ≈ 0.5 dl sör ≈ 0.2 egység. Nem orvosi tanács — igyál vizet és felelősen!
                </div>
              </div>
            </div>
          </div>
        )}
      </div>"""
assert old in html, "FAIL: EndScreen leaderboard anchor"
html = html.replace(old, new, 1)

# ── version bump
old_v = "const APP_VERSION = 'v9.271';"
new_v = "const APP_VERSION = 'v9.272';"
assert old_v in html, "FAIL: version"
html = html.replace(old_v, new_v, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.272 — ital egység kalkulátor EndScreen + LeaderRow")
