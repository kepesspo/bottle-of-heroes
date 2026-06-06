#!/usr/bin/env python3
"""Redesign Power Hour and OVFJ Observer writing phase UI"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Power Hour: replace the rendered JSX (not the logic) ──────────────────
OLD_PH = """  if (ended) {
    return (
      <div style={{display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',height:'100%',gap:24,padding:32,textAlign:'center'}}>
        <div style={{fontSize:64}}>🏆</div>
        <div style={{fontSize:24,fontWeight:700,color:T.gold||'#F59E0B'}}>Power Hour teljesítve!</div>
        <div style={{fontSize:16,color:T.sub||'#aaa'}}>{minutesDone} korty megivott</div>
        <button onClick={()=>{if(!advancedRef.current){advancedRef.current=true;onAdvance && onAdvance();}}}
          style={{marginTop:16,padding:'14px 32px',borderRadius:16,background:T.mint||'#22C55E',color:'#fff',fontWeight:700,fontSize:18,border:'none',cursor:'pointer'}}>
          Következő
        </button>
      </div>
    );
  }

  return (
    <div style={{display:'flex',flexDirection:'column',height:'100%',background:T.bg||'#1a1a2e',color:T.text||'#fff',position:'relative',overflow:'hidden'}}>
      <audio ref={audioRef} src={MASHUP_URL} preload="auto" />

      {showDrink && (
        <div style={{position:'fixed',inset:0,display:'flex',alignItems:'center',justifyContent:'center',zIndex:999,background:'rgba(245,158,11,0.18)',pointerEvents:'none'}}>
          <div style={{fontSize:80,animation:'pulse 0.5s ease-in-out infinite alternate'}}>🍺</div>
        </div>
      )}

      <div style={{flex:1,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:24,padding:24}}>
        <div style={{fontSize:48}}>⚡</div>
        <div style={{fontSize:22,fontWeight:700,color:T.gold||'#F59E0B',letterSpacing:1}}>MASHUP POWER HOUR</div>

        {!started ? (
          <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:16,textAlign:'center'}}>
            <div style={{fontSize:14,color:T.sub||'#aaa',maxWidth:280}}>
              60 percen át folyamatos zene. Percenként hangjelzés — igyál egyet!
            </div>
            <button onClick={startGame}
              style={{marginTop:8,padding:'16px 40px',borderRadius:20,background:'#F59E0B',color:'#fff',fontWeight:700,fontSize:20,border:'none',cursor:'pointer',boxShadow:'0 4px 16px #F59E0B44'}}>
              ▶ INDÍTÁS
            </button>
          </div>
        ) : (
          <>
            <div style={{width:'100%',maxWidth:320}}>
              <div style={{background:T.card||'#16213e',borderRadius:16,padding:20,textAlign:'center'}}>
                <div style={{fontSize:13,color:T.sub||'#aaa',marginBottom:4}}>HÁTRALÉVŐ IDŐ</div>
                <div style={{fontSize:48,fontWeight:700,fontVariantNumeric:'tabular-nums',color:T.gold||'#F59E0B',letterSpacing:2}}>{fmt(remaining)}</div>
              </div>
            </div>

            <div style={{width:'100%',maxWidth:320,background:T.card||'#16213e',borderRadius:16,padding:'14px 20px',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
              <div style={{textAlign:'center'}}>
                <div style={{fontSize:11,color:T.sub||'#aaa'}}>MEGIVOTT</div>
                <div style={{fontSize:28,fontWeight:700,color:T.mint||'#22C55E'}}>{minutesDone}</div>
              </div>
              <div style={{textAlign:'center'}}>
                <div style={{fontSize:11,color:T.sub||'#aaa'}}>KÖVETKEZŐ KORTY</div>
                <div style={{fontSize:28,fontWeight:700,color:nextDrinkIn<=10?(T.coral||'#F87171'):(T.text||'#fff')}}>{nextDrinkIn}mp</div>
              </div>
            </div>

            <div style={{width:'100%',maxWidth:320}}>
              <div style={{height:8,background:T.border||'#333',borderRadius:4,overflow:'hidden'}}>
                <div style={{height:'100%',width:`${pct}%`,background:'linear-gradient(90deg,#F59E0B,#F87171)',borderRadius:4,transition:'width 1s linear'}} />
              </div>
              <div style={{display:'flex',justifyContent:'space-between',fontSize:11,color:T.sub||'#aaa',marginTop:4}}>
                <span>{fmt(elapsed)}</span><span>60:00</span>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}"""

NEW_PH = """  if (ended) {
    return (
      <div style={{display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',height:'100%',gap:24,padding:32,textAlign:'center',background:T.bg,fontFamily:T.font}}>
        <div style={{fontSize:64}}>🏆</div>
        <div style={{fontSize:24,fontWeight:T.weightDisplay,color:T.ink,letterSpacing:T.letterDisplay}}>POWER HOUR TELJESÍTVE!</div>
        <div style={{fontSize:16,color:T.inkSoft}}>{minutesDone} korty megivott 🍺</div>
        <PrimaryButton onClick={()=>{if(!advancedRef.current){advancedRef.current=true;onAdvance && onAdvance();}}} style={{maxWidth:280}}>Következő</PrimaryButton>
      </div>
    );
  }

  const ringR = 90;
  const ringCirc = 2 * Math.PI * ringR;
  const ringOffset = ringCirc * (1 - nextDrinkIn / DRINK_EVERY);

  return (
    <div style={{display:'flex',flexDirection:'column',height:'100%',background:T.bg,color:T.ink,position:'relative',overflow:'hidden',fontFamily:T.font}}>
      <audio ref={audioRef} src={MASHUP_URL} preload="auto" />

      {showDrink && (
        <div style={{position:'fixed',inset:0,display:'flex',alignItems:'center',justifyContent:'center',zIndex:999,background:'rgba(245,158,11,0.15)',pointerEvents:'none'}}>
          <div style={{fontSize:96}}>🍺</div>
        </div>
      )}

      <div style={{flex:1,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:20,padding:'20px 24px'}}>

        {!started ? (
          <>
            <div style={{fontSize:48,marginBottom:4}}>⚡</div>
            <div style={{fontWeight:T.weightDisplay,fontSize:22,color:T.ink,letterSpacing:T.letterDisplay,textTransform:'uppercase',textAlign:'center'}}>MASHUP POWER HOUR</div>
            <div style={{fontSize:14,color:T.inkSoft,maxWidth:280,textAlign:'center',lineHeight:1.6}}>
              60 percen át folyamatos zene. Percenként hangjelzés — igyál egyet!
            </div>
            <PrimaryButton onClick={startGame} style={{maxWidth:260,marginTop:8}}>▶ INDÍTÁS</PrimaryButton>
          </>
        ) : (
          <>
            {/* Circular countdown ring */}
            <div style={{position:'relative',width:220,height:220,flexShrink:0}}>
              <svg width="220" height="220" style={{transform:'rotate(-90deg)'}}>
                <circle cx="110" cy="110" r={ringR} fill="none" stroke={T.surfaceMuted} strokeWidth="14" />
                <circle cx="110" cy="110" r={ringR} fill="none"
                  stroke={nextDrinkIn<=10?T.coral:'#F59E0B'}
                  strokeWidth="14"
                  strokeLinecap="round"
                  strokeDasharray={ringCirc}
                  strokeDashoffset={ringOffset}
                  style={{transition:'stroke-dashoffset 1s linear, stroke 0.3s'}}
                />
              </svg>
              <div style={{position:'absolute',inset:0,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:2}}>
                <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:44,color:nextDrinkIn<=10?T.coral:'#F59E0B',fontVariantNumeric:'tabular-nums',lineHeight:1}}>{nextDrinkIn}</div>
                <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.1em'}}>MP A KORTYIG</div>
              </div>
            </div>

            {/* Mushroom badge */}
            <div style={{display:'flex',alignItems:'center',gap:8,background:T.surface,borderRadius:999,padding:'8px 18px',boxShadow:T.shadow}}>
              <span style={{fontSize:20}}>🍄</span>
              <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:13,color:T.inkSoft,letterSpacing:'0.04em'}}>Super Mario hang = KORTY</span>
            </div>

            {/* Stats card */}
            <div style={{width:'100%',maxWidth:320,background:T.surface,borderRadius:20,padding:'18px 24px',boxShadow:T.shadowLift,display:'flex',justifyContent:'space-between',alignItems:'center'}}>
              <div>
                <div style={{fontFamily:T.font,fontSize:10,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.12em',marginBottom:2}}>HÁTRALÉVŐ IDŐ</div>
                <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:28,color:T.ink,fontVariantNumeric:'tabular-nums',letterSpacing:1}}>{fmt(remaining)}</div>
              </div>
              <div style={{textAlign:'right'}}>
                <div style={{fontFamily:T.font,fontSize:10,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.12em',marginBottom:2}}>MEGIVOTT</div>
                <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:28,color:T.mint}}>{minutesDone} 🍺</div>
              </div>
            </div>

            {/* Progress bar */}
            <div style={{width:'100%',maxWidth:320}}>
              <div style={{height:8,background:T.surfaceMuted,borderRadius:999,overflow:'hidden'}}>
                <div style={{height:'100%',width:`${pct}%`,background:'linear-gradient(90deg,#F59E0B,#F87171)',borderRadius:999,transition:'width 1s linear'}} />
              </div>
              <div style={{display:'flex',justifyContent:'space-between',fontFamily:T.font,fontSize:11,color:T.inkMute,marginTop:5}}>
                <span>{fmt(elapsed)}</span><span>60:00</span>
              </div>
            </div>

            {/* Surrender button */}
            <button onClick={()=>{if(!advancedRef.current){advancedRef.current=true;clearInterval(timerRef.current);if(audioRef.current)audioRef.current.pause();onAdvance&&onAdvance();}}}
              style={{marginTop:4,padding:'12px 28px',borderRadius:14,border:`1.5px solid ${T.coral}`,background:'transparent',color:T.coral,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:14,cursor:'pointer',letterSpacing:'0.04em'}}>
              Feladom — kiesem 🏳
            </button>
          </>
        )}
      </div>
    </div>
  );
}"""

assert OLD_PH in content, "PowerHourGame render section not found"
content = content.replace(OLD_PH, NEW_PH, 1)
print("✓ Power Hour redesigned")

# ── 2. OVFJ Observer: redesign the writing phase ─────────────────────────────
OLD_OBS_WRITING = """  if (phase === 'writing') {"""

# Find exact block in observer view to replace
# The observer writing phase starts with the inputs grid
OLD_OBS_BLOCK = """  if (phase === 'writing') {
    const timedOut = localTimer === 0 || (ovfj.maxTimer !== null && ovfj.maxTimer !== undefined && ovfj.maxTimer <= 0);
    const locked = submitted || timedOut;
    const cd=ovfj.countdown;
    return (
      <div style={pageOuter}><div style={pageInner}>
        <Hdr />
        <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:16,marginBottom:4}}>
          <div style={{width:72,height:72,borderRadius:18,background:`linear-gradient(135deg,${T.mint},${T.mintDeep||'#3DA888'})`,display:'grid',placeItems:'center',boxShadow:T.shadowLift,flexShrink:0}}>
            <span style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:44,color:'#fff',lineHeight:1}}>{letter}</span>
          </div>
          <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:4}}>
            {timedOut ? (
              <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:20,color:T.coral}}>⏰ Lejárt!</div>
            ) : cd!=null ? (
              <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:28,color:cd<=5?T.coral:T.ink}}>{cd}s</div>
            ) : localTimer!=null ? (
              <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:26,color:localTimer<=30?T.coral:localTimer<=60?T.yellow||'#F4C95A':T.ink}}>{Math.floor(localTimer/60)}:{String(localTimer%60).padStart(2,'0')}</div>
            ) : null}
            {localTimer!=null && !timedOut && <div style={{fontFamily:T.font,fontSize:10,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.06em'}}>hátralévő</div>}
          </div>
        </div>
        {OVFJ_CATS.map((cat,idx)=>(
          <div key={cat.key} style={{display:'flex',alignItems:'center',gap:10,background:T.surface,borderRadius:14,padding:'10px 14px',boxShadow:locked?'none':T.shadow,opacity:locked?0.6:1}}>
            <span style={{fontSize:18,flexShrink:0,width:24,textAlign:'center'}}>{cat.emoji}</span>
            <div style={{flex:1,minWidth:0}}>
              <label style={{fontFamily:T.font,fontSize:10,fontWeight:T.weightTitle,color:T.inkSoft,display:'block',marginBottom:2,textTransform:'uppercase',letterSpacing:'0.06em'}}>{cat.label}</label>
              <input ref={el=>inputRefs.current[idx]=el} type="text" value={localAns[cat.key]||''} onChange={e=>!locked&&setLocalAns(p=>({...p,[cat.key]:e.target.value}))}
                onKeyDown={e=>{if(e.key==='Enter'&&idx<OVFJ_CATS.length-1)inputRefs.current[idx+1]?.focus();}}
                disabled={locked} placeholder={`${letter}...`}
                style={{width:'100%',boxSizing:'border-box',padding:'4px 0',border:'none',borderBottom:`1.5px solid ${locked?T.surfaceMuted:T.mint}`,fontFamily:T.font,fontSize:15,fontWeight:T.weightTitle,background:'transparent',color:T.ink,outline:'none'}} />
            </div>
          </div>
        ))}
        <div ref={submitAreaRef}>
          {timedOut && !submitted ? (
            <div style={{textAlign:'center',fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,color:T.coral,padding:'16px',background:T.coralSoft,borderRadius:16,marginTop:4}}>⏰ Az idő lejárt — nem lehet több választ beadni</div>
          ) : !submitted ? (
            <PrimaryButton onClick={submitAnswers} style={{marginTop:4}}>✓ KÉSZ — Leadom!</PrimaryButton>
          ) : (
            <div style={{textAlign:'center',fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,color:T.mint,padding:'16px',background:T.mintSoft,borderRadius:16,marginTop:4}}>✅ Beadva! Várd a többieket...</div>
          )}
        </div>
      </div></div>
    );
  }"""

NEW_OBS_BLOCK = """  if (phase === 'writing') {
    const timedOut = localTimer === 0 || (ovfj.maxTimer !== null && ovfj.maxTimer !== undefined && ovfj.maxTimer <= 0);
    const locked = submitted || timedOut;
    const cd=ovfj.countdown;
    const fmtT = s => s != null ? `${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}` : '';
    return (
      <div style={pageOuter}><div style={pageInner}>
        <Hdr />
        {/* Letter card + timer card row */}
        <div style={{display:'flex',gap:10,alignItems:'stretch'}}>
          {/* Large letter card */}
          <div style={{flex:'0 0 auto',width:96,minHeight:96,borderRadius:22,background:`linear-gradient(135deg,#F59E0B,#F87171)`,display:'grid',placeItems:'center',boxShadow:T.shadowLift}}>
            <span style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:52,color:'#fff',lineHeight:1}}>{letter}</span>
          </div>
          {/* Timer / status card */}
          <div style={{flex:1,background:T.surface,borderRadius:22,padding:'14px 16px',boxShadow:T.shadow,display:'flex',flexDirection:'column',justifyContent:'center',gap:4}}>
            {timedOut ? (
              <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:18,color:T.coral}}>⏰ Lejárt!</div>
            ) : cd!=null ? (
              <>
                <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.08em'}}>Siess a befejezéssel!</div>
                <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:28,color:cd<=5?T.coral:T.ink,lineHeight:1}}>{cd}s</div>
              </>
            ) : localTimer!=null ? (
              <>
                <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.08em'}}>Hátralévő idő</div>
                <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:32,color:localTimer<=30?T.coral:localTimer<=60?'#F59E0B':T.ink,lineHeight:1,fontVariantNumeric:'tabular-nums'}}>{fmtT(localTimer)}</div>
              </>
            ) : (
              <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft}}>Írj a betűre!</div>
            )}
          </div>
        </div>

        {/* 2-column grid of category input cards */}
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>
          {OVFJ_CATS.map((cat,idx)=>(
            <div key={cat.key} style={{background:T.surface,borderRadius:16,padding:'10px 12px',boxShadow:locked?'none':T.shadow,opacity:locked?0.65:1,display:'flex',flexDirection:'column',gap:4}}>
              <div style={{display:'flex',alignItems:'center',gap:6}}>
                <span style={{fontSize:16,flexShrink:0}}>{cat.emoji}</span>
                <span style={{fontFamily:T.font,fontSize:10,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.07em',flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{cat.label}</span>
                {(localAns[cat.key]||'').trim() && <span style={{fontSize:13}}>✅</span>}
              </div>
              <input
                ref={el=>inputRefs.current[idx]=el}
                type="text"
                value={localAns[cat.key]||''}
                onChange={e=>!locked&&setLocalAns(p=>({...p,[cat.key]:e.target.value}))}
                onKeyDown={e=>{if(e.key==='Enter'&&idx<OVFJ_CATS.length-1)inputRefs.current[idx+1]?.focus();}}
                disabled={locked}
                placeholder={`${letter}...`}
                style={{width:'100%',boxSizing:'border-box',padding:'5px 0',border:'none',borderBottom:`1.5px solid ${locked?T.surfaceMuted:T.mint}`,fontFamily:T.font,fontSize:14,fontWeight:T.weightTitle,background:'transparent',color:T.ink,outline:'none'}}
              />
            </div>
          ))}
        </div>

        <div ref={submitAreaRef}>
          {timedOut && !submitted ? (
            <div style={{textAlign:'center',fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,color:T.coral,padding:'16px',background:T.coralSoft,borderRadius:16}}>⏰ Az idő lejárt — nem lehet több választ beadni</div>
          ) : !submitted ? (
            <PrimaryButton onClick={submitAnswers} style={{marginTop:4}}>Kész vagyok! ✏️</PrimaryButton>
          ) : (
            <div style={{textAlign:'center',fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,color:T.mint,padding:'16px',background:T.mintSoft,borderRadius:16}}>✅ Beadva! Várd a többieket...</div>
          )}
        </div>
      </div></div>
    );
  }"""

assert OLD_OBS_BLOCK in content, "OVFJObserverView writing phase not found"
content = content.replace(OLD_OBS_BLOCK, NEW_OBS_BLOCK, 1)
print("✓ OVFJ Observer writing phase redesigned")

# ── 3. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.34';"
NEW_VER = "const APP_VERSION = 'v8.35';"
assert OLD_VER in content, "Version not found"
content = content.replace(OLD_VER, NEW_VER, 1)
print("✓ Version bumped to v8.35")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ index.html saved")
