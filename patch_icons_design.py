#!/usr/bin/env python3
"""
1. Base64 embed ovfj + powerhour icons/banners into IMGS
2. Update GAMES entries to reference them
3. Redesign OVFJGame host writing phase
"""
import base64

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Load images ────────────────────────────────────────────────────────────
def b64img(path, mime='image/png'):
    with open(path, 'rb') as f:
        return f'data:{mime};base64,{base64.b64encode(f.read()).decode()}'

ovfj_icon   = b64img('orszagvaros-icon-2.png')
ovfj_banner = b64img('orszagvaros.png')
ph_icon     = b64img('powerhour-icon-2.png')
ph_banner   = b64img('powerhour.png')

# ── 2. Add to IMGS dict (before closing }; at end of IMGS block) ──────────────
# The IMGS object ends at line ~33805. We find a unique anchor to insert before.
# Use the line right before the closing '};' of IMGS (which is followed by the GAMES array)
OLD_IMGS_END = "  'szures-paros': 'data:image/png;base64,"
# We'll append keys AFTER all existing entries by targeting the closing of IMGS
# Find a safe insertion point: right before the IMGS closing '};'
# We know IMGS is followed by const GAMES, so we look for the exact closing pattern
OLD_IMGS_CLOSE = """};\nconst IMG = '';  // images embedded below\nconst GAMES = ["""

NEW_IMGS_CLOSE = f""",
  'ovfj_icon.png': '{ovfj_icon}',
  'ovfj_banner.png': '{ovfj_banner}',
  'powerhour_icon.png': '{ph_icon}',
  'powerhour_banner.png': '{ph_banner}'
}};\nconst IMG = '';  // images embedded below\nconst GAMES = ["""

assert OLD_IMGS_CLOSE in content, "IMGS closing not found"
content = content.replace(OLD_IMGS_CLOSE, NEW_IMGS_CLOSE, 1)
print("✓ IMGS entries added")

# ── 3. Update GAMES entries ───────────────────────────────────────────────────
OLD_PH_GAME = "{ id:'powerhour', name:'Power Hour',            difficulty:'nehéz',   category:'Egyéni', emoji:'⚡', symbol:null, img:null, banner:null, color:'#F59E0B'"
NEW_PH_GAME = "{ id:'powerhour', name:'Power Hour',            difficulty:'nehéz',   category:'Egyéni', emoji:'⚡', symbol:null, img:IMGS['powerhour_icon.png'], banner:IMGS['powerhour_banner.png'], color:'#F59E0B'"
assert OLD_PH_GAME in content, "PowerHour GAMES entry not found"
content = content.replace(OLD_PH_GAME, NEW_PH_GAME, 1)
print("✓ PowerHour GAMES entry updated")

OLD_OVFJ_GAME = "{ id:'ovfj', name:'Ország-Város', difficulty:'közepes', category:'Csapat', emoji:'🌍', symbol:null, img:null, banner:null, color:'#22C55E'"
NEW_OVFJ_GAME = "{ id:'ovfj', name:'Ország-Város', difficulty:'közepes', category:'Csapat', emoji:'🌍', symbol:null, img:IMGS['ovfj_icon.png'], banner:IMGS['ovfj_banner.png'], color:'#22C55E'"
assert OLD_OVFJ_GAME in content, "OVFJ GAMES entry not found"
content = content.replace(OLD_OVFJ_GAME, NEW_OVFJ_GAME, 1)
print("✓ OVFJ GAMES entry updated")

# ── 4. Redesign OVFJGame host writing phase ───────────────────────────────────
OLD_HOST_WRITING = """  if (phase === 'writing') {
    const doneCount=Object.values(answers).filter(a=>a.done).length;
    return (
      <div style={{display:'flex',flexDirection:'column',gap:10,width:'100%'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
          <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:32,color:T.mint,letterSpacing:T.letterDisplay}}>{letter}</div>
          <div style={{display:'flex',alignItems:'center',gap:8}}>
            {countdown!==null ? (
              <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:20,color:countdown<=5?T.coral:T.ink}}>⏱ {countdown}s</div>
            ) : maxTimer!==null ? (
              <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:16,color:maxTimer<=30?T.coral:T.inkSoft}}>⏱ {Math.floor(maxTimer/60)}:{String(maxTimer%60).padStart(2,'0')}</div>
            ) : null}
            <span style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,background:T.surfaceMuted,padding:'4px 10px',borderRadius:999,fontWeight:T.weightTitle}}>{doneCount}/{pl.length} kész</span>
          </div>
        </div>
        {pl.map(p=>{
          const ans=answers[p.id]||{};
          return (
            <div key={p.id} style={{display:'flex',alignItems:'center',gap:10,background:T.surface,borderRadius:14,padding:'10px 14px',boxShadow:T.shadow}}>
              <div style={{width:30,height:30,borderRadius:'50%',background:p.color||T.mint,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:12,color:'#fff',flexShrink:0}}>{p.name?.[0]||'?'}</div>
              <span style={{fontFamily:T.font,fontSize:14,fontWeight:T.weightTitle,color:T.ink,flex:1}}>{p.name}</span>
              <span style={{fontSize:18}}>{ans.done?'✅':'✏️'}</span>
            </div>
          );
        })}
        <button onClick={forceStop} style={{width:'100%',padding:'12px',borderRadius:14,border:`1.5px solid ${T.coral}`,background:'transparent',color:T.coral,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:14,cursor:'pointer'}}>
          ⏹ Azonnali leállítás
        </button>
      </div>
    );
  }"""

NEW_HOST_WRITING = """  if (phase === 'writing') {
    const doneCount=Object.values(answers).filter(a=>a.done).length;
    const fmtT = s => s != null ? `${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}` : '';
    return (
      <div style={{display:'flex',flexDirection:'column',gap:10,width:'100%'}}>
        {/* Letter + timer row */}
        <div style={{display:'flex',gap:10,alignItems:'stretch'}}>
          <div style={{flex:'0 0 auto',width:88,minHeight:88,borderRadius:20,background:`linear-gradient(135deg,#F59E0B,#F87171)`,display:'grid',placeItems:'center',boxShadow:T.shadowLift}}>
            <span style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:48,color:'#fff',lineHeight:1}}>{letter}</span>
          </div>
          <div style={{flex:1,background:T.surface,borderRadius:20,padding:'12px 16px',boxShadow:T.shadow,display:'flex',flexDirection:'column',justifyContent:'center',gap:4}}>
            {countdown!==null ? (
              <>
                <div style={{fontFamily:T.font,fontSize:10,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.08em'}}>Első kész — siess!</div>
                <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:30,color:countdown<=5?T.coral:T.ink,lineHeight:1}}>{countdown}s</div>
              </>
            ) : maxTimer!==null ? (
              <>
                <div style={{fontFamily:T.font,fontSize:10,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.08em'}}>Hátralévő idő</div>
                <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:30,color:maxTimer<=30?T.coral:maxTimer<=60?'#F59E0B':T.ink,lineHeight:1,fontVariantNumeric:'tabular-nums'}}>{fmtT(maxTimer)}</div>
              </>
            ) : null}
            <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,marginTop:2}}>{doneCount}/{pl.length} játékos kész</div>
          </div>
        </div>
        {/* Player status cards */}
        {pl.map(p=>{
          const ans=answers[p.id]||{};
          return (
            <div key={p.id} style={{display:'flex',alignItems:'center',gap:10,background:T.surface,borderRadius:14,padding:'10px 14px',boxShadow:T.shadow}}>
              <div style={{width:30,height:30,borderRadius:'50%',background:p.color||T.mint,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:12,color:'#fff',flexShrink:0}}>{p.name?.[0]||'?'}</div>
              <span style={{fontFamily:T.font,fontSize:14,fontWeight:T.weightTitle,color:T.ink,flex:1}}>{p.name}</span>
              <span style={{fontSize:18}}>{ans.done?'✅':'✏️'}</span>
            </div>
          );
        })}
        <button onClick={forceStop} style={{width:'100%',padding:'12px',borderRadius:14,border:`1.5px solid ${T.coral}`,background:'transparent',color:T.coral,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:14,cursor:'pointer'}}>
          ⏹ Azonnali leállítás
        </button>
      </div>
    );
  }"""

assert OLD_HOST_WRITING in content, "OVFJGame host writing phase not found"
content = content.replace(OLD_HOST_WRITING, NEW_HOST_WRITING, 1)
print("✓ OVFJGame host writing phase redesigned")

# ── 5. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.35';"
NEW_VER = "const APP_VERSION = 'v8.36';"
assert OLD_VER in content, "Version not found"
content = content.replace(OLD_VER, NEW_VER, 1)
print("✓ Version bumped to v8.36")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ index.html saved")
