#!/usr/bin/env python3
"""v8.43: Busz — Szerencsétlen popup: gomb helyett 3mp auto-zárás, 0.5s fade-in"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Auto-dismiss after 3s (set timer when lastCardFail becomes true) ───────
OLD_TRIGGER = "    if (!myRes.correct && myStep === busStepsCount - 1) setTimeout(() => { setGuessResult(null); setLastCardFail(true); }, 1000);"
NEW_TRIGGER = "    if (!myRes.correct && myStep === busStepsCount - 1) setTimeout(() => { setGuessResult(null); setLastCardFail(true); setTimeout(() => setLastCardFail(false), 3000); }, 1000);"
assert OLD_TRIGGER in content, "trigger not found"
content = content.replace(OLD_TRIGGER, NEW_TRIGGER, 1)
print("✓ Auto-dismiss after 3s")

# ── 2. Popup: remove button, add fade-in 0.5s, auto style ────────────────────
OLD_POPUP = """      {lastCardFail && (
        <div style={{position:'fixed',inset:0,background:'rgba(14,14,24,0.78)',zIndex:80,display:'flex',alignItems:'center',justifyContent:'center',padding:28,animation:'fadeIn .2s'}}>
          <div style={{background:T.surface,borderRadius:28,padding:'32px 24px 24px',width:'100%',maxWidth:320,display:'flex',flexDirection:'column',alignItems:'center',gap:12,boxShadow:'0 24px 64px rgba(0,0,0,0.35)',animation:'popIn .35s cubic-bezier(.2,.9,.3,1.3)'}}>
            <div style={{fontSize:56,lineHeight:1}}>😖</div>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:24,color:T.coral,letterSpacing:'-0.02em'}}>Szerencsétlen!</div>
            <div style={{fontFamily:T.font,fontSize:15,color:T.inkSoft,textAlign:'center',lineHeight:1.5}}>Az utolsó lapnál hibáztál.<br/>Kezd előlről!</div>
            <button onClick={() => setLastCardFail(false)} style={{marginTop:8,width:'100%',padding:'15px',borderRadius:16,border:'none',background:T.coral,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:17,cursor:'pointer',boxShadow:'0 5px 16px -5px rgba(240,100,80,0.5)'}}>OK, kezdem előlről</button>
          </div>
        </div>
      )}"""

NEW_POPUP = """      {lastCardFail && (
        <div style={{position:'fixed',inset:0,background:'rgba(14,14,24,0.78)',zIndex:80,display:'flex',alignItems:'center',justifyContent:'center',padding:28,animation:'fadeIn .5s'}}>
          <div style={{background:T.surface,borderRadius:28,padding:'32px 24px 28px',width:'100%',maxWidth:320,display:'flex',flexDirection:'column',alignItems:'center',gap:12,boxShadow:'0 24px 64px rgba(0,0,0,0.35)',animation:'popIn .5s cubic-bezier(.2,.9,.3,1.3)'}}>
            <div style={{fontSize:56,lineHeight:1}}>😖</div>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:24,color:T.coral,letterSpacing:'-0.02em'}}>Szerencsétlen!</div>
            <div style={{fontFamily:T.font,fontSize:15,color:T.inkSoft,textAlign:'center',lineHeight:1.5}}>Az utolsó lapnál hibáztál.<br/>Kezd előlről!</div>
          </div>
        </div>
      )}"""

assert OLD_POPUP in content, "popup not found"
content = content.replace(OLD_POPUP, NEW_POPUP, 1)
print("✓ Popup: gomb eltávolítva, 0.5s fade-in")

# ── 3. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.42';"
NEW_VER = "const APP_VERSION = 'v8.43';"
assert OLD_VER in content
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.43 saved")
