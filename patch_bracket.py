with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# Add BracketView component before BeerPongObserverView
insert_before = "function BeerPongObserverView({ room, code, onLeave }) {"

bracket_component = '''function BracketView({ seRoundsArr, seCurRound, seCurMatch }) {
  if (!seRoundsArr || seRoundsArr.length === 0) return null;

  const totalRounds = seRoundsArr.length;
  const MATCH_H = 72;   // height of one match box
  const MATCH_W = 130;  // width of one match box
  const COL_GAP = 32;   // gap between columns

  // Normalize each round to array
  const rounds = seRoundsArr.map(r => Array.isArray(r) ? r : Object.values(r));

  // Calculate total height based on first round match count
  const firstCount = rounds[0].length;
  const totalH = firstCount * MATCH_H * 2;

  const PlayerRow = ({ p, isWinner, score }) => (
    <div style={{
      display:'flex', alignItems:'center', gap:6,
      padding:'5px 8px',
      background: isWinner ? `${p?.color || T.mint}22` : 'transparent',
      borderRadius:6,
      opacity: isWinner === false ? 0.45 : 1,
    }}>
      <div style={{ width:20, height:20, borderRadius:'50%', background:p?.color || T.inkMute, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:8, color:'#fff', flexShrink:0 }}>
        {(p?.name||'?').charAt(0).toUpperCase()}
      </div>
      <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:11, color: isWinner ? T.ink : T.inkSoft, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
        {p?.name || 'TBD'}
      </div>
      {score != null && (
        <div style={{ fontFamily:'monospace', fontWeight:700, fontSize:12, color: isWinner ? T.mint : T.coral, flexShrink:0 }}>{score}</div>
      )}
    </div>
  );

  return (
    <div style={{ overflowX:'auto', WebkitOverflowScrolling:'touch', paddingBottom:4 }}>
      <div style={{ display:'flex', gap:0, alignItems:'flex-start', minWidth: totalRounds * (MATCH_W + COL_GAP) }}>
        {rounds.map((round, ri) => {
          const matchCount = round.length;
          const slotH = totalH / matchCount;
          const isCurrentRound = ri === (seCurRound ?? 0);

          return (
            <div key={ri} style={{ display:'flex', flexDirection:'column', width: MATCH_W + COL_GAP, flexShrink:0 }}>
              {/* Round label */}
              <div style={{ fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:8, paddingLeft:4 }}>
                {ri === totalRounds - 1 ? (matchCount === 1 ? '🏆 Döntő' : 'Elődöntő') : `${ri+1}. kör`}
              </div>
              {/* Matches */}
              {round.map((m, mi) => {
                const isActive = isCurrentRound && mi === (seCurMatch ?? 0) && !m?.winner;
                const p1win = m?.winner?.id === m?.p1?.id;
                const p2win = m?.winner?.id === m?.p2?.id;
                return (
                  <div key={mi} style={{ height: slotH, display:'flex', alignItems:'center', position:'relative' }}>
                    {/* Connector line from left (except first round) */}
                    {ri > 0 && (
                      <div style={{ position:'absolute', left:0, top:'50%', width:COL_GAP/2, height:1, background:`${T.inkMute}40`, transform:'translateY(-50%)' }} />
                    )}
                    {/* Match box */}
                    <div style={{
                      width: MATCH_W, marginLeft: ri > 0 ? COL_GAP/2 : 0,
                      background: T.surface,
                      borderRadius:12,
                      border: isActive ? `2px solid ${T.mint}` : `2px solid ${T.surfaceMuted}`,
                      boxShadow: isActive ? `0 0 0 3px ${T.mint}22` : T.shadow,
                      overflow:'hidden',
                      flexShrink:0,
                    }}>
                      {m?.p1 ? (
                        <PlayerRow p={m.p1} isWinner={m.winner ? p1win : null} score={m.score?.p1} />
                      ) : (
                        <div style={{ padding:'5px 8px', fontFamily:T.font, fontSize:11, color:T.inkMute, fontStyle:'italic' }}>—</div>
                      )}
                      <div style={{ height:1, background:T.surfaceMuted, margin:'0 8px' }} />
                      {m?.p2 ? (
                        <PlayerRow p={m.p2} isWinner={m.winner ? p2win : null} score={m.score?.p2} />
                      ) : (
                        <div style={{ padding:'5px 8px', fontFamily:T.font, fontSize:11, color:T.inkMute, fontStyle:'italic' }}>—</div>
                      )}
                    </div>
                    {/* Connector line to right */}
                    {ri < totalRounds - 1 && (
                      <div style={{ position:'absolute', right:0, top:'50%', width:COL_GAP/2, height:1, background:`${T.inkMute}40`, transform:'translateY(-50%)' }} />
                    )}
                    {/* Vertical connector (top or bottom half) */}
                    {ri < totalRounds - 1 && (() => {
                      const isTopHalf = mi % 2 === 0;
                      return (
                        <div style={{
                          position:'absolute', right:0,
                          top: isTopHalf ? '50%' : 0,
                          bottom: isTopHalf ? 0 : '50%',
                          width:1,
                          background:`${T.inkMute}40`,
                        }} />
                      );
                    })()}
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}

'''

assert insert_before in html, "BeerPongObserverView not found"
html = html.replace(insert_before, bracket_component + insert_before, 1)

# Replace the SE bracket list in BeerPongObserverView with BracketView
old = '''        {/* SE Bracket */}
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
        )}'''

new = '''        {/* SE Bracket */}
        {bp.tournament === 'se' && seRoundsArr.length > 0 && (
          <div style={{ background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:'14px 14px' }}>
            <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:12 }}>🏆 Kieséses ágrajz</div>
            <BracketView seRoundsArr={seRoundsArr} seCurRound={bp.seCurRound} seCurMatch={bp.seCurMatch} />
          </div>
        )}'''

assert old in html, "SE bracket block not found"
html = html.replace(old, new, 1)

# Replace the Finals SE bracket list with BracketView
old = '''        {/* Finals SE bracket (group tournament) */}
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
                    <div key={ri+'-'+mi} style={{ display:'flex', alignItems:'center', gap:6, padding:'6px 8px', borderRadius:10, background: !m.winner ? `${T.blue}12` : 'transparent', marginBottom:3 }}>
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
        )}'''

new = '''        {/* Finals SE bracket (group tournament) */}
        {bp.tournament?.startsWith('grp_') && bp.phase === 'finals' && seRoundsArr.length > 0 && (
          <div style={{ background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:'14px 14px' }}>
            <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:12 }}>🏆 Főszakasz ágrajz</div>
            <BracketView seRoundsArr={seRoundsArr} seCurRound={bp.seCurRound} seCurMatch={bp.seCurMatch} />
          </div>
        )}'''

assert old in html, "Finals bracket block not found"
html = html.replace(old, new, 1)

assert html != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("done")
