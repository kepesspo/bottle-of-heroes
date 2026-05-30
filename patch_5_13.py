import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Add CSS keyframes ──────────────────────────────────────────────────────
OLD_KF = '    @keyframes alertPulse { 0%,100%{box-shadow:0 0 0 0 rgba(244,160,74,0)} 50%{box-shadow:0 0 0 6px rgba(244,160,74,0.35)} }'
NEW_KF = OLD_KF + """
    @keyframes vinylSpin  { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
    @keyframes waveBar    { 0%,100%{transform:scaleY(0.25)} 50%{transform:scaleY(1)} }"""
html = html.replace(OLD_KF, NEW_KF, 1)

# ── 2. Replace ZeneGame ───────────────────────────────────────────────────────
OLD_ZENE = '''function ZeneGame({ gameIdx }) {
  const song = ZENE_SONGS[gameIdx % ZENE_SONGS.length];
  const [playing, setPlaying] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const ctrlRef = useRef(null);
  const containerRef = useRef(null);

  // Create a new Spotify embed controller whenever the song changes
  useEffect(() => {
    setPlaying(false);
    setRevealed(false);

    const setupCtrl = (IFrameAPI) => {
      // Destroy previous controller
      try { if (ctrlRef.current) ctrlRef.current.pause(); } catch(e) {}
      ctrlRef.current = null;
      if (containerRef.current) containerRef.current.innerHTML = '';

      IFrameAPI.createController(containerRef.current, {
        uri: `spotify:track:${song.spotifyId}`,
        width: '100%',
        height: 80,
      }, (ctrl) => { ctrlRef.current = ctrl; });
    };

    if (window._spotifyIFrameAPI) {
      setupCtrl(window._spotifyIFrameAPI);
    } else {
      const iv = setInterval(() => {
        if (window._spotifyIFrameAPI) { clearInterval(iv); setupCtrl(window._spotifyIFrameAPI); }
      }, 300);
      return () => clearInterval(iv);
    }

    return () => {
      try { if (ctrlRef.current) ctrlRef.current.pause(); } catch(e) {}
    };
  }, [song.spotifyId]);

  const handlePlay = () => {
    try { ctrlRef.current.play(); setPlaying(true); } catch(e) {}
  };
  const handleStop = () => {
    try { ctrlRef.current.pause(); setPlaying(false); } catch(e) {}
  };

  return (
    <div style={{ width:\'100%\', display:\'flex\', flexDirection:\'column\', gap:8, alignItems:\'center\' }}>
      {/* Spotify embed lives here — covered by our UI overlay */}
      <div onContextMenu={e=>e.preventDefault()} style={{ position:\'relative\', width:\'100%\', maxWidth:340, height:80, borderRadius:12, overflow:\'hidden\', boxShadow:T.shadow, userSelect:\'none\', WebkitUserSelect:\'none\' }}>
        <div ref={containerRef} style={{ width:\'100%\', height:\'100%\' }} />
        {/* Full overlay — completely hides Spotify UI incl. track name */}
        <div style={{ position:\'absolute\', inset:0, background: playing ? \'linear-gradient(135deg,#1a1a2e,#16213e)\' : \'#121212\', display:\'flex\', alignItems:\'center\', justifyContent:\'center\', gap:12 }}>
          {playing
            ? <><div style={{ fontSize:32, animation:\'pulse 1.4s infinite\' }}>🎵</div><div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:\'rgba(255,255,255,0.7)\', textTransform:\'uppercase\', letterSpacing:\'0.07em\' }}>Hallgasd meg!</div></>
            : <div style={{ fontFamily:T.font, fontSize:11, color:\'rgba(255,255,255,0.4)\', textTransform:\'uppercase\', letterSpacing:\'0.07em\' }}>Spotify betöltés…</div>
          }
        </div>
      </div>
      <div style={{ display:\'flex\', gap:8 }}>
        {!playing
          ? <button onClick={handlePlay} style={{ padding:\'10px 22px\', background:`${T.purple}22`, border:`2px solid ${T.purple}`, color:T.purple, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, borderRadius:12, cursor:\'pointer\', display:\'flex\', alignItems:\'center\', gap:6 }}>▶ Lejátszás</button>
          : <button onClick={handleStop} style={{ padding:\'10px 22px\', background:T.coralSoft, border:\'none\', color:T.coral, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, borderRadius:12, cursor:\'pointer\' }}>⏹ Stop</button>
        }
        <button onClick={() => setRevealed(r => !r)} style={{ padding:\'8px 20px\', background: revealed ? T.mint : T.surface, border:\'none\', color: revealed ? \'#fff\' : T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, borderRadius:12, cursor:\'pointer\', boxShadow:T.shadow }}>
          {revealed ? \'▲ Elrejt\' : \'🎵 Felfed\'}
        </button>
      </div>
      {revealed && (
        <div style={{ background:T.surface, borderRadius:14, padding:\'10px 18px\', textAlign:\'center\', boxShadow:T.shadow, animation:\'popIn .3s\' }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:T.ink, textTransform:\'uppercase\', letterSpacing:T.letterDisplay }}>{song.artist}</div>
          <div style={{ fontFamily:T.font, fontSize:13, fontWeight:600, color:T.inkSoft, marginTop:3 }}>„{song.title}"</div>
        </div>
      )}
    </div>
  );
}'''

NEW_ZENE = '''function ZeneGame({ gameIdx, onAdvance }) {
  const song = ZENE_SONGS[gameIdx % ZENE_SONGS.length];
  const [playing, setPlaying] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const [result, setResult] = useState(null); // null | 'yes' | 'no'
  const ctrlRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    setPlaying(false);
    setRevealed(false);
    setResult(null);

    const setupCtrl = (IFrameAPI) => {
      try { if (ctrlRef.current) ctrlRef.current.pause(); } catch(e) {}
      ctrlRef.current = null;
      if (containerRef.current) containerRef.current.innerHTML = '';
      IFrameAPI.createController(containerRef.current, {
        uri: `spotify:track:${song.spotifyId}`,
        width: '100%',
        height: 80,
      }, (ctrl) => { ctrlRef.current = ctrl; });
    };

    if (window._spotifyIFrameAPI) {
      setupCtrl(window._spotifyIFrameAPI);
    } else {
      const iv = setInterval(() => {
        if (window._spotifyIFrameAPI) { clearInterval(iv); setupCtrl(window._spotifyIFrameAPI); }
      }, 300);
      return () => clearInterval(iv);
    }
    return () => { try { if (ctrlRef.current) ctrlRef.current.pause(); } catch(e) {} };
  }, [song.spotifyId]);

  const handlePlay = () => { try { ctrlRef.current.play(); setPlaying(true); } catch(e) {} };
  const handleStop = () => { try { ctrlRef.current.pause(); setPlaying(false); } catch(e) {} };

  const handleResult = (r) => {
    setResult(r);
    handleStop();
    if (onAdvance) setTimeout(() => onAdvance(), 1800);
  };

  // Vinyl SVG grooves
  const vinylEl = (
    <svg viewBox="0 0 160 160" width="160" height="160" style={{ display:'block', animation: playing ? 'vinylSpin 2.4s linear infinite' : 'none' }}>
      <circle cx="80" cy="80" r="80" fill="#1a1a1a"/>
      {[72,62,52,42,32].map(r2 => <circle key={r2} cx="80" cy="80" r={r2} fill="none" stroke="#2a2a2a" strokeWidth="2"/>)}
      <circle cx="80" cy="80" r="22" fill="#111"/>
      <circle cx="80" cy="80" r="14" fill="#c8a84b"/>
      <circle cx="80" cy="80" r="5" fill="#111"/>
      <text x="80" y="83" textAnchor="middle" fontSize="5" fontFamily="sans-serif" fill="#111" fontWeight="bold">♪</text>
    </svg>
  );

  // Waveform bars
  const bars = Array.from({length:9}, (_,i) => (
    <div key={i} style={{
      width:5, borderRadius:3,
      background: playing ? '#c8a84b' : '#444',
      height: 36,
      transformOrigin:'center bottom',
      animation: playing ? `waveBar ${0.6 + i*0.08}s ease-in-out infinite` : 'none',
      animationDelay: `${i*0.07}s`,
      transform: playing ? undefined : 'scaleY(0.25)',
    }}/>
  ));

  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:0 }}>
      {/* Hidden Spotify embed */}
      <div ref={containerRef} style={{ position:'absolute', left:-9999, top:-9999, width:1, height:1, overflow:'hidden' }} />

      {/* Vinyl */}
      <div style={{ margin:'8px 0 12px', filter: playing ? 'drop-shadow(0 0 18px rgba(200,168,75,0.45))' : 'none', transition:'filter .4s' }}>
        {vinylEl}
      </div>

      {/* Waveform */}
      <div style={{ display:'flex', alignItems:'center', gap:4, height:40, marginBottom:18 }}>
        {bars}
      </div>

      {/* Buttons — hidden after result */}
      {!result && (
        <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:10, paddingLeft:4, paddingRight:4 }}>
          {!playing
            ? <button onClick={handlePlay} style={{ width:'100%', padding:'14px 0', background:'#1B2340', border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', letterSpacing:'0.04em' }}>▶ Lejátszás</button>
            : <button onClick={handleStop} style={{ width:'100%', padding:'14px 0', background:'#1B2340', border:'none', borderRadius:14, color:'#F5A623', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', letterSpacing:'0.04em' }}>⏸ Megállítás</button>
          }
          <button onClick={() => setRevealed(r => !r)} style={{ width:'100%', padding:'13px 0', background: revealed ? '#2e3a5c' : T.surface, border:'none', borderRadius:14, color: revealed ? '#c8a84b' : T.ink, fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer', boxShadow:T.shadow }}>
            {revealed ? '▲ Elrejt' : '🎵 Felfedés'}
          </button>
        </div>
      )}

      {/* Revealed artist/title */}
      {revealed && !result && (
        <div style={{ marginTop:12, background:T.surface, borderRadius:14, padding:'10px 22px', textAlign:'center', boxShadow:T.shadow, animation:'popIn .25s' }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay }}>{song.artist}</div>
          <div style={{ fontFamily:T.font, fontSize:13, fontWeight:600, color:T.inkSoft, marginTop:3 }}>„{song.title}"</div>
        </div>
      )}

      {/* Result buttons — appear after reveal */}
      {revealed && !result && (
        <div style={{ width:'100%', display:'flex', gap:10, marginTop:14, paddingLeft:4, paddingRight:4 }}>
          <button onClick={() => handleResult('no')} style={{ flex:1, padding:'13px 0', background:'#FF6B6B22', border:'2px solid #FF6B6B', borderRadius:14, color:'#FF6B6B', fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>
            ✗ Nem ismertem fel
          </button>
          <button onClick={() => handleResult('yes')} style={{ flex:1, padding:'13px 0', background:'#2ECC7122', border:'2px solid #2ECC71', borderRadius:14, color:'#2ECC71', fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>
            ✓ Felismertem!
          </button>
        </div>
      )}

      {/* Result feedback */}
      {result && (
        <div style={{ marginTop:8, textAlign:'center', animation:'burstPop .3s' }}>
          <div style={{ fontSize:42 }}>{result === 'yes' ? '🎉' : '😅'}</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color: result === 'yes' ? '#2ECC71' : '#FF6B6B', marginTop:4 }}>
            {result === 'yes' ? 'Felismerted!' : 'Nem ismerted fel'}
          </div>
        </div>
      )}
    </div>
  );
}'''

html = html.replace(OLD_ZENE, NEW_ZENE, 1)

# ── 3. Replace KivagyokGame ───────────────────────────────────────────────────
OLD_KIVA = '''function KivagyokGame({ gameIdx }) {
  const celeb = KIVAGYOK_CELEBS[gameIdx % KIVAGYOK_CELEBS.length];
  const [revealed, setRevealed] = useState(false);
  return (
    <div style={{ width:\'100%\', display:\'flex\', flexDirection:\'column\', gap:8, alignItems:\'center\' }}>
      <div style={{ width:140, height:160, borderRadius:16, overflow:\'hidden\', boxShadow:T.shadowLift, flexShrink:0 }}>
        <img src={celeb.img} alt="celeb" style={{ width:\'100%\', height:\'100%\', objectFit:\'cover\', objectPosition:\'top\' }} onError={e => { e.target.style.display=\'none\'; }} />
      </div>
      <button onClick={() => setRevealed(r => !r)} style={{ padding:\'10px 24px\', background: revealed ? T.mint : T.surface, border:\'none\', color: revealed ? \'#fff\' : T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:15, borderRadius:12, cursor:\'pointer\', boxShadow:T.shadow }}>
        {revealed ? \'▲ Elrejt\' : \'🔍 Felfed\'}
      </button>
      {revealed && (
        <div style={{ background:T.surface, borderRadius:14, padding:\'10px 18px\', textAlign:\'center\', boxShadow:T.shadow, animation:\'popIn .3s\' }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:18, color:T.ink, textTransform:\'uppercase\', letterSpacing:T.letterDisplay }}>{celeb.name}</div>
          <div style={{ fontFamily:T.font, fontSize:13, fontWeight:600, color:T.inkSoft, marginTop:3 }}>{celeb.info}</div>
        </div>
      )}
    </div>
  );
}'''

NEW_KIVA = '''function KivagyokGame({ gameIdx, onAdvance }) {
  const celeb = KIVAGYOK_CELEBS[gameIdx % KIVAGYOK_CELEBS.length];
  const [revealed, setRevealed] = useState(false);
  const [result, setResult] = useState(null); // null | 'yes' | 'no'

  const infoParts = (celeb.info || '').split(' · ');
  const lifespan = infoParts[0] || '';
  const occupation = infoParts[1] || '';

  const handleResult = (r) => {
    setResult(r);
    if (onAdvance) setTimeout(() => onAdvance(), 1800);
  };

  const BlackBar = ({ label, value, show }) => (
    <div style={{ display:'flex', alignItems:'center', gap:10, padding:'9px 12px', borderBottom:'1px solid rgba(0,0,0,0.07)' }}>
      <div style={{ fontFamily:'monospace', fontSize:10, fontWeight:700, color:'#888', letterSpacing:'0.12em', minWidth:88, textTransform:'uppercase' }}>{label}</div>
      <div style={{
        flex:1, padding:'4px 8px', borderRadius:4,
        background: show ? 'transparent' : '#1a1a1a',
        color: show ? '#1a1a1a' : 'transparent',
        fontSize:13, fontFamily:T.font, fontWeight:600,
        transition:'background .3s, color .3s',
        minHeight:22,
      }}>{value}</div>
    </div>
  );

  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:0 }}>
      {/* Dossier card */}
      <div style={{ width:'100%', maxWidth:340, background:'#F5F0E4', borderRadius:16, overflow:'hidden', boxShadow:'0 4px 20px rgba(0,0,0,0.18)', position:'relative' }}>
        {/* Red stamp */}
        <div style={{ position:'absolute', top:14, right:14, zIndex:3, transform:'rotate(12deg)', border:'3px solid #cc2222', borderRadius:4, padding:'2px 8px', color:'#cc2222', fontFamily:'monospace', fontWeight:900, fontSize:11, letterSpacing:'0.15em', opacity:0.85, pointerEvents:'none' }}>
          AKTA #{String((gameIdx % KIVAGYOK_CELEBS.length) + 1).padStart(2,'0')}
        </div>

        {/* Photo */}
        <div style={{ width:'100%', height:180, background:'#c8bfa8', overflow:'hidden', display:'flex', alignItems:'center', justifyContent:'center' }}>
          <img src={celeb.img} alt="celeb"
            style={{ width:'100%', height:'100%', objectFit:'cover', objectPosition:'top',
              filter: revealed ? 'none' : 'blur(14px) brightness(0.6)',
              transition:'filter .5s',
            }}
            onError={e => { e.target.style.display='none'; }} />
        </div>

        {/* Fields */}
        <div style={{ padding:'8px 0 4px' }}>
          <BlackBar label="NÉV" value={celeb.name} show={revealed} />
          {lifespan && <BlackBar label="ÉLETKOR" value={lifespan} show={revealed} />}
          {occupation && <BlackBar label="FOGLALKOZÁS" value={occupation} show={revealed} />}
        </div>
      </div>

      {/* Akta felfedése button */}
      {!result && (
        <button onClick={() => setRevealed(r => !r)} style={{ width:'100%', maxWidth:340, marginTop:14, padding:'14px 0', background: revealed ? '#2e3a5c' : '#1B2340', border:'none', borderRadius:14, color: revealed ? '#c8a84b' : '#fff', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', letterSpacing:'0.04em' }}>
          {revealed ? '▲ Elrejt' : '🗂 Akta felfedése'}
        </button>
      )}

      {/* Result buttons */}
      {revealed && !result && (
        <div style={{ width:'100%', maxWidth:340, display:'flex', gap:10, marginTop:10 }}>
          <button onClick={() => handleResult('no')} style={{ flex:1, padding:'13px 0', background:'#FF6B6B22', border:'2px solid #FF6B6B', borderRadius:14, color:'#FF6B6B', fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>
            ✗ Nem ismertem meg
          </button>
          <button onClick={() => handleResult('yes')} style={{ flex:1, padding:'13px 0', background:'#2ECC7122', border:'2px solid #2ECC71', borderRadius:14, color:'#2ECC71', fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>
            ✓ Megismertem!
          </button>
        </div>
      )}

      {/* Result feedback */}
      {result && (
        <div style={{ marginTop:12, textAlign:'center', animation:'burstPop .3s' }}>
          <div style={{ fontSize:42 }}>{result === 'yes' ? '🎉' : '😅'}</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color: result === 'yes' ? '#2ECC71' : '#FF6B6B', marginTop:4 }}>
            {result === 'yes' ? 'Megismerted!' : 'Nem ismerted meg'}
          </div>
        </div>
      )}
    </div>
  );
}'''

html = html.replace(OLD_KIVA, NEW_KIVA, 1)

# ── 4. Update GameContent router ──────────────────────────────────────────────
html = html.replace(
    "if (gameId === 'zene') return <ZeneGame key={gameIdx} gameIdx={gameIdx} />;",
    "if (gameId === 'zene') return <ZeneGame key={gameIdx} gameIdx={gameIdx} onAdvance={onAdvance} />;",
    1
)
html = html.replace(
    "if (gameId === 'kivagyok') return <KivagyokGame key={gameIdx} gameIdx={gameIdx} />;",
    "if (gameId === 'kivagyok') return <KivagyokGame key={gameIdx} gameIdx={gameIdx} onAdvance={onAdvance} />;",
    1
)

# ── 5. Version bump ───────────────────────────────────────────────────────────
html = html.replace(
    'Verzió 5.12 · DNR · 2026.05.30 17:00',
    'Verzió 5.13 · DNR · 2026.05.30 18:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
