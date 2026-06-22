import re

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# ── 1. Add coin3DFlip keyframe (inject after existing coinFlip) ──────────────
OLD_KF = '@keyframes coinFlip    {'
assert OLD_KF in src, 'coinFlip keyframe not found'

NEW_KF_BLOCK = """@keyframes coin3DFlip {
  0%   { transform: perspective(600px) rotateY(0deg)   scaleX(1); }
  25%  { transform: perspective(600px) rotateY(360deg) scaleX(1); }
  50%  { transform: perspective(600px) rotateY(720deg) scaleX(1); }
  75%  { transform: perspective(600px) rotateY(1080deg) scaleX(1); }
  100% { transform: perspective(600px) rotateY(1440deg) scaleX(1); }
}
@keyframes coinSettle {
  0%   { transform: perspective(600px) rotateY(0deg)  scale(0.85); opacity:0; }
  60%  { transform: perspective(600px) rotateY(0deg)  scale(1.08); opacity:1; }
  100% { transform: perspective(600px) rotateY(0deg)  scale(1);    opacity:1; }
}
@keyframes eremWin {
  0%   { transform: scale(0.8) translateY(10px); opacity:0; }
  60%  { transform: scale(1.05) translateY(-4px); opacity:1; }
  100% { transform: scale(1) translateY(0); opacity:1; }
}
"""

src = src.replace(OLD_KF, NEW_KF_BLOCK + OLD_KF, 1)
assert '@keyframes coin3DFlip' in src

# ── 2. Replace the full EremGame function ────────────────────────────────────
OLD_EREM = """function EremGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
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
    }, 1600);
  };

  const correct = pick !== null && result !== null && pick === result;

  const CoinFace = ({ side }) => (
    <svg width="160" height="160" viewBox="-72 -72 144 144">
      <ellipse cx="0" cy="60" rx="52" ry="9" fill="rgba(0,0,0,0.10)"/>
      <circle r="68" fill={T.yellow} stroke={T.ink} strokeWidth="5.5"/>
      <circle r="54" fill="none" stroke={T.ink} strokeWidth="1.5" strokeDasharray="6 4" opacity="0.5"/>
      {side === 'fej' ? (
        <g>
          <circle cy="-14" r="18" fill={T.ink}/>
          <path d="M -28,22 Q -28,4 0,4 Q 28,4 28,22 Z" fill="#1B2340"/>
        </g>
      ) : (
        <g>
          <path d="M -28,-18 C -14,-30 14,-6 28,-18" fill="none" stroke={T.ink} strokeWidth="3.5" strokeLinecap="round"/>
          <path d="M -28,-2 C -14,-14 14,10 28,-2" fill="none" stroke={T.ink} strokeWidth="3.5" strokeLinecap="round"/>
          <path d="M -28,14 C -14,2 14,26 28,14" fill="none" stroke={T.ink} strokeWidth="3.5" strokeLinecap="round"/>
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
          <div style={{ background:T.yellow, borderRadius:12, padding:'4px 10px', fontFamily:T.font, fontWeight:800, fontSize:12, color:T.ink }}>
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


    </div>
  );
}"""

assert OLD_EREM in src, 'EremGame not found'

NEW_EREM = """function EremGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
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

  const won = pick !== null && result !== null && pick === result;

  /* ── Coin SVG ── */
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
              {/* Crown */}
              <path d="M -22,-28 L -22,-8 L -14,-16 L 0,-6 L 14,-16 L 22,-8 L 22,-28 Z"
                    fill="#8A5F06" opacity="0.85"/>
              <path d="M -22,-28 L -14,-38 L 0,-30 L 14,-38 L 22,-28"
                    fill="none" stroke="#8A5F06" strokeWidth="2.5" strokeLinejoin="round"/>
              {/* Gems on crown */}
              <circle cx="-14" cy="-35" r="4" fill="#e74c3c"/>
              <circle cx="0"   cy="-28" r="4.5" fill="#2980b9"/>
              <circle cx="14"  cy="-35" r="4" fill="#27ae60"/>
              {/* Face profile */}
              <ellipse cx="0" cy="12" rx="14" ry="17" fill="#C8960C" opacity="0.7"/>
              <circle cx="0" cy="6" r="10" fill="#8A5F06" opacity="0.5"/>
            </g>
          ) : (
            <g transform={`translate(${r},${r})`}>
              {/* Star/decorative pattern for "írás" */}
              <text x="0" y="14" textAnchor="middle" fontSize="52" fontWeight="900"
                    fill="#8A5F06" opacity="0.6" fontFamily="serif">₮</text>
              {/* Corner ornaments */}
              {[[-30,-30],[30,-30],[-30,30],[30,30]].map(([x,y],i) => (
                <circle key={i} cx={x} cy={y} r="4.5" fill="#8A5F06" opacity="0.4"/>
              ))}
              <path d="M -16,0 L 16,0 M 0,-16 L 0,16" stroke="#8A5F06" strokeWidth="1.5" opacity="0.3"/>
            </g>
          )}
        </svg>
      </div>
    );
  };

  /* ── Pick option button ── */
  const PickBtn = ({ side, label, icon }) => (
    <button
      onClick={() => doFlip(side)}
      style={{
        flex:1, display:'flex', flexDirection:'column', alignItems:'center',
        gap:10, padding:'18px 12px',
        background: `linear-gradient(160deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.8) 100%)`,
        border: `2.5px solid rgba(245,197,24,0.35)`,
        borderRadius: 22, cursor:'pointer',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.9)',
        transition: 'transform 0.12s, box-shadow 0.12s',
      }}
      onPointerDown={e => e.currentTarget.style.transform='scale(0.96)'}
      onPointerUp={e => e.currentTarget.style.transform='scale(1)'}
      onPointerLeave={e => e.currentTarget.style.transform='scale(1)'}
    >
      <Coin side={side} size={90}/>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, letterSpacing:'0.04em' }}>
        {label}
      </div>
      <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, fontWeight:600, textTransform:'uppercase', letterSpacing:'0.1em' }}>
        {side === 'fej' ? 'Korona oldal' : 'Írásos oldal'}
      </div>
    </button>
  );

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:20, padding:'4px 0' }}>

      {/* Phase: pick */}
      {phase === 'pick' && (
        <>
          {challenger && (
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <div style={{ width:30, height:30, borderRadius:'50%', background:challenger.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>
                {challenger.name.charAt(0).toUpperCase()}
              </div>
              <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.inkSoft }}>
                {challenger.name}, válassz oldalt!
              </span>
            </div>
          )}
          <div style={{ display:'flex', gap:14, width:'100%' }}>
            <PickBtn side="fej"  label="FEJ"  />
            <PickBtn side="iras" label="ÍRÁS" />
          </div>
        </>
      )}

      {/* Phase: flipping */}
      {phase === 'flipping' && (
        <>
          {/* Pick reminder */}
          <div style={{ display:'flex', alignItems:'center', gap:8, background:'rgba(255,255,255,0.7)', borderRadius:20, padding:'7px 14px' }}>
            {challenger && (
              <div style={{ width:26, height:26, borderRadius:'50%', background:challenger.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff' }}>
                {challenger.name.charAt(0).toUpperCase()}
              </div>
            )}
            <span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft }}>
              {challenger?.name} tippje:
            </span>
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink,
              background: `linear-gradient(135deg, #FFE97A, #F5C518)`,
              borderRadius:10, padding:'3px 10px' }}>
              {pick === 'fej' ? 'FEJ' : 'ÍRÁS'}
            </span>
          </div>

          <Coin side="fej" size={180} spinning={true}/>

          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.inkSoft,
            letterSpacing:'0.12em', textTransform:'uppercase',
            animation:'pulse 0.6s ease-in-out infinite' }}>
            Pörög…
          </div>
        </>
      )}

      {/* Phase: result */}
      {phase === 'result' && (
        <>
          <Coin side={result} size={180} settling={true}/>

          {/* What came up */}
          <div style={{
            fontFamily:T.font, fontWeight:900, fontSize:20, letterSpacing:'0.1em',
            textTransform:'uppercase', color:T.ink,
            animation:'popIn .3s cubic-bezier(0.34,1.56,0.64,1)',
          }}>
            {result === 'fej' ? '👑 FEJ' : '✍️ ÍRÁS'}
          </div>

          {/* Win/Lose banner */}
          <div style={{
            width:'100%', borderRadius:20, padding:'18px 16px',
            background: won
              ? `linear-gradient(135deg, ${T.mint}22, ${T.mint}44)`
              : `linear-gradient(135deg, ${T.coral}18, ${T.coral}38)`,
            border: `2.5px solid ${won ? T.mint : T.coral}`,
            display:'flex', flexDirection:'column', alignItems:'center', gap:6,
            animation:'eremWin 0.5s cubic-bezier(0.34,1.56,0.64,1)',
          }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22,
              color: won ? T.mint : T.coral, letterSpacing:'0.04em' }}>
              {won ? '🎉 Eltaláltad!' : '😬 Mellément!'}
            </div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink, textAlign:'center' }}>
              {won
                ? <>{opponent?.name || 'Ellenfél'} <span style={{ color:T.coral }}>iszik 1-et</span></>
                : <>{challenger?.name || 'Kihívó'} <span style={{ color:T.coral }}>iszik 1-et</span></>
              }
            </div>
          </div>
        </>
      )}

    </div>
  );
}"""

src = src.replace(OLD_EREM, NEW_EREM, 1)
assert 'coin3DFlip' in src
assert 'coinSettle' in src
assert 'eremWin' in src

# ── 3. Version bump ──────────────────────────────────────────────────────────
import re
m = re.search(r'Aktuális verzió.*?v(\d+\.\d+)', src)
if m:
    old_ver = m.group(0)
    parts = m.group(1).split('.')
    new_ver_str = f"{parts[0]}.{int(parts[1])+1}"
    src = src.replace(old_ver, old_ver.replace(m.group(1), new_ver_str), 1)

ver_m = re.search(r"appVersion\s*=\s*['\"]v([\d.]+)['\"]", src)
if ver_m:
    old_v = ver_m.group(0)
    parts2 = ver_m.group(1).split('.')
    new_v = f"{parts2[0]}.{int(parts2[1])+1}"
    new_line = old_v.replace(ver_m.group(1), new_v)
    src = src.replace(old_v, new_line, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print('OK — EremGame refactored')
