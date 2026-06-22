with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

OLD = """function EremGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
  const [pick, setPick] = React.useState(null);
  const [phase, setPhase] = React.useState('pick');
  const [result, setResult] = React.useState(null);
  const advancedRef = React.useRef(false);

  React.useEffect(() => { setPick(null); setPhase('pick'); setResult(null); advancedRef.current = false; }, [gameIdx]);

  const doFlip = (choice) => {
    setPick(choice);
    setPhase('flipping');
    setTimeout(() => {
      const r = Math.random() < 0.5 ? 'fej' : 'iras';
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
    }, 2000);
  };

  const won = pick !== null && result !== null && pick === result;"""

assert OLD in src, 'EremGame state+doFlip block not found'

NEW = """function EremGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
  const [pick, setPick] = React.useState(null);
  const [phase, setPhase] = React.useState('pick');
  const [result, setResult] = React.useState(null);
  const [flipAngle, setFlipAngle] = React.useState(0);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPick(null); setPhase('pick'); setResult(null); setFlipAngle(0);
    advancedRef.current = false;
  }, [gameIdx]);

  const FLIP_DURATION = 2400; // ms

  const doFlip = (choice) => {
    // Pre-compute result so we can animate to the correct face
    const r = Math.random() < 0.5 ? 'fej' : 'iras';
    const spins = 5 + Math.floor(Math.random() * 3); // 5-7 full rotations
    const faceAngle = r === 'iras' ? 180 : 0;
    setFlipAngle(spins * 360 + faceAngle);
    setPick(choice);
    setPhase('flipping');
    setTimeout(() => {
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
    }, FLIP_DURATION + 200);
  };

  const won = pick !== null && result !== null && pick === result;"""

src = src.replace(OLD, NEW, 1)
assert 'flipAngle' in src

# ── Replace Coin component to use real 3D two-face flip ──────────────────────
OLD_COIN = """  /* ── Coin SVG ── */
  const Coin = ({ side, size = 180, spinning = false, settling = false }) => {
    const s = size;
    const r = s / 2;
    const id = `cg_${side}`;
    return (
      <div style={{
        width: s, height: s,
        animation: spinning ? 'coin3DFlip 1.9s cubic-bezier(0.25,0.1,0.1,1) forwards'
                 : settling ? 'coinSettle 0.5s cubic-bezier(0.34,1.56,0.64,1) forwards'
                 : 'none',
        filter: spinning ? 'drop-shadow(0 8px 24px rgba(0,0,0,0.25))' : 'drop-shadow(0 6px 18px rgba(0,0,0,0.22))',
      }}>
        <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`}>
          <defs>
            <radialGradient id={id} cx="38%" cy="32%" r="65%">
              <stop offset="0%"   stopColor="#FFE97A"/>
              <stop offset="45%"  stopColor="#F5C518"/>
              <stop offset="100%" stopColor="#C8960C"/>
            </radialGradient>
            <radialGradient id={`${id}_edge`} cx="50%" cy="50%" r="50%">
              <stop offset="85%"  stopColor="#B8820A"/>
              <stop offset="100%" stopColor="#8A5F06"/>
            </radialGradient>
          </defs>
          {/* Shadow */}
          <ellipse cx={r} cy={s - 10} rx={r * 0.72} ry={8} fill="rgba(0,0,0,0.13)"/>
          {/* Edge ring */}
          <circle cx={r} cy={r} r={r - 2} fill={`url(#${id}_edge)`}/>
          {/* Face */}
          <circle cx={r} cy={r} r={r - 8} fill={`url(#${id})`}/>
          {/* Rim detail */}
          <circle cx={r} cy={r} r={r - 8} fill="none" stroke="rgba(255,255,255,0.35)" strokeWidth="2.5"/>
          <circle cx={r} cy={r} r={r - 14} fill="none" stroke="rgba(0,0,0,0.12)" strokeWidth="1.5" strokeDasharray="5 3"/>
          {side === 'fej' ? (
            <g transform={`translate(${r},${r})`}>
              {/* Crown icon */}
              <path d="M -26,-14 L -26,4 L 26,4 L 26,-14 L 14,-4 L 0,-20 L -14,-4 Z"
                    fill="#8A5F06" opacity="0.8"/>
              <circle cx="-26" cy="-14" r="4.5" fill="#e74c3c"/>
              <circle cx="0"   cy="-24" r="5" fill="#2980b9"/>
              <circle cx="26"  cy="-14" r="4.5" fill="#27ae60"/>
              {/* FEJ label */}
              <text x="0" y="28" textAnchor="middle"
                    fontSize={s > 120 ? 22 : 14} fontWeight="900"
                    fill="#8A5F06" opacity="0.9"
                    fontFamily="system-ui,sans-serif" letterSpacing="4">FEJ</text>
            </g>
          ) : (
            <g transform={`translate(${r},${r})`}>
              {/* Quill/pen lines */}
              <path d="M -18,-22 L 10,22" stroke="#8A5F06" strokeWidth="3" strokeLinecap="round" opacity="0.7"/>
              <path d="M -6,-22 L 22,22" stroke="#8A5F06" strokeWidth="3" strokeLinecap="round" opacity="0.45"/>
              <path d="M -30,-10 L -4,22" stroke="#8A5F06" strokeWidth="3" strokeLinecap="round" opacity="0.25"/>
              {/* ÍRÁS label */}
              <text x="0" y="28" textAnchor="middle"
                    fontSize={s > 120 ? 19 : 12} fontWeight="900"
                    fill="#8A5F06" opacity="0.9"
                    fontFamily="system-ui,sans-serif" letterSpacing="2">ÍRÁS</text>
            </g>
          )}
        </svg>
      </div>
    );
  };"""

assert OLD_COIN in src, 'Coin component not found'

NEW_COIN = """  /* ── Coin face SVG (single side) ── */
  const CoinFaceSVG = ({ side, size }) => {
    const s = size;
    const r = s / 2;
    const gid = `cf_${side}_${size}`;
    return (
      <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`}>
        <defs>
          <radialGradient id={gid} cx="38%" cy="32%" r="65%">
            <stop offset="0%"   stopColor="#FFE97A"/>
            <stop offset="45%"  stopColor="#F5C518"/>
            <stop offset="100%" stopColor="#C8960C"/>
          </radialGradient>
          <radialGradient id={`${gid}_e`} cx="50%" cy="50%" r="50%">
            <stop offset="85%"  stopColor="#B8820A"/>
            <stop offset="100%" stopColor="#8A5F06"/>
          </radialGradient>
        </defs>
        <circle cx={r} cy={r} r={r - 2} fill={`url(#${gid}_e)`}/>
        <circle cx={r} cy={r} r={r - 8} fill={`url(#${gid})`}/>
        <circle cx={r} cy={r} r={r - 8}  fill="none" stroke="rgba(255,255,255,0.35)" strokeWidth="2.5"/>
        <circle cx={r} cy={r} r={r - 14} fill="none" stroke="rgba(0,0,0,0.12)" strokeWidth="1.5" strokeDasharray="5 3"/>
        {side === 'fej' ? (
          <g transform={`translate(${r},${r})`}>
            <path d="M -26,-14 L -26,4 L 26,4 L 26,-14 L 14,-4 L 0,-20 L -14,-4 Z"
                  fill="#8A5F06" opacity="0.8"/>
            <circle cx="-26" cy="-14" r="4.5" fill="#e74c3c"/>
            <circle cx="0"   cy="-24" r="5"   fill="#2980b9"/>
            <circle cx="26"  cy="-14" r="4.5" fill="#27ae60"/>
            <text x="0" y="28" textAnchor="middle"
                  fontSize={s > 120 ? 22 : 14} fontWeight="900"
                  fill="#8A5F06" opacity="0.9"
                  fontFamily="system-ui,sans-serif" letterSpacing="4">FEJ</text>
          </g>
        ) : (
          <g transform={`translate(${r},${r})`}>
            <path d="M -18,-22 L 10,22" stroke="#8A5F06" strokeWidth="3" strokeLinecap="round" opacity="0.7"/>
            <path d="M -6,-22 L 22,22"  stroke="#8A5F06" strokeWidth="3" strokeLinecap="round" opacity="0.45"/>
            <path d="M -30,-10 L -4,22" stroke="#8A5F06" strokeWidth="3" strokeLinecap="round" opacity="0.25"/>
            <text x="0" y="28" textAnchor="middle"
                  fontSize={s > 120 ? 19 : 12} fontWeight="900"
                  fill="#8A5F06" opacity="0.9"
                  fontFamily="system-ui,sans-serif" letterSpacing="2">ÍRÁS</text>
          </g>
        )}
      </svg>
    );
  };

  /* ── 3D two-face Coin ── */
  const Coin = ({ size = 180 }) => {
    const isFlipping = phase === 'flipping';
    return (
      <div style={{
        perspective: '700px',
        width: size, height: size,
        filter: 'drop-shadow(0 6px 20px rgba(0,0,0,0.22))',
      }}>
        <div style={{
          width: '100%', height: '100%',
          position: 'relative',
          transformStyle: 'preserve-3d',
          transform: `rotateY(${flipAngle}deg)`,
          transition: isFlipping
            ? `transform ${FLIP_DURATION}ms cubic-bezier(0.15,0.45,0.18,1)`
            : 'none',
        }}>
          {/* Front face: FEJ (0 deg) */}
          <div style={{ position:'absolute', inset:0, backfaceVisibility:'hidden' }}>
            <CoinFaceSVG side="fej" size={size}/>
          </div>
          {/* Back face: ÍRÁS (180 deg) */}
          <div style={{ position:'absolute', inset:0, backfaceVisibility:'hidden', transform:'rotateY(180deg)' }}>
            <CoinFaceSVG side="iras" size={size}/>
          </div>
        </div>
      </div>
    );
  };"""

src = src.replace(OLD_COIN, NEW_COIN, 1)
assert 'CoinFaceSVG' in src

# ── Fix Coin usages: remove old props (side/spinning/settling) ───────────────
# In flipping phase
src = src.replace('<Coin side="fej" size={180} spinning={true}/>', '<Coin size={180}/>', 1)
# In result phase
src = src.replace('<Coin side={result} size={180} settling={true}/>', '<Coin size={180}/>', 1)
# In PickBtn (small coin preview)
src = src.replace(
    '<Coin side={side} size={90}/>',
    '<CoinFaceSVG side={side} size={90}/>',
    1
)

# ── Version bump ─────────────────────────────────────────────────────────────
import re
m = re.search(r"APP_VERSION = 'v([\d.]+)'", src)
if m:
    parts = m.group(1).split('.')
    nv = f"{parts[0]}.{int(parts[1])+1}"
    src = src.replace(m.group(0), f"APP_VERSION = 'v{nv}'", 1)
    print(f"Version → v{nv}")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print('OK — 3D two-face coin flip done')
