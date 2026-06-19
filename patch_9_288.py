#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = """function KezCsereGame({ gameIdx, players, onAdvance }) {
  const [loserPid, setLoserPid] = React.useState(null);
  React.useEffect(() => { setLoserPid(null); }, [gameIdx]);
  const loser = loserPid ? players.find(p => p.id === loserPid) : null;
  const proceed = () => {
    const dm = {};
    if (loserPid) dm[loserPid] = 1;
    onAdvance && onAdvance(dm);
  };
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, width:'100%' }}>
      <div style={{ width:130, height:130, borderRadius:'50%', background:'#fff', boxShadow:'0 4px 18px rgba(0,0,0,0.10)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:60 }}>
        ✋
      </div>
      <div style={{ fontFamily:T.font, fontWeight:800, fontSize:18, color:T.ink }}>Ki rontott el?</div>
      <div style={{ display:'flex', gap:8, overflowX:'auto', WebkitOverflowScrolling:'touch', paddingBottom:4, width:'100%' }}>
        {players.map(p => {
          const selected = loserPid === p.id;
          return (
            <div key={p.id} onClick={() => setLoserPid(selected ? null : p.id)} style={{
              display:'flex', flexDirection:'column', alignItems:'center', gap:6,
              padding:'10px 14px', borderRadius:14,
              background: selected ? '#FFF0EE' : '#fff',
              border:`2px solid ${selected ? '#F87171' : 'transparent'}`,
              boxShadow:'0 2px 8px rgba(0,0,0,0.08)', cursor:'pointer', minWidth:70, flexShrink:0,
            }}>
              <div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff' }}>
                {p.name.charAt(0).toUpperCase()}
              </div>
              <div style={{ fontFamily:T.font, fontWeight:600, fontSize:12, color:selected?'#E55':T.ink }}>
                {p.name}
              </div>
            </div>
          );
        })}
      </div>
      {loser ? (
        <button onClick={proceed} style={{ width:'100%', padding:'15px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow, animation:'popIn .2s' }}>
          {loser.name} iszik — uj kor →
        </button>
      ) : (
        <button onClick={() => onAdvance && onAdvance({})} style={{ width:'100%', padding:'15px', background:'rgba(255,255,255,0.6)', color:T.inkSoft, fontFamily:T.font, fontWeight:600, fontSize:15, borderRadius:16, border:`2px solid rgba(0,0,0,0.1)`, cursor:'pointer' }}>
          Senki nem rontott — tovabb →
        </button>
      )}
    </div>
  );
}"""

new = """function KezCsereGame({ gameIdx, players, onAdvance, onResult }) {
  const TOTAL_ROUNDS = 5;
  const TOTAL_MISTAKES = 5;
  // mistakes: { [pid]: count }
  const [mistakes, setMistakes] = React.useState({});
  const [round, setRound] = React.useState(1);
  const [done, setDone] = React.useState(false);
  React.useEffect(() => { setMistakes({}); setRound(1); setDone(false); }, [gameIdx]);

  const totalMistakes = Object.values(mistakes).reduce((s,v)=>s+v,0);
  const canFinish = round > TOTAL_ROUNDS || totalMistakes >= TOTAL_MISTAKES;

  const addMistake = (pid) => {
    if (done) return;
    setMistakes(m => ({ ...m, [pid]: (m[pid]||0)+1 }));
  };
  const removeMistake = (pid) => {
    if (done) return;
    setMistakes(m => {
      const cur = m[pid]||0;
      if (cur <= 0) return m;
      const next = { ...m };
      if (cur === 1) delete next[pid];
      else next[pid] = cur - 1;
      return next;
    });
  };

  const nextRound = () => {
    if (canFinish) return finish();
    setRound(r => r + 1);
  };

  const finish = () => {
    if (done) return;
    setDone(true);
    const dm = { ...mistakes };
    const losers = players.filter(p => dm[p.id]);
    let subtitle;
    if (losers.length === 0) {
      subtitle = 'Mindenki hibátlan!';
    } else {
      subtitle = losers.map(p => `${p.name}: ${dm[p.id]} rontás`).join(', ');
    }
    onResult && onResult({ correct: losers.length === 0, playerName: losers[0]?.name || null, drinks: losers.length > 0 ? 1 : 0, subtitle });
    onAdvance && onAdvance(dm);
  };

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:14, width:'100%' }}>
      {/* Header: kör és rontások számlálója */}
      <div style={{ display:'flex', gap:10, width:'100%' }}>
        <div style={{ flex:1, background:T.surface, borderRadius:14, padding:'10px 14px', textAlign:'center', boxShadow:T.shadow }}>
          <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>KÖR</div>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.ink }}>{Math.min(round, TOTAL_ROUNDS)}<span style={{ fontSize:13, color:T.inkSoft, fontWeight:600 }}>/{TOTAL_ROUNDS}</span></div>
        </div>
        <div style={{ flex:1, background:T.surface, borderRadius:14, padding:'10px 14px', textAlign:'center', boxShadow:T.shadow }}>
          <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>RONTÁS</div>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color: totalMistakes >= TOTAL_MISTAKES ? T.coral : T.ink }}>{totalMistakes}<span style={{ fontSize:13, color:T.inkSoft, fontWeight:600 }}>/{TOTAL_MISTAKES}</span></div>
        </div>
      </div>

      {/* Rontás progress bar */}
      <div style={{ width:'100%', height:6, background:T.bgSoft, borderRadius:6, overflow:'hidden' }}>
        <div style={{ width:`${Math.min(totalMistakes/TOTAL_MISTAKES*100,100)}%`, height:'100%', background:T.coral, borderRadius:6, transition:'width .25s' }} />
      </div>

      {/* Kézcsere ikon */}
      <div style={{ width:90, height:90, borderRadius:'50%', background:'#fff', boxShadow:'0 4px 18px rgba(0,0,0,0.10)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:44 }}>
        🤝
      </div>
      <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color:T.ink }}>Ki rontott el?</div>

      {/* Játékos kártyák */}
      <div style={{ display:'flex', flexWrap:'wrap', gap:8, justifyContent:'center', width:'100%' }}>
        {players.map(p => {
          const cnt = mistakes[p.id] || 0;
          const selected = cnt > 0;
          return (
            <div key={p.id} style={{
              display:'flex', flexDirection:'column', alignItems:'center', gap:6,
              padding:'10px 10px', borderRadius:14,
              background: selected ? `${T.coral}18` : T.surface,
              border:`2px solid ${selected ? T.coral : 'transparent'}`,
              boxShadow:T.shadow, minWidth:76, position:'relative',
            }}>
              <div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff' }}>
                {p.name.charAt(0).toUpperCase()}
              </div>
              <div style={{ fontFamily:T.font, fontWeight:600, fontSize:12, color: selected ? T.coral : T.ink }}>{p.name}</div>
              {/* +/- gombok */}
              <div style={{ display:'flex', alignItems:'center', gap:4 }}>
                <button onClick={() => removeMistake(p.id)} disabled={cnt===0}
                  style={{ width:26, height:26, borderRadius:8, border:'none', background: cnt>0 ? T.coral : T.bgSoft, color: cnt>0 ? '#fff' : T.inkMute, fontWeight:900, fontSize:16, cursor: cnt>0?'pointer':'default', display:'flex', alignItems:'center', justifyContent:'center', lineHeight:1 }}>−</button>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color: cnt>0 ? T.coral : T.inkMute, minWidth:16, textAlign:'center' }}>{cnt}</span>
                <button onClick={() => addMistake(p.id)}
                  style={{ width:26, height:26, borderRadius:8, border:'none', background:T.mint, color:'#fff', fontWeight:900, fontSize:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', lineHeight:1 }}>+</button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Következő kör / Befejezés gomb */}
      {canFinish ? (
        <button onClick={finish} style={{ width:'100%', padding:'15px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow, animation:'popIn .2s' }}>
          🏁 Befejezés
        </button>
      ) : (
        <button onClick={nextRound} style={{ width:'100%', padding:'15px', background:T.bgSoft, color:T.ink, fontFamily:T.font, fontWeight:700, fontSize:15, borderRadius:16, border:'none', cursor:'pointer' }}>
          Következő kör ({round}/{TOTAL_ROUNDS}) →
        </button>
      )}
    </div>
  );
}"""

assert old in html, "FAIL: KezCsereGame"
html = html.replace(old, new, 1)

# Add onResult prop to KezCsereGame call
old2 = """  if (gameId === 'kezcsere') return <KezCsereGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;"""
new2 = """  if (gameId === 'kezcsere') return <KezCsereGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;"""
assert old2 in html, "FAIL: KezCsereGame call"
html = html.replace(old2, new2, 1)

html = html.replace("const APP_VERSION = 'v9.287';", "const APP_VERSION = 'v9.288';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.288 — KezCsere 5 körös, több rontás/játékos, result banner")
