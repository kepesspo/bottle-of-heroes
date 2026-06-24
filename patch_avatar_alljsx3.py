#!/usr/bin/env python3
"""
v9.604 — Avatar minden játékban 3. kör: utolsó maradék körök
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.603') >= 1
html = html.replace('v9.603', 'v9.604', 1)

count = 0

replacements = [
    # rp? 20px fontWeight:700 (second occurrence - different fontSize from earlier)
    (
        "<div style={{ width:20, height:20, borderRadius:'50%', background:rp?.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:11, color:'#fff' }}>{(rp?.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{ width:20, height:20, borderRadius:'50%', background:rp?.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:11, color:'#fff', overflow:'hidden' }}>{rp?.img ? <img src={rp.img} style={{width:20,height:20,objectFit:'cover'}} /> : (rp?.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # player 38px fontWeight:700 fontSize:16
    (
        "<div style={{ width:38, height:38, borderRadius:'50%', background:player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:16, color:'#fff', flexShrink:0 }}>{(player.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{ width:38, height:38, borderRadius:'50%', background:player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:16, color:'#fff', flexShrink:0, overflow:'hidden' }}>{player.img ? <img src={player.img} style={{width:38,height:38,objectFit:'cover'}} /> : (player.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # p isMe?28:22 dynamic size
    (
        "<div style={{ width: isMe?28:22, height: isMe?28:22, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize: isMe?11:9, color:'#fff', flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{ width: isMe?28:22, height: isMe?28:22, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize: isMe?11:9, color:'#fff', flexShrink:0, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:isMe?28:22,height:isMe?28:22,objectFit:'cover'}} /> : (p.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # p 36px fontWeight:700 fontSize:15
    (
        "<div style={{ width:36, height:36, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{ width:36, height:36, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:36,height:36,objectFit:'cover'}} /> : (p.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # p? 18px T.inkMute fontSize:8
    (
        "<div style={{ width:18, height:18, borderRadius:'50%', background:p?.color||T.inkMute, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:8, color:'#fff', flexShrink:0 }}>{(p?.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{ width:18, height:18, borderRadius:'50%', background:p?.color||T.inkMute, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:8, color:'#fff', flexShrink:0, overflow:'hidden' }}>{p?.img ? <img src={p.img} style={{width:18,height:18,objectFit:'cover'}} /> : (p?.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # s.player 24px fontWeight:700 fontSize:12
    (
        "<div style={{ width:24, height:24, borderRadius:'50%', background:s.player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#fff', flexShrink:0 }}>{(s.player.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{ width:24, height:24, borderRadius:'50%', background:s.player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#fff', flexShrink:0, overflow:'hidden' }}>{s.player.img ? <img src={s.player.img} style={{width:24,height:24,objectFit:'cover'}} /> : (s.player.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # p 28px fontWeight:700 fontSize:12
    (
        "<div style={{ width:28, height:28, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#fff', flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{ width:28, height:28, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#fff', flexShrink:0, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:28,height:28,objectFit:'cover'}} /> : (p.name||'?').charAt(0).toUpperCase()}</div>"
    ),
]

for old, new in replacements:
    cnt = html.count(old)
    if cnt >= 1:
        html = html.replace(old, new)
        count += cnt
        print(f"  OK ({cnt}x): {old[:70]}...")
    else:
        print(f"  MISS: {old[:80]}...")

remaining = [l for l in html.split('\n') if "charAt(0).toUpperCase()" in l and "borderRadius:'50%'" in l and ".img ?" not in l and ".img?" not in l]
print(f"\n{count} cserék. Maradék: {len(remaining)}")
for r in remaining:
    print(f"  {r.strip()[:120]}")

print(f"Final size: {len(html):,} chars")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
