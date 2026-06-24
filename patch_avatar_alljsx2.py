#!/usr/bin/env python3
"""
v9.603 — Avatar minden játékban 2. kör: maradék körök
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.602') >= 1
html = html.replace('v9.602', 'v9.603', 1)

count = 0

replacements = [
    # 32px p.color fontWeight:900 fontSize:13
    (
        "<div style={{width:32,height:32,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:13,color:'#fff',flexShrink:0}}>{p.name.charAt(0).toUpperCase()}</div>",
        "<div style={{width:32,height:32,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:13,color:'#fff',flexShrink:0,overflow:'hidden'}}>{p.img ? <img src={p.img} style={{width:32,height:32,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()}</div>"
    ),
    # 38px p.color fontWeight:900 fontSize:15
    (
        "<div style={{width:38,height:38,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff'}}>{p.name.charAt(0).toUpperCase()}</div>",
        "<div style={{width:38,height:38,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',overflow:'hidden'}}>{p.img ? <img src={p.img} style={{width:38,height:38,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()}</div>"
    ),
    # 24px p.color fontWeight:900 fontSize:10
    (
        "<div style={{width:24,height:24,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:10,color:'#fff'}}>{p.name.charAt(0).toUpperCase()}</div>",
        "<div style={{width:24,height:24,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:10,color:'#fff',overflow:'hidden'}}>{p.img ? <img src={p.img} style={{width:24,height:24,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()}</div>"
    ),
    # 28px p.color fontWeight:900 fontSize:11
    (
        "<div style={{width:28,height:28,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:11,color:'#fff',flexShrink:0}}>{p.name.charAt(0).toUpperCase()}</div>",
        "<div style={{width:28,height:28,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:11,color:'#fff',flexShrink:0,overflow:'hidden'}}>{p.img ? <img src={p.img} style={{width:28,height:28,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()}</div>"
    ),
    # 44px p?.color fontWeight:700 fontSize:18
    (
        "<div style={{ width:44, height:44, borderRadius:'50%', background:p?.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:18, color:'#fff' }}>{(p?.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{ width:44, height:44, borderRadius:'50%', background:p?.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:18, color:'#fff', overflow:'hidden' }}>{p?.img ? <img src={p.img} style={{width:44,height:44,objectFit:'cover'}} /> : (p?.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # p1 36px T.mint
    (
        "<div style={{width:36,height:36,borderRadius:'50%',background:p1?.color||T.mint,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0}}>{(p1?.name||'P1').charAt(0).toUpperCase()}</div>",
        "<div style={{width:36,height:36,borderRadius:'50%',background:p1?.color||T.mint,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0,overflow:'hidden'}}>{p1?.img ? <img src={p1.img} style={{width:36,height:36,objectFit:'cover'}} /> : (p1?.name||'P1').charAt(0).toUpperCase()}</div>"
    ),
    # p2 36px T.coral
    (
        "<div style={{width:36,height:36,borderRadius:'50%',background:p2?.color||T.coral,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0}}>{(p2?.name||'P2').charAt(0).toUpperCase()}</div>",
        "<div style={{width:36,height:36,borderRadius:'50%',background:p2?.color||T.coral,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0,overflow:'hidden'}}>{p2?.img ? <img src={p2.img} style={{width:36,height:36,objectFit:'cover'}} /> : (p2?.name||'P2').charAt(0).toUpperCase()}</div>"
    ),
    # p1 34px T.mint
    (
        "<div style={{width:34,height:34,borderRadius:'50%',background:p1?.color||T.mint,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:14,color:'#fff',flexShrink:0}}>{(p1?.name||'P1').charAt(0).toUpperCase()}</div>",
        "<div style={{width:34,height:34,borderRadius:'50%',background:p1?.color||T.mint,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:14,color:'#fff',flexShrink:0,overflow:'hidden'}}>{p1?.img ? <img src={p1.img} style={{width:34,height:34,objectFit:'cover'}} /> : (p1?.name||'P1').charAt(0).toUpperCase()}</div>"
    ),
    # p2 34px T.coral
    (
        "<div style={{width:34,height:34,borderRadius:'50%',background:p2?.color||T.coral,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:14,color:'#fff',flexShrink:0}}>{(p2?.name||'P2').charAt(0).toUpperCase()}</div>",
        "<div style={{width:34,height:34,borderRadius:'50%',background:p2?.color||T.coral,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:14,color:'#fff',flexShrink:0,overflow:'hidden'}}>{p2?.img ? <img src={p2.img} style={{width:34,height:34,objectFit:'cover'}} /> : (p2?.name||'P2').charAt(0).toUpperCase()}</div>"
    ),
    # p? 32px T.inkMute margin:0 auto
    (
        "<div style={{width:32,height:32,borderRadius:'50%',background:p?.color||T.inkMute,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:13,color:'#fff',margin:'0 auto 6px'}}>{(p?.name||'P').charAt(0).toUpperCase()}</div>",
        "<div style={{width:32,height:32,borderRadius:'50%',background:p?.color||T.inkMute,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:13,color:'#fff',margin:'0 auto 6px',overflow:'hidden'}}>{p?.img ? <img src={p.img} style={{width:32,height:32,objectFit:'cover'}} /> : (p?.name||'P').charAt(0).toUpperCase()}</div>"
    ),
    # bonusOverlay.player 52px
    (
        "<div style={{ width:52, height:52, borderRadius:'50%', background:bonusOverlay.player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:22, color:'#fff' }}>{bonusOverlay.player.name.charAt(0).toUpperCase()}</div>",
        "<div style={{ width:52, height:52, borderRadius:'50%', background:bonusOverlay.player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:22, color:'#fff', overflow:'hidden' }}>{bonusOverlay.player.img ? <img src={bonusOverlay.player.img} style={{width:52,height:52,objectFit:'cover'}} /> : bonusOverlay.player.name.charAt(0).toUpperCase()}</div>"
    ),
    # r.color 38px (bonus overlay row)
    (
        "<div style={{ width:38, height:38, borderRadius:'50%', background:r.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff' }}>{r.name.charAt(0).toUpperCase()}</div>",
        "<div style={{ width:38, height:38, borderRadius:'50%', background:r.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', overflow:'hidden' }}>{r.img ? <img src={r.img} style={{width:38,height:38,objectFit:'cover'}} /> : r.name.charAt(0).toUpperCase()}</div>"
    ),
    # isFirst?52:40 podium (game-internal, different from EndScreen)
    (
        "<div style={{ width:isFirst?52:40, height:isFirst?52:40, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:isFirst?20:15, color:'#fff', boxShadow:`0 0 0 2.5px ${tone}`, marginBottom:4 }}>{p.name.charAt(0).toUpperCase()}</div>",
        "<div style={{ width:isFirst?52:40, height:isFirst?52:40, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:isFirst?20:15, color:'#fff', boxShadow:`0 0 0 2.5px ${tone}`, marginBottom:4, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:isFirst?52:40,height:isFirst?52:40,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()}</div>"
    ),
    # player 54px
    (
        "<div style={{ width:54, height:54, borderRadius:'50%', background:player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:22, color:'#fff' }}>{(player.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{ width:54, height:54, borderRadius:'50%', background:player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:22, color:'#fff', overflow:'hidden' }}>{player.img ? <img src={player.img} style={{width:54,height:54,objectFit:'cover'}} /> : (player.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # player? 32px T.mint fontSize:14
    (
        "<div style={{ width:32, height:32, borderRadius:'50%', background:player?.color||T.mint, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:14, color:'#fff', flexShrink:0 }}>{(player?.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{ width:32, height:32, borderRadius:'50%', background:player?.color||T.mint, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:14, color:'#fff', flexShrink:0, overflow:'hidden' }}>{player?.img ? <img src={player.img} style={{width:32,height:32,objectFit:'cover'}} /> : (player?.name||'?').charAt(0).toUpperCase()}</div>"
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

# Check remaining
remaining = [l for l in html.split('\n') if "charAt(0).toUpperCase()" in l and "borderRadius:'50%'" in l and ".img ?" not in l and ".img?" not in l]
print(f"\n{count} cserék elvégezve. Maradék körök: {len(remaining)}")
for r in remaining[:5]:
    print(f"  {r.strip()[:100]}")

print(f"Final size: {len(html):,} chars")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
