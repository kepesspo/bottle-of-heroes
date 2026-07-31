#!/usr/bin/env python3
# v10.198 — Szerencsekerék: tényleg kerék
#
# A jatek neve kerek, a kepernyon viszont egy fuggoleges nevsor pergett, mint
# egy gyumolcsautomata. A terv szerinti kerek nem csak szebb: egyszerre latszik
# rajta MINDENKI, es az esely is (egyforma cikkek) — a listaban egyszerre csak
# ot nev fert el, a tobbi lathatatlan volt.
#
# A pergetes ugyanaz marad: veletlen nyertes, majd lassulo animacio.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

start = src.index('function SzerencsekerékGame({')
end = src.index('// ─── DRINK DISTRIBUTOR')
old = src[start:end]
assert 'visibleItems' in old, 'nem a jo blokk'

NEW = '''// Cikkely-szinek. Halvanyak, hogy a sotet nev es az avatar megmaradjon
// olvashatonak; hat szin, igy hat jatekosig nincs ket egyforma szomszed.
const WHEEL_TONES = ['#F2C4C4', '#CFE0F5', '#C9E8D2', '#F5E0AC', '#DFCCF2', '#F7CFE0'];

function SzerencsekerékGame({ gameIdx, players, onAdvance, onResult }) {
  const [phase, setPhase] = React.useState('ready'); // ready | spinning | result
  const [rotation, setRotation] = React.useState(0);
  const [winner, setWinner] = React.useState(null);
  const timerRef = React.useRef(null);

  React.useEffect(() => {
    setPhase('ready'); setWinner(null); setRotation(0);
  }, [gameIdx]);
  React.useEffect(() => () => clearTimeout(timerRef.current), []);

  const n = Math.max(players.length, 1);
  const seg = 360 / n;
  const SPIN_MS = 3600;

  const spin = () => {
    if (phase === 'spinning' || players.length === 0) return;
    setPhase('spinning'); setWinner(null);
    const winnerIdx = Math.floor(Math.random() * n);
    // A mutato 12 oranal all. Az i. cikkely kozepe a kerek sajat rendszereben
    // (i*seg + seg/2) fokra van a 12 oratol, tehat ennyivel kell VISSZAforgatni.
    let target = -(winnerIdx * seg + seg / 2);
    while (target < rotation) target += 360;
    target += 360 * 4;                       // negy teljes kor, hogy pörögjön is
    setRotation(target);
    timerRef.current = setTimeout(() => {
      const w = players[winnerIdx];
      setWinner(w); setPhase('result');
      timerRef.current = setTimeout(() => {
        if (w) {
          onResult && onResult({ correct: false, playerName: w.name, drinks: 1, subtitle: w.name + ' iszik egyet!' });
          onAdvance && onAdvance({ [w.id]: 1 });
        }
      }, 700);
    }, SPIN_MS);
  };

  const SIZE = 288, R = SIZE / 2, rad = R - 6;
  const pt = (angDeg, r) => {
    const a = (angDeg - 90) * Math.PI / 180;
    return [R + r * Math.cos(a), R + r * Math.sin(a)];
  };
  // Egy jatekosnal nincs cikkely-hatar, ott teli kort rajzolunk.
  const nameSize = n <= 4 ? 13 : n <= 7 ? 11.5 : 10;
  const avSize = n <= 4 ? 42 : n <= 7 ? 34 : 26;
  const labelR = rad * (n <= 2 ? 0.45 : 0.62);

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, width:'100%' }}>

      <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:T.ink,
                    letterSpacing:T.letterDisplay, textAlign:'center', lineHeight:1.3 }}>
        PÖRGESD MEG<br/>A KEREKET!
      </div>

      <div style={{ position:'relative', width:SIZE, height:SIZE + 14 }}>
        {/* Mutato — a kerek FOLOTT, hogy a pergo cikkelyek ne takarjak */}
        <div style={{ position:'absolute', top:0, left:'50%', transform:'translateX(-50%)', zIndex:3 }}>
          <svg width="26" height="34" viewBox="0 0 26 34">
            <path d="M13 34C13 34 24 20.5 24 13A11 11 0 1 0 2 13c0 7.5 11 21 11 21z"
                  fill={T.coral} stroke="#fff" strokeWidth="2.5" strokeLinejoin="round"/>
            <circle cx="13" cy="13" r="4" fill="#fff"/>
          </svg>
        </div>

        <div style={{ position:'absolute', top:14, left:0, width:SIZE, height:SIZE,
                      transform:`rotate(${rotation}deg)`,
                      transition: phase === 'spinning' ? `transform ${SPIN_MS}ms cubic-bezier(.16,.84,.28,1)` : 'none' }}>
          <svg width={SIZE} height={SIZE} style={{ display:'block', filter:'drop-shadow(0 6px 16px rgba(20,30,50,0.16))' }}>
            <circle cx={R} cy={R} r={rad + 5} fill={T.surface} />
            {players.map((p, i) => {
              const tone = WHEEL_TONES[i % WHEEL_TONES.length];
              if (n === 1) return <circle key={p.id} cx={R} cy={R} r={rad} fill={tone} />;
              const [x0, y0] = pt(i * seg, rad);
              const [x1, y1] = pt((i + 1) * seg, rad);
              const large = seg > 180 ? 1 : 0;
              return (
                <path key={p.id} d={`M ${R} ${R} L ${x0} ${y0} A ${rad} ${rad} 0 ${large} 1 ${x1} ${y1} Z`}
                      fill={tone} stroke={T.surface} strokeWidth="2.5" />
              );
            })}
          </svg>
          {/* Az avatar es a nev a cikkelyben — HTML, mert a kep kerekre vagasa
              SVG-ben csak maszkkal menne, es a nev tordelese is ide kell. */}
          {players.map((p, i) => {
            const [cx, cy] = pt(i * seg + seg / 2, labelR);
            return (
              <div key={p.id} style={{ position:'absolute', left:cx, top:cy, transform:'translate(-50%,-50%)',
                                       display:'flex', flexDirection:'column', alignItems:'center', gap:3, pointerEvents:'none' }}>
                <div style={{ width:avSize, height:avSize, borderRadius:'50%', overflow:'hidden', flexShrink:0,
                              background:p.color, border:'2.5px solid #fff', display:'grid', placeItems:'center' }}>
                  {p.img
                    ? <img src={p.img} alt="" style={{ width:'100%', height:'100%', objectFit:'cover' }} />
                    : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:avSize*0.42, color:'#fff' }}>{(p.name||'?').charAt(0).toUpperCase()}</span>}
                </div>
                <span style={{ fontFamily:T.font, fontWeight:800, fontSize:nameSize, color:T.ink,
                               maxWidth:76, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</span>
              </div>
            );
          })}
        </div>

        {/* Kozepen a gomb — a kerekkel EGYUTT nem forog, kulonben a felirat fejre allna */}
        <button onClick={spin} disabled={phase === 'spinning'}
          style={{ position:'absolute', top:14 + R, left:R, transform:'translate(-50%,-50%)', zIndex:2,
                   width:92, height:92, borderRadius:'50%', border:'none', background:T.surface,
                   boxShadow:T.shadow, cursor: phase === 'spinning' ? 'default' : 'pointer',
                   display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:2,
                   WebkitTapHighlightColor:'transparent', padding:0 }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={T.coral} strokeWidth="2.4"
               strokeLinecap="round" strokeLinejoin="round"
               style={{ animation: phase === 'spinning' ? 'spin 1s linear infinite' : 'none' }}>
            <path d="M20 12a8 8 0 1 1-2.6-5.9" /><path d="M20 4v4.5h-4.5" />
          </svg>
          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:T.coral, letterSpacing:'0.06em' }}>
            {phase === 'spinning' ? 'PÖRÖG…' : 'PÖRGESS!'}
          </span>
        </button>
      </div>

      {/* A kivalasztott — a kerek megall, de a nev a cikkelyben aprobb, mint
          amit egy asztal tuloldalarol el lehet olvasni. */}
      {winner && (
        <div style={{ width:'100%', boxSizing:'border-box', background:T.surface, borderRadius:18,
                      padding:'12px 16px', boxShadow:T.shadow, display:'flex', alignItems:'center', gap:13,
                      animation:'popIn .3s' }}>
          <div style={{ width:52, height:52, borderRadius:'50%', overflow:'hidden', flexShrink:0,
                        background:winner.color, display:'grid', placeItems:'center' }}>
            {winner.img
              ? <img src={winner.img} alt="" style={{ width:'100%', height:'100%', objectFit:'cover' }} />
              : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:'#fff' }}>{(winner.name||'?').charAt(0).toUpperCase()}</span>}
          </div>
          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:9.5, color:T.inkSoft, letterSpacing:1.6 }}>A KIVÁLASZTOTT</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.ink, lineHeight:1.2,
                          overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{winner.name}</div>
          </div>
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:1, flexShrink:0 }}>
            <BohIcon name="beer" size={20} />
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, lineHeight:1 }}>1</span>
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:8.5, color:T.inkSoft, letterSpacing:1.2 }}>KORTY</span>
          </div>
        </div>
      )}
    </div>
  );
}

'''
src = src[:start] + NEW + src[end:]

assert src.count("const APP_VERSION = 'v10.197';") == 1
src = src.replace("const APP_VERSION = 'v10.197';", "const APP_VERSION = 'v10.198';", 1)
open(P, 'w', encoding='utf-8').write(src)
print('OK — Szerencsekerek: valodi kerek')
