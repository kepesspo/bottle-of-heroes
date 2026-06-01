import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Add coinFlip keyframe to CSS ─────────────────────────────────────────
html = html.replace(
    '@keyframes vinylSpin  { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }',
    '@keyframes vinylSpin  { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }\n    @keyframes coinFlip    { 0%,100%{transform:scaleX(1)} 15%,45%,75%{transform:scaleX(0.05)} 30%,60%{transform:scaleX(1)} }',
    1
)

# ── 2. EremGame: cta [] ──────────────────────────────────────────────────────
html = html.replace(
    "  erem:      { prompt:'Fej vagy írás — döntsétek el, ki iszik!', cta:['Vesztettem','Nyertem!'] },",
    "  erem:      { prompt:'Fej vagy írás — döntsétek el, ki iszik!', cta:[] },",
    1
)

# ── 3. Páros CTA buttons guard ───────────────────────────────────────────────
html = html.replace(
    "          <div className='play-actions'>\n            <button onClick={() => advancePaired(false)} disabled={transitioning} style={{ flex:1, minHeight:60, border:'none', background:T.coral, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:17, borderRadius:16, cursor:'pointer', boxShadow:T.shadow }}>Vesztettem 😔</button>\n            <button onClick={() => advancePaired(true)} disabled={transitioning} style={{ flex:1, minHeight:60, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:17, borderRadius:16, cursor:'pointer', boxShadow:T.shadow }}>Nyertem! 🎉</button>\n          </div>",
    "          {scenario.cta.length > 0 && (\n          <div className='play-actions'>\n            <button onClick={() => advancePaired(false)} disabled={transitioning} style={{ flex:1, minHeight:60, border:'none', background:T.coral, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:17, borderRadius:16, cursor:'pointer', boxShadow:T.shadow }}>Vesztettem 😔</button>\n            <button onClick={() => advancePaired(true)} disabled={transitioning} style={{ flex:1, minHeight:60, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:17, borderRadius:16, cursor:'pointer', boxShadow:T.shadow }}>Nyertem! 🎉</button>\n          </div>\n          )}",
    1
)

# ── 4. EremGame redesign ─────────────────────────────────────────────────────
NEW_EREM = r"""function EremGame({ gameIdx, challenger, opponent, onAdvance }) {
  const [pick, setPick] = React.useState(null);
  const [phase, setPhase] = React.useState('pick');
  const [result, setResult] = React.useState(null);

  React.useEffect(() => { setPick(null); setPhase('pick'); setResult(null); }, [gameIdx]);

  const doFlip = (choice) => {
    setPick(choice);
    setPhase('flipping');
    setTimeout(() => {
      setResult(Math.random() < 0.5 ? 'fej' : 'iras');
      setPhase('result');
    }, 1600);
  };

  const correct = pick !== null && result !== null && pick === result;

  const advance = (win) => {
    const dm = {};
    if (win && opponent) dm[opponent.id] = 1;
    if (!win && challenger) dm[challenger.id] = 1;
    onAdvance && onAdvance(dm);
  };

  const CoinFace = ({ side }) => (
    <svg width="160" height="160" viewBox="-72 -72 144 144">
      <ellipse cx="0" cy="60" rx="52" ry="9" fill="rgba(0,0,0,0.10)"/>
      <circle r="68" fill="#F4C95A" stroke="#1B2340" strokeWidth="5.5"/>
      <circle r="54" fill="none" stroke="#1B2340" strokeWidth="1.5" strokeDasharray="6 4" opacity="0.5"/>
      {side === 'fej' ? (
        <g>
          <circle cy="-14" r="18" fill="#1B2340"/>
          <path d="M -28,22 Q -28,4 0,4 Q 28,4 28,22 Z" fill="#1B2340"/>
        </g>
      ) : (
        <g>
          <path d="M -28,-18 C -14,-30 14,-6 28,-18" fill="none" stroke="#1B2340" strokeWidth="3.5" strokeLinecap="round"/>
          <path d="M -28,-2 C -14,-14 14,10 28,-2" fill="none" stroke="#1B2340" strokeWidth="3.5" strokeLinecap="round"/>
          <path d="M -28,14 C -14,2 14,26 28,14" fill="none" stroke="#1B2340" strokeWidth="3.5" strokeLinecap="round"/>
        </g>
      )}
    </svg>
  );

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:14 }}>

      {/* Challenger tip pill */}
      {pick && challenger && (
        <div style={{ display:'flex', alignItems:'center', gap:8, background:'#fff', borderRadius:24, padding:'8px 14px', boxShadow:T.shadow, animation:'popIn .2s' }}>
          <div style={{ width:32, height:32, borderRadius:'50%', background:challenger.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff' }}>
            {challenger.name.charAt(0).toUpperCase()}
          </div>
          <span style={{ fontFamily:T.font, fontWeight:600, fontSize:12, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em' }}>{challenger.name} tippje</span>
          <div style={{ background:T.yellow, borderRadius:12, padding:'4px 10px', fontFamily:T.font, fontWeight:800, fontSize:12, color:'#1B2340' }}>
            {pick === 'fej' ? 'FEJ' : 'ÍRÁS'}
          </div>
        </div>
      )}

      {/* Coin */}
      <div style={{ animation: phase==='flipping' ? 'coinFlip 1.5s ease-in-out' : phase==='result' ? 'popIn .4s' : 'none' }}>
        <CoinFace side={phase === 'result' ? result : (pick || 'fej')} />
      </div>

      {/* Result label */}
      {phase === 'result' && (
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.12em', animation:'popIn .3s' }}>
          {result === 'fej' ? 'FEJ LETT' : 'ÍRÁS LETT'}
        </div>
      )}

      {/* Pick buttons */}
      {phase === 'pick' && (
        <div style={{ display:'flex', gap:10, width:'100%' }}>
          <button onClick={() => doFlip('fej')} style={{ flex:1, padding:'16px', background:'rgba(255,255,255,0.7)', border:`2px solid ${T.mint}`, color:T.ink, fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
            <span style={{ fontSize:20 }}>👑</span> Fej
          </button>
          <button onClick={() => doFlip('iras')} style={{ flex:1, padding:'16px', background:'rgba(255,255,255,0.7)', border:`2px solid ${T.mint}`, color:T.ink, fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
            <span style={{ fontSize:20 }}>✍️</span> Írás
          </button>
        </div>
      )}

      {/* Flipping */}
      {phase === 'flipping' && (
        <div style={{ fontFamily:T.font, fontSize:15, color:T.inkSoft, animation:'pulse 0.5s infinite' }}>
          🌀 Repül a levegőben…
        </div>
      )}

      {/* Result actions */}
      {phase === 'result' && (
        <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8, animation:'popIn .3s' }}>
          <button onClick={() => advance(correct)} style={{ width:'100%', padding:'15px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow }}>
            {correct ? '🎉 Eltalálta — megúszta!' : `Nem találta el — ${challenger?.name||'ő'} iszik!`}
          </button>
          <button onClick={() => advance(!correct)} style={{ width:'100%', padding:'13px', background:'rgba(255,255,255,0.6)', color:T.inkSoft, fontFamily:T.font, fontWeight:600, fontSize:15, borderRadius:16, border:`2px solid rgba(0,0,0,0.1)`, cursor:'pointer' }}>
            Következő játékos →
          </button>
        </div>
      )}
    </div>
  );
}"""

html = re.sub(
    r'function EremGame\(\{ gameIdx \}\) \{.*?\n\}(?=\n\nfunction TapperGame)',
    NEW_EREM, html, flags=re.DOTALL
)

# ── 5. GameContent router: pass challenger+opponent+onAdvance to EremGame ────
html = html.replace(
    "  if (gameId === 'erem') return <EremGame key={gameIdx} gameIdx={gameIdx} />;",
    "  if (gameId === 'erem') return <EremGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} />;",
    1
)

# ── 6. CollectBoomGame: Lóverseny-style indicator ────────────────────────────
OLD_COLLECT_CHIPS = """      {/* Player score chips */}
      <div style={{display:'flex',gap:6,flexWrap:'wrap',justifyContent:'center',width:'100%'}}>
        {players.map(p => {
          const isActive = !bombPid && p.id===currentPlayer?.id;
          const isBombed = p.id===bombPid;
          const pts = scores[p.id]||0;
          return (
            <div key={p.id} style={{
              display:'flex', flexDirection:'column', alignItems:'center', gap:2,
              padding:'8px 10px', borderRadius:14, minWidth:58,
              background: isBombed?'#FFF0EE' : isActive?'rgba(255,255,255,0.92)':'rgba(255,255,255,0.5)',
              border:`2px solid ${isBombed?'#F87171':isActive?p.color:'transparent'}`,
              boxShadow: isActive ? '0 2px 8px rgba(0,0,0,0.10)' : 'none',
            }}>
              <div style={{width:34,height:34,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:14,color:'#fff'}}>
                {isBombed ? '💥' : p.name.charAt(0).toUpperCase()}
              </div>
              <div style={{fontFamily:'monospace',fontWeight:700,fontSize:14,color:isBombed?'#E55':T.ink,lineHeight:1}}>
                {isBombed ? '💣' : pts>0 ? pts : <span style={{color:T.inkSoft,fontWeight:400,fontSize:11}}>—</span>}
              </div>
            </div>
          );
        })}
      </div>"""

NEW_COLLECT_INDICATOR = """      {/* Player turn indicator */}
      {!bombPid && (
        <div style={{ display:'flex', alignItems:'center', gap:10, background:'rgba(255,255,255,0.92)', borderRadius:14, padding:'10px 14px', boxShadow:T.shadow, width:'100%' }}>
          <div style={{ width:36, height:36, borderRadius:'50%', background:currentPlayer?.color||T.ink, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>
            {(currentPlayer?.name||'?').charAt(0).toUpperCase()}
          </div>
          <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink }}>
            {currentPlayer?.name} választ lapot
          </div>
          <div style={{ display:'flex', alignItems:'center', gap:3 }}>
            {players.map((p,i) => <div key={p.id} style={{ width:7, height:7, borderRadius:'50%', background: p.id===currentPlayer?.id ? (currentPlayer.color) : T.inkMute+'40' }} />)}
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginLeft:3 }}>{(turn%Math.max(players.length,1))+1}/{players.length}</div>
          </div>
        </div>
      )}"""

html = html.replace(OLD_COLLECT_CHIPS, NEW_COLLECT_INDICATOR, 1)

# Remove old inline turn indicator text
html = html.replace(
    """      {/* Turn indicator */}
      {!bombPid && !allSafe && (
        <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,textAlign:'center'}}>
          <span style={{fontWeight:700,color:currentPlayer?.color||T.ink}}>{currentPlayer?.name}</span>
          {' '}választ lapot
        </div>
      )}""",
    "",
    1
)

# ── 7. KisebbGame: Lóverseny-style indicator ─────────────────────────────────
OLD_KISEBB_INDICATOR = """      {/* Current player + drink pot counter */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', width:'100%' }}>
        <div style={{ display:'flex', flexDirection:'column', alignItems:'flex-start', gap:4 }}>
          <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.12em' }}>Ő tippel</div>
          <div style={{ display:'flex', alignItems:'center', gap:8 }}>
            <div style={{ width:40, height:40, borderRadius:'50%', background:currentPlayer?.color||T.coral, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:'#fff' }}>
              {(currentPlayer?.name||'?').charAt(0).toUpperCase()}
            </div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:17, color:T.ink }}>{currentPlayer?.name||'?'}</div>
          </div>
        </div>

        {/* Drink pot */}
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:2, background:'rgba(255,255,255,0.65)', borderRadius:14, padding:'8px 14px', boxShadow:'0 1px 6px rgba(0,0,0,0.08)' }}>
          <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>Tét</div>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:22, color: pot>=3 ? '#D05040' : pot>=2 ? '#E0A030' : '#1B2340', lineHeight:1 }}>{pot}</div>
          <div style={{ fontFamily:T.font, fontSize:10, color:T.inkSoft }}>korty</div>
        </div>
      </div>"""

NEW_KISEBB_INDICATOR = """      {/* Player turn indicator + pot */}
      <div style={{ display:'flex', alignItems:'center', gap:8, width:'100%' }}>
        <div style={{ flex:1, display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:14, padding:'10px 14px', boxShadow:T.shadow }}>
          <div style={{ width:36, height:36, borderRadius:'50%', background:currentPlayer?.color||T.coral, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>
            {(currentPlayer?.name||'?').charAt(0).toUpperCase()}
          </div>
          <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink }}>
            {currentPlayer?.name||'?'} tippel
          </div>
          <div style={{ display:'flex', alignItems:'center', gap:3 }}>
            {activePids.map((_,i) => <div key={i} style={{ width:7, height:7, borderRadius:'50%', background: i===turnPos%Math.max(activePids.length,1) ? (currentPlayer?.color||T.mint) : T.inkMute+'40' }} />)}
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginLeft:3 }}>{(turnPos%Math.max(activePids.length,1))+1}/{activePids.length}</div>
          </div>
        </div>
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:1, background:'rgba(255,255,255,0.65)', borderRadius:14, padding:'8px 12px', boxShadow:'0 1px 6px rgba(0,0,0,0.08)', flexShrink:0 }}>
          <div style={{ fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>Tét</div>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:20, color: pot>=3 ? '#D05040' : pot>=2 ? '#E0A030' : '#1B2340', lineHeight:1 }}>{pot}</div>
        </div>
      </div>"""

html = html.replace(OLD_KISEBB_INDICATOR, NEW_KISEBB_INDICATOR, 1)

# ── 8. MemoriaGame: Lóverseny-style indicator ────────────────────────────────
html = html.replace(
    """      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft }}>
        <span style={{ fontWeight:700, color:currentPlayer?.color||T.ink }}>{currentPlayer?.name}</span> fordit lapot
      </div>""",
    """      <div style={{ display:'flex', alignItems:'center', gap:10, background:'rgba(255,255,255,0.92)', borderRadius:14, padding:'10px 14px', boxShadow:T.shadow, width:'100%' }}>
        <div style={{ width:36, height:36, borderRadius:'50%', background:currentPlayer?.color||T.ink, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>
          {(currentPlayer?.name||'?').charAt(0).toUpperCase()}
        </div>
        <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink }}>
          {currentPlayer?.name} fordít lapot
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:3 }}>
          {players.map((_,i) => <div key={i} style={{ width:7, height:7, borderRadius:'50%', background: i===turn%n ? (currentPlayer?.color||T.mint) : T.inkMute+'40' }} />)}
          <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginLeft:3 }}>{(turn%n)+1}/{n}</div>
        </div>
      </div>""",
    1
)

# ── 9. Version bump ──────────────────────────────────────────────────────────
html = html.replace(
    'Verzió 5.25 · DNR · 2026.06.01 01:00',
    'Verzió 5.26 · DNR · 2026.06.01 02:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
