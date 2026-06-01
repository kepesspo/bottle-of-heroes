import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. ImposztorGame reveal phase: replace progress chips with Lóverseny pill ─
OLD_REVEAL_CHIPS = """        {/* Progress chips */}
        <div style={{ display:'flex', gap:8, flexWrap:'wrap', justifyContent:'center' }}>
          {players.map((p, i) => {
            const done = i < revealStep;
            const active = i === revealStep;
            return (
              <div key={p.id} style={{ position:'relative', width:44, height:44, borderRadius:'50%', background: active ? p.color : done ? p.color : T.surfaceMuted, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:18, color: active||done ? '#fff' : T.inkMute, opacity: active ? 1 : done ? 0.75 : 0.45, border: active ? `3px solid ${p.color}` : '2px solid transparent', boxShadow: active ? `0 0 0 3px rgba(255,255,255,0.5)` : 'none', transition:'all .2s' }}>
                {p.name.charAt(0).toUpperCase()}
                {done && <div style={{ position:'absolute', bottom:-2, right:-2, width:16, height:16, borderRadius:'50%', background:'#50A882', border:'1.5px solid #fff', display:'grid', placeItems:'center', fontSize:9, color:'#fff', fontWeight:700 }}>✓</div>}
              </div>
            );
          })}
        </div>
        <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>
          Szerepek — {revealStep+1}/{players.length}
        </div>"""

NEW_REVEAL_PILL = """        {/* Player turn indicator */}
        <div style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:14, padding:'10px 14px', boxShadow:T.shadow, width:'100%' }}>
          <div style={{ width:36, height:36, borderRadius:'50%', background:pl.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>
            {pl.name.charAt(0).toUpperCase()}
          </div>
          <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink }}>
            {pl.name} jön
          </div>
          <div style={{ display:'flex', alignItems:'center', gap:3 }}>
            {players.map((p,i) => (
              <div key={p.id} style={{ width:7, height:7, borderRadius:'50%', background: i < revealStep ? T.mint : i === revealStep ? pl.color : T.inkMute+'40' }} />
            ))}
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginLeft:3 }}>{revealStep+1}/{players.length}</div>
          </div>
        </div>"""

html = html.replace(OLD_REVEAL_CHIPS, NEW_REVEAL_PILL, 1)

# ── 2. ImposztorGame vote phase: replace header with Lóverseny pill ───────────
OLD_VOTE_HEADER = """        <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em' }}>Szavazás — {voteStep+1}/{players.length}</div>
        <div style={{ display:'flex', alignItems:'center', gap:8 }}>
          <div style={{ width:34, height:34, borderRadius:'50%', background:voter.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, color:'#fff' }}>{voter.name.charAt(0).toUpperCase()}</div>
          <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink }}>{voter.name}, ki az Imposztor?</div>
        </div>"""

NEW_VOTE_PILL = """        <div style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:14, padding:'10px 14px', boxShadow:T.shadow, width:'100%' }}>
          <div style={{ width:36, height:36, borderRadius:'50%', background:voter.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>
            {voter.name.charAt(0).toUpperCase()}
          </div>
          <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink }}>
            {voter.name} szavaz
          </div>
          <div style={{ display:'flex', alignItems:'center', gap:3 }}>
            {players.map((p,i) => (
              <div key={p.id} style={{ width:7, height:7, borderRadius:'50%', background: i < voteStep ? T.mint : i === voteStep ? voter.color : T.inkMute+'40' }} />
            ))}
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginLeft:3 }}>{voteStep+1}/{players.length}</div>
          </div>
        </div>"""

html = html.replace(OLD_VOTE_HEADER, NEW_VOTE_PILL, 1)

# ── 3. Version bump ──────────────────────────────────────────────────────────
html = html.replace(
    'Verzió 5.26 · DNR · 2026.06.01 02:00',
    'Verzió 5.27 · DNR · 2026.06.01 03:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
