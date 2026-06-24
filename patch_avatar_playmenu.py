#!/usr/bin/env python3
"""
v9.601 — Avatar megjelenítés: PlayScreen menü + játékon belüli kijelzők
1. LeaderRow (Állás tab) — 36px kör
2. Szerkesztés tab — 36px kör
3. Vezérlés tab vezető — 40px kör
4. MAGYARÁZ/TIPPEL játékos jelzők — 32px kör
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.600') >= 1
html = html.replace('v9.600', 'v9.601', 1)

# ── 1. LeaderRow (Állás tab) 36px kör ────────────────────────────────────────
OLD_LEADER_ROW = "      <div style={{ position:'relative', width:36, height:36, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', color:'#fff', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15 }}>{p.name.charAt(0).toUpperCase()||'?'}</div>"
NEW_LEADER_ROW = "      <div style={{ position:'relative', width:36, height:36, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', color:'#fff', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:36,height:36,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()||'?'}</div>"
assert html.count(OLD_LEADER_ROW) == 1, f"leaderrow: {html.count(OLD_LEADER_ROW)}"
html = html.replace(OLD_LEADER_ROW, NEW_LEADER_ROW, 1)

# ── 2. Szerkesztés tab 36px kör ───────────────────────────────────────────────
OLD_EDIT = "          <div style={{ width:36, height:36, borderRadius:'50%', background: p.disabled ? T.inkMute : p.color, display:'grid', placeItems:'center', color:'#fff', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>"
NEW_EDIT = "          <div style={{ width:36, height:36, borderRadius:'50%', background: p.disabled ? T.inkMute : p.color, display:'grid', placeItems:'center', color:'#fff', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, flexShrink:0, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:36,height:36,objectFit:'cover',opacity:p.disabled?0.5:1}} /> : (p.name||'?').charAt(0).toUpperCase()}</div>"
assert html.count(OLD_EDIT) == 1, f"edit: {html.count(OLD_EDIT)}"
html = html.replace(OLD_EDIT, NEW_EDIT, 1)

# ── 3. Vezérlés tab vezető 40px kör ──────────────────────────────────────────
OLD_VEZETO = "                    <div style={{ width:40, height:40, borderRadius:'50%', background:mLeader.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:18, color:'#fff', flexShrink:0 }}>{(mLeader.name||'?').charAt(0).toUpperCase()}</div>"
NEW_VEZETO = "                    <div style={{ width:40, height:40, borderRadius:'50%', background:mLeader.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:18, color:'#fff', flexShrink:0, overflow:'hidden' }}>{mLeader.img ? <img src={mLeader.img} style={{width:40,height:40,objectFit:'cover'}} /> : (mLeader.name||'?').charAt(0).toUpperCase()}</div>"
assert html.count(OLD_VEZETO) == 1, f"vezeto: {html.count(OLD_VEZETO)}"
html = html.replace(OLD_VEZETO, NEW_VEZETO, 1)

# ── 4. MAGYARÁZ jelző 32px kör ────────────────────────────────────────────────
OLD_MAG = "          <div style={{ width:32, height:32, borderRadius:'50%', background:challenger?.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:14, color:'#fff' }}>{(challenger?.name||'?').charAt(0).toUpperCase()}</div>"
NEW_MAG = "          <div style={{ width:32, height:32, borderRadius:'50%', background:challenger?.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:14, color:'#fff', overflow:'hidden' }}>{challenger?.img ? <img src={challenger.img} style={{width:32,height:32,objectFit:'cover'}} /> : (challenger?.name||'?').charAt(0).toUpperCase()}</div>"
assert html.count(OLD_MAG) == 1, f"magyaraz: {html.count(OLD_MAG)}"
html = html.replace(OLD_MAG, NEW_MAG, 1)

# ── 5. TIPPEL jelző 32px kör ──────────────────────────────────────────────────
OLD_TIPP = "          <div style={{ width:32, height:32, borderRadius:'50%', background:opponent?.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:14, color:'#fff' }}>{(opponent?.name||'?').charAt(0).toUpperCase()}</div>"
NEW_TIPP = "          <div style={{ width:32, height:32, borderRadius:'50%', background:opponent?.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:14, color:'#fff', overflow:'hidden' }}>{opponent?.img ? <img src={opponent.img} style={{width:32,height:32,objectFit:'cover'}} /> : (opponent?.name||'?').charAt(0).toUpperCase()}</div>"
assert html.count(OLD_TIPP) == 1, f"tippel: {html.count(OLD_TIPP)}"
html = html.replace(OLD_TIPP, NEW_TIPP, 1)

print(f"Final size: {len(html):,} chars")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
