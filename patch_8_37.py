#!/usr/bin/env python3
"""
v8.37:
1. OVFJ kizárva a 'Ki rontott?' szekcióból
2. Betű kártya hangsúlyosabb a letter phase-ben (host + observer)
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Exclude OVFJ from "Ki rontott?" section ───────────────────────────────
OLD_COND = "currentGameId !== 'powerhour' && ("
NEW_COND = "currentGameId !== 'powerhour' && currentGameId !== 'ovfj' && ("
assert OLD_COND in content, "Ki rontott? condition not found"
content = content.replace(OLD_COND, NEW_COND, 1)
print("✓ OVFJ excluded from Ki rontott?")

# ── 2. Letter phase – host side: make letter card bigger/bolder ───────────────
# Current letter phase host render (after writing/voting/roundEnd/done phases)
OLD_LETTER_HOST = """      <div style={{display:'flex',flexWrap:'wrap',gap:6,justifyContent:'center',maxWidth:320}}>
        {OVFJ_CATS.map(c=>(
          <span key={c.key} style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,background:T.surfaceMuted,padding:'4px 10px',borderRadius:999}}>
            {c.emoji} {c.label}
          </span>
        ))}
      </div>
      <PrimaryButton onClick={startWriting} style={{maxWidth:300}}>✏️ Kör kezdése!</PrimaryButton>"""

NEW_LETTER_HOST = """      {/* Big letter display */}
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

assert OLD_LETTER_HOST in content, "Letter host phase categories not found"
content = content.replace(OLD_LETTER_HOST, NEW_LETTER_HOST, 1)
print("✓ Host letter card made bigger")

# ── 3. Letter phase – observer side: bigger card ──────────────────────────────
OLD_LETTER_OBS = """  if (phase === 'letter') return (
    <div style={pageOuter}><div style={pageInner}>
      <Hdr />
      <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:20,padding:'24px 0'}}>
        <div style={{width:120,height:120,borderRadius:28,background:T.surfaceMuted,display:'grid',placeItems:'center',boxShadow:T.shadow}}>
          <span style={{fontSize:56}}>🎲</span>
        </div>
        <div style={{fontFamily:T.font,fontSize:14,fontWeight:T.weightTitle,color:T.inkSoft,textAlign:'center'}}>A host felfedi a betűt...</div>"""

NEW_LETTER_OBS = """  if (phase === 'letter') return (
    <div style={pageOuter}><div style={pageInner}>
      <Hdr />
      <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:20,padding:'24px 0'}}>
        <div style={{width:160,height:160,borderRadius:36,background:`linear-gradient(135deg,#F59E0B,#F87171)`,display:'grid',placeItems:'center',boxShadow:T.shadowLift}}>
          <span style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:96,color:'#fff',lineHeight:1}}>{letter||'?'}</span>
        </div>
        <div style={{fontFamily:T.font,fontSize:14,fontWeight:T.weightTitle,color:T.inkSoft,textAlign:'center'}}>A host felfedi a betűt...</div>"""

assert OLD_LETTER_OBS in content, "Observer letter phase not found"
content = content.replace(OLD_LETTER_OBS, NEW_LETTER_OBS, 1)
print("✓ Observer letter card made bigger")

# ── 4. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.36';"
NEW_VER = "const APP_VERSION = 'v8.37';"
assert OLD_VER in content
content = content.replace(OLD_VER, NEW_VER, 1)
print("✓ Version bumped to v8.37")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ index.html saved")
