with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace OTDOLOG_CATEGORIES with 50 entries + shuffle
OLD_CATS = """const OTDOLOG_CATEGORIES = [
  'Filmcímek','Állatfajták','Zenekarok','Fővárosok','Sportok',
  'Gyümölcsök','Zöldségek','Magyar városok','Autómárkák','Ételek',
  'Italok','Foglalkozások','Tánctípusok','Szerszámok','Bútorok',
  'Ruhafélék','Virágok','Madárfajták','Hegyek','Folyók',
  'Filmszínészek','Énekesek','Sportolók','Márkák','Konyhai eszközök',
  'Technológiai cégek','Magyar sütemények','Tengergyümölcsök','Hüvelyesek','Fűszerek',
];"""

NEW_CATS = """const OTDOLOG_CATEGORIES = [
  'Filmcímek','Állatfajták','Zenekarok','Fővárosok','Sportok',
  'Gyümölcsök','Zöldségek','Magyar városok','Autómárkák','Ételek',
  'Italok','Foglalkozások','Tánctípusok','Szerszámok','Bútorok',
  'Ruhafélék','Virágok','Madárfajták','Hegyek','Folyók',
  'Filmszínészek','Énekesek','Sportolók','Márkák','Konyhai eszközök',
  'Technológiai cégek','Magyar sütemények','Tengergyümölcsök','Hüvelyesek','Fűszerek',
  'Mesehősök','Szuperhősök','Hangszerek','Nyelvek','Vallások',
  'Bolygók','Rovarfajták','Halak','Gombafajták','Fafajták',
  'Magyar ételek','Koktélok','Sörök','Sportcsapatok','Olimpiai sportok',
  'Oscar-díjas filmek','Zenei műfajok','Társasjátékok','Kártyajátékok','Videójátékok',
];
(()=>{ for(let i=OTDOLOG_CATEGORIES.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [OTDOLOG_CATEGORIES[i],OTDOLOG_CATEGORIES[j]]=[OTDOLOG_CATEGORIES[j],OTDOLOG_CATEGORIES[i]]; } })();"""

assert OLD_CATS in content, 'OTDOLOG_CATEGORIES not found'
content = content.replace(OLD_CATS, NEW_CATS, 1)

# 2. Rewrite OtdologGame: add category reveal step, onResult, play-actions style buttons
OLD_GAME = """function OtdologGame({ gameIdx, challenger, onAdvance }) {
  const cat = OTDOLOG_CATEGORIES[gameIdx % OTDOLOG_CATEGORIES.length];
  const [timeLeft, setTimeLeft] = React.useState(5);
  const [checked, setChecked] = React.useState([false,false,false,false,false]);
  const [running, setRunning] = React.useState(false);
  const [expired, setExpired] = React.useState(false);

  React.useEffect(() => {
    setTimeLeft(5); setChecked([false,false,false,false,false]); setRunning(false); setExpired(false);
  }, [gameIdx]);

  React.useEffect(() => {
    if (!running || expired) return;
    const iv = setInterval(() => {
      setTimeLeft(prev => {
        const next = +(prev - 0.05).toFixed(2);
        if (next <= 0) { setExpired(true); setRunning(false); return 0; }
        return next;
      });
    }, 50);
    return () => clearInterval(iv);
  }, [running, expired]);

  const checkedCount = checked.filter(Boolean).length;
  const pct = timeLeft / 5;
  const r = 72, circ = +(2 * Math.PI * r).toFixed(1);
  const timerColor = pct > 0.5 ? T.mint : pct > 0.2 ? T.yellow : T.coral;
  const doWin = () => onAdvance && onAdvance({});
  const doLose = () => onAdvance && onAdvance(challenger ? {[challenger.id]:1} : {});

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, width:'100%' }}>
      <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'20px 24px', textAlign:'center', boxShadow:T.shadow }}>
        <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, letterSpacing:'0.08em', textTransform:'uppercase', marginBottom:6 }}>KATEGÓRIA</div>
        <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:26, color:T.ink, lineHeight:1.1 }}>{cat}</div>
      </div>

      {(!running && !expired) ? (
        <button onClick={() => setRunning(true)} style={{ width:148, height:148, borderRadius:'50%', background:T.mint, border:'none', cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:4, boxShadow:T.shadow }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:36, color:'#fff', lineHeight:1 }}>▶</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)' }}>Indítás</div>
        </button>
      ) : (
        <div style={{ position:'relative', width:160, height:160 }}>
          <svg viewBox="0 0 160 160" style={{ position:'absolute', inset:0, width:'100%', height:'100%', transform:'rotate(-90deg)' }}>
            <circle cx="80" cy="80" r={r} fill="none" stroke={`${T.inkMute}30`} strokeWidth="11" />
            <circle cx="80" cy="80" r={r} fill="none" stroke={timerColor} strokeWidth="11"
              strokeDasharray={circ} strokeDashoffset={+(circ*(1-pct)).toFixed(1)} strokeLinecap="round"
              style={{ transition:'stroke .3s' }} />
          </svg>
          <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:52, color:T.ink, lineHeight:1 }}>{expired ? '0' : Math.ceil(timeLeft)}</div>
            <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft, letterSpacing:'0.07em' }}>MP</div>
          </div>
        </div>
      )}

      {(running || expired) && (
        <div style={{ display:'flex', gap:8 }}>
          {checked.map((c, i) => (
            <div key={i} onClick={() => { const n=[...checked]; n[i]=!n[i]; setChecked(n); }}
              style={{ width:50, height:50, borderRadius:14, cursor:'pointer', background:c?T.mint:T.surface, display:'grid', placeItems:'center', boxShadow:T.shadow, border:`2px solid ${c?T.mint:'transparent'}`, transition:'all .15s' }}>
              {c ? <span style={{ color:'#fff', fontSize:20 }}>✓</span>
                 : <span style={{ fontFamily:T.font, fontWeight:700, fontSize:17, color:T.inkSoft }}>{i+1}</span>}
            </div>
          ))}
        </div>
      )}

      {(running || expired) && (
        <div style={{ fontFamily:T.font, fontSize:14, fontWeight:600, color:T.inkSoft }}>
          {checkedCount===5 ? '\\U0001f389 Mind megvan!' : checkedCount>0 ? `${checkedCount} / 5 megvan — hajrá!` : expired ? 'Idő lejárt!' : 'Jelöld be amit kimondottál!'}
        </div>
      )}

      {(running || expired) && (
        <div style={{ display:'flex', gap:10, width:'100%' }}>
          <button onClick={doLose} style={{ flex:1, padding:'14px', background:T.coral, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow }}>Nem sikerült</button>
          <button onClick={doWin} style={{ flex:1, padding:'14px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, cursor:'pointer', boxShadow:T.shadow }}>Megvan! \\U0001f389</button>
        </div>
      )}
    </div>
  );
}"""

NEW_GAME = """function OtdologGame({ gameIdx, challenger, onAdvance, onResult }) {
  const cat = OTDOLOG_CATEGORIES[gameIdx % OTDOLOG_CATEGORIES.length];
  const [phase, setPhase] = React.useState('ready'); // 'ready' | 'running' | 'done'
  const [timeLeft, setTimeLeft] = React.useState(5);
  const [checked, setChecked] = React.useState([false,false,false,false,false]);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPhase('ready'); setTimeLeft(5); setChecked([false,false,false,false,false]); advancedRef.current = false;
  }, [gameIdx]);

  React.useEffect(() => {
    if (phase !== 'running') return;
    const iv = setInterval(() => {
      setTimeLeft(prev => {
        const next = +(prev - 0.05).toFixed(2);
        if (next <= 0) { setPhase('done'); return 0; }
        return next;
      });
    }, 50);
    return () => clearInterval(iv);
  }, [phase]);

  const checkedCount = checked.filter(Boolean).length;
  const pct = timeLeft / 5;
  const r = 72, circ = +(2 * Math.PI * r).toFixed(1);
  const timerColor = pct > 0.5 ? T.mint : pct > 0.2 ? T.yellow : T.coral;

  const handleResult = (correct) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    const dm = {};
    const pm = {};
    if (!correct && challenger) dm[challenger.id] = 1;
    if (correct && challenger) pm[challenger.id] = 1;
    onAdvance && onAdvance(dm, pm);
    onResult && onResult({ correct, playerName: challenger ? challenger.name : null, drinks: correct ? 0 : 1 });
  };

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, width:'100%' }}>

      {/* Category card — hidden until started */}
      <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'20px 24px', textAlign:'center', boxShadow:T.shadow }}>
        <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, letterSpacing:'0.08em', textTransform:'uppercase', marginBottom:6 }}>KATEGÓRIA</div>
        {phase === 'ready' ? (
          <div style={{ height:34, borderRadius:8, background:'repeating-linear-gradient(-45deg,#e0e4f0,#e0e4f0 4px,#d0d4e4 4px,#d0d4e4 8px)' }}/>
        ) : (
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:26, color:T.ink, lineHeight:1.1, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)' }}>{cat}</div>
        )}
      </div>

      {phase === 'ready' ? (
        <button onClick={() => setPhase('running')} style={{ width:148, height:148, borderRadius:'50%', background:T.mint, border:'none', cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:4, boxShadow:T.shadow }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:36, color:'#fff', lineHeight:1 }}>▶</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)' }}>Felfed & Indít</div>
        </button>
      ) : (
        <div style={{ position:'relative', width:160, height:160 }}>
          <svg viewBox="0 0 160 160" style={{ position:'absolute', inset:0, width:'100%', height:'100%', transform:'rotate(-90deg)' }}>
            <circle cx="80" cy="80" r={r} fill="none" stroke={`${T.inkMute}30`} strokeWidth="11" />
            <circle cx="80" cy="80" r={r} fill="none" stroke={timerColor} strokeWidth="11"
              strokeDasharray={circ} strokeDashoffset={+(circ*(1-pct)).toFixed(1)} strokeLinecap="round"
              style={{ transition:'stroke .3s' }} />
          </svg>
          <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:52, color:T.ink, lineHeight:1 }}>{phase==='done' ? '0' : Math.ceil(timeLeft)}</div>
            <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft, letterSpacing:'0.07em' }}>MP</div>
          </div>
        </div>
      )}

      {phase !== 'ready' && (
        <div style={{ display:'flex', gap:8 }}>
          {checked.map((c, i) => (
            <div key={i} onClick={() => { const n=[...checked]; n[i]=!n[i]; setChecked(n); }}
              style={{ width:50, height:50, borderRadius:14, cursor:'pointer', background:c?T.mint:T.surface, display:'grid', placeItems:'center', boxShadow:T.shadow, border:`2px solid ${c?T.mint:'transparent'}`, transition:'all .15s' }}>
              {c ? <span style={{ color:'#fff', fontSize:20 }}>✓</span>
                 : <span style={{ fontFamily:T.font, fontWeight:700, fontSize:17, color:T.inkSoft }}>{i+1}</span>}
            </div>
          ))}
        </div>
      )}

      {phase !== 'ready' && (
        <div style={{ fontFamily:T.font, fontSize:14, fontWeight:600, color:T.inkSoft }}>
          {checkedCount===5 ? '🎉 Mind megvan!' : checkedCount>0 ? `${checkedCount} / 5 megvan — hajrá!` : phase==='done' ? 'Idő lejárt!' : 'Jelöld be amit kimondottál!'}
        </div>
      )}

      {/* Result buttons — play-actions style, shown after timer started */}
      {phase !== 'ready' && !advancedRef.current && (
        <div className="play-actions" style={{ width:'100%' }}>
          <button onClick={() => handleResult(false)} style={{ flex:1, minHeight:60, border:'none', background:T.coral, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:17, borderRadius:16, cursor:'pointer', boxShadow:T.shadow }}>Nem sikerült 😔</button>
          <button onClick={() => handleResult(true)} style={{ flex:1, minHeight:60, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:17, borderRadius:16, cursor:'pointer', boxShadow:T.shadow }}>Megvan! 🎉</button>
        </div>
      )}
    </div>
  );
}"""

assert OLD_GAME in content, 'OtdologGame not found'
content = content.replace(OLD_GAME, NEW_GAME, 1)

# 3. Pass onResult to OtdologGame in GameContent
OLD_GC = "if (gameId === 'otdolog') return <OtdologGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} />;"
NEW_GC = "if (gameId === 'otdolog') return <OtdologGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;"
assert OLD_GC in content, 'OtdologGame GameContent call not found'
content = content.replace(OLD_GC, NEW_GC, 1)

# 4. Version bump
assert 'Verzió 5.78' in content
content = content.replace('Verzió 5.78', 'Verzió 5.79', 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('OK — OtdologGame: 50 kategória, random, felfed gomb, onResult, play-actions gombok, v5.79')
