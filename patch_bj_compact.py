#!/usr/bin/env python3
# v9.810 — BJ host felt table: 3 seats per row, compact, full width, Uj kor under felt
import io

P = '/home/user/bottle-of-heroes/index.html'
c = io.open(P, encoding='utf-8').read()

def rep(old, new, n=1):
    global c
    assert c.count(old) == n, f"count {c.count(old)} != {n} for: {old[:80]!r}"
    c = c.replace(old, new)

# 3. Outer wrapper padding (PlayingView + ResultsView only — anchored)
rep("""      <div style={{ padding:'0 16px 16px' }}>
        <div style={{ background:'radial-gradient(ellipse at 50% 0%,""",
    """      <div style={{ padding:'0 6px 12px' }}>
        <div style={{ background:'radial-gradient(ellipse at 50% 0%,""")
rep("""      <div style={{ padding:'0 16px 16px' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, marginBottom:12, textAlign:'center' }}>Eredmények</div>""",
    """      <div style={{ padding:'0 6px 12px' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, marginBottom:8, textAlign:'center' }}>Eredmények</div>""")

# 2. Felt padding + border (both views)
rep("border:'6px solid #175636', borderRadius:'150px 150px 22px 22px', padding:'26px 12px 18px'",
    "border:'4px solid #175636', borderRadius:'150px 150px 22px 22px', padding:'10px 8px 8px'", 2)
# Dealer block margin
rep("alignItems:'center', gap:8, marginBottom:16 }}",
    "alignItems:'center', gap:6, marginBottom:10 }}", 2)
# Seats row gap
rep("<div style={{ display:'flex', flexWrap:'wrap', justifyContent:'center', gap:10 }}>",
    "<div style={{ display:'flex', flexWrap:'wrap', justifyContent:'center', gap:6 }}>", 2)

# 1. Seat sizing — PlayingView seat
rep("<div key={pid} style={{ width:106, display:'flex', flexDirection:'column', alignItems:'center', gap:5, background:'rgba(255,255,255,0.08)', border:`1.5px solid ${isTurn ? '#F4D46B' : 'rgba(255,255,255,0.18)'}`, borderRadius:14, padding:'10px 6px 8px'",
    "<div key={pid} style={{ flex:'0 0 calc(33.33% - 8px)', minWidth:0, boxSizing:'border-box', display:'flex', flexDirection:'column', alignItems:'center', gap:4, background:'rgba(255,255,255,0.08)', border:`1.5px solid ${isTurn ? '#F4D46B' : 'rgba(255,255,255,0.18)'}`, borderRadius:14, padding:'6px 4px'")
# ResultsView seat
rep("<div key={pid} style={{ width:106, display:'flex', flexDirection:'column', alignItems:'center', gap:5, background:'rgba(255,255,255,0.08)', border:'1.5px solid rgba(255,255,255,0.18)', borderRadius:14, padding:'10px 6px 8px'",
    "<div key={pid} style={{ flex:'0 0 calc(33.33% - 8px)', minWidth:0, boxSizing:'border-box', display:'flex', flexDirection:'column', alignItems:'center', gap:4, background:'rgba(255,255,255,0.08)', border:'1.5px solid rgba(255,255,255,0.18)', borderRadius:14, padding:'6px 4px'")

# Seat internals (both views)
rep("                  <BJAvatar p={p} size={30} />", "                  <BJAvatar p={p} size={28} />", 2)  # 18-space indent = seat cards only (BettingView is 14)
rep("fontWeight:900, fontSize:12, color:'#fff', maxWidth:'100%', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'",
    "fontWeight:900, fontSize:11, color:'#fff', maxWidth:'100%', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'", 2)
# TET/KESZLET row gap
rep("<div style={{ display:'flex', alignItems:'flex-start', gap:10 }}>",
    "<div style={{ display:'flex', alignItems:'flex-start', gap:8 }}>", 2)
# TET disc 26 -> 20
rep("width:26, height:26, borderRadius:'50%', background:T.coral, border:'1.5px dashed rgba(255,255,255,0.9)', display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:11",
    "width:20, height:20, borderRadius:'50%', background:T.coral, border:'1.5px dashed rgba(255,255,255,0.9)', display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:10", 2)
# chip pile row
rep("gap:3, height:26 }}><BJChipStack count={rowChips} size={20} hideCount /><span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff' }}>",
    "gap:3, height:20 }}><BJChipStack count={rowChips} size={16} hideCount /><span style={{ fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff' }}>", 2)
# labels 8 -> 7
rep("const lblS = { fontFamily:T.font, fontSize:8, fontWeight:800",
    "const lblS = { fontFamily:T.font, fontSize:7, fontWeight:800", 2)
# status 9.5 -> 9
rep("fontWeight:900, fontSize:9.5, color:status.c", "fontWeight:900, fontSize:9, color:status.c", 2)

# 2b. ResultsView: felt marginBottom, move Uj kor button directly under felt
rep("boxShadow:'inset 0 2px 12px rgba(0,0,0,0.25)', marginBottom:14 }}",
    "boxShadow:'inset 0 2px 12px rgba(0,0,0,0.25)', marginBottom:10 }}")
BTN_OLD = """        <button onClick={hostNewRound} style={{ width:'100%', padding:'14px', borderRadius:16, background:'#1a6b3c', border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer', marginTop:14 }}>Új kör 🔄</button>
"""
rep(BTN_OLD, "")
rep("""        {(bjState.participants || []).map(pid => {
          const p = getPlayer(pid);
          const startStack = stackOf(pid);""",
    """        <button onClick={hostNewRound} style={{ width:'100%', padding:'14px', borderRadius:16, background:'#1a6b3c', border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer', marginBottom:10 }}>Új kör 🔄</button>
        {(bjState.participants || []).map(pid => {
          const p = getPlayer(pid);
          const startStack = stackOf(pid);""")

# Broke/cash-out list tighter
rep("<div key={pid} style={{ marginBottom:8, padding:'10px 12px', borderRadius:12, background:T.coralSoft }}>",
    "<div key={pid} style={{ marginBottom:6, padding:'8px 10px', borderRadius:12, background:T.coralSoft }}>")
rep("<div key={pid} style={{ display:'flex', alignItems:'center', gap:8, marginBottom:8 }}>",
    "<div key={pid} style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6 }}>")
rep("<div key={pid} style={{ display:'flex', alignItems:'center', gap:8, marginBottom:8, opacity:0.6 }}>",
    "<div key={pid} style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6, opacity:0.6 }}>")

# Version bump
assert c.count('v9.809') >= 1, 'version not found'
c = c.replace('v9.809', 'v9.810')

io.open(P, 'w', encoding='utf-8').write(c)
print('patch OK')
