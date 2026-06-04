with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# Add BracketView component before BeerPongObserverView
insert_before = "function BeerPongObserverView({ room, code, onLeave }) {"

bracket_component = '''function BracketView({ seRoundsArr, seCurRound, seCurMatch }) {
  if (!seRoundsArr || seRoundsArr.length === 0) return null;
  const rounds = seRoundsArr.map(r => Array.isArray(r) ? r : Object.values(r));
  const totalRounds = rounds.length;
  const MATCH_H = 70;
  const MATCH_W = 128;
  const COL_GAP = 28;
  const firstCount = rounds[0].length;
  const totalH = firstCount * MATCH_H * 2;

  const PlayerRow = ({ p, isWinner, score }) => (
    <div style={{ display:'flex', alignItems:'center', gap:5, padding:'5px 7px', background: isWinner ? `${p?.color||T.mint}22` : 'transparent', borderRadius:6, opacity: isWinner===false ? 0.4 : 1 }}>
      <div style={{ width:18, height:18, borderRadius:'50%', background:p?.color||T.inkMute, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:8, color:'#fff', flexShrink:0 }}>{(p?.name||'?').charAt(0).toUpperCase()}</div>
      <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:11, color: isWinner ? T.ink : T.inkSoft, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p?.name||'TBD'}</div>
      {score != null && <div style={{ fontFamily:'monospace', fontWeight:700, fontSize:12, color: isWinner ? T.mint : T.coral, flexShrink:0 }}>{score}</div>}
    </div>
  );

  return (
    <div style={{ overflowX:'auto', WebkitOverflowScrolling:'touch', paddingBottom:4, marginRight:-4 }}>
      <div style={{ display:'flex', alignItems:'flex-start', width: totalRounds*(MATCH_W+COL_GAP) }}>
        {rounds.map((round, ri) => {
          const matchCount = round.length;
          const slotH = totalH / matchCount;
          const isCurrentRound = ri === (seCurRound ?? 0);
          return (
            <div key={ri} style={{ width: MATCH_W+COL_GAP, flexShrink:0 }}>
              <div style={{ fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:6, paddingLeft:2 }}>
                {ri===totalRounds-1 ? (matchCount===1?'🏆 Döntő':'Elődöntő') : `${ri+1}. kör`}
              </div>
              {round.map((m, mi) => {
                const isActive = isCurrentRound && mi===(seCurMatch??0) && !m?.winner;
                const p1win = m?.winner?.id===m?.p1?.id;
                const p2win = m?.winner?.id===m?.p2?.id;
                const isTopOfPair = mi%2===0;
                return (
                  <div key={mi} style={{ height:slotH, display:'flex', alignItems:'center', position:'relative' }}>
                    {ri>0 && <div style={{ position:'absolute', left:0, top:'50%', width:COL_GAP/2, height:2, background:`${T.inkMute}35` }}/>}
                    {ri<totalRounds-1 && <div style={{ position:'absolute', right:0, top:'50%', width:COL_GAP/2, height:2, background:`${T.inkMute}35` }}/>}
                    {ri<totalRounds-1 && <div style={{ position:'absolute', right:0, top:isTopOfPair?'50%':0, bottom:isTopOfPair?0:'50%', width:2, background:`${T.inkMute}35` }}/>}
                    <div style={{ width:MATCH_W, marginLeft:ri>0?COL_GAP/2:0, background:T.surface, borderRadius:10, border:`2px solid ${isActive?T.mint:T.surfaceMuted}`, boxShadow:isActive?`0 0 0 3px ${T.mint}22`:T.shadow, overflow:'hidden', flexShrink:0 }}>
                      {m?.p1 ? <PlayerRow p={m.p1} isWinner={m.winner?p1win:null} score={m.score?.p1}/> : <div style={{padding:'5px 7px',fontFamily:T.font,fontSize:10,color:T.inkMute,fontStyle:'italic'}}>—</div>}
                      <div style={{ height:1, background:T.surfaceMuted, margin:'0 6px' }}/>
                      {m?.p2 ? <PlayerRow p={m.p2} isWinner={m.winner?p2win:null} score={m.score?.p2}/> : <div style={{padding:'5px 7px',fontFamily:T.font,fontSize:10,color:T.inkMute,fontStyle:'italic'}}>—</div>}
                    </div>
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

assert insert_before in html
html = html.replace(insert_before, bracket_component + insert_before, 1)

# Replace SE bracket list in BeerPongObserverView
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
new_se = '''        {/* SE Bracket */}
        {bp.tournament === 'se' && seRoundsArr.length > 0 && (
          <div style={{ background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:'14px 14px' }}>
            <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:12 }}>🏆 Kieséses ágrajz</div>
            <BracketView seRoundsArr={seRoundsArr} seCurRound={bp.seCurRound} seCurMatch={bp.seCurMatch} />
          </div>
        )}'''
assert old in html, "SE bracket not found"
html = html.replace(old, new_se, 1)

# Replace Finals SE bracket list
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
new_finals = '''        {/* Finals SE bracket (group tournament) */}
        {bp.tournament?.startsWith('grp_') && bp.phase === 'finals' && seRoundsArr.length > 0 && (
          <div style={{ background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:'14px 14px' }}>
            <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:12 }}>🏆 Főszakasz ágrajz</div>
            <BracketView seRoundsArr={seRoundsArr} seCurRound={bp.seCurRound} seCurMatch={bp.seCurMatch} />
          </div>
        )}'''
assert old in html, "Finals bracket not found"
html = html.replace(old, new_finals, 1)

assert html != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("done")
