import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

NEW_UVEG = r"""function UvegGame({ gameIdx, players }) {
  const [angle, setAngle] = React.useState(0);
  const [spinning, setSpinning] = React.useState(false);
  const [winner, setWinner] = React.useState(null);

  React.useEffect(() => { setAngle(0); setSpinning(false); setWinner(null); }, [gameIdx]);

  const n = Math.max(players.length, 1);

  const spin = () => {
    if (spinning || winner) return;
    const winnerIdx = Math.floor(Math.random() * n);
    const targetDeg = winnerIdx * (360 / n);
    const curNorm = ((angle % 360) + 360) % 360;
    const delta = ((targetDeg - curNorm) + 360) % 360 || 360;
    const totalAngle = angle + (4 + Math.floor(Math.random() * 3)) * 360 + delta;
    setSpinning(true);
    setAngle(totalAngle);
    setTimeout(() => { setSpinning(false); setWinner(players[winnerIdx]); }, 3600);
  };

  const CX = 180, CY = 180;
  const DIAL_R = 104;
  const PLAYER_R = 127;
  const NAME_R = 150;
  const NUM_TICKS = 60;

  const ticks = Array.from({ length: NUM_TICKS }, (_, i) => {
    const a = (i * 360 / NUM_TICKS - 90) * Math.PI / 180;
    const isMaj = i % 5 === 0;
    const ri = isMaj ? 94 : 98;
    return {
      x1: (CX + ri * Math.cos(a)).toFixed(1),
      y1: (CY + ri * Math.sin(a)).toFixed(1),
      x2: (CX + 103 * Math.cos(a)).toFixed(1),
      y2: (CY + 103 * Math.sin(a)).toFixed(1),
      isMaj,
    };
  });

  const playerData = players.map((p, i) => {
    const a = (i * (360 / n) - 90) * Math.PI / 180;
    return {
      p,
      ax: (CX + PLAYER_R * Math.cos(a)).toFixed(1),
      ay: (CY + PLAYER_R * Math.sin(a)).toFixed(1),
      nx: (CX + NAME_R * Math.cos(a)).toFixed(1),
      ny: (CY + NAME_R * Math.sin(a)).toFixed(1),
    };
  });

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:10 }}>
      <svg width="280" height="280" viewBox="0 0 360 360" style={{ overflow:'visible' }}>

        {/* Dial face */}
        <circle cx={CX} cy={CY} r={DIAL_R} fill="#F5F0E4" stroke="#1B2340" strokeWidth="3.5" />

        {/* Tick marks */}
        {ticks.map((t, i) => (
          <line key={i} x1={t.x1} y1={t.y1} x2={t.x2} y2={t.y2}
            stroke="#C4B898" strokeWidth={t.isMaj ? 2 : 1} />
        ))}

        {/* Inner dashed ring */}
        <circle cx={CX} cy={CY} r={74} fill="none" stroke="#D0C8B0" strokeWidth="1" strokeDasharray="5 4" />

        {/* Bottle group — centered at CX,CY so rotation works cleanly */}
        <g transform={`translate(${CX} ${CY})`}>
          <g style={{
            transform: `rotate(${angle}deg)`,
            transformOrigin: '0px 0px',
            transition: spinning ? 'transform 3.6s cubic-bezier(0.13,0.60,0.06,1)' : 'none',
          }}>
            {/* Dashed pointer line */}
            <line x1="0" y1="0" x2="0" y2="-93" stroke="#E55555" strokeWidth="1.5" strokeDasharray="5 3" opacity="0.65" />
            {/* Arrow tip */}
            <polygon points="0,-97 -5,-85 5,-85" fill="#E55555" />
            {/* Bottle cap */}
            <rect x="-7" y="-82" width="14" height="7" rx="2.5" fill="#1B2340" />
            {/* Neck */}
            <rect x="-5" y="-76" width="10" height="18" rx="4" fill="#2D6A4F" />
            {/* Shoulder taper */}
            <path d="M -5,-58 Q -14,-54 -14,-46 L 14,-46 Q 14,-54 5,-58 Z" fill="#2D6A4F" />
            {/* Body */}
            <rect x="-14" y="-46" width="28" height="48" rx="8" fill="#2D6A4F" />
            {/* Label highlight */}
            <rect x="-10" y="-40" width="20" height="24" rx="4" fill="rgba(255,255,255,0.2)" />
            {/* Bottom rim */}
            <rect x="-14" y="2" width="28" height="5" rx="3" fill="#1B4332" />
          </g>
        </g>

        {/* Center hub */}
        <circle cx={CX} cy={CY} r={11} fill="#1B2340" />
        <circle cx={CX} cy={CY} r={5} fill="#fff" />

        {/* Player avatars + names */}
        {playerData.map(({ p, ax, ay, nx, ny }) => {
          const isW = winner && winner.id === p.id;
          return (
            <g key={p.id}>
              {isW && <circle cx={ax} cy={ay} r="24" fill={p.color} opacity="0.2" />}
              <circle cx={ax} cy={ay} r="20" fill={p.color} stroke="#fff" strokeWidth={isW ? 3 : 2} />
              <text x={ax} y={ay} textAnchor="middle" dominantBaseline="middle"
                fill="#fff" fontSize="13" fontWeight="bold" style={{ userSelect:'none' }}>
                {p.name.charAt(0).toUpperCase()}
              </text>
              <text x={nx} y={ny} textAnchor="middle" dominantBaseline="middle"
                fill={isW ? p.color : '#1B2340'} fontSize="11" fontWeight={isW ? '800' : '600'}
                style={{ userSelect:'none' }}>
                {p.name}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Result card */}
      {winner && (
        <div style={{ width:'100%', padding:'10px 18px', borderRadius:14, background:'rgba(255,255,255,0.9)', boxShadow:T.shadow, textAlign:'center', animation:'popIn .3s' }}>
          <span style={{ fontFamily:T.font, fontSize:14, color:T.ink }}>
            🧭 A palack{' '}
            <span style={{ fontWeight:800, color:winner.color }}>{winner.name}</span>
            {' '}felé áll — iszik!
          </span>
        </div>
      )}

      {/* Spin button */}
      <button onClick={spin} disabled={spinning} style={{
        width:'100%', padding:'14px', borderRadius:16,
        background: spinning ? 'rgba(255,255,255,0.45)' : 'rgba(255,255,255,0.7)',
        border:`2px solid ${T.mint}`, color:T.mint,
        fontFamily:T.font, fontWeight:700, fontSize:16,
        cursor: spinning ? 'default' : 'pointer',
        opacity: spinning ? 0.65 : 1,
      }}>
        {spinning ? '🌀 Pörög…' : '🍾 Pörgetés!'}
      </button>
    </div>
  );
}"""

html = re.sub(
    r'function UvegGame\(\{ gameIdx, players \}\) \{.*?\n\}(?=\n\nfunction TicktakGame)',
    NEW_UVEG, html, flags=re.DOTALL
)

# Version bump
html = html.replace(
    'Verzió 5.23 · DNR · 2026.05.31 04:00',
    'Verzió 5.24 · DNR · 2026.05.31 05:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
