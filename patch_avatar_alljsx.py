#!/usr/bin/env python3
"""
v9.602 — Avatar minden játékban: regex alapú globális csere
Minden player kör div ahol .charAt(0).toUpperCase() van → img || betű
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.601') >= 1
html = html.replace('v9.601', 'v9.602', 1)

count = 0

# Pattern: <div style={{ ...borderRadius:'50%'... }}>{ (expr).charAt(0).toUpperCase() }</div>
# We capture:
#   group 1: the full style string
#   group 2: the player expression (e.g. p.name, currentRider?.name, etc.)
#   group 3: the size (used to infer img size from width:NN)
# Strategy: find all remaining charAt patterns inside div circles and add img check

# We'll do targeted replacements for each remaining unique pattern

replacements = [
    # ── line ~35566 Csapat játék bajnok kör ──────────────────────────────────────
    (
        "<div style={{ width:32, height:32, borderRadius:'50%', background:t.champion.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', flexShrink:0 }}>{t.champion.name.charAt(0).toUpperCase()}</div>",
        "<div style={{ width:32, height:32, borderRadius:'50%', background:t.champion.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', flexShrink:0, overflow:'hidden' }}>{t.champion.img ? <img src={t.champion.img} style={{width:32,height:32,objectFit:'cover'}} /> : t.champion.name.charAt(0).toUpperCase()}</div>"
    ),
    # ── line ~40421 Kis RR standings 22px ────────────────────────────────────────
    (
        "<div style={{ width:22, height:22, borderRadius:'50%', background:s.player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:11, color:'#fff', flexShrink:0 }}>{s.player.name.charAt(0).toUpperCase()}</div>",
        "<div style={{ width:22, height:22, borderRadius:'50%', background:s.player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:11, color:'#fff', flexShrink:0, overflow:'hidden' }}>{s.player.img ? <img src={s.player.img} style={{width:22,height:22,objectFit:'cover'}} /> : s.player.name.charAt(0).toUpperCase()}</div>"
    ),
    # ── line ~42708 cp kör 36px ───────────────────────────────────────────────────
    (
        "<div style={{ width:36, height:36, borderRadius:'50%', background:cp.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>{(cp.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{ width:36, height:36, borderRadius:'50%', background:cp.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0, overflow:'hidden' }}>{cp.img ? <img src={cp.img} style={{width:36,height:36,objectFit:'cover'}} /> : (cp.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # ── line ~42841 p kör 32px ────────────────────────────────────────────────────
    (
        "<div style={{ width:32, height:32, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:13, color:'#fff', flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{ width:32, height:32, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:13, color:'#fff', flexShrink:0, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:32,height:32,objectFit:'cover'}} /> : (p.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # ── line ~43204 imposztor szavazás 40px ───────────────────────────────────────
    (
        "<div style={{ width:40, height:40, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</div>",
        "<div style={{ width:40, height:40, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:'#fff', overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:40,height:40,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()}</div>"
    ),
    # ── line ~43225 imposztor felfed 44px ─────────────────────────────────────────
    (
        "<div style={{ width:44, height:44, borderRadius:'50%', background:impostor.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:'#fff' }}>{impostor.name.charAt(0).toUpperCase()}</div>",
        "<div style={{ width:44, height:44, borderRadius:'50%', background:impostor.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:'#fff', overflow:'hidden' }}>{impostor.img ? <img src={impostor.img} style={{width:44,height:44,objectFit:'cover'}} /> : impostor.name.charAt(0).toUpperCase()}</div>"
    ),
    # ── line ~43235 imposztor mini 26px ───────────────────────────────────────────
    (
        "<div style={{ width:26, height:26, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontSize:11, fontWeight:700, color:'#fff', flexShrink:0 }}>{p.name.charAt(0).toUpperCase()}</div>",
        "<div style={{ width:26, height:26, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontSize:11, fontWeight:700, color:'#fff', flexShrink:0, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:26,height:26,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()}</div>"
    ),
    # ── line ~43585 Busz init overlapping 42px ───────────────────────────────────
    (
        "style={{width:42,height:42,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:700,fontSize:16,color:'#fff',border:`2.5px solid ${T.bg}`,marginLeft:idx?-10:0,zIndex:players.length-idx,boxShadow:'0 1px 4px rgba(0,0,0,0.15)'}}>{(p.name||'?').charAt(0).toUpperCase()}</div>",
        "style={{width:42,height:42,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:700,fontSize:16,color:'#fff',border:`2.5px solid ${T.bg}`,marginLeft:idx?-10:0,zIndex:players.length-idx,boxShadow:'0 1px 4px rgba(0,0,0,0.15)',overflow:'hidden'}}>{p.img ? <img src={p.img} style={{width:42,height:42,objectFit:'cover'}} /> : (p.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # ── line ~43640 Busz sorban 42px ─────────────────────────────────────────────
    (
        "<div style={{ width:42, height:42, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:18, color:'#fff', flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{ width:42, height:42, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:18, color:'#fff', flexShrink:0, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:42,height:42,objectFit:'cover'}} /> : (p.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # ── line ~43770 28px kör ──────────────────────────────────────────────────────
    (
        "<div style={{width:28,height:28,borderRadius:'50%',background:p?.color||T.coral,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:700,fontSize:12,color:'#fff',flexShrink:0}}>{(p?.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{width:28,height:28,borderRadius:'50%',background:p?.color||T.coral,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:700,fontSize:12,color:'#fff',flexShrink:0,overflow:'hidden'}}>{p?.img ? <img src={p.img} style={{width:28,height:28,objectFit:'cover'}} /> : (p?.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # ── line ~43795 currentRider 46px ────────────────────────────────────────────
    (
        "<div style={{width:46,height:46,borderRadius:'50%',background:currentRider?.color||T.coral,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:700,fontSize:20,color:'#fff'}}>{(currentRider?.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{width:46,height:46,borderRadius:'50%',background:currentRider?.color||T.coral,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:700,fontSize:20,color:'#fff',overflow:'hidden'}}>{currentRider?.img ? <img src={currentRider.img} style={{width:46,height:46,objectFit:'cover'}} /> : (currentRider?.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # ── line ~43843 rp mini 20px ──────────────────────────────────────────────────
    (
        "<div style={{width:20,height:20,borderRadius:'50%',background:rp?.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:700,fontSize:11,color:'#fff'}}>{(rp?.name||'?').charAt(0).toUpperCase()}</div>",
        "<div style={{width:20,height:20,borderRadius:'50%',background:rp?.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:700,fontSize:11,color:'#fff',overflow:'hidden'}}>{rp?.img ? <img src={rp.img} style={{width:20,height:20,objectFit:'cover'}} /> : (rp?.name||'?').charAt(0).toUpperCase()}</div>"
    ),
    # ── line ~44146 winner 42px ───────────────────────────────────────────────────
    (
        "<div style={{ width:42, height:42, borderRadius:'50%', background:winner.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:17, color:'#fff', flexShrink:0 }}>{winner.name.charAt(0).toUpperCase()}</div>",
        "<div style={{ width:42, height:42, borderRadius:'50%', background:winner.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:17, color:'#fff', flexShrink:0, overflow:'hidden' }}>{winner.img ? <img src={winner.img} style={{width:42,height:42,objectFit:'cover'}} /> : winner.name.charAt(0).toUpperCase()}</div>"
    ),
    # ── line ~44155 p kör 42px (a winner kör után a többi játékos) ────────────────
    (
        "<div style={{ width:42, height:42, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:17, color:'#fff', flexShrink:0 }}>{p.name.charAt(0).toUpperCase()}</div>",
        "<div style={{ width:42, height:42, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:17, color:'#fff', flexShrink:0, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:42,height:42,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()}</div>"
    ),
]

for old, new in replacements:
    cnt = html.count(old)
    if cnt == 1:
        html = html.replace(old, new, 1)
        count += 1
        print(f"  OK: {old[:60]}...")
    elif cnt == 0:
        print(f"  MISS (0): {old[:80]}...")
    else:
        html = html.replace(old, new)
        count += cnt
        print(f"  OK ({cnt}x): {old[:60]}...")

print(f"\n{count} cserék elvégezve.")
print(f"Final size: {len(html):,} chars")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
