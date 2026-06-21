# -*- coding: utf-8 -*-
with open('index.html','r',encoding='utf-8') as f: src=f.read()

# Replace the entire reveal + done phases with a merged animated reveal
OLD = """  // ── REVEAL ────────────────────────────────────────────────────────────────
  if (S.phase === 'reveal') {
    const {rounds, p1W, p2W} = results;
    return (
      <div style={{background:CB_BG,borderRadius:20,padding:'12px',display:'flex',flexDirection:'column',gap:8,overflowY:'auto'}}>
        {/* Összesítő */}
        <div style={{background:'rgba(255,255,255,.85)',borderRadius:16,padding:'10px 16px',textAlign:'center'}}>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:T.ink,display:'flex',alignItems:'center',justifyContent:'center',gap:10}}>
            <span style={{color:p1Color}}>{p1Name}</span>
            <span style={{fontSize:20}}>{p1W} — {p2W}</span>
            <span style={{color:p2Color}}>{p2Name}</span>
          </div>
          <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,marginTop:2}}>A sávok átfordulnak, körönt</div>
        </div>

        {/* Oszlopfejléc */}
        <div style={{display:'flex',alignItems:'center',padding:'0 14px'}}>
          <div style={{flex:1,fontFamily:T.font,fontWeight:800,fontSize:13,color:p1Color}}>{p1Name}</div>
          <div style={{fontFamily:T.font,fontSize:11,fontWeight:700,color:T.inkSoft,width:36,textAlign:'center'}}>vs</div>
          <div style={{flex:1,fontFamily:T.font,fontWeight:800,fontSize:13,color:p2Color,textAlign:'right'}}>{p2Name}</div>
        </div>

        {/* Körlista */}
        {rounds.map((r,i) => {
          const win1=r.w==='p1', win2=r.w==='p2', tie=!r.w;
          const rowBg = win1 ? p1Color+'18' : win2 ? p2Color+'18' : 'rgba(255,255,255,.6)';
          const icon  = win1 ? '🏆' : win2 ? '×' : '🤝';
          const iconColor = win2 ? CB_RED : T.inkSoft;
          return (
            <div key={i} style={{
              display:'flex',alignItems:'center',gap:8,padding:'8px 12px',
              background:rowBg, borderRadius:14,
              border:'1.5px solid '+(win1?p1Color+'44':win2?p2Color+'44':'rgba(0,0,0,.08)'),
              animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)',
              animationDelay:(i*.06)+'s', animationFillMode:'both',
            }}>
              <div style={{fontFamily:T.font,fontWeight:700,fontSize:11,color:T.inkSoft,width:18}}>{i+1}</div>
              <div style={{flex:1,display:'flex',justifyContent:'flex-start'}}>
                {r.p1s>0 ? <CardChip value={r.p1s} color={p1Color} /> : <div style={{width:42,height:56,borderRadius:11,background:'rgba(0,0,0,.06)',border:'2px dashed rgba(0,0,0,.1)'}} />}
              </div>
              <div style={{fontFamily:T.font,fontSize:win2?18:20,fontWeight:900,color:iconColor,width:28,textAlign:'center'}}>{icon}</div>
              <div style={{flex:1,display:'flex',justifyContent:'flex-end'}}>
                {r.p2s>0 ? <CardChip value={r.p2s} color={p2Color} /> : <div style={{width:42,height:56,borderRadius:11,background:'rgba(0,0,0,.06)',border:'2px dashed rgba(0,0,0,.1)'}} />}
              </div>
            </div>
          );
        })}

        <button onClick={()=>setS(s=>({...s,phase:'done'}))} style={{
          marginTop:4,padding:'15px',borderRadius:16,border:'none',
          background:CB_GREEN,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:16,
          cursor:'pointer',boxShadow:'0 5px 16px -5px '+CB_GREEN+'88',
        }}>Eredmény →</button>
      </div>
    );
  }

  // ── DONE ──────────────────────────────────────────────────────────────────
  if (S.phase === 'done') {
    const {p1W, p2W} = results;
    const tie = p1W === p2W;
    const winName  = p1W>p2W ? p1Name : p2W>p1W ? p2Name : null;
    const loseName = p1W>p2W ? p2Name : p2W>p1W ? p1Name : null;
    const diff = Math.abs(p1W - p2W);
    return (
      <div style={{background:CB_BG,borderRadius:20,padding:'12px',display:'flex',flexDirection:'column',gap:10,overflowY:'auto'}}>
        {/* Eredmény kártya */}
        <div style={{
          background: tie ? T.inkSoft : CB_GREEN,
          borderRadius:20,padding:'24px 16px',
          display:'flex',flexDirection:'column',alignItems:'center',gap:10,
          animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)',textAlign:'center',
        }}>
          <div style={{fontSize:44}}>🃏</div>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:24,color:'#fff'}}>
            {winName ? winName+' nyert!' : 'Döntetlen!'}
          </div>
          <div style={{fontFamily:T.font,fontSize:13,color:'rgba(255,255,255,.85)'}}>
            {winName ? `${p1W} : ${p2W} a megnyert körökben` : 'Mindenki egyforma!'}
          </div>
          {loseName && (
            <div style={{
              background:'rgba(255,255,255,.25)',borderRadius:999,
              padding:'10px 22px',fontFamily:T.font,fontWeight:800,fontSize:15,color:'#fff',marginTop:4,
            }}>🎴 {loseName} iszik {diff} kortyot</div>
          )}
          {tie && (
            <div style={{
              background:'rgba(255,255,255,.25)',borderRadius:999,
              padding:'10px 22px',fontFamily:T.font,fontWeight:800,fontSize:15,color:'#fff',marginTop:4,
            }}>🍺 Mindenki iszik 1 kortyot</div>
          )}
        </div>

        {/* Végeredmény */}
        <div style={{background:'rgba(255,255,255,.8)',borderRadius:16,padding:'14px 20px'}}>
          <div style={{fontFamily:T.font,fontSize:11,fontWeight:700,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'.1em',textAlign:'center',marginBottom:10}}>VÉGEREDMÉNY</div>
          <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:16}}>
            <div style={{textAlign:'center'}}>
              <div style={{fontFamily:T.font,fontWeight:900,fontSize:38,color:p1Color}}>{p1W}</div>
              <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft}}>{p1Name}</div>
            </div>
            <div style={{fontFamily:T.font,fontSize:26,color:T.inkMute,fontWeight:700}}>:</div>
            <div style={{textAlign:'center'}}>
              <div style={{fontFamily:T.font,fontWeight:900,fontSize:38,color:p2Color}}>{p2W}</div>
              <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft}}>{p2Name}</div>
            </div>
          </div>
        </div>


      </div>
    );
  }"""

NEW = """  // ── REVEAL (animated, merged result) ────────────────────────────────────
  if (S.phase === 'reveal') {
    const {rounds, p1W, p2W} = results;
    const NR_total = rounds.length;

    // animStep: how many rows are revealed so far
    const [animStep, setAnimStep] = React.useState(0);
    const animTimer = React.useRef(null);

    React.useEffect(() => {
      setAnimStep(0);
    }, [S.phase]);

    React.useEffect(() => {
      if (animStep >= NR_total) return;
      animTimer.current = setTimeout(() => setAnimStep(s => s+1), 800);
      return () => clearTimeout(animTimer.current);
    }, [animStep, NR_total]);

    // Fire result after last row revealed + short pause
    React.useEffect(() => {
      if (animStep < NR_total) return;
      const t = setTimeout(() => {
        const p1id = challenger?.id;
        const p2id = opponent?.id;
        const diff = Math.abs(p1W - p2W);
        if (p1W > p2W) {
          if (onAdvance) onAdvance({[p2id]: diff}, {[p1id]: 1});
          if (onResult) onResult({ correct: true, playerName: p1Name, drinks: 0, subtitle: p1Name + ' nyerte a meccset!' });
        } else if (p2W > p1W) {
          if (onAdvance) onAdvance({[p1id]: diff}, {[p2id]: 1});
          if (onResult) onResult({ correct: false, playerName: p2Name, drinks: 0, subtitle: p2Name + ' nyerte a meccset!' });
        } else {
          if (onAdvance) onAdvance({[p1id]: 1, [p2id]: 1}, {});
          if (onResult) onResult({ correct: false, playerName: null, drinks: 1, subtitle: 'Döntetlen — mindenki iszik!' });
        }
        setS(s=>({...s,phase:'done'}));
      }, 1600);
      return () => clearTimeout(t);
    }, [animStep, NR_total]);

    const allDone = animStep >= NR_total;
    const tie = p1W === p2W;
    const winName  = p1W>p2W ? p1Name : p2W>p1W ? p2Name : null;
    const loseName = p1W>p2W ? p2Name : p2W>p1W ? p1Name : null;
    const diff = Math.abs(p1W - p2W);
    const resultBg = tie ? T.inkSoft : CB_GREEN;

    return (
      <div style={{background:CB_BG,borderRadius:20,padding:'12px',display:'flex',flexDirection:'column',gap:7,overflowY:'auto'}}>

        {/* Oszlopfejléc */}
        <div style={{display:'flex',alignItems:'center',padding:'2px 14px 0'}}>
          <div style={{flex:1,fontFamily:T.font,fontWeight:800,fontSize:13,color:p1Color}}>{p1Name}</div>
          <div style={{fontFamily:T.font,fontSize:11,fontWeight:700,color:T.inkSoft,width:36,textAlign:'center'}}>vs</div>
          <div style={{flex:1,fontFamily:T.font,fontWeight:800,fontSize:13,color:p2Color,textAlign:'right'}}>{p2Name}</div>
        </div>

        {/* Körlista — soronként felfedezve */}
        {rounds.map((r,i) => {
          const revealed = i < animStep;
          const win1=r.w==='p1', win2=r.w==='p2';
          const rowBg = !revealed ? 'rgba(255,255,255,.35)' : win1 ? p1Color+'22' : win2 ? p2Color+'22' : 'rgba(255,255,255,.65)';
          const icon  = !revealed ? '❓' : win1 ? '🏆' : win2 ? '✗' : '🤝';
          const iconColor = !revealed ? T.inkMute : win2 ? CB_RED : T.inkSoft;
          return (
            <div key={i} style={{
              display:'flex',alignItems:'center',gap:8,padding:'7px 10px',
              background:rowBg, borderRadius:13,
              border:'1.5px solid '+(revealed?(win1?p1Color+'44':win2?p2Color+'44':'rgba(0,0,0,.08)'):'rgba(0,0,0,.07)'),
              transition:'background .4s, border .4s',
            }}>
              <div style={{fontFamily:T.font,fontWeight:700,fontSize:11,color:T.inkSoft,width:16}}>{i+1}</div>
              <div style={{flex:1,display:'flex',justifyContent:'flex-start'}}>
                {revealed && r.p1s>0
                  ? <CardChip value={r.p1s} color={p1Color} />
                  : <div style={{width:36,height:48,borderRadius:9,background:'rgba(0,0,0,.1)',border:'2px dashed rgba(0,0,0,.15)'}} />}
              </div>
              <div style={{fontFamily:T.font,fontSize:revealed&&!win2?20:16,fontWeight:900,color:iconColor,width:28,textAlign:'center',transition:'all .3s'}}>{icon}</div>
              <div style={{flex:1,display:'flex',justifyContent:'flex-end'}}>
                {revealed && r.p2s>0
                  ? <CardChip value={r.p2s} color={p2Color} />
                  : <div style={{width:36,height:48,borderRadius:9,background:'rgba(0,0,0,.1)',border:'2px dashed rgba(0,0,0,.15)'}} />}
              </div>
            </div>
          );
        })}

        {/* Végeredmény — csak ha minden felfedve */}
        {allDone && (
          <div style={{
            background:resultBg,borderRadius:16,padding:'14px 16px',
            display:'flex',alignItems:'center',justifyContent:'space-between',gap:12,
            animation:'popIn .45s cubic-bezier(.2,.9,.3,1.2)',
          }}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:20,color:'#fff'}}>
              {winName ? winName+' nyert!' : 'Döntetlen!'}
            </div>
            <div style={{
              background:'rgba(255,255,255,.25)',borderRadius:999,
              padding:'7px 16px',fontFamily:T.font,fontWeight:800,fontSize:14,color:'#fff',whiteSpace:'nowrap',
            }}>
              {loseName ? `🎴 ${loseName} iszik ${diff}` : '🍺 +1 mindenki'}
            </div>
          </div>
        )}
      </div>
    );
  }

  // ── DONE (üres — auto-transition a reveal végén) ──────────────────────────
  if (S.phase === 'done') {
    return <div style={{background:CB_BG,borderRadius:20,padding:'40px',textAlign:'center',fontFamily:T.font,color:T.inkSoft}}>...</div>;
  }"""

assert OLD in src, 'CardBattle reveal+done block not found'
src = src.replace(OLD, NEW, 1)

# Remove the duplicate useEffect for done phase (it fires onAdvance/onResult — now handled in reveal)
OLD2 = """  React.useEffect(() => {
    if (S.phase !== 'done') return;
    const {p1W, p2W} = results;
    const p1id = challenger?.id;
    const p2id = opponent?.id;
    const diff = Math.abs(p1W - p2W);
    if (p1W > p2W) {
      if (onAdvance) onAdvance({[p2id]: diff}, {[p1id]: 1});
      if (onResult) onResult({ correct: true, playerName: p1Name, drinks: 0, subtitle: p1Name + ' nyerte a meccset!' });
    } else if (p2W > p1W) {
      if (onAdvance) onAdvance({[p1id]: diff}, {[p2id]: 1});
      if (onResult) onResult({ correct: false, playerName: p2Name, drinks: 0, subtitle: p2Name + ' nyerte a meccset!' });
    } else {
      if (onAdvance) onAdvance({[p1id]: 1, [p2id]: 1}, {});
      if (onResult) onResult({ correct: false, playerName: null, drinks: 1, subtitle: 'Döntetlen — mindenki iszik!' });
    }
  }, [S.phase]);"""
NEW2 = "  // onAdvance/onResult is now fired inside the reveal phase animation useEffect"
assert OLD2 in src, 'done useEffect not found'
src = src.replace(OLD2, NEW2, 1)

# version bump
assert 'v9.440' in src, 'version not found'
src = src.replace('v9.440', 'v9.441', 1)

with open('index.html','w',encoding='utf-8') as f: f.write(src)
print('OK')
