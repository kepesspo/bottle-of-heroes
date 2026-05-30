import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── New ZeneGame ──────────────────────────────────────────────────────────────
NEW_ZENE = r"""function ZeneGame({ gameIdx, onAdvance }) {
  const song = ZENE_SONGS[gameIdx % ZENE_SONGS.length];
  const [playing, setPlaying] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const [result, setResult] = useState(null);
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
        width: '100%', height: 80,
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

  const WAVE_H = [12,20,30,40,48,42,52,44,34,46,38,28,18,12];

  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:10 }}>
      <div ref={containerRef} style={{ position:'absolute', left:-9999, top:-9999, width:1, height:1, overflow:'hidden' }} />

      {/* Vinyl + static tonearm */}
      <div style={{ position:'relative', width:270, height:270, flexShrink:0 }}>
        {/* Spinning disc */}
        <div style={{ position:'absolute', left:10, top:10, width:250, height:250, transformOrigin:'center', animation: playing ? 'vinylSpin 2.6s linear infinite' : 'none' }}>
          <svg width="250" height="250" viewBox="0 0 250 250">
            <circle cx="125" cy="125" r="123" fill="#181818"/>
            {[112,100,88,76,65,56,47].map(r2 => (
              <circle key={r2} cx="125" cy="125" r={r2} fill="none" stroke="#282828" strokeWidth="1.8"/>
            ))}
            <circle cx="125" cy="125" r="46" fill="#B97060"/>
            <text x="125" y="133" textAnchor="middle" fontSize="26" fill="#1a1a1a">♫</text>
            <circle cx="125" cy="125" r="7" fill="#080808"/>
          </svg>
        </div>
        {/* Tonearm — does NOT spin */}
        <svg width="270" height="270" viewBox="0 0 270 270" style={{ position:'absolute', left:0, top:0, pointerEvents:'none' }}>
          <line x1="248" y1="22" x2="158" y2="150" stroke="#E0D8C8" strokeWidth="7" strokeLinecap="round"/>
          <circle cx="248" cy="22" r="12" fill="#1B2340" stroke="#E0D8C8" strokeWidth="2.5"/>
          <rect x="151" y="146" width="16" height="10" rx="2" fill="#333" transform="rotate(-52 159 151)"/>
        </svg>
      </div>

      {/* Waveform */}
      <div style={{ display:'flex', alignItems:'center', gap:3, height:54, marginTop:-6 }}>
        {WAVE_H.map((h, i) => (
          <div key={i} style={{
            width:5, borderRadius:3,
            background:'#1B2340',
            height:h,
            transformOrigin:'center',
            animation: playing ? `waveBar ${0.48 + i*0.065}s ease-in-out infinite` : 'none',
            animationDelay:`${i*0.055}s`,
            opacity: playing ? 1 : 0.4,
            transition:'opacity .3s',
          }}/>
        ))}
      </div>

      {/* Play + Reveal buttons */}
      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8 }}>
        {!playing
          ? <button onClick={handlePlay} style={{ width:'100%', padding:'15px 0', background:'#1B2340', border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:17, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:10 }}>
              <span style={{ fontSize:14 }}>▶</span><span>Lejátszás</span>
            </button>
          : <button onClick={handleStop} style={{ width:'100%', padding:'15px 0', background:'#1B2340', border:'none', borderRadius:16, color:'#F0C040', fontFamily:T.font, fontWeight:700, fontSize:17, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:10 }}>
              <span style={{ fontSize:14 }}>⏸</span><span>Megállítás</span>
            </button>
        }
        <button onClick={() => setRevealed(r=>!r)} style={{ width:'100%', padding:'14px 0', background:'#fff', border:'none', borderRadius:16, color:'#1B2340', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', boxShadow:'0 2px 10px rgba(0,0,0,0.14)', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
          <span>🔍</span><span>{revealed ? 'Elrejt' : 'Felfedés'}</span>
        </button>
      </div>

      {/* Revealed artist/title */}
      {revealed && (
        <div style={{ background:'rgba(255,255,255,0.65)', borderRadius:12, padding:'8px 18px', textAlign:'center' }}>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:16, color:'#1B2340', textTransform:'uppercase', letterSpacing:'0.06em' }}>{song.artist}</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:'#555', marginTop:2 }}>„{song.title}"</div>
        </div>
      )}

      {/* Result buttons — always visible */}
      {!result && (
        <div style={{ width:'100%', display:'flex', gap:10, marginTop:2 }}>
          <button onClick={() => handleResult('no')} style={{ flex:1, padding:'18px 8px', background:'#E8A090', border:'none', borderRadius:20, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer', lineHeight:1.35 }}>
            Nem ismertem<br/>fel
          </button>
          <button onClick={() => handleResult('yes')} style={{ flex:1, padding:'18px 8px', background:'#50A882', border:'none', borderRadius:20, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer' }}>
            Felismertem!
          </button>
        </div>
      )}

      {result && (
        <div style={{ marginTop:8, textAlign:'center', animation:'burstPop .3s' }}>
          <div style={{ fontSize:46 }}>{result === 'yes' ? '🎉' : '😅'}</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:16, color: result==='yes' ? '#50A882' : '#E8A090', marginTop:6 }}>
            {result === 'yes' ? 'Felismerted!' : 'Nem ismerted fel'}
          </div>
        </div>
      )}
    </div>
  );
}"""

# ── New KivagyokGame ──────────────────────────────────────────────────────────
NEW_KIVA = r"""function KivagyokGame({ gameIdx, onAdvance }) {
  const celeb = KIVAGYOK_CELEBS[gameIdx % KIVAGYOK_CELEBS.length];
  const [revealed, setRevealed] = useState(false);
  const [result, setResult] = useState(null);

  const infoParts = (celeb.info || '').split(' · ');
  const lifespan   = infoParts[0] || '';
  const occupation = infoParts[1] || '';

  const handleResult = (r) => {
    setResult(r);
    if (onAdvance) setTimeout(() => onAdvance(), 1800);
  };

  const stripeStyle = (w) => ({
    height:14, borderRadius:3,
    width: w || '100%',
    background:'repeating-linear-gradient(-45deg,#1e1e2e,#1e1e2e 4px,#2e2e3e 4px,#2e2e3e 8px)',
  });

  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:12 }}>
      {/* Dossier card */}
      <div style={{ width:'100%', background:'#EDE5CF', borderRadius:20, border:'2.5px solid #1B2340', overflow:'visible', position:'relative' }}>

        {/* Top section: photo (left) + fields (right) */}
        <div style={{ display:'flex', gap:12, padding:'14px 14px 12px', position:'relative' }}>
          {/* AKTA stamp */}
          <div style={{ position:'absolute', top:10, right:12, border:'2.5px solid #CC2222', borderRadius:5, padding:'2px 9px', color:'#CC2222', fontFamily:'monospace', fontWeight:900, fontSize:11, letterSpacing:'0.12em', transform:'rotate(8deg)', background:'transparent', zIndex:3, pointerEvents:'none' }}>
            AKTA #{String((gameIdx % KIVAGYOK_CELEBS.length) + 1).padStart(2,'0')}
          </div>

          {/* Photo */}
          <div style={{ width:100, height:118, background:'#C4CDD8', borderRadius:10, overflow:'hidden', flexShrink:0, display:'flex', alignItems:'center', justifyContent:'center', border:'1.5px solid #9aabb8' }}>
            {revealed
              ? <img src={celeb.img} alt="celeb" style={{ width:'100%', height:'100%', objectFit:'cover', objectPosition:'top' }} onError={e=>{e.target.style.display='none';}}/>
              : <svg width="56" height="64" viewBox="0 0 56 64" fill="none">
                  <circle cx="28" cy="20" r="14" fill="#8a9db0"/>
                  <ellipse cx="28" cy="54" rx="22" ry="14" fill="#8a9db0"/>
                </svg>
            }
          </div>

          {/* Fields */}
          <div style={{ flex:1, display:'flex', flexDirection:'column', gap:8, paddingRight:40 }}>
            <div>
              <div style={{ fontFamily:'monospace', fontSize:9, fontWeight:700, color:'#888', letterSpacing:'0.16em', marginBottom:4 }}>NÉV</div>
              {revealed
                ? <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'#1B2340', lineHeight:1.3 }}>{celeb.name}</div>
                : <div style={stripeStyle('90%')}/>
              }
            </div>
            {lifespan && (
              <div>
                <div style={{ fontFamily:'monospace', fontSize:9, fontWeight:700, color:'#888', letterSpacing:'0.16em', marginBottom:4 }}>ÉLETKOR</div>
                {revealed
                  ? <div style={{ fontFamily:T.font, fontSize:12, color:'#1B2340' }}>{lifespan}</div>
                  : <div style={stripeStyle('68%')}/>
                }
              </div>
            )}
            {occupation && (
              <div>
                <div style={{ fontFamily:'monospace', fontSize:9, fontWeight:700, color:'#888', letterSpacing:'0.16em', marginBottom:4 }}>FOGLALKOZÁS</div>
                {revealed
                  ? <div style={{ fontFamily:T.font, fontSize:12, color:'#1B2340' }}>{occupation}</div>
                  : <div style={stripeStyle('80%')}/>
                }
              </div>
            )}
          </div>
        </div>

        {/* Dashed separator */}
        <div style={{ borderTop:'1.5px dashed rgba(27,35,64,0.3)', margin:'0 14px' }}/>

        {/* Hint box + Akta felfedése button */}
        <div style={{ padding:'12px 14px 14px', display:'flex', flexDirection:'column', gap:10 }}>
          <div style={{ display:'flex', gap:10, alignItems:'flex-start' }}>
            <div style={{ width:36, height:36, minWidth:36, background:'#1B2340', borderRadius:10, display:'flex', alignItems:'center', justifyContent:'center' }}>
              <span style={{ fontSize:18, color:'#F0C040', fontWeight:900 }}>?</span>
            </div>
            <div style={{ fontFamily:T.font, fontSize:13, color:'#2a2a3a', lineHeight:1.5 }}>
              Tippelj az <strong>életkorára</strong> vagy a <strong>foglalkozására</strong> — aztán fedd fel az aktát.
            </div>
          </div>
          <button onClick={() => setRevealed(r=>!r)} style={{ width:'100%', padding:'14px 0', background:'#1B2340', border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
            <span>🔍</span><span>{revealed ? 'Elrejt' : 'Akta felfedése'}</span>
          </button>
        </div>
      </div>

      {/* Result buttons — always visible, outside card */}
      {!result && (
        <div style={{ width:'100%', display:'flex', gap:10, marginTop:2 }}>
          <button onClick={() => handleResult('no')} style={{ flex:1, padding:'18px 8px', background:'#E8A090', border:'none', borderRadius:20, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer', lineHeight:1.35 }}>
            Nem ismertem<br/>meg
          </button>
          <button onClick={() => handleResult('yes')} style={{ flex:1, padding:'18px 8px', background:'#50A882', border:'none', borderRadius:20, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer' }}>
            Megismertem!
          </button>
        </div>
      )}

      {result && (
        <div style={{ marginTop:8, textAlign:'center', animation:'burstPop .3s' }}>
          <div style={{ fontSize:46 }}>{result === 'yes' ? '🎉' : '😅'}</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:16, color: result==='yes' ? '#50A882' : '#E8A090', marginTop:6 }}>
            {result === 'yes' ? 'Megismerted!' : 'Nem ismerted meg'}
          </div>
        </div>
      )}
    </div>
  );
}"""

# ── Replace ZeneGame (from function def to just before KivagyokGame) ──────────
html = re.sub(
    r'function ZeneGame\(\{ gameIdx, onAdvance \}\) \{.*?\n\}(?=\n\nfunction KivagyokGame)',
    NEW_ZENE,
    html,
    flags=re.DOTALL
)

# ── Replace KivagyokGame (from function def to just before IGAZ_HAMIS) ────────
html = re.sub(
    r'function KivagyokGame\(\{ gameIdx, onAdvance \}\) \{.*?\n\}(?=\n\nconst IGAZ_HAMIS)',
    NEW_KIVA,
    html,
    flags=re.DOTALL
)

# ── Version bump ──────────────────────────────────────────────────────────────
html = html.replace(
    'Verzió 5.13 · DNR · 2026.05.30 18:00',
    'Verzió 5.14 · DNR · 2026.05.30 19:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
