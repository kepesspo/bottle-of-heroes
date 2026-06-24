#!/usr/bin/env python3
"""
v9.598 — Avatar megjelenítés minden helyen:
1. 5x tap (handleSecretTap): PRESET_PLAYERS avatarral tölti be
2. Csapat footer körök: kép megjelenítés
3. Páros ellenfél kör: kép megjelenítés
4. Standings lista (Beer Pong): kép megjelenítés
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.597') >= 1
html = html.replace('v9.597', 'v9.598', 1)

# ── 1. handleSecretTap: img:null → PRESET_PLAYERS avatar ────────────────────
OLD_SECRET = "        return { id:'p'+Date.now()+i, name:p.nickname||p.name, color, drinks:0, points:0, profileId:p.id, img:null };"
NEW_SECRET = "        return { id:'p'+Date.now()+i, name:p.nickname||p.name, color: p.color||color, drinks:0, points:0, profileId:p.id, avatarId:p.avatarId||null, img:p.img||null };"
assert html.count(OLD_SECRET) == 1, f"secret: {html.count(OLD_SECRET)}"
html = html.replace(OLD_SECRET, NEW_SECRET, 1)

# ── 2. Csapat footer körök: betű → kép ──────────────────────────────────────
OLD_TEAM = """                  <div key={p.id} style={{ position:'absolute', left:i*18, top:0, width:32, height:32, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', color:'#fff', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:12, border:`2px solid ${T.surface}`, zIndex:i }}>{p.name.charAt(0).toUpperCase()}</div>"""
NEW_TEAM = """                  <div key={p.id} style={{ position:'absolute', left:i*18, top:0, width:32, height:32, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', color:'#fff', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:12, border:`2px solid ${T.surface}`, zIndex:i, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:32,height:32,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()}</div>"""
assert html.count(OLD_TEAM) == 1, f"team: {html.count(OLD_TEAM)}"
html = html.replace(OLD_TEAM, NEW_TEAM, 1)

# ── 3. Páros ellenfél kör: betű → kép ───────────────────────────────────────
OLD_OPP = """              <div style={{ position:'absolute', left:16, top:4, width:24, height:24, borderRadius:'50%', background:selectedOpponent.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:12, color:'#fff', opacity:0.85, border:`2px solid ${T.surface}`, zIndex:1 }}>{selectedOpponent.name.charAt(0).toUpperCase()}</div>"""
NEW_OPP = """              <div style={{ position:'absolute', left:16, top:4, width:24, height:24, borderRadius:'50%', background:selectedOpponent.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:12, color:'#fff', opacity:0.85, border:`2px solid ${T.surface}`, zIndex:1, overflow:'hidden' }}>{selectedOpponent.img ? <img src={selectedOpponent.img} style={{width:24,height:24,objectFit:'cover'}} /> : selectedOpponent.name.charAt(0).toUpperCase()}</div>"""
assert html.count(OLD_OPP) == 1, f"opp: {html.count(OLD_OPP)}"
html = html.replace(OLD_OPP, NEW_OPP, 1)

# ── 4. Standings (Beer Pong) lista: betű → kép ──────────────────────────────
OLD_BP_STATS = """                    <div style={{ width:40, height:40, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff', flexShrink:0, overflow:'hidden' }}>
                      {p.name.charAt(0).toUpperCase()}
                    </div>"""
NEW_BP_STATS = """                    <div style={{ width:40, height:40, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff', flexShrink:0, overflow:'hidden' }}>
                      {p.img ? <img src={p.img} style={{width:40,height:40,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()}
                    </div>"""
assert html.count(OLD_BP_STATS) == 1, f"bp stats: {html.count(OLD_BP_STATS)}"
html = html.replace(OLD_BP_STATS, NEW_BP_STATS, 1)

print(f"Final size: {len(html):,} chars")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
