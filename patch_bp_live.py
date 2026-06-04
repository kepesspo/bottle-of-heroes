with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Add cups1, cups2 to bpState sync ──────────────────────────────────
OLD_SYNC_BODY = '''    syncRoom(roomCode, { bpState: {
      tournament: TOURNAMENT,
      phase: tsPhase,
      seRounds: seRoundsObj, seCurRound, seCurMatch,
      rrMatches, rrIdx, rrDone,
      tsGroups: tsGroupsFlat, champion: champion ? { id: champion.id, name: champion.name, color: champion.color } : null,
      drinkMap,
    }});
  }, [seRounds, seCurRound, seCurMatch, rrMatches, tsGroups, champion, rrDone, tsPhase]);'''

NEW_SYNC_BODY = '''    syncRoom(roomCode, { bpState: {
      tournament: TOURNAMENT,
      phase: tsPhase,
      seRounds: seRoundsObj, seCurRound, seCurMatch,
      cups1, cups2,
      rrMatches, rrIdx, rrDone,
      tsGroups: tsGroupsFlat, champion: champion ? { id: champion.id, name: champion.name, color: champion.color } : null,
      drinkMap,
    }});
  }, [seRounds, seCurRound, seCurMatch, cups1, cups2, rrMatches, tsGroups, champion, rrDone, tsPhase]);'''

assert OLD_SYNC_BODY in html, 'sync body not found'
html = html.replace(OLD_SYNC_BODY, NEW_SYNC_BODY, 1)

# ── 2. Observer current match: use bp.cups1/cups2 as live score ──────────
OLD_SCORE_BLOCK = '''              {curMatch.score ? (
                <div style={{ display:\'flex\', flexDirection:\'column\', alignItems:\'center\', gap:2, flexShrink:0 }}>
                  <div style={{ fontFamily:\'monospace\', fontWeight:900, fontSize:22, color:T.ink, lineHeight:1 }}>
                    {curMatch.score.p1}<span style={{ color:T.inkMute, fontSize:16 }}> – </span>{curMatch.score.p2}
                  </div>
                  <div style={{ fontFamily:T.font, fontSize:9, color:T.inkMute, textTransform:\'uppercase\', letterSpacing:\'0.06em\' }}>pohár</div>
                </div>
              ) : (
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.inkSoft, flexShrink:0 }}>VS</div>
              )}'''

NEW_SCORE_BLOCK = '''              {(() => {
                const liveCups1 = bp.cups1 ?? null;
                const liveCups2 = bp.cups2 ?? null;
                const hasLive = liveCups1 !== null && liveCups2 !== null;
                const s = curMatch.score;
                if (s) {
                  return (
                    <div style={{ display:\'flex\', flexDirection:\'column\', alignItems:\'center\', gap:2, flexShrink:0 }}>
                      <div style={{ fontFamily:\'monospace\', fontWeight:900, fontSize:22, color:T.ink, lineHeight:1 }}>
                        {s.p1}<span style={{ color:T.inkMute, fontSize:16 }}> – </span>{s.p2}
                      </div>
                      <div style={{ fontFamily:T.font, fontSize:9, color:T.inkMute, textTransform:\'uppercase\', letterSpacing:\'0.06em\' }}>pohár marad</div>
                    </div>
                  );
                }
                if (hasLive) {
                  return (
                    <div style={{ display:\'flex\', flexDirection:\'column\', alignItems:\'center\', gap:2, flexShrink:0 }}>
                      <div style={{ fontFamily:\'monospace\', fontWeight:900, fontSize:22, color:T.mint, lineHeight:1 }}>
                        {liveCups1}<span style={{ color:T.inkMute, fontSize:16 }}> – </span>{liveCups2}
                      </div>
                      <div style={{ fontFamily:T.font, fontSize:9, color:T.mint, textTransform:\'uppercase\', letterSpacing:\'0.06em\' }}>marad</div>
                    </div>
                  );
                }
                return <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.inkSoft, flexShrink:0 }}>VS</div>;
              })()}'''

assert OLD_SCORE_BLOCK in html, 'score block not found'
html = html.replace(OLD_SCORE_BLOCK, NEW_SCORE_BLOCK, 1)

# ── 3. Observer drinks leaderboard: use bpState.drinkMap instead of p.drinks ──
OLD_DRINKS_LIST = '''          {[...players].sort((a,b) => (b.drinks - a.drinks)).map((p, i) => (
              <div key={p.id} style={{ display:\'flex\', alignItems:\'center\', gap:10, padding:\'7px 6px\', borderRadius:10, background: i===0 && p.drinks > 0 ? `${T.coral}12` : \'transparent\' }}>
                <div style={{ width:28, height:28, borderRadius:\'50%\', background:p.color, display:\'grid\', placeItems:\'center\', fontFamily:T.font, fontWeight:700, fontSize:12, color:\'#fff\', flexShrink:0 }}>{(p.name||\'?\').charAt(0).toUpperCase()}</div>
                <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>{p.name}</div>
                <div style={{ display:\'flex\', alignItems:\'center\', gap:4 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color: p.drinks > 0 ? T.coral : T.inkMute }}>{p.drinks}</span>
                  <span style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>korty</span>
                </div>
              </div>
            ))}'''

NEW_DRINKS_LIST = '''          {[...players].map(p => ({ ...p, bpDrinks: (bp.drinkMap && bp.drinkMap[p.id]) || p.drinks || 0 })).sort((a,b) => b.bpDrinks - a.bpDrinks).map((p, i) => (
              <div key={p.id} style={{ display:\'flex\', alignItems:\'center\', gap:10, padding:\'7px 6px\', borderRadius:10, background: i===0 && p.bpDrinks > 0 ? `${T.coral}12` : \'transparent\' }}>
                <div style={{ width:28, height:28, borderRadius:\'50%\', background:p.color, display:\'grid\', placeItems:\'center\', fontFamily:T.font, fontWeight:700, fontSize:12, color:\'#fff\', flexShrink:0 }}>{(p.name||\'?\').charAt(0).toUpperCase()}</div>
                <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>{p.name}</div>
                <div style={{ display:\'flex\', alignItems:\'center\', gap:4 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color: p.bpDrinks > 0 ? T.coral : T.inkMute }}>{p.bpDrinks}</span>
                  <span style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>korty</span>
                </div>
              </div>
            ))}'''

assert OLD_DRINKS_LIST in html, 'drinks list not found'
html = html.replace(OLD_DRINKS_LIST, NEW_DRINKS_LIST, 1)

# ── 4. Version bump ───────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v7.25'"
NEW_VER = "const APP_VERSION = 'v7.26'"
assert OLD_VER in html, 'version not found'
html = html.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("done")
