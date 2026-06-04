with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# 1. Insert BeerPongObserverView component before ObserverStatus
insert_before = "function ObserverStatus({ icon, title, sub, spinning, actionLabel, onAction }) {"

bp_component = '''function BeerPongObserverView({ room, code, onLeave }) {
  const bp = room.bpState || {};
  const players = room.players || [];
  const selGames = room.selectedGames || [];
  const gameIdx = room.gameIdx || 0;
  const currentGameId = selGames[gameIdx % Math.max(1, selGames.length)];
  const isBP = currentGameId === 'beerpong';

  const getRRSt = (parts, matches) => {
    if (!parts || !matches) return [];
    const st = {};
    parts.forEach(p => { if (p) st[p.id] = { player:p, wins:0, losses:0, draws:0, pts:0, diff:0 }; });
    (Array.isArray(matches) ? matches : Object.values(matches)).forEach(m => {
      if (!m || !m.score) return;
      const MAX = 10;
      const p1pot = MAX - m.score.p1, p2pot = MAX - m.score.p2;
      if (m.draw) {
        if (st[m.p1?.id]) { st[m.p1.id].draws++; st[m.p1.id].pts++; }
        if (st[m.p2?.id]) { st[m.p2.id].draws++; st[m.p2.id].pts++; }
      } else if (m.winner) {
        if (st[m.winner.id]) { st[m.winner.id].wins++; st[m.winner.id].pts += 3; }
        if (m.loser && st[m.loser.id]) st[m.loser.id].losses++;
        const d = p1pot - p2pot;
        if (st[m.p1?.id]) st[m.p1.id].diff += d;
        if (st[m.p2?.id]) st[m.p2.id].diff -= d;
      }
    });
    return Object.values(st).sort((a,b) => b.pts - a.pts || b.diff - a.diff);
  };

  const seRoundsArr = bp.seRounds ? (Array.isArray(bp.seRounds) ? bp.seRounds : Object.values(bp.seRounds)) : [];
  const rrMatchesArr = bp.rrMatches ? (Array.isArray(bp.rrMatches) ? bp.rrMatches : Object.values(bp.rrMatches)) : [];
  const tsGroupsArr = bp.tsGroups ? (Array.isArray(bp.tsGroups) ? bp.tsGroups : Object.values(bp.tsGroups)) : [];

  // Current active match
  const curMatch = (() => {
    if (bp.tournament === 'se' && seRoundsArr.length > 0) {
      const r = seRoundsArr[bp.seCurRound ?? 0];
      return r ? (Array.isArray(r) ? r[bp.seCurMatch ?? 0] : Object.values(r)[bp.seCurMatch ?? 0]) : null;
    }
    if (bp.tournament === 'rr' && rrMatchesArr.length > 0) {
      return rrMatchesArr.find(m => m && !m.winner && !m.draw) || null;
    }
    if (bp.tournament?.startsWith('grp_')) {
      if (bp.phase === 'groups') {
        for (const g of tsGroupsArr) {
          const ms = Array.isArray(g.matches) ? g.matches : Object.values(g.matches || {});
          const m = ms.find(m => m && !m.winner && !m.draw);
          if (m) return m;
        }
      } else if (bp.phase === 'finals' && seRoundsArr.length > 0) {
        const r = seRoundsArr[bp.seCurRound ?? 0];
        return r ? (Array.isArray(r) ? r[bp.seCurMatch ?? 0] : Object.values(r)[bp.seCurMatch ?? 0]) : null;
      }
    }
    return null;
  })();

  const PlayerChip = ({ p, highlight }) => p ? (
    <div style={{ display:'flex', alignItems:'center', gap:8, flex:1, minWidth:0, padding:'8px 10px', borderRadius:12, background: highlight ? `${p.color}22` : T.surfaceMuted, border: highlight ? `2px solid ${p.color}60` : '2px solid transparent' }}>
      <div style={{ width:32, height:32, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:13, color:'#fff', flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>
      <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
    </div>
  ) : null;

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      {/* Status bar */}
      <div style={{ margin:'10px 16px 4px', display:'flex', alignItems:'center', justifyContent:'space-between', padding:'10px 14px', background:T.surface, borderRadius:14, boxShadow:T.shadow, flexShrink:0 }}>
        <div style={{ display:'flex', alignItems:'center', gap:8 }}>
          <span style={{ width:8, height:8, borderRadius:'50%', background:'#E03A3A', animation:'pulse 1.4s infinite' }}/>
          <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.ink, letterSpacing:'0.08em', textTransform:'uppercase' }}>🏓 Beer Pong · Szoba {code}</span>
        </div>
        <button onClick={onLeave} style={{ padding:'4px 10px', border:'none', background:T.coralSoft, color:T.coral, borderRadius:999, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:11, cursor:'pointer', textTransform:'uppercase', letterSpacing:'0.06em' }}>Kilépés</button>
      </div>

      <div style={{ flex:1, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'8px 16px 24px', display:'flex', flexDirection:'column', gap:12 }}>

        {/* Champion banner */}
        {bp.champion && (
          <div style={{ background:`linear-gradient(135deg, ${T.yellow}33, ${T.yellow}11)`, border:`2px solid ${T.yellow}`, borderRadius:18, padding:'16px 18px', display:'flex', alignItems:'center', gap:12 }}>
            <div style={{ fontSize:36 }}>🏆</div>
            <div>
              <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>Bajnok</div>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.ink }}>{bp.champion.name}</div>
            </div>
          </div>
        )}

        {/* Current match */}
        {isBP && curMatch && curMatch.p1 && curMatch.p2 && !bp.champion && (
          <div style={{ background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:'14px 14px' }}>
            <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:10 }}>⚡ Aktuális meccs</div>
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <PlayerChip p={curMatch.p1} highlight />
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.inkSoft, flexShrink:0 }}>VS</div>
              <PlayerChip p={curMatch.p2} highlight />
            </div>
          </div>
        )}

        {/* SE Bracket */}
        {bp.tournament === 'se' && seRoundsArr.length > 0 && (
          <div style={{ background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:'14px 14px' }}>
            <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:10 }}>🏆 Kieséses tábla</div>
            {seRoundsArr.map((round, ri) => {
              const roundArr = Array.isArray(round) ? round : Object.values(round);
              const isLast = ri === seRoundsArr.length - 1;
              const label = isLast ? (roundArr.length === 1 ? 'Döntő' : 'Elődöntő') : `${ri + 1}. kör`;
              return (
                <div key={ri} style={{ marginBottom: ri < seRoundsArr.length - 1 ? 10 : 0 }}>
                  <div style={{ fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:4 }}>{label}</div>
                  {roundArr.map((m, mi) => m && m.p1 && m.p2 ? (
                    <div key={mi} style={{ display:'flex', alignItems:'center', gap:6, padding:'6px 8px', borderRadius:10, background: !m.winner ? `${T.blue}12` : 'transparent', marginBottom:3 }}>
                      <div style={{ width:22, height:22, borderRadius:'50%', background:m.p1.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:9, color:'#fff', flexShrink:0 }}>{(m.p1.name||'?').charAt(0).toUpperCase()}</div>
                      <span style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color: m.winner?.id===m.p1?.id ? T.mint : m.winner ? T.inkMute : T.ink, flex:1 }}>{m.p1.name}</span>
                      <span style={{ fontFamily:'monospace', fontSize:12, color:T.inkSoft, flexShrink:0 }}>{m.score ? `${m.score.p1} – ${m.score.p2}` : 'vs'}</span>
                      <span style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color: m.winner?.id===m.p2?.id ? T.mint : m.winner ? T.inkMute : T.ink, flex:1, textAlign:'right' }}>{m.p2.name}</span>
                      <div style={{ width:22, height:22, borderRadius:'50%', background:m.p2.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:9, color:'#fff', flexShrink:0 }}>{(m.p2.name||'?').charAt(0).toUpperCase()}</div>
                    </div>
                  ) : null)}
                </div>
              );
            })}
          </div>
        )}

        {/* RR Standings */}
        {bp.tournament === 'rr' && rrMatchesArr.length > 0 && (() => {
          const parts = rrMatchesArr.flatMap(m => [m.p1, m.p2]).filter((p,i,a) => p && a.findIndex(x=>x&&x.id===p.id)===i);
          const st = getRRSt(parts, rrMatchesArr);
          return (
            <div style={{ background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:'14px 14px' }}>
              <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:10 }}>📊 Körmérkőzés állás</div>
              <div style={{ display:'flex', gap:4, padding:'4px 6px', borderBottom:`1px solid ${T.surfaceMuted}`, marginBottom:6 }}>
                <div style={{ flex:1, fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkMute, textTransform:'uppercase' }}>Játékos</div>
                {['GY','D','V','Pt'].map(h => <div key={h} style={{ fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkMute, textTransform:'uppercase', minWidth:26, textAlign:'center' }}>{h}</div>)}
              </div>
              {st.map((s,i) => (
                <div key={s.player.id} style={{ display:'flex', alignItems:'center', gap:6, padding:'6px 6px', borderRadius:8, background: i===0 ? `${T.yellow}12` : 'transparent' }}>
                  <div style={{ fontFamily:T.font, fontSize:11, color:i===0?T.yellow:T.inkSoft, fontWeight:700, minWidth:16 }}>{i+1}.</div>
                  <div style={{ width:24, height:24, borderRadius:'50%', background:s.player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:10, color:'#fff', flexShrink:0 }}>{(s.player.name||'?').charAt(0).toUpperCase()}</div>
                  <div style={{ flex:1, fontFamily:T.font, fontSize:13, fontWeight:700, color:T.ink }}>{s.player.name}</div>
                  <div style={{ fontFamily:'monospace', fontSize:12, color:T.mint, minWidth:26, textAlign:'center' }}>{s.wins}</div>
                  <div style={{ fontFamily:'monospace', fontSize:12, color:T.inkSoft, minWidth:26, textAlign:'center' }}>{s.draws}</div>
                  <div style={{ fontFamily:'monospace', fontSize:12, color:T.coral, minWidth:26, textAlign:'center' }}>{s.losses}</div>
                  <div style={{ fontFamily:'monospace', fontSize:13, fontWeight:700, color:T.ink, minWidth:26, textAlign:'center' }}>{s.pts}</div>
                </div>
              ))}
            </div>
          );
        })()}

        {/* Group phase */}
        {bp.tournament?.startsWith('grp_') && tsGroupsArr.length > 0 && bp.phase === 'groups' && (
          <div style={{ background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:'14px 14px' }}>
            <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:10 }}>🔵 Csoportkör</div>
            {tsGroupsArr.map((g, gi) => {
              const ms = Array.isArray(g.matches) ? g.matches : Object.values(g.matches || {});
              const st = getRRSt(g.players || [], ms);
              return (
                <div key={gi} style={{ marginBottom: gi < tsGroupsArr.length - 1 ? 12 : 0 }}>
                  <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.blue, textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:6 }}>
                    {g.label} {g.done ? <span style={{ color:T.mint }}>✓</span> : <span style={{ color:T.yellow }}>●</span>}
                  </div>
                  {st.map((s,si) => (
                    <div key={s.player.id} style={{ display:'flex', alignItems:'center', gap:8, padding:'5px 6px', borderRadius:8, background: si < 2 ? `${T.mint}0A` : 'transparent' }}>
                      <div style={{ fontFamily:T.font, fontSize:11, color:si===0?T.yellow:T.inkSoft, fontWeight:700, minWidth:16 }}>{si+1}.</div>
                      <div style={{ width:22, height:22, borderRadius:'50%', background:s.player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:9, color:'#fff', flexShrink:0 }}>{(s.player.name||'?').charAt(0).toUpperCase()}</div>
                      <div style={{ flex:1, fontFamily:T.font, fontSize:13, fontWeight:700, color:T.ink }}>{s.player.name}</div>
                      <div style={{ fontFamily:'monospace', fontSize:12, color:T.ink, fontWeight:700 }}>{s.pts}pt</div>
                      {si < 2 && <div style={{ fontFamily:T.font, fontSize:9, color:T.mint, fontWeight:700 }}>↑ tovább</div>}
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        )}

        {/* Finals SE bracket (group tournament) */}
        {bp.tournament?.startsWith('grp_') && bp.phase === 'finals' && seRoundsArr.length > 0 && (
          <div style={{ background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:'14px 14px' }}>
            <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:10 }}>🏆 Főszakasz</div>
            {seRoundsArr.map((round, ri) => {
              const roundArr = Array.isArray(round) ? round : Object.values(round);
              const isLast = ri === seRoundsArr.length - 1;
              const label = isLast ? (roundArr.length === 1 ? 'Döntő' : 'Elődöntő') : `${ri + 1}. kör`;
              return (
                <div key={ri} style={{ marginBottom: ri < seRoundsArr.length - 1 ? 10 : 0 }}>
                  <div style={{ fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:4 }}>{label}</div>
                  {roundArr.map((m, mi) => m && m.p1 && m.p2 ? (
                    <div key={mi} style={{ display:'flex', alignItems:'center', gap:6, padding:'6px 8px', borderRadius:10, background: !m.winner ? `${T.blue}12` : 'transparent', marginBottom:3 }}>
                      <div style={{ width:22, height:22, borderRadius:'50%', background:m.p1.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:9, color:'#fff', flexShrink:0 }}>{(m.p1.name||'?').charAt(0).toUpperCase()}</div>
                      <span style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color: m.winner?.id===m.p1?.id ? T.mint : m.winner ? T.inkMute : T.ink, flex:1 }}>{m.p1.name}</span>
                      <span style={{ fontFamily:'monospace', fontSize:12, color:T.inkSoft, flexShrink:0 }}>{m.score ? `${m.score.p1} – ${m.score.p2}` : 'vs'}</span>
                      <span style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color: m.winner?.id===m.p2?.id ? T.mint : m.winner ? T.inkMute : T.ink, flex:1, textAlign:'right' }}>{m.p2.name}</span>
                      <div style={{ width:22, height:22, borderRadius:'50%', background:m.p2.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:9, color:'#fff', flexShrink:0 }}>{(m.p2.name||'?').charAt(0).toUpperCase()}</div>
                    </div>
                  ) : null)}
                </div>
              );
            })}
          </div>
        )}

        {/* Drinks leaderboard */}
        {players.length > 0 && (
          <div style={{ background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:'14px 14px' }}>
            <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:10 }}>🍺 Korty összesítő</div>
            {[...players].sort((a,b) => (b.drinks - a.drinks)).map((p, i) => (
              <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10, padding:'7px 6px', borderRadius:10, background: i===0 && p.drinks > 0 ? `${T.coral}12` : 'transparent' }}>
                <div style={{ width:28, height:28, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#fff', flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>
                <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>{p.name}</div>
                <div style={{ display:'flex', alignItems:'center', gap:4 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color: p.drinks > 0 ? T.coral : T.inkMute }}>{p.drinks}</span>
                  <span style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>korty</span>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

'''

assert insert_before in html, "ObserverStatus not found"
html = html.replace(insert_before, bp_component + insert_before, 1)

# 2. In ObserverWatching, add BeerPong detection after the Busz check
old = """  // Busz player mode — replace observer UI with player hand view
  if (room.buszState || (room.selectedGames||[]).includes('busz')) {"""

new = """  // BeerPong observer mode
  const _selGames2 = room.selectedGames || [];
  const _curGameId2 = _selGames2[(room.gameIdx || 0) % Math.max(1, _selGames2.length)];
  if (room.bpState && _curGameId2 === 'beerpong') {
    return <BeerPongObserverView room={room} code={code} onLeave={onLeave} />;
  }

  // Busz player mode — replace observer UI with player hand view
  if (room.buszState || (room.selectedGames||[]).includes('busz')) {"""

assert old in html, "Busz check not found"
html = html.replace(old, new, 1)

assert html != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("done")
