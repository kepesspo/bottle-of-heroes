import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Replace IGAZ_HAMIS data with cat field ─────────────────────────────────
OLD_DATA = """const IGAZ_HAMIS = [
  { text:'Az ember szíve percenként átlagosan 60–100-szor ver.', igaz:true },
  { text:'Magyarország fővárosa Debrecen.', igaz:false },
  { text:'A gyémánt a legeményebb természetes anyag a Földön.', igaz:true },
  { text:'A cápa emlős állat.', igaz:false },
  { text:'A Nílus a világ leghosszabb folyója.', igaz:true },
  { text:'A kávé Kínából ered.', igaz:false },
  { text:'Az alkohol valójában melegít a hidegtől.', igaz:false },
  { text:'A csimpánz az ember legközelebbi élő rokona.', igaz:true },
  { text:'A Hold saját fényt bocsát ki.', igaz:false },
  { text:'Az oktopusznak három szíve van.', igaz:true },
  { text:'A denevér teljesen vak állat.', igaz:false },
  { text:'A víz pontosan 0°C-on fagy meg normál légnyomáson.', igaz:true },
  { text:'Mozart 35 éves korában halt meg.', igaz:true },
  { text:'A Titanic 1912-ben süllyedt el.', igaz:true },
  { text:'Az emberi testnek 206 csontja van felnőttkorban.', igaz:true },
  { text:'Európa a világ legkisebb kontinense.', igaz:false },
  { text:'A fény sebessége kb. 300 000 km/s.', igaz:true },
  { text:'A struccok homokba dugják a fejüket, ha megijednek.', igaz:false },
  { text:'A méhek elpusztulnak, miután egyszer megcsíptek valakit.', igaz:true },
  { text:'Az arany nem oldódik sósavban.', igaz:true },
];"""

NEW_DATA = """const IGAZ_HAMIS = [
  { text:'Az ember szíve percenként átlagosan 60–100-szor ver.', igaz:true,  cat:'🫀 Emberi test' },
  { text:'Magyarország fővárosa Debrecen.', igaz:false, cat:'🌍 Földrajz' },
  { text:'A gyémánt a legeményebb természetes anyag a Földön.', igaz:true,  cat:'🔬 Tudomány' },
  { text:'A cápa emlős állat.', igaz:false, cat:'🐾 Állatok' },
  { text:'A Nílus a világ leghosszabb folyója.', igaz:true,  cat:'🌍 Földrajz' },
  { text:'A kávé Kínából ered.', igaz:false, cat:'💡 Érdekesség' },
  { text:'Az alkohol valójában melegít a hidegtől.', igaz:false, cat:'💡 Érdekesség' },
  { text:'A csimpánz az ember legközelebbi élő rokona.', igaz:true,  cat:'🐾 Állatok' },
  { text:'A Hold saját fényt bocsát ki.', igaz:false, cat:'🔬 Tudomány' },
  { text:'Az oktopusznak három szíve van.', igaz:true,  cat:'🐾 Állatok' },
  { text:'A denevér teljesen vak állat.', igaz:false, cat:'🐾 Állatok' },
  { text:'A víz pontosan 0°C-on fagy meg normál légnyomáson.', igaz:true,  cat:'🔬 Tudomány' },
  { text:'Mozart 35 éves korában halt meg.', igaz:true,  cat:'📜 Történelem' },
  { text:'A Titanic 1912-ben süllyedt el.', igaz:true,  cat:'📜 Történelem' },
  { text:'Az emberi testnek 206 csontja van felnőttkorban.', igaz:true,  cat:'🫀 Emberi test' },
  { text:'Európa a világ legkisebb kontinense.', igaz:false, cat:'🌍 Földrajz' },
  { text:'A fény sebessége kb. 300 000 km/s.', igaz:true,  cat:'🔬 Tudomány' },
  { text:'A struccok homokba dugják a fejüket, ha megijednek.', igaz:false, cat:'🐾 Állatok' },
  { text:'A méhek elpusztulnak, miután egyszer megcsíptek valakit.', igaz:true,  cat:'🐾 Állatok' },
  { text:'Az arany nem oldódik sósavban.', igaz:true,  cat:'🔬 Tudomány' },
];"""

html = html.replace(OLD_DATA, NEW_DATA, 1)

# ── 2. Replace IgazHamisGame function ─────────────────────────────────────────
NEW_IGAZ = r"""function IgazHamisGame({ gameIdx }) {
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
}"""

html = re.sub(
    r'function IgazHamisGame\(\{ gameIdx \}\) \{.*?\n\}(?=\n\nfunction SzerencsekerékGame)',
    NEW_IGAZ, html, flags=re.DOTALL
)

# ── Version bump ──────────────────────────────────────────────────────────────
html = html.replace(
    'Verzió 5.15 · DNR · 2026.05.30 20:00',
    'Verzió 5.16 · DNR · 2026.05.30 21:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
