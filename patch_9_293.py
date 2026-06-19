#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. PlayerCard: add badge prop + render in bottom-right corner
old = """function PlayerCard({ p, onEdit, onRemove, index }) {
  return (
    <div onClick={onEdit} style={{
      position:'relative', background:T.surface, borderRadius:16,
      padding:'10px 8px 10px', boxShadow:T.shadow,
      display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6,
      cursor:'pointer', aspectRatio:'1/1.18', minHeight:120,
      animation:'fadeInUp 0.32s ease both', animationDelay:`${(index||0)*0.06}s`,
    }}>"""
new = """function PlayerCard({ p, onEdit, onRemove, index, badge }) {
  return (
    <div onClick={onEdit} style={{
      position:'relative', background:T.surface, borderRadius:16,
      padding:'10px 8px 10px', boxShadow:T.shadow,
      display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6,
      cursor:'pointer', aspectRatio:'1/1.18', minHeight:120,
      animation:'fadeInUp 0.32s ease both', animationDelay:`${(index||0)*0.06}s`,
    }}>
      {badge && <div style={{ position:'absolute', bottom:6, right:6, fontSize:16, lineHeight:1 }}>{badge}</div>}"""
assert old in html, "FAIL: PlayerCard"
html = html.replace(old, new, 1)

# ── 2. PlayersScreen: compute badge per player and pass it
old2 = """            <PlayerCard key={p.id} p={p} index={i} onEdit={() => setEditing(p.id)} onRemove={() => removePlayer(p.id)} />"""
new2 = """            <PlayerCard key={p.id} p={p} index={i} onEdit={() => setEditing(p.id)} onRemove={() => removePlayer(p.id)} badge={(() => { const sorted=[...players].sort((a,b)=>b.points-a.points); const ri=sorted.findIndex(x=>x.id===p.id); return p.points>0&&ri<3?['🥇','🥈','🥉'][ri]:null; })()} />"""
assert old2 in html, "FAIL: PlayerCard call"
html = html.replace(old2, new2, 1)

html = html.replace("const APP_VERSION = 'v9.292';", "const APP_VERSION = 'v9.293';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.293 — PlayerCard badge jobb alsó sarokba")
