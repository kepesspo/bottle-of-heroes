with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Rewrite KivagyokGame: image spinner + fallback, buttons styled like play-actions
OLD_GAME = """function KivagyokGame({ gameIdx, challenger, onAdvance, onResult }) {
  const celeb = KIVAGYOK_CELEBS[gameIdx % KIVAGYOK_CELEBS.length];
  const [revealed, setRevealed] = useState(false);
  const [decided, setDecided] = useState(null); // 'correct' | 'wrong'
  const advancedRef = React.useRef(false);

  React.useEffect(() => { advancedRef.current = false; setRevealed(false); setDecided(null); }, [gameIdx]);

  const infoParts = (celeb.info || '').split(' · ');
  const lifespan   = infoParts[0] || '';
  const occupation = infoParts[1] || '';

  const stripeStyle = (w) => ({
    height:14, borderRadius:3, width: w || '100%',
    background:'repeating-linear-gradient(-45deg,#1e1e2e,#1e1e2e 4px,#2e2e3e 4px,#2e2e3e 8px)',
  });

  const handleResult = (correct) => {
    if (decided || advancedRef.current) return;
    advancedRef.current = true;
    setDecided(correct ? 'correct' : 'wrong');
    const dm = {};
    const pm = {};
    if (!correct && challenger) dm[challenger.id] = 1;
    if (correct && challenger) pm[challenger.id] = 1;
    onAdvance && onAdvance(dm, pm);
    onResult && onResult({ correct, playerName: challenger ? challenger.name : null, drinks: correct ? 0 : 1 });
  };

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
            <img src={celeb.img} alt="celeb" style={{ width:'100%', height:'100%', objectFit:'cover', objectPosition:'top' }} onError={e=>{e.target.style.display='none';}}/>
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
          {!revealed ? (
            <>
              <div style={{ display:'flex', gap:10, alignItems:'flex-start' }}>
                <div style={{ width:36, height:36, minWidth:36, background:'#1B2340', borderRadius:10, display:'flex', alignItems:'center', justifyContent:'center' }}>
                  <span style={{ fontSize:18, color:'#F0C040', fontWeight:900 }}>?</span>
                </div>
                <div style={{ fontFamily:T.font, fontSize:13, color:'#2a2a3a', lineHeight:1.5 }}>
                  Tippeld meg a <strong>hírességet</strong> — aztán fedd fel az aktát.
                </div>
              </div>
              <button onClick={() => setRevealed(true)} style={{ width:'100%', padding:'14px 0', background:'#1B2340', border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
                <span>🔍</span><span>Akta felfedése</span>
              </button>
            </>
          ) : !decided ? (
            <>
              <div style={{ fontFamily:T.font, fontSize:13, color:'#2a2a3a', lineHeight:1.5, textAlign:'center' }}>
                Sikerült kitalálni?
              </div>
              <div style={{ display:'flex', gap:10 }}>
                <button onClick={() => handleResult(false)} style={{ flex:1, padding:'13px 0', background:'rgba(232,160,144,0.18)', border:'2px solid #E8A090', borderRadius:14, color:'#C05050', fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer' }}>
                  🍺 Nem ismertem
                </button>
                <button onClick={() => handleResult(true)} style={{ flex:1, padding:'13px 0', background:'rgba(80,168,130,0.12)', border:'2px solid #50A882', borderRadius:14, color:'#50A882', fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer' }}>
                  🎉 Megismertem!
                </button>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </div>"""

NEW_GAME = """function KivagyokGame({ gameIdx, challenger, onAdvance, onResult }) {
  const celeb = KIVAGYOK_CELEBS[gameIdx % KIVAGYOK_CELEBS.length];
  const [revealed, setRevealed] = useState(false);
  const [decided, setDecided] = useState(null);
  const [imgState, setImgState] = useState('loading'); // 'loading' | 'ok' | 'err'
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    advancedRef.current = false;
    setRevealed(false);
    setDecided(null);
    setImgState('loading');
  }, [gameIdx]);

  const infoParts = (celeb.info || '').split(' · ');
  const lifespan   = infoParts[0] || '';
  const occupation = infoParts[1] || '';

  const stripeStyle = (w) => ({
    height:14, borderRadius:3, width: w || '100%',
    background:'repeating-linear-gradient(-45deg,#1e1e2e,#1e1e2e 4px,#2e2e3e 4px,#2e2e3e 8px)',
  });

  const handleResult = (correct) => {
    if (decided || advancedRef.current) return;
    advancedRef.current = true;
    setDecided(correct ? 'correct' : 'wrong');
    const dm = {};
    const pm = {};
    if (!correct && challenger) dm[challenger.id] = 1;
    if (correct && challenger) pm[challenger.id] = 1;
    onAdvance && onAdvance(dm, pm);
    onResult && onResult({ correct, playerName: challenger ? challenger.name : null, drinks: correct ? 0 : 1 });
  };

  const initials = celeb.name.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase();

  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:12 }}>
      <div style={{ width:'100%', background:'#EDE5CF', borderRadius:20, border:'2.5px solid #1B2340', overflow:'visible', position:'relative' }}>

        <div style={{ display:'flex', gap:12, padding:'14px 14px 12px', position:'relative' }}>
          {/* AKTA stamp */}
          <div style={{ position:'absolute', top:10, right:12, border:'2.5px solid #CC2222', borderRadius:5, padding:'2px 9px', color:'#CC2222', fontFamily:'monospace', fontWeight:900, fontSize:11, letterSpacing:'0.12em', transform:'rotate(8deg)', zIndex:3, pointerEvents:'none' }}>
            AKTA #{String((gameIdx % KIVAGYOK_CELEBS.length) + 1).padStart(2,'0')}
          </div>

          {/* Photo with spinner/fallback */}
          <div style={{ width:100, height:118, background:'#C4CDD8', borderRadius:10, overflow:'hidden', flexShrink:0, display:'flex', alignItems:'center', justifyContent:'center', border:'1.5px solid #9aabb8', position:'relative' }}>
            {imgState === 'loading' && (
              <div style={{ position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center', background:'#C4CDD8' }}>
                <div style={{ width:28, height:28, border:'3px solid #9aabb8', borderTopColor:'#1B2340', borderRadius:'50%', animation:'spin 0.8s linear infinite' }}/>
              </div>
            )}
            {imgState === 'err' && (
              <div style={{ position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center', background:'#b0bec8', fontFamily:T.font, fontWeight:900, fontSize:28, color:'#fff' }}>
                {initials}
              </div>
            )}
            <img
              key={celeb.img}
              src={celeb.img}
              alt="celeb"
              style={{ width:'100%', height:'100%', objectFit:'cover', objectPosition:'top', display: imgState === 'ok' ? 'block' : 'none' }}
              onLoad={() => setImgState('ok')}
              onError={() => setImgState('err')}
            />
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
              Tippeld meg a <strong>hírességet</strong> — aztán fedd fel az aktát.
            </div>
          </div>
          {!revealed && (
            <button onClick={() => setRevealed(true)} style={{ width:'100%', padding:'14px 0', background:'#1B2340', border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
              <span>🔍</span><span>Akta felfedése</span>
            </button>
          )}
        </div>
      </div>

      {/* Result buttons — styled like play-actions, only shown after reveal */}
      {revealed && !decided && (
        <div className="play-actions" style={{ width:'100%' }}>
          <button onClick={() => handleResult(false)} style={{ flex:1, minHeight:60, border:'none', background:T.coral, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:17, borderRadius:16, cursor:'pointer', boxShadow:T.shadow }}>Nem ismertem 🍺</button>
          <button onClick={() => handleResult(true)} style={{ flex:1, minHeight:60, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:17, borderRadius:16, cursor:'pointer', boxShadow:T.shadow }}>Megismertem! 🎉</button>
        </div>
      )}
    </div>"""

assert OLD_GAME in content, 'KivagyokGame not found'
content = content.replace(OLD_GAME, NEW_GAME, 1)

# Add spin keyframe if not present
if '@keyframes spin' not in content:
    OLD_ANIM = '@keyframes popIn     {'
    NEW_ANIM = '@keyframes spin      { to { transform: rotate(360deg); } }\n    @keyframes popIn     {'
    assert OLD_ANIM in content, 'popIn keyframe not found'
    content = content.replace(OLD_ANIM, NEW_ANIM, 1)

# Version bump
assert 'Verzió 5.77' in content
content = content.replace('Verzió 5.77', 'Verzió 5.78', 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('OK — KivagyokGame: kép spinner + fallback, gombok play-actions stílusban, v5.78')
