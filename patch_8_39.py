#!/usr/bin/env python3
"""
v8.39:
1. Host letter phase: betű elrejtve indítás előtt (kérdőjel helyette)
2. QR gomb hangsúlyosabb a letter phase-ben
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Host letter phase: hide letter before start, prominent QR ─────────────
OLD = """      <div style={{display:'flex',alignItems:'center',gap:8}}>
        <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.12em'}}>{round}. kör / {totalRounds}</div>
        {roomCode && (
          <button onClick={()=>setShowQR(true)} style={{padding:'3px 10px',borderRadius:999,border:'none',background:T.surfaceMuted,color:T.inkSoft,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:11,cursor:'pointer',letterSpacing:'0.04em',textTransform:'uppercase'}}>📱 QR</button>
        )}
      </div>
      {/* Big letter display */}
      <div style={{width:160,height:160,borderRadius:36,background:`linear-gradient(135deg,#F59E0B,#F87171)`,display:'grid',placeItems:'center',boxShadow:T.shadowLift}}>
        <span style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:96,color:'#fff',lineHeight:1}}>{letter}</span>
      </div>
      <div style={{display:'flex',flexWrap:'wrap',gap:6,justifyContent:'center',maxWidth:320}}>
        {OVFJ_CATS.map(c=>(
          <span key={c.key} style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,background:T.surfaceMuted,padding:'4px 10px',borderRadius:999}}>
            {c.emoji} {c.label}
          </span>
        ))}
      </div>
      <PrimaryButton onClick={startWriting} style={{maxWidth:300}}>✏️ Kör kezdése!</PrimaryButton>"""

NEW = """      <div style={{display:'flex',alignItems:'center',gap:8}}>
        <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.12em'}}>{round}. kör / {totalRounds}</div>
      </div>
      {/* Hidden letter card — ? until game starts */}
      <div style={{width:160,height:160,borderRadius:36,background:T.surfaceMuted,display:'grid',placeItems:'center',boxShadow:T.shadow}}>
        <span style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:96,color:T.inkMute,lineHeight:1}}>?</span>
      </div>
      {/* Prominent QR button */}
      {roomCode && (
        <button onClick={()=>setShowQR(true)} style={{display:'flex',alignItems:'center',gap:10,padding:'14px 28px',borderRadius:18,border:`2px solid ${T.mint}`,background:T.mintSoft,color:T.mint,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:16,cursor:'pointer',boxShadow:T.shadow}}>
          <span style={{fontSize:22}}>📱</span> QR kód — Csatlakozás
        </button>
      )}
      <div style={{display:'flex',flexWrap:'wrap',gap:6,justifyContent:'center',maxWidth:320}}>
        {OVFJ_CATS.map(c=>(
          <span key={c.key} style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,background:T.surfaceMuted,padding:'4px 10px',borderRadius:999}}>
            {c.emoji} {c.label}
          </span>
        ))}
      </div>
      <PrimaryButton onClick={startWriting} style={{maxWidth:300}}>✏️ Kör kezdése!</PrimaryButton>"""

assert OLD in content, "Host letter phase not found"
content = content.replace(OLD, NEW, 1)
print("✓ Host letter phase updated")

# ── 2. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.38';"
NEW_VER = "const APP_VERSION = 'v8.39';"
assert OLD_VER in content
content = content.replace(OLD_VER, NEW_VER, 1)
print("✓ Version bumped to v8.39")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Saved")
