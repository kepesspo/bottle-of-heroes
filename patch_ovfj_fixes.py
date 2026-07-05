with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── FIX 1: Add hostVotes state + submitHostVote function ───────────────────────
OLD1 = """  const [hostLocalAns, setHostLocalAns] = React.useState({});
  const hostSubmittedRef = React.useRef(false);
  const [hostPlayerId, setHostPlayerId] = React.useState(null);"""

NEW1 = """  const [hostLocalAns, setHostLocalAns] = React.useState({});
  const hostSubmittedRef = React.useRef(false);
  const [hostPlayerId, setHostPlayerId] = React.useState(null);
  const [hostVotes, setHostVotes] = React.useState({});

  const submitHostVote = (targetPid, catKey, value) => {
    if (!hostPlayerId) return;
    const vk = `${targetPid}_${catKey}`;
    const nv = { ...hostVotes, [vk]: value };
    setHostVotes(nv);
    if (roomCode && typeof syncRoom === 'function') {
      syncRoom(roomCode, { [ovfjVKey(hostPlayerId)]: { pid: hostPlayerId, round, votes: nv } });
    }
    // also update local votes state so host sees own vote reflected immediately
    setVotes(prev => {
      const updated = { ...prev };
      if (!updated[vk]) updated[vk] = {};
      updated[vk][hostPlayerId] = value;
      return updated;
    });
  };"""

assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# ── FIX 2: Voting phase — host can vote (replace the read-only vote display with interactive buttons when hostPlayer) ──
OLD2 = """      <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,textAlign:'center',marginTop:-6}}>Telefonon szavaznak a játékosok</div>
      {pl.map(p=>{
        const ans=answers[p.id]||{};
        return (
          <div key={p.id} style={{background:T.surface,borderRadius:18,padding:'12px 14px',boxShadow:T.shadow}}>
            <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:10}}>
              <div style={{width:28,height:28,borderRadius:'50%',background:p.color||T.mint,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:12,color:'#fff',flexShrink:0}}>{p.name?.[0]||'?'}</div>
              <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,color:T.ink,flex:1}}>{p.name}</span>
              {ans.done && <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,background:T.mintSoft,color:T.mint,padding:'3px 9px',borderRadius:999,letterSpacing:'0.04em',textTransform:'uppercase'}}>KÉSZ</span>}
            </div>
            {OVFJ_CATS.map(cat=>{
              const val=(ans[cat.key]||'').trim(), vk=`${p.id}_${cat.key}`, vm=votes[vk]||{};
              const yes=Object.values(vm).filter(Boolean).length, no=Object.values(vm).filter(x=>!x).length;
              const isDup = val && dupMap[cat.key].has(val.toLowerCase());
              return (
                <div key={cat.key} style={{display:'flex',alignItems:'center',gap:6,marginBottom:5,paddingBottom:4,borderBottom:`1px solid ${T.surfaceMuted}`}}>
                  <span style={{fontSize:13,flexShrink:0,width:20,textAlign:'center'}}>{cat.emoji}</span>
                  <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:T.inkSoft,width:66,flexShrink:0,textTransform:'uppercase',letterSpacing:'0.04em'}}>{cat.label}</span>
                  <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:13,flex:1,color:isDup?T.coral:val?T.ink:T.inkMute,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',textDecoration:isDup?'line-through':'none',opacity:isDup?0.7:1}}>{val||'—'}</span>
                  {val && !isDup && <span style={{fontFamily:T.font,fontSize:11,color:T.inkSoft,flexShrink:0}}>👍{yes} 👎{no}</span>}
                  {isDup && <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:T.coral,flexShrink:0}}>×</span>}
                  {val && <a href={`https://www.google.com/search?q=${encodeURIComponent(val)}`} target="_blank" rel="noreferrer" style={{fontSize:13,flexShrink:0,textDecoration:'none',opacity:0.55,lineHeight:1}}>🔍</a>}
                </div>
              );
            })}
          </div>
        );
      })}"""

NEW2 = """      <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,textAlign:'center',marginTop:-6}}>{hostPlayer ? '👆 Te is szavazhatsz!' : 'Telefonon szavaznak a játékosok'}</div>
      {pl.map(p=>{
        const ans=answers[p.id]||{};
        const isHostSelf = hostPlayer && p.id === hostPlayer.id;
        return (
          <div key={p.id} style={{background:T.surface,borderRadius:18,padding:'12px 14px',boxShadow:T.shadow,border:isHostSelf?`2px solid ${T.mint}40`:'none'}}>
            <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:10}}>
              <div style={{width:28,height:28,borderRadius:'50%',background:p.color||T.mint,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:12,color:'#fff',flexShrink:0}}>{p.name?.[0]||'?'}</div>
              <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,color:T.ink,flex:1}}>{p.name}{isHostSelf ? ' (Te)' : ''}</span>
              {ans.done && <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,background:T.mintSoft,color:T.mint,padding:'3px 9px',borderRadius:999,letterSpacing:'0.04em',textTransform:'uppercase'}}>KÉSZ</span>}
            </div>
            {OVFJ_CATS.map(cat=>{
              const val=(ans[cat.key]||'').trim(), vk=`${p.id}_${cat.key}`, vm=votes[vk]||{};
              const yes=Object.values(vm).filter(Boolean).length, no=Object.values(vm).filter(x=>!x).length;
              const isDup = val && dupMap[cat.key].has(val.toLowerCase());
              const hostVote = hostPlayer && !isHostSelf ? hostVotes[vk] : undefined;
              return (
                <div key={cat.key} style={{display:'flex',alignItems:'center',gap:6,marginBottom:5,paddingBottom:4,borderBottom:`1px solid ${T.surfaceMuted}`}}>
                  <span style={{fontSize:13,flexShrink:0,width:20,textAlign:'center'}}>{cat.emoji}</span>
                  <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:T.inkSoft,width:66,flexShrink:0,textTransform:'uppercase',letterSpacing:'0.04em'}}>{cat.label}</span>
                  <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:13,flex:1,color:isDup?T.coral:val?T.ink:T.inkMute,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',textDecoration:isDup?'line-through':'none',opacity:isDup?0.7:1}}>{val||'—'}</span>
                  {val && !isDup && !isHostSelf && hostPlayer ? (
                    <div style={{display:'flex',gap:3,flexShrink:0,alignItems:'center'}}>
                      <span style={{fontFamily:T.font,fontSize:10,color:T.inkSoft}}>👍{yes} 👎{no}</span>
                      <button onClick={()=>submitHostVote(p.id,cat.key,true)} style={{width:30,height:28,borderRadius:8,border:`1.5px solid ${hostVote===true?T.mint:T.surfaceMuted}`,background:hostVote===true?T.mintSoft:'transparent',cursor:'pointer',fontSize:13,display:'grid',placeItems:'center'}}>👍</button>
                      <button onClick={()=>submitHostVote(p.id,cat.key,false)} style={{width:30,height:28,borderRadius:8,border:`1.5px solid ${hostVote===false?T.coral:T.surfaceMuted}`,background:hostVote===false?T.coralSoft:'transparent',cursor:'pointer',fontSize:13,display:'grid',placeItems:'center'}}>👎</button>
                    </div>
                  ) : val && !isDup ? (
                    <span style={{fontFamily:T.font,fontSize:11,color:T.inkSoft,flexShrink:0}}>👍{yes} 👎{no}</span>
                  ) : null}
                  {isDup && <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:T.coral,flexShrink:0}}>×</span>}
                  {val && <a href={`https://www.google.com/search?q=${encodeURIComponent(val)}`} target="_blank" rel="noreferrer" style={{fontSize:13,flexShrink:0,textDecoration:'none',opacity:0.55,lineHeight:1}}>🔍</a>}
                </div>
              );
            })}
          </div>
        );
      })}"""

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# ── FIX 3: Observer writing phase — first letter auto-check (red/strikethrough if wrong) ──
OLD3 = """              <input
                ref={el=>inputRefs.current[idx]=el}
                type="text"
                value={localAns[cat.key]||''}
                onChange={e=>!locked&&setLocalAns(p=>({...p,[cat.key]:e.target.value}))}
                onKeyDown={e=>{if(e.key==='Enter'&&idx<OVFJ_CATS.length-1)inputRefs.current[idx+1]?.focus();}}
                disabled={locked}
                placeholder={`${letter}...`}
                style={{width:'100%',boxSizing:'border-box',padding:'5px 0',border:'none',borderBottom:`1.5px solid ${locked?T.surfaceMuted:T.mint}`,fontFamily:T.font,fontSize:14,fontWeight:T.weightTitle,background:'transparent',color:T.ink,outline:'none'}}
              />"""

NEW3 = """              {(()=>{
                const v = localAns[cat.key]||'';
                const wrongLetter = v.trim().length > 0 && v.trim()[0].toLowerCase() !== letter.toLowerCase();
                return (
                  <input
                    ref={el=>inputRefs.current[idx]=el}
                    type="text"
                    value={v}
                    onChange={e=>!locked&&setLocalAns(p=>({...p,[cat.key]:e.target.value}))}
                    onKeyDown={e=>{if(e.key==='Enter'&&idx<OVFJ_CATS.length-1)inputRefs.current[idx+1]?.focus();}}
                    disabled={locked}
                    placeholder={`${letter}...`}
                    style={{width:'100%',boxSizing:'border-box',padding:'5px 0',border:'none',borderBottom:`1.5px solid ${locked?T.surfaceMuted:wrongLetter?T.coral:T.mint}`,fontFamily:T.font,fontSize:14,fontWeight:T.weightTitle,background:'transparent',color:wrongLetter?T.coral:T.ink,outline:'none',textDecoration:wrongLetter?'line-through':'none'}}
                  />
                );
              })()}"""

assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

import re
content = re.sub(r'v9\.771', 'v9.772', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.772")
