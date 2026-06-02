with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. GameContent: pass challenger + onAdvance to IgazHamisGame
OLD_GC = "if (gameId === 'igazhamis') return <IgazHamisGame key={gameIdx} gameIdx={gameIdx} />;"
NEW_GC = "if (gameId === 'igazhamis') return <IgazHamisGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} />;"
assert OLD_GC in content, 'GameContent igazhamis not found'
content = content.replace(OLD_GC, NEW_GC, 1)

# 2. Replace full IgazHamisGame function
OLD_GAME = '''function IgazHamisGame({ gameIdx }) {
  const item = IGAZ_HAMIS[gameIdx % IGAZ_HAMIS.length];
  const [decided, setDecided] = useState(null); // null | 'igaz' | 'hamis'
  const [dragX, setDragX] = useState(0);
  const [dragging, setDragging] = useState(false);
  const startXRef = useRef(null);

  useEffect(() => { setDecided(null); setDragX(0); setDragging(false); }, [gameIdx]);

  const decide = (choice) => {
    if (decided) return;
    setDecided(choice);
    setDragX(0);
    setDragging(false);
  };

  const onPointerDown = (e) => {
    if (decided) return;
    e.currentTarget.setPointerCapture(e.pointerId);
    startXRef.current = e.clientX;
    setDragging(true);
  };
  const onPointerMove = (e) => {
    if (!dragging || decided) return;
    setDragX(e.clientX - startXRef.current);
  };
  const onPointerUp = (e) => {
    if (!dragging) return;
    const dx = e.clientX - (startXRef.current || e.clientX);
    if (dx > 75) decide('igaz');
    else if (dx < -75) decide('hamis');
    else { setDragging(false); setDragX(0); }
  };

  const THRESHOLD = 75;
  const swipeRatio = Math.min(Math.abs(dragX) / THRESHOLD, 1);
  const dragDir = dragX > 0 ? 'igaz' : dragX < 0 ? 'hamis' : null;

  const cardStyle = {
    position:'relative', width:'100%', height:290,
    background:'#fff', borderRadius:22,
    boxShadow:'0 8px 32px rgba(0,0,0,0.14)',
    transform: dragging
      ? `translateX(${dragX}px) rotate(${dragX / 18}deg)`
      : decided
        ? 'translateX(0) rotate(0deg)'
        : 'translateX(0) rotate(0deg)',
    transition: dragging ? 'none' : 'transform .4s cubic-bezier(.2,.9,.3,1.2)',
    cursor: decided ? 'default' : 'grab',
    userSelect:'none', WebkitUserSelect:'none',
    display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center',
    padding:'20px 22px 48px',
    touchAction:'none',
    flexShrink:0,
  };

  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:12 }}>

      {/* Card area */}
      <div style={{ position:'relative', width:'100%', paddingLeft:52, paddingRight:52, boxSizing:'border-box' }}>

        {/* HAMIS indicator — left */}
        <div onClick={() => !decided && decide('hamis')} style={{ position:'absolute', left:0, top:'50%', transform:'translateY(-50%)', display:'flex', flexDirection:'column', alignItems:'center', gap:4, cursor: decided ? 'default' : 'pointer', zIndex:10 }}>
          <div style={{ width:42, height:42, borderRadius:'50%', border:`2.5px solid #E8A090`, display:'grid', placeItems:'center', background: (dragDir==='hamis'&&dragging) ? `rgba(232,160,144,${swipeRatio*0.25})` : decided==='hamis' ? 'rgba(232,160,144,0.18)' : 'transparent', transition:'background .2s' }}>
            <span style={{ color:'#E8A090', fontWeight:900, fontSize:18, lineHeight:1 }}>✕</span>
          </div>
          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:9, color:'#E8A090', letterSpacing:'0.1em' }}>HAMIS</span>
        </div>

        {/* Card stack (2 background cards) */}
        <div style={{ position:'relative' }}>
          <div style={{ position:'absolute', inset:0, borderRadius:22, background:'rgba(255,255,255,0.55)', transform:'rotate(-3.5deg) translateY(5px)' }}/>
          <div style={{ position:'absolute', inset:0, borderRadius:22, background:'rgba(255,255,255,0.75)', transform:'rotate(1.8deg) translateY(3px)' }}/>

          {/* Main card */}
          <div
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerCancel={() => { setDragging(false); setDragX(0); }}
            style={cardStyle}>

            {/* Answer chip — top right, appears after decision */}
            {decided && (
              <div style={{ position:'absolute', top:14, right:14, background: item.igaz ? '#50A882' : '#E8A090', borderRadius:20, padding:'5px 13px', display:'flex', alignItems:'center', gap:4, animation:'burstPop .3s' }}>
                <span style={{ color:'#fff', fontWeight:800, fontSize:12 }}>{item.igaz ? '✓ IGAZ' : '✗ HAMIS'}</span>
              </div>
            )}

            {/* Drag preview chip */}
            {dragging && swipeRatio > 0.35 && (
              <div style={{ position:'absolute', top:14, ...(dragDir==='igaz' ? {right:14} : {left:14}), background: dragDir==='igaz' ? `rgba(80,168,130,${0.6+swipeRatio*0.4})` : `rgba(232,160,144,${0.6+swipeRatio*0.4})`, borderRadius:20, padding:'5px 13px', pointerEvents:'none' }}>
                <span style={{ color:'#fff', fontWeight:800, fontSize:12 }}>{dragDir==='igaz' ? '✓ IGAZ' : '✗ HAMIS'}</span>
              </div>
            )}

            {/* Category chip */}
            {item.cat && (
              <div style={{ position:'absolute', top:54, background:'#F5ECD8', borderRadius:20, padding:'5px 13px' }}>
                <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:'#7a6550', letterSpacing:'0.06em' }}>{item.cat}</span>
              </div>
            )}

            {/* Statement */}
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:19, color:'#1B2340', textAlign:'center', lineHeight:1.45, marginTop: item.cat ? 32 : 0 }}>
              {item.text}
            </div>

            {/* Swipe hint */}
            {!decided && (
              <div style={{ position:'absolute', bottom:16, fontFamily:T.font, fontSize:11, color:'rgba(0,0,0,0.22)', letterSpacing:'0.05em' }}>
                — húzd · döntsd el · húzd —
              </div>
            )}
          </div>
        </div>

        {/* IGAZ indicator — right */}
        <div onClick={() => !decided && decide('igaz')} style={{ position:'absolute', right:0, top:'50%', transform:'translateY(-50%)', display:'flex', flexDirection:'column', alignItems:'center', gap:4, cursor: decided ? 'default' : 'pointer', zIndex:10 }}>
          <div style={{ width:42, height:42, borderRadius:'50%', border:`2.5px solid #50A882`, display:'grid', placeItems:'center', background: (dragDir==='igaz'&&dragging) ? `rgba(80,168,130,${swipeRatio*0.25})` : decided==='igaz' ? 'rgba(80,168,130,0.18)' : 'transparent', transition:'background .2s' }}>
            <span style={{ color:'#50A882', fontWeight:900, fontSize:18 }}>✓</span>
          </div>
          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:9, color:'#50A882', letterSpacing:'0.1em' }}>IGAZ</span>
        </div>
      </div>
    </div>
  );
}'''

NEW_GAME = '''function IgazHamisGame({ gameIdx, challenger, onAdvance }) {
  const item = IGAZ_HAMIS[gameIdx % IGAZ_HAMIS.length];
  const [decided, setDecided] = useState(null); // null | 'igaz' | 'hamis'
  const [dragX, setDragX] = useState(0);
  const [dragging, setDragging] = useState(false);
  const startXRef = useRef(null);
  const advancedRef = useRef(false);

  useEffect(() => { setDecided(null); setDragX(0); setDragging(false); advancedRef.current = false; }, [gameIdx]);

  const decide = (choice) => {
    if (decided) return;
    setDecided(choice);
    setDragX(0);
    setDragging(false);
  };

  const correct = decided !== null ? (decided === (item.igaz ? 'igaz' : 'hamis')) : null;

  useEffect(() => {
    if (decided === null || advancedRef.current) return;
    advancedRef.current = true;
    const dm = {};
    if (!correct && challenger) dm[challenger.id] = 1;
    onAdvance && onAdvance(dm);
  }, [decided]);

  const onPointerDown = (e) => {
    if (decided) return;
    e.currentTarget.setPointerCapture(e.pointerId);
    startXRef.current = e.clientX;
    setDragging(true);
  };
  const onPointerMove = (e) => {
    if (!dragging || decided) return;
    setDragX(e.clientX - startXRef.current);
  };
  const onPointerUp = (e) => {
    if (!dragging) return;
    const dx = e.clientX - (startXRef.current || e.clientX);
    if (dx > 75) decide('igaz');
    else if (dx < -75) decide('hamis');
    else { setDragging(false); setDragX(0); }
  };

  const THRESHOLD = 75;
  const swipeRatio = Math.min(Math.abs(dragX) / THRESHOLD, 1);
  const dragDir = dragX > 0 ? 'igaz' : dragX < 0 ? 'hamis' : null;

  const cardStyle = {
    position:'relative', width:'100%', height:290,
    background:'#fff', borderRadius:22,
    boxShadow:'0 8px 32px rgba(0,0,0,0.14)',
    transform: dragging
      ? `translateX(${dragX}px) rotate(${dragX / 18}deg)`
      : 'translateX(0) rotate(0deg)',
    transition: dragging ? 'none' : 'transform .4s cubic-bezier(.2,.9,.3,1.2)',
    cursor: decided ? 'default' : 'grab',
    userSelect:'none', WebkitUserSelect:'none',
    display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center',
    padding:'20px 22px 48px',
    touchAction:'none',
    flexShrink:0,
  };

  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:12 }}>

      {/* Card area */}
      <div style={{ position:'relative', width:'100%', paddingLeft:52, paddingRight:52, boxSizing:'border-box' }}>

        {/* HAMIS indicator — left */}
        <div onClick={() => !decided && decide('hamis')} style={{ position:'absolute', left:0, top:'50%', transform:'translateY(-50%)', display:'flex', flexDirection:'column', alignItems:'center', gap:4, cursor: decided ? 'default' : 'pointer', zIndex:10 }}>
          <div style={{ width:42, height:42, borderRadius:'50%', border:`2.5px solid #E8A090`, display:'grid', placeItems:'center', background: (dragDir==='hamis'&&dragging) ? `rgba(232,160,144,${swipeRatio*0.25})` : decided==='hamis' ? 'rgba(232,160,144,0.18)' : 'transparent', transition:'background .2s' }}>
            <span style={{ color:'#E8A090', fontWeight:900, fontSize:18, lineHeight:1 }}>✕</span>
          </div>
          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:9, color:'#E8A090', letterSpacing:'0.1em' }}>HAMIS</span>
        </div>

        {/* Card stack (2 background cards) */}
        <div style={{ position:'relative' }}>
          <div style={{ position:'absolute', inset:0, borderRadius:22, background:'rgba(255,255,255,0.55)', transform:'rotate(-3.5deg) translateY(5px)' }}/>
          <div style={{ position:'absolute', inset:0, borderRadius:22, background:'rgba(255,255,255,0.75)', transform:'rotate(1.8deg) translateY(3px)' }}/>

          {/* Main card */}
          <div
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerCancel={() => { setDragging(false); setDragX(0); }}
            style={cardStyle}>

            {/* Drag preview chip */}
            {dragging && swipeRatio > 0.35 && (
              <div style={{ position:'absolute', top:14, ...(dragDir==='igaz' ? {right:14} : {left:14}), background: dragDir==='igaz' ? `rgba(80,168,130,${0.6+swipeRatio*0.4})` : `rgba(232,160,144,${0.6+swipeRatio*0.4})`, borderRadius:20, padding:'5px 13px', pointerEvents:'none' }}>
                <span style={{ color:'#fff', fontWeight:800, fontSize:12 }}>{dragDir==='igaz' ? '✓ IGAZ' : '✗ HAMIS'}</span>
              </div>
            )}

            {/* Category chip */}
            {item.cat && !decided && (
              <div style={{ position:'absolute', top:16, background:'#F5ECD8', borderRadius:20, padding:'5px 13px' }}>
                <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:'#7a6550', letterSpacing:'0.06em' }}>{item.cat}</span>
              </div>
            )}

            {/* After decision: correct answer chip */}
            {decided && (
              <div style={{ position:'absolute', top:16, background: item.igaz ? '#50A882' : '#E8A090', borderRadius:20, padding:'5px 13px', animation:'burstPop .3s' }}>
                <span style={{ color:'#fff', fontWeight:800, fontSize:12 }}>{item.igaz ? '✓ IGAZ' : '✗ HAMIS'}</span>
              </div>
            )}

            {/* Statement */}
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:19, color:'#1B2340', textAlign:'center', lineHeight:1.45, marginTop:32 }}>
              {item.text}
            </div>

            {/* After decision: explanation */}
            {decided && item.exp && (
              <div style={{ position:'absolute', bottom:14, left:16, right:16, fontFamily:T.font, fontSize:12, color:'#555', textAlign:'center', lineHeight:1.4, fontStyle:'italic' }}>
                {item.exp}
              </div>
            )}

            {/* Swipe hint */}
            {!decided && (
              <div style={{ position:'absolute', bottom:16, fontFamily:T.font, fontSize:11, color:'rgba(0,0,0,0.22)', letterSpacing:'0.05em' }}>
                — húzd · döntsd el · húzd —
              </div>
            )}
          </div>
        </div>

        {/* IGAZ indicator — right */}
        <div onClick={() => !decided && decide('igaz')} style={{ position:'absolute', right:0, top:'50%', transform:'translateY(-50%)', display:'flex', flexDirection:'column', alignItems:'center', gap:4, cursor: decided ? 'default' : 'pointer', zIndex:10 }}>
          <div style={{ width:42, height:42, borderRadius:'50%', border:`2.5px solid #50A882`, display:'grid', placeItems:'center', background: (dragDir==='igaz'&&dragging) ? `rgba(80,168,130,${swipeRatio*0.25})` : decided==='igaz' ? 'rgba(80,168,130,0.18)' : 'transparent', transition:'background .2s' }}>
            <span style={{ color:'#50A882', fontWeight:900, fontSize:18 }}>✓</span>
          </div>
          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:9, color:'#50A882', letterSpacing:'0.1em' }}>IGAZ</span>
        </div>
      </div>

      {/* Result banner */}
      {decided && (
        <div style={{ width:'100%', borderRadius:16, padding:'14px 18px', display:'flex', alignItems:'center', gap:12, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)', background: correct ? 'rgba(80,168,130,0.12)' : 'rgba(232,160,144,0.18)', border:`2px solid ${correct ? '#50A882' : '#E8A090'}` }}>
          <div style={{ fontSize:28 }}>{correct ? '🎉' : '🍺'}</div>
          <div>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color: correct ? '#50A882' : '#C05050' }}>
              {correct ? 'Helyes! Nem kell innod.' : 'Rossz tipp — inni kell!'}
            </div>
            {challenger && !correct && (
              <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>{challenger.name} iszik egyet</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}'''

assert OLD_GAME in content, 'IgazHamisGame old block not found'
content = content.replace(OLD_GAME, NEW_GAME, 1)

# Version bump
assert 'Verzió 5.67' in content
content = content.replace('Verzió 5.67', 'Verzió 5.68', 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('OK — IgazHamisGame updated, v5.68')
