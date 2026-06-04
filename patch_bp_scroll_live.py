with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# Fix 1: scroll — add minHeight:0 to the scroll container
old = "      <div style={{ flex:1, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'8px 16px 24px', display:'flex', flexDirection:'column', gap:12 }}>"
new = "      <div style={{ flex:1, minHeight:0, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'8px 16px 24px', display:'flex', flexDirection:'column', gap:12 }}>"
assert old in html, "scroll container not found"
html = html.replace(old, new, 1)

# Fix 2: Current match card — add live score + pulse animation
old = '''        {/* Current match */}
        {isBP && curMatch && curMatch.p1 && curMatch.p2 && !bp.champion && (
          <div style={{ background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:'14px 14px' }}>
            <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:10 }}>⚡ Aktuális meccs</div>
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <PlayerChip p={curMatch.p1} highlight />
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.inkSoft, flexShrink:0 }}>VS</div>
              <PlayerChip p={curMatch.p2} highlight />
            </div>
          </div>
        )}'''

new = '''        {/* Current match */}
        {isBP && curMatch && curMatch.p1 && curMatch.p2 && !bp.champion && (
          <div style={{ background:T.surface, borderRadius:18, boxShadow:`0 0 0 2px ${T.mint}40, ${T.shadow}`, padding:'14px 14px' }}>
            <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:10 }}>
              <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>⚡ Aktuális meccs</div>
              <div style={{ display:'flex', alignItems:'center', gap:5 }}>
                <span style={{ width:7, height:7, borderRadius:'50%', background:'#E03A3A', animation:'pulse 1.4s infinite' }}/>
                <span style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:'#E03A3A', letterSpacing:'0.08em' }}>ÉLŐ</span>
              </div>
            </div>
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <PlayerChip p={curMatch.p1} highlight />
              {curMatch.score ? (
                <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:2, flexShrink:0 }}>
                  <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:22, color:T.ink, lineHeight:1 }}>
                    {curMatch.score.p1}<span style={{ color:T.inkMute, fontSize:16 }}> – </span>{curMatch.score.p2}
                  </div>
                  <div style={{ fontFamily:T.font, fontSize:9, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.06em' }}>pohár</div>
                </div>
              ) : (
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.inkSoft, flexShrink:0 }}>VS</div>
              )}
              <PlayerChip p={curMatch.p2} highlight />
            </div>
          </div>
        )}'''

assert old in html, "current match block not found"
html = html.replace(old, new, 1)

assert html != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("done")
