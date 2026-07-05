with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── FIX 1: resetRound — add setHostVotes({}) ──────────────────────────────────
OLD1 = """  const resetRound = () => { cdStartedRef.current = false; setAnswers({}); setVotes({}); setRoundScores({}); setCountdown(null); setMaxTimer(null); calcCalledRef.current = false; setHostLocalAns({}); hostSubmittedRef.current = false; };"""
NEW1 = """  const resetRound = () => { cdStartedRef.current = false; setAnswers({}); setVotes({}); setRoundScores({}); setCountdown(null); setMaxTimer(null); calcCalledRef.current = false; setHostLocalAns({}); hostSubmittedRef.current = false; setHostVotes({}); };"""
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# ── FIX 2: calcScores — duplicates get 5 pts, not 0; exclude wrong-first-letter answers ──
OLD2 = """        const vk=`${pid}_${cat.key}`, vm=votes[vk]||{}, vl=Object.values(vm);
        const yes=vl.filter(Boolean).length, no=vl.filter(x=>!x).length;
        if(vl.length>0 && no>yes) return;
        rs[pid]=(rs[pid]||0)+(vals[v]>1?0:10);"""
NEW2 = """        const vk=`${pid}_${cat.key}`, vm=votes[vk]||{}, vl=Object.values(vm);
        const yes=vl.filter(Boolean).length, no=vl.filter(x=>!x).length;
        if(vl.length>0 && no>yes) return;
        // Exclude wrong first letter (digraph-aware)
        const letterL = letter.toLowerCase();
        if (!v.startsWith(letterL)) return;
        rs[pid]=(rs[pid]||0)+(vals[v]>1?5:10);"""
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# ── FIX 3: Observer first-letter check — digraph-aware ───────────────────────
OLD3 = """                const wrongLetter = v.trim().length > 0 && v.trim()[0].toLowerCase() !== letter.toLowerCase();"""
NEW3 = """                const wrongLetter = v.trim().length > 0 && !v.trim().toLowerCase().startsWith(letter.toLowerCase());"""
assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# ── FIX 4: Host writing form — first-letter validation + correct placeholder ──
OLD4 = """                <input
                  value={hostLocalAns[cat.key]||''}
                  onChange={e => setHostLocalAns(prev => ({...prev, [cat.key]: e.target.value}))}
                  placeholder={`${cat.label}...`}
                  style={{flex:1,padding:'7px 10px',borderRadius:10,border:`1px solid ${T.surfaceMuted}`,background:T.bgSoft,fontFamily:T.font,fontSize:13,color:T.ink,outline:'none'}}
                />"""
NEW4 = """                {(()=>{
                  const hv = hostLocalAns[cat.key]||'';
                  const hwrong = hv.trim().length > 0 && !hv.trim().toLowerCase().startsWith(letter.toLowerCase());
                  return (
                    <input
                      value={hv}
                      onChange={e => setHostLocalAns(prev => ({...prev, [cat.key]: e.target.value}))}
                      placeholder={`${letter}...`}
                      style={{flex:1,padding:'7px 10px',borderRadius:10,border:`1.5px solid ${hwrong?T.coral:T.surfaceMuted}`,background:T.bgSoft,fontFamily:T.font,fontSize:13,color:hwrong?T.coral:T.ink,outline:'none',textDecoration:hwrong?'line-through':'none'}}
                    />
                  );
                })()}"""
assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

# ── FIX 5: dupMap display — show strikethrough for wrong-first-letter too ─────
# In voting phase host view, add wrong-letter detection for display
OLD5 = """              const isDup = val && dupMap[cat.key].has(val.toLowerCase());
              const hostVote = hostPlayer && !isHostSelf ? hostVotes[vk] : undefined;
              return (
                <div key={cat.key} style={{display:'flex',alignItems:'center',gap:6,marginBottom:5,paddingBottom:4,borderBottom:`1px solid ${T.surfaceMuted}`}}>
                  <span style={{fontSize:13,flexShrink:0,width:20,textAlign:'center'}}>{cat.emoji}</span>
                  <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:T.inkSoft,width:66,flexShrink:0,textTransform:'uppercase',letterSpacing:'0.04em'}}>{cat.label}</span>
                  <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:13,flex:1,color:isDup?T.coral:val?T.ink:T.inkMute,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',textDecoration:isDup?'line-through':'none',opacity:isDup?0.7:1}}>{val||'—'}</span>
                  {val && !isDup && !isHostSelf && hostPlayer ? ("""
NEW5 = """              const isDup = val && dupMap[cat.key].has(val.toLowerCase());
              const isWrongLetter = val && !val.toLowerCase().startsWith(letter.toLowerCase());
              const isInvalid = isDup || isWrongLetter;
              const hostVote = hostPlayer && !isHostSelf ? hostVotes[vk] : undefined;
              return (
                <div key={cat.key} style={{display:'flex',alignItems:'center',gap:6,marginBottom:5,paddingBottom:4,borderBottom:`1px solid ${T.surfaceMuted}`}}>
                  <span style={{fontSize:13,flexShrink:0,width:20,textAlign:'center'}}>{cat.emoji}</span>
                  <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:T.inkSoft,width:66,flexShrink:0,textTransform:'uppercase',letterSpacing:'0.04em'}}>{cat.label}</span>
                  <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:13,flex:1,color:isInvalid?T.coral:val?T.ink:T.inkMute,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',textDecoration:isInvalid?'line-through':'none',opacity:isInvalid?0.7:1}}>{val||'—'}</span>
                  {val && !isInvalid && !isHostSelf && hostPlayer ? ("""
assert OLD5 in content, "OLD5 not found"
content = content.replace(OLD5, NEW5, 1)

# Also fix the isDup references after hostVote block in host voting view
OLD6 = """                  ) : val && !isDup ? (
                    <span style={{fontFamily:T.font,fontSize:11,color:T.inkSoft,flexShrink:0}}>👍{yes} 👎{no}</span>
                  ) : null}
                  {isDup && <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:T.coral,flexShrink:0}}>×</span>}"""
NEW6 = """                  ) : val && !isInvalid ? (
                    <span style={{fontFamily:T.font,fontSize:11,color:T.inkSoft,flexShrink:0}}>👍{yes} 👎{no}</span>
                  ) : null}
                  {isInvalid && <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:T.coral,flexShrink:0}}>{isWrongLetter?'✗ betű':'× egyező'}</span>}"""
assert OLD6 in content, "OLD6 not found"
content = content.replace(OLD6, NEW6, 1)

import re
content = re.sub(r'v9\.772', 'v9.773', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.773")
