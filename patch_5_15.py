import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. ZeneGame: remove result state/buttons, fix Spotify hide ────────────────
NEW_ZENE = r"""function ZeneGame({ gameIdx }) {
  const song = ZENE_SONGS[gameIdx % ZENE_SONGS.length];
  const [playing, setPlaying] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const ctrlRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    setPlaying(false);
    setRevealed(false);
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

  const WAVE_H = [12,20,30,40,48,42,52,44,34,46,38,28,18,12];

  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:10 }}>
      {/* Spotify embed hidden with collapsed wrapper */}
      <div style={{ height:0, overflow:'hidden', width:'100%' }}>
        <div ref={containerRef} style={{ width:'100%', height:80 }} />
      </div>

      {/* Vinyl + static tonearm */}
      <div style={{ position:'relative', width:270, height:270, flexShrink:0 }}>
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
            width:5, borderRadius:3, background:'#1B2340', height:h,
            transformOrigin:'center',
            animation: playing ? `waveBar ${0.48 + i*0.065}s ease-in-out infinite` : 'none',
            animationDelay:`${i*0.055}s`,
            opacity: playing ? 1 : 0.4, transition:'opacity .3s',
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

      {revealed && (
        <div style={{ background:'rgba(255,255,255,0.65)', borderRadius:12, padding:'8px 18px', textAlign:'center' }}>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:16, color:'#1B2340', textTransform:'uppercase', letterSpacing:'0.06em' }}>{song.artist}</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:'#555', marginTop:2 }}>„{song.title}"</div>
        </div>
      )}
    </div>
  );
}"""

# ── 2. KivagyokGame: remove result state/buttons ──────────────────────────────
NEW_KIVA = r"""function KivagyokGame({ gameIdx }) {
  const celeb = KIVAGYOK_CELEBS[gameIdx % KIVAGYOK_CELEBS.length];
  const [revealed, setRevealed] = useState(false);

  const infoParts = (celeb.info || '').split(' · ');
  const lifespan   = infoParts[0] || '';
  const occupation = infoParts[1] || '';

  const stripeStyle = (w) => ({
    height:14, borderRadius:3, width: w || '100%',
    background:'repeating-linear-gradient(-45deg,#1e1e2e,#1e1e2e 4px,#2e2e3e 4px,#2e2e3e 8px)',
  });

  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:12 }}>
      <div style={{ width:'100%', background:'#EDE5CF', borderRadius:20, border:'2.5px solid #1B2340', overflow:'visible', position:'relative' }}>

        <div style={{ display:'flex', gap:12, padding:'14px 14px 12px', position:'relative' }}>
          {/* AKTA stamp */}
          <div style={{ position:'absolute', top:10, right:12, border:'2.5px solid #CC2222', borderRadius:5, padding:'2px 9px', color:'#CC2222', fontFamily:'monospace', fontWeight:900, fontSize:11, letterSpacing:'0.12em', transform:'rotate(8deg)', zIndex:3, pointerEvents:'none' }}>
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
              {revealed ? <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'#1B2340', lineHeight:1.3 }}>{celeb.name}</div> : <div style={stripeStyle('90%')}/>}
            </div>
            {lifespan && (
              <div>
                <div style={{ fontFamily:'monospace', fontSize:9, fontWeight:700, color:'#888', letterSpacing:'0.16em', marginBottom:4 }}>ÉLETKOR</div>
                {revealed ? <div style={{ fontFamily:T.font, fontSize:12, color:'#1B2340' }}>{lifespan}</div> : <div style={stripeStyle('68%')}/>}
              </div>
            )}
            {occupation && (
              <div>
                <div style={{ fontFamily:'monospace', fontSize:9, fontWeight:700, color:'#888', letterSpacing:'0.16em', marginBottom:4 }}>FOGLALKOZÁS</div>
                {revealed ? <div style={{ fontFamily:T.font, fontSize:12, color:'#1B2340' }}>{occupation}</div> : <div style={stripeStyle('80%')}/>}
              </div>
            )}
          </div>
        </div>

        <div style={{ borderTop:'1.5px dashed rgba(27,35,64,0.3)', margin:'0 14px' }}/>

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
    </div>
  );
}"""

# ── 3. RulettGame redesign ────────────────────────────────────────────────────
NEW_RULETT = r"""function RulettGame({ gameIdx }) {
  const [layout, setLayout] = useState(null);
  const [picked, setPicked] = useState(null);
  const [stress] = useState(() => Math.floor(Math.random() * 45) + 28);

  useEffect(() => {
    const cards = ['fire','fire','pia'];
    for (let i = 2; i > 0; i--) { const j = Math.floor(Math.random()*(i+1)); [cards[i],cards[j]]=[cards[j],cards[i]]; }
    setLayout(cards);
    setPicked(null);
  }, [gameIdx]);

  if (!layout) return null;
  const result = picked !== null ? layout[picked] : null;
  const ANGLES = [-22, 0, 22];

  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:12 }}>

      {/* Outcome chips */}
      <div style={{ display:'flex', gap:10 }}>
        <div style={{ display:'flex', alignItems:'center', gap:6, background:'rgba(255,255,255,0.7)', borderRadius:24, padding:'6px 14px', boxShadow:'0 1px 6px rgba(0,0,0,0.08)' }}>
          <span style={{ fontSize:16 }}>🔥</span>
          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:'#D05040' }}>2× tűz</span>
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:6, background:'rgba(255,255,255,0.7)', borderRadius:24, padding:'6px 14px', boxShadow:'0 1px 6px rgba(0,0,0,0.08)' }}>
          <span style={{ fontSize:16 }}>🥃</span>
          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:'#50A882' }}>1× pia</span>
        </div>
      </div>

      {/* VÁLASZTVA label */}
      {picked !== null && (
        <div style={{ background:'#1B2340', color:'#fff', padding:'3px 16px', borderRadius:20, fontFamily:T.font, fontWeight:700, fontSize:11, letterSpacing:'0.12em' }}>
          VÁLASZTVA
        </div>
      )}

      {/* Card fan */}
      <div style={{ position:'relative', width:'100%', height:210 }}>
        {[0,1,2].map(i => {
          const isSelected = picked === i;
          const res = isSelected ? layout[i] : null;
          return (
            <div key={i}
              onClick={() => picked === null && setPicked(i)}
              style={{
                position:'absolute', left:'50%', bottom:0,
                marginLeft:-60, width:120, height:168,
                transformOrigin:'bottom center',
                transform:`rotate(${ANGLES[i]}deg)${isSelected ? ' scale(1.06) translateY(-6px)' : ''}`,
                zIndex: isSelected ? 5 : i===1 ? 2 : 1,
                cursor: picked===null ? 'pointer' : 'default',
                transition:'transform .25s',
                borderRadius:16,
                background:'repeating-linear-gradient(45deg,transparent,transparent 12px,rgba(255,255,255,0.05) 12px,rgba(255,255,255,0.05) 24px),linear-gradient(160deg,#4060d8,#2a40b0)',
                border: isSelected ? '3px solid #1B2340' : '3px solid rgba(255,255,255,0.82)',
                boxShadow: isSelected ? '0 10px 28px rgba(0,0,0,0.3)' : '0 4px 14px rgba(0,0,0,0.18)',
                display:'flex', alignItems:'center', justifyContent:'center',
              }}>
              {res ? (
                <div style={{ fontSize:42, animation:'burstPop .3s' }}>{res === 'pia' ? '🍺' : '🔥'}</div>
              ) : (
                <span style={{ fontFamily:'Georgia,serif', fontWeight:900, fontSize:48, color:'rgba(255,255,255,0.5)' }}>?</span>
              )}
            </div>
          );
        })}
      </div>

      {/* Result text */}
      {result && (
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:16, color: result==='pia' ? '#50A882' : '#D05040', animation:'popIn .3s', textAlign:'center' }}>
          {result === 'pia' ? '🍺 Pia! Megúsztad!' : '🔥 Tűz! Iszol!'}
        </div>
      )}

      {/* Stress meter */}
      <div style={{ width:'100%', marginTop:4 }}>
        <div style={{ display:'flex', justifyContent:'space-between', marginBottom:5 }}>
          <span style={{ fontFamily:T.font, fontSize:12, color:'#50A882', fontWeight:600 }}>Nyugi</span>
          <span style={{ fontFamily:T.font, fontSize:12, color:'#D05040', fontWeight:600 }}>Para 😬</span>
        </div>
        <div style={{ position:'relative', height:10, borderRadius:6, background:'linear-gradient(to right,#50A882,#F0C040 50%,#D05040)' }}>
          <div style={{ position:'absolute', top:'50%', left:`${stress}%`, transform:'translate(-50%,-50%)', width:18, height:18, borderRadius:'50%', background:'#fff', border:'2.5px solid #1B2340', boxShadow:'0 1px 5px rgba(0,0,0,0.25)' }}/>
        </div>
      </div>
    </div>
  );
}"""

# ── 4. ImposztorGame redesign (reveal phase only) ─────────────────────────────
NEW_IMPOSZTOR = r"""function ImposztorGame({ gameIdx, players, onAdvance }) {
  const [impostorIdx, setImpostorIdx] = useState(0);
  const [wordIdx, setWordIdx] = useState(0);
  const [phase, setPhase] = useState('reveal');
  const [revealStep, setRevealStep] = useState(0);
  const [holding, setHolding] = useState(false);
  const [votes, setVotes] = useState({});
  const [voteStep, setVoteStep] = useState(0);

  useEffect(() => {
    setImpostorIdx(Math.floor(Math.random() * players.length));
    setWordIdx(gameIdx % IMPOSZTOR_SZAVAK.length);
    setPhase('reveal'); setRevealStep(0); setHolding(false); setVotes({}); setVoteStep(0);
  }, [gameIdx]);

  const word = IMPOSZTOR_SZAVAK[wordIdx];

  if (phase === 'reveal') {
    const pl = players[revealStep];
    if (!pl) return null;
    const isImpostor = revealStep === impostorIdx;
    return (
      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:10, alignItems:'center' }}>

        {/* Progress chips */}
        <div style={{ display:'flex', gap:8, flexWrap:'wrap', justifyContent:'center' }}>
          {players.map((p, i) => {
            const done = i < revealStep;
            const active = i === revealStep;
            return (
              <div key={p.id} style={{ position:'relative', width:44, height:44, borderRadius:'50%', background: active ? p.color : done ? p.color : T.surfaceMuted, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:18, color: active||done ? '#fff' : T.inkMute, opacity: active ? 1 : done ? 0.75 : 0.45, border: active ? `3px solid ${p.color}` : '2px solid transparent', boxShadow: active ? `0 0 0 3px rgba(255,255,255,0.5)` : 'none', transition:'all .2s' }}>
                {p.name.charAt(0).toUpperCase()}
                {done && <div style={{ position:'absolute', bottom:-2, right:-2, width:16, height:16, borderRadius:'50%', background:'#50A882', border:'1.5px solid #fff', display:'grid', placeItems:'center', fontSize:9, color:'#fff', fontWeight:700 }}>✓</div>}
              </div>
            );
          })}
        </div>
        <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>
          Szerepek — {revealStep+1}/{players.length}
        </div>

        {/* Dark reveal card */}
        <div style={{ width:'100%', background:'#1B2340', borderRadius:20, padding:'20px 18px 16px', display:'flex', flexDirection:'column', alignItems:'center', gap:14 }}>
          {/* Player avatar */}
          <div style={{ width:54, height:54, borderRadius:'50%', background:pl.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:'#fff', boxShadow:`0 0 0 3px rgba(255,255,255,0.15)` }}>
            {pl.name.charAt(0).toUpperCase()}
          </div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:18, color:'#fff' }}>{pl.name}, te jössz</div>

          {/* Eye / reveal area */}
          <div style={{ width:94, height:94, borderRadius:18, border:'2px dashed rgba(255,255,255,0.28)', background:'rgba(255,255,255,0.05)', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6, padding:8 }}>
            {holding ? (
              isImpostor ? (
                <div style={{ textAlign:'center', animation:'burstPop .25s' }}>
                  <div style={{ fontSize:26 }}>🕵️</div>
                  <div style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:'#EF4444', letterSpacing:'0.05em' }}>IMPOSZTOR</div>
                </div>
              ) : (
                <div style={{ textAlign:'center', animation:'burstPop .25s' }}>
                  <div style={{ fontFamily:T.font, fontSize:10, color:'rgba(255,255,255,0.45)', letterSpacing:'0.08em', textTransform:'uppercase', marginBottom:2 }}>Titkos szó</div>
                  <div style={{ fontFamily:T.font, fontWeight:700, fontSize:17, color:'#fff' }}>{word}</div>
                </div>
              )
            ) : (
              <svg width="34" height="34" viewBox="0 0 34 34" fill="none">
                <ellipse cx="17" cy="17" rx="14" ry="9" stroke="rgba(255,255,255,0.4)" strokeWidth="2"/>
                <circle cx="17" cy="17" r="5" stroke="rgba(255,255,255,0.4)" strokeWidth="2"/>
              </svg>
            )}
          </div>

          <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.38)', textAlign:'center' }}>Tartsd lenyomva a felfedéshez</div>

          {/* Hold button */}
          <button
            onPointerDown={e=>{e.preventDefault();setHolding(true);}}
            onPointerUp={()=>setHolding(false)}
            onPointerLeave={()=>setHolding(false)}
            onPointerCancel={()=>setHolding(false)}
            style={{ width:'100%', padding:'14px 0', background: holding ? '#8C7AE6' : '#6C5CE7', border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', userSelect:'none', WebkitUserSelect:'none', display:'flex', alignItems:'center', justifyContent:'center', gap:8, transition:'background .1s' }}>
            <span style={{ fontSize:14 }}>⬇</span><span>Nyomd &amp; tartsd</span>
          </button>
        </div>

        {/* Pass to next */}
        <button onClick={() => { setHolding(false); if(revealStep+1 < players.length) setRevealStep(revealStep+1); else setPhase('describe'); }}
          style={{ width:'100%', padding:'14px 0', background:'#1B2340', border:'none', borderRadius:14, color:'rgba(255,255,255,0.9)', fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
          <span>Láttam — adom tovább</span><span style={{ fontSize:14 }}>→</span>
        </button>
      </div>
    );
  }

  if (phase === 'describe') {
    return (
      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:12, alignItems:'center' }}>
        <div style={{ background:T.surface, borderRadius:14, padding:'12px 16px', width:'100%', boxShadow:T.shadow, textAlign:'center' }}>
          <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:6 }}>Mit kell tenni</div>
          <div style={{ fontFamily:T.font, fontSize:14, color:T.ink, lineHeight:1.5 }}>Mindenki mondjon <strong>egy tippet</strong> a titkos szóra (anélkül hogy kimondaná). Az Imposztor blöfföljön!</div>
        </div>
        <div style={{ display:'flex', flexWrap:'wrap', gap:6, justifyContent:'center' }}>
          {players.map(p => (
            <div key={p.id} style={{ display:'flex', alignItems:'center', gap:5, padding:'4px 10px', borderRadius:10, background:T.surfaceMuted }}>
              <div style={{ width:18, height:18, borderRadius:'50%', background:p.color }} />
              <div style={{ fontFamily:T.font, fontSize:12, fontWeight:600, color:T.ink }}>{p.name}</div>
            </div>
          ))}
        </div>
        <button onClick={() => setPhase('vote')} style={{ padding:'10px 26px', background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, borderRadius:14, cursor:'pointer' }}>
          Mindenki mondott → Szavazás
        </button>
      </div>
    );
  }

  if (phase === 'vote') {
    const voter = players[voteStep];
    if (!voter) return null;
    const alreadyVoted = votes[voter.id] !== undefined;
    return (
      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:10, alignItems:'center' }}>
        <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em' }}>Szavazás — {voteStep+1}/{players.length}</div>
        <div style={{ display:'flex', alignItems:'center', gap:8 }}>
          <div style={{ width:34, height:34, borderRadius:'50%', background:voter.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, color:'#fff' }}>{voter.name.charAt(0).toUpperCase()}</div>
          <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink }}>{voter.name}, ki az Imposztor?</div>
        </div>
        <div style={{ display:'flex', flexWrap:'wrap', gap:8, justifyContent:'center', width:'100%' }}>
          {players.map((p, pIdx) => {
            if (pIdx === voteStep) return null;
            const picked = votes[voter.id] === pIdx;
            return (
              <button key={p.id} disabled={alreadyVoted} onClick={() => {
                const nv = {...votes, [voter.id]: pIdx};
                setVotes(nv);
                setTimeout(() => { if(voteStep+1 < players.length) setVoteStep(voteStep+1); else setPhase('result'); }, 400);
              }} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:4, padding:'8px 14px', border:`2px solid ${picked ? T.coral : 'transparent'}`, background: picked ? `${T.coral}18` : T.surfaceMuted, borderRadius:14, cursor: alreadyVoted ? 'default' : 'pointer' }}>
                <div style={{ width:40, height:40, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</div>
                <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:11, color:T.ink }}>{p.name}</div>
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  if (phase === 'result') {
    const impostor = players[impostorIdx];
    const voteCounts = {};
    Object.values(votes).forEach(idx => { voteCounts[idx] = (voteCounts[idx]||0)+1; });
    const topIdx = Object.entries(voteCounts).sort((a,b)=>b[1]-a[1])[0]?.[0];
    const found = parseInt(topIdx) === impostorIdx;
    return (
      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:10, alignItems:'center' }}>
        <div style={{ background:'#1a1a2e', borderRadius:16, padding:'12px 18px', textAlign:'center', boxShadow:T.shadow, animation:'popIn .4s', width:'100%' }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:'rgba(255,255,255,0.45)', textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:4 }}>Az Imposztor</div>
          <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:10 }}>
            <div style={{ width:44, height:44, borderRadius:'50%', background:impostor.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:'#fff' }}>{impostor.name.charAt(0).toUpperCase()}</div>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:'#EF4444' }}>{impostor.name}</div>
            <div style={{ fontSize:22 }}>🕵️</div>
          </div>
          <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.45)', marginTop:4 }}>Szó: <strong style={{ color:'rgba(255,255,255,0.85)' }}>{word}</strong></div>
        </div>
        <div style={{ padding:'10px 18px', borderRadius:14, background: found ? `${T.mint}22` : `${T.coral}22`, border:`2px solid ${found ? T.mint : T.coral}`, textAlign:'center', animation:'popIn .5s', width:'100%' }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:16, color: found ? T.mint : T.coral }}>
            {found ? '🎉 Megtalálták! Imposztor iszik 3-at!' : '😈 Blöff sikerült! Mindenki más iszik 2-t!'}
          </div>
        </div>
        <div style={{ display:'flex', flexDirection:'column', gap:4, width:'100%' }}>
          {players.map((p, i) => (
            <div key={p.id} style={{ display:'flex', alignItems:'center', gap:8, padding:'5px 10px', background:T.surface, borderRadius:10 }}>
              <div style={{ width:26, height:26, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontSize:11, fontWeight:700, color:'#fff', flexShrink:0 }}>{p.name.charAt(0).toUpperCase()}</div>
              <div style={{ flex:1, fontFamily:T.font, fontSize:13, fontWeight:600, color:T.ink }}>{p.name}</div>
              {i===impostorIdx && <div style={{ fontSize:13 }}>🕵️</div>}
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>{voteCounts[i]||0} szavazat</div>
            </div>
          ))}
        </div>
        <button onClick={() => {
          const dm = {};
          if (found) { dm[impostor.id] = 3; }
          else { players.forEach(p => { if(p.id !== impostor.id) dm[p.id] = 2; }); }
          if(onAdvance) onAdvance(dm);
        }} style={{ width:'100%', padding:'12px 0', background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:15, borderRadius:14, cursor:'pointer', boxShadow:T.shadow }}>
          Következő ▶
        </button>
      </div>
    );
  }

  return null;
}"""

# ── Apply replacements ────────────────────────────────────────────────────────

html = re.sub(
    r'function ZeneGame\(\{ gameIdx(?:, onAdvance)? \}\) \{.*?\n\}(?=\n\nfunction KivagyokGame)',
    NEW_ZENE, html, flags=re.DOTALL
)

html = re.sub(
    r'function KivagyokGame\(\{ gameIdx(?:, onAdvance)? \}\) \{.*?\n\}(?=\n\nconst IGAZ_HAMIS)',
    NEW_KIVA, html, flags=re.DOTALL
)

html = re.sub(
    r'function RulettGame\(\{ gameIdx \}\) \{.*?\n\}(?=\n\nfunction KisebbGame)',
    NEW_RULETT, html, flags=re.DOTALL
)

html = re.sub(
    r'function ImposztorGame\(\{ gameIdx, players, onAdvance \}\) \{.*?\n\}(?=\n\nfunction PlayingCard)',
    NEW_IMPOSZTOR, html, flags=re.DOTALL
)

# ── Fix GameContent router: remove onAdvance from zene/kivagyok ───────────────
html = html.replace(
    "if (gameId === 'zene') return <ZeneGame key={gameIdx} gameIdx={gameIdx} onAdvance={onAdvance} />;",
    "if (gameId === 'zene') return <ZeneGame key={gameIdx} gameIdx={gameIdx} />;",
    1
)
html = html.replace(
    "if (gameId === 'kivagyok') return <KivagyokGame key={gameIdx} gameIdx={gameIdx} onAdvance={onAdvance} />;",
    "if (gameId === 'kivagyok') return <KivagyokGame key={gameIdx} gameIdx={gameIdx} />;",
    1
)

# ── Version bump ──────────────────────────────────────────────────────────────
html = html.replace(
    'Verzió 5.14 · DNR · 2026.05.30 19:00',
    'Verzió 5.15 · DNR · 2026.05.30 20:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
