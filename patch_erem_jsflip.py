with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# ── Find and replace the entire EremGame function ────────────────────────────
import re

START = 'function EremGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {'
assert START in src, 'EremGame start not found'

# Find end of EremGame (next top-level function)
START_IDX = src.index(START)
END_MARKER = '\nfunction TapperGame('
END_IDX = src.index(END_MARKER, START_IDX)

OLD_EREM = src[START_IDX:END_IDX]

NEW_EREM = '''function EremGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
  const [pick, setPick] = React.useState(null);
  const [phase, setPhase] = React.useState('pick');
  const [result, setResult] = React.useState(null);
  const [displaySide, setDisplaySide] = React.useState('fej');
  const [squish, setSquish] = React.useState(false);
  const advancedRef = React.useRef(false);
  const flipTimerRef = React.useRef(null);

  React.useEffect(() => {
    if (flipTimerRef.current) clearTimeout(flipTimerRef.current);
    setPick(null); setPhase('pick'); setResult(null);
    setDisplaySide('fej'); setSquish(false);
    advancedRef.current = false;
  }, [gameIdx]);

  const doFlip = (choice) => {
    if (flipTimerRef.current) clearTimeout(flipTimerRef.current);
    const r = Math.random() < 0.5 ? 'fej' : 'iras';
    setPick(choice);
    setPhase('flipping');

    // JS-driven flip simulation: starts fast, decelerates, lands on correct face
    let elapsed = 0;
    let interval = 70;
    let current = 'fej';
    const TOTAL = 2600;
    const SQUISH_MS = 60;

    const step = () => {
      current = current === 'fej' ? 'iras' : 'fej';
      setSquish(true);
      setDisplaySide(current);
      setTimeout(() => setSquish(false), SQUISH_MS);

      elapsed += interval;
      // Ease out: interval grows as elapsed increases
      interval = Math.min(75 + elapsed * 0.75, 550);

      if (elapsed < TOTAL) {
        flipTimerRef.current = setTimeout(step, interval);
      } else {
        // Snap to correct result face
        setSquish(true);
        setTimeout(() => {
          setDisplaySide(r);
          setSquish(false);
          setResult(r);
          setPhase('result');
          const isCorrect = choice === r;
          if (!advancedRef.current) {
            advancedRef.current = true;
            const dm = {};
            const pm = {};
            if (isCorrect && opponent) dm[opponent.id] = 1;
            if (!isCorrect && challenger) dm[challenger.id] = 1;
            if (isCorrect && challenger) pm[challenger.id] = 1;
            const sub = isCorrect
              ? `${challenger?.name||''} nyert — ${opponent?.name||'ellenfél'} iszik`
              : `${challenger?.name||''} veszített — iszik egyet`;
            onResult && onResult({ correct: isCorrect, playerName: isCorrect ? opponent?.name : challenger?.name, drinks: 1, subtitle: sub });
            onAdvance && onAdvance(dm, pm);
          }
        }, SQUISH_MS + 80);
      }
    };

    flipTimerRef.current = setTimeout(step, interval);
  };

  const won = pick !== null && result !== null && pick === result;

  /* ── Coin face SVG ── */
  const CoinFaceSVG = ({ side, size }) => {
    const s = size;
    const r = s / 2;
    const isFej = side === 'fej';
    // FEJ = arany, ÍRÁS = ezüst
    const gradMain  = isFej ? ['#FFF0A0','#F5C518','#C8960C'] : ['#F0F0F0','#C8C8C8','#8A8A8A'];
    const gradEdge  = isFej ? ['#B8820A','#7A5506'] : ['#909090','#505050'];
    const inkColor  = isFej ? '#7A5506' : '#404040';
    const gid = `cf_${side}_${size}`;
    return (
      <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`}>
        <defs>
          <radialGradient id={gid} cx="38%" cy="32%" r="65%">
            <stop offset="0%"   stopColor={gradMain[0]}/>
            <stop offset="45%"  stopColor={gradMain[1]}/>
            <stop offset="100%" stopColor={gradMain[2]}/>
          </radialGradient>
          <radialGradient id={`${gid}_e`} cx="50%" cy="50%" r="50%">
            <stop offset="80%"  stopColor={gradEdge[0]}/>
            <stop offset="100%" stopColor={gradEdge[1]}/>
          </radialGradient>
        </defs>
        <circle cx={r} cy={r} r={r - 2} fill={`url(#${gid}_e)`}/>
        <circle cx={r} cy={r} r={r - 8} fill={`url(#${gid})`}/>
        <circle cx={r} cy={r} r={r - 8}  fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="2.5"/>
        <circle cx={r} cy={r} r={r - 14} fill="none" stroke="rgba(0,0,0,0.1)" strokeWidth="1.5" strokeDasharray="5 3"/>
        {isFej ? (
          <g transform={`translate(${r},${r})`}>
            <path d="M -26,-14 L -26,4 L 26,4 L 26,-14 L 14,-4 L 0,-20 L -14,-4 Z"
                  fill={inkColor} opacity="0.8"/>
            <circle cx="-26" cy="-14" r="4.5" fill="#e74c3c"/>
            <circle cx="0"   cy="-24" r="5"   fill="#2980b9"/>
            <circle cx="26"  cy="-14" r="4.5" fill="#27ae60"/>
            <text x="0" y="28" textAnchor="middle"
                  fontSize={s > 120 ? 22 : 14} fontWeight="900"
                  fill={inkColor} opacity="0.95"
                  fontFamily="system-ui,sans-serif" letterSpacing="4">FEJ</text>
          </g>
        ) : (
          <g transform={`translate(${r},${r})`}>
            <path d="M -18,-22 L 10,22" stroke={inkColor} strokeWidth="3" strokeLinecap="round" opacity="0.7"/>
            <path d="M -6,-22 L 22,22"  stroke={inkColor} strokeWidth="3" strokeLinecap="round" opacity="0.45"/>
            <path d="M -30,-10 L -4,22" stroke={inkColor} strokeWidth="3" strokeLinecap="round" opacity="0.25"/>
            <text x="0" y="28" textAnchor="middle"
                  fontSize={s > 120 ? 19 : 12} fontWeight="900"
                  fill={inkColor} opacity="0.95"
                  fontFamily="system-ui,sans-serif" letterSpacing="2">ÍRÁS</text>
          </g>
        )}
      </svg>
    );
  };

  /* ── Animated Coin wrapper ── */
  const Coin = ({ size = 180 }) => (
    <div style={{
      width: size, height: size,
      filter: 'drop-shadow(0 6px 20px rgba(0,0,0,0.22))',
      transform: squish ? 'scaleX(0.08)' : 'scaleX(1)',
      transition: squish ? 'transform 0.06s ease-in' : 'transform 0.06s ease-out',
      animation: phase === 'result' ? 'popIn 0.4s cubic-bezier(0.34,1.56,0.64,1)' : 'none',
    }}>
      <CoinFaceSVG side={displaySide} size={size}/>
    </div>
  );

  /* ── Pick button ── */
  const PickBtn = ({ side, label }) => (
    <button
      onClick={() => doFlip(side)}
      style={{
        flex:1, display:'flex', flexDirection:'column', alignItems:'center',
        gap:10, padding:'18px 12px',
        background:'linear-gradient(160deg,rgba(255,255,255,0.95),rgba(255,255,255,0.8))',
        border:`2.5px solid ${side==='fej' ? 'rgba(245,197,24,0.4)' : 'rgba(160,160,160,0.4)'}`,
        borderRadius:22, cursor:'pointer',
        boxShadow:'0 4px 20px rgba(0,0,0,0.08),inset 0 1px 0 rgba(255,255,255,0.9)',
      }}
      onPointerDown={e=>e.currentTarget.style.transform='scale(0.96)'}
      onPointerUp={e=>e.currentTarget.style.transform='scale(1)'}
      onPointerLeave={e=>e.currentTarget.style.transform='scale(1)'}
    >
      <CoinFaceSVG side={side} size={90}/>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, letterSpacing:'0.04em' }}>
        {label}
      </div>
      <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, fontWeight:600,
        textTransform:'uppercase', letterSpacing:'0.1em' }}>
        {side === 'fej' ? '🟡 Arany oldal' : '⚪ Ezüst oldal'}
      </div>
    </button>
  );

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:20, padding:'4px 0' }}>

      {/* Pick phase */}
      {phase === 'pick' && (
        <>
          {challenger && (
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <div style={{ width:30, height:30, borderRadius:'50%', background:challenger.color,
                display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>
                {challenger.name.charAt(0).toUpperCase()}
              </div>
              <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.inkSoft }}>
                {challenger.name}, válassz oldalt!
              </span>
            </div>
          )}
          <div style={{ display:'flex', gap:14, width:'100%' }}>
            <PickBtn side="fej"  label="FEJ"/>
            <PickBtn side="iras" label="ÍRÁS"/>
          </div>
        </>
      )}

      {/* Flipping phase */}
      {phase === 'flipping' && (
        <>
          <div style={{ display:'flex', alignItems:'center', gap:8,
            background:'rgba(255,255,255,0.7)', borderRadius:20, padding:'7px 14px' }}>
            {challenger && (
              <div style={{ width:26, height:26, borderRadius:'50%', background:challenger.color,
                display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff' }}>
                {challenger.name.charAt(0).toUpperCase()}
              </div>
            )}
            <span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft }}>
              {challenger?.name} tippje:
            </span>
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink,
              background: pick==='fej' ? 'linear-gradient(135deg,#FFE97A,#F5C518)' : 'linear-gradient(135deg,#E8E8E8,#C0C0C0)',
              borderRadius:10, padding:'3px 10px' }}>
              {pick === 'fej' ? 'FEJ' : 'ÍRÁS'}
            </span>
          </div>

          <Coin size={180}/>

          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.inkSoft,
            letterSpacing:'0.12em', textTransform:'uppercase',
            animation:'pulse 0.6s ease-in-out infinite' }}>
            Pörög…
          </div>
        </>
      )}

      {/* Result phase */}
      {phase === 'result' && (
        <>
          <Coin size={180}/>

          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, letterSpacing:'0.1em',
            textTransform:'uppercase', color:T.ink,
            animation:'popIn .3s cubic-bezier(0.34,1.56,0.64,1)' }}>
            {result === 'fej' ? '🟡 FEJ' : '⚪ ÍRÁS'}
          </div>

          <div style={{
            width:'100%', borderRadius:20, padding:'18px 16px',
            background: won
              ? `linear-gradient(135deg,${T.mint}22,${T.mint}44)`
              : `linear-gradient(135deg,${T.coral}18,${T.coral}38)`,
            border:`2.5px solid ${won ? T.mint : T.coral}`,
            display:'flex', flexDirection:'column', alignItems:'center', gap:6,
            animation:'eremWin 0.5s cubic-bezier(0.34,1.56,0.64,1)',
          }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22,
              color: won ? T.mint : T.coral, letterSpacing:'0.04em' }}>
              {won ? '🎉 Eltaláltad!' : '😬 Mellément!'}
            </div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink, textAlign:'center' }}>
              {won
                ? <>{opponent?.name||'Ellenfél'} <span style={{ color:T.coral }}>iszik 1-et</span></>
                : <>{challenger?.name||'Kihívó'} <span style={{ color:T.coral }}>iszik 1-et</span></>
              }
            </div>
          </div>
        </>
      )}

    </div>
  );
}
'''

src = src[:START_IDX] + NEW_EREM + src[END_IDX:]

# ── Version bump ──────────────────────────────────────────────────────────────
m = re.search(r"APP_VERSION = 'v([\d.]+)'", src)
if m:
    parts = m.group(1).split('.')
    nv = f"{parts[0]}.{int(parts[1])+1}"
    src = src.replace(m.group(0), f"APP_VERSION = 'v{nv}'", 1)
    print(f"Version → v{nv}")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print('OK — JS-driven coin flip done')
