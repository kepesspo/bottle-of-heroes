with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Add timerSecs to bpState sync ─────────────────────────────────────
OLD_SYNC = '''    syncRoom(roomCode, { bpState: {
      tournament: TOURNAMENT,
      phase: tsPhase,
      seRounds: seRoundsObj, seCurRound, seCurMatch,
      cups1, cups2,
      rrMatches, rrIdx, rrDone,
      tsGroups: tsGroupsFlat, champion: champion ? { id: champion.id, name: champion.name, color: champion.color } : null,
      drinkMap,
    }});
  }, [seRounds, seCurRound, seCurMatch, cups1, cups2, rrMatches, tsGroups, champion, rrDone, tsPhase]);'''

NEW_SYNC = '''    syncRoom(roomCode, { bpState: {
      tournament: TOURNAMENT,
      phase: tsPhase,
      seRounds: seRoundsObj, seCurRound, seCurMatch,
      cups1, cups2,
      timerSecs,
      rrMatches, rrIdx, rrDone,
      tsGroups: tsGroupsFlat, champion: champion ? { id: champion.id, name: champion.name, color: champion.color } : null,
      drinkMap,
    }});
  }, [seRounds, seCurRound, seCurMatch, cups1, cups2, timerSecs, rrMatches, tsGroups, champion, rrDone, tsPhase]);'''

assert OLD_SYNC in html, 'sync not found'
html = html.replace(OLD_SYNC, NEW_SYNC, 1)

# ── 2. Observer current match: add timer display below the score ──────────
OLD_MATCH_END = '''            <div style={{ display:\'flex\', alignItems:\'center\', gap:8 }}>
              <PlayerChip p={curMatch.p1} highlight />
              {(() => {'''

NEW_MATCH_END = '''            <div style={{ display:\'flex\', alignItems:\'center\', gap:8 }}>
              <PlayerChip p={curMatch.p1} highlight />
              {(() => {
'''

# Actually let me find a unique string after the score block to insert timer display
# Insert timer right after the closing }) of the score IIFE, before closing </div> of the match card

OLD_TIMER_INSERT = '''            </div>
          </div>
        )}

        {/* SE Bracket */}'''

NEW_TIMER_INSERT = '''            </div>
            {(() => {
              const secs = bp.timerSecs ?? 0;
              if (!secs) return null;
              const mins = Math.floor(secs / 60);
              const timerColor = secs > 60 ? T.inkSoft : T.coral;
              const timerText = secs < 60 ? '< 1 perc' : mins + ' perc';
              return (
                <div style={{ display:\'flex\', alignItems:\'center\', justifyContent:\'center\', gap:6, marginTop:8, padding:\'5px 10px\', borderRadius:999, background:T.surfaceMuted, alignSelf:\'center\' }}>
                  <span style={{ fontSize:12 }}>{secs < 60 ? \'⚠️\' : \'⏱\'}</span>
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:timerColor }}>{timerText} van hátra</span>
                </div>
              );
            })()}
          </div>
        )}

        {/* SE Bracket */}'''

assert OLD_TIMER_INSERT in html, 'timer insert point not found'
html = html.replace(OLD_TIMER_INSERT, NEW_TIMER_INSERT, 1)

# ── 3. Version bump ───────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v7.26'"
NEW_VER = "const APP_VERSION = 'v7.27'"
assert OLD_VER in html, 'version not found'
html = html.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("done")
