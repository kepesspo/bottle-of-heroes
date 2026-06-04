with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Auto-switch to next incomplete group after current group is done ───
OLD_HANDLE_GROUP_END = '''      // Check if ALL groups are done → start finals
      const allDone = ng.every(g => g.done);
      if (allDone) {'''

NEW_HANDLE_GROUP_END = '''      // Auto-switch to next incomplete group
      const thisGroupDone = ng[viewGroup]?.done;
      if (thisGroupDone) {
        const nextGroup = ng.findIndex((g, gi) => gi > viewGroup && !g.done);
        if (nextGroup !== -1) setViewGroup(nextGroup);
      }

      // Check if ALL groups are done → start finals
      const allDone = ng.every(g => g.done);
      if (allDone) {'''

assert OLD_HANDLE_GROUP_END in html, 'handle group end not found'
html = html.replace(OLD_HANDLE_GROUP_END, NEW_HANDLE_GROUP_END, 1)

# ── 2. Add playersPerGroup config option ─────────────────────────────────
# Add to config destructuring
OLD_CFG_DESTRUCTURE = '''  const groupAdvance = config.groupAdvance ?? 1;'''
NEW_CFG_DESTRUCTURE = '''  const groupAdvance = config.groupAdvance ?? 1;
  const playersPerGroup = config.playersPerGroup ?? 4;'''
assert OLD_CFG_DESTRUCTURE in html, 'groupAdvance destructure not found'
html = html.replace(OLD_CFG_DESTRUCTURE, NEW_CFG_DESTRUCTURE, 1)

# Add the playersPerGroup setting below groupAdvance setting in the config UI
OLD_GROUP_ADV_UI = '''        {/* Group advance (two-stage only) */}
        {isTwo && (
          <div style={{ display:\'flex\', alignItems:\'center\', justifyContent:\'space-between\', padding:\'13px 0\', borderTop:\'1px solid rgba(26,42,74,0.10)\' }}>
            <div>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>Továbbjutók/csoport</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>Hányan jutnak tovább a főszakaszra</div>
            </div>
            <div style={{ display:\'flex\', alignItems:\'center\', gap:8 }}>
              <button onClick={() => setConfig(c => ({...c, groupAdvance: Math.max(1,(c.groupAdvance??1)-1)}))} style={{ width:33, height:33, borderRadius:10, background:T.surfaceMuted, border:\'none\', cursor:\'pointer\', display:\'grid\', placeItems:\'center\', fontSize:20, fontWeight:900, color:\'#D85F5C\' }}>-</button>
              <span style={{ fontFamily:\'monospace\', fontWeight:900, fontSize:18, color:T.ink, minWidth:30, textAlign:\'center\' }}>{groupAdvance}</span>
              <button onClick={() => setConfig(c => ({...c, groupAdvance: Math.min(3,(c.groupAdvance??1)+1)}))} style={{ width:33, height:33, borderRadius:10, background:T.surfaceMuted, border:\'none\', cursor:\'pointer\', display:\'grid\', placeItems:\'center\', fontSize:20, fontWeight:900, color:T.mintDeep }}>+</button>
            </div>
          </div>
        )}'''

NEW_GROUP_ADV_UI = '''        {/* Group settings (two-stage only) */}
        {isTwo && (
          <>
          <div style={{ display:\'flex\', alignItems:\'center\', justifyContent:\'space-between\', padding:\'13px 0\', borderTop:\'1px solid rgba(26,42,74,0.10)\' }}>
            <div>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>Játékosok/csoport</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>Hány játékos kerüljön egy csoportba</div>
            </div>
            <div style={{ display:\'flex\', alignItems:\'center\', gap:8 }}>
              <button onClick={() => setConfig(c => ({...c, playersPerGroup: Math.max(3,(c.playersPerGroup??4)-1)}))} style={{ width:33, height:33, borderRadius:10, background:T.surfaceMuted, border:\'none\', cursor:\'pointer\', display:\'grid\', placeItems:\'center\', fontSize:20, fontWeight:900, color:\'#D85F5C\' }}>-</button>
              <span style={{ fontFamily:\'monospace\', fontWeight:900, fontSize:18, color:T.ink, minWidth:30, textAlign:\'center\' }}>{playersPerGroup}</span>
              <button onClick={() => setConfig(c => ({...c, playersPerGroup: Math.min(8,(c.playersPerGroup??4)+1)}))} style={{ width:33, height:33, borderRadius:10, background:T.surfaceMuted, border:\'none\', cursor:\'pointer\', display:\'grid\', placeItems:\'center\', fontSize:20, fontWeight:900, color:T.mintDeep }}>+</button>
            </div>
          </div>
          <div style={{ display:\'flex\', alignItems:\'center\', justifyContent:\'space-between\', padding:\'13px 0\', borderTop:\'1px solid rgba(26,42,74,0.10)\' }}>
            <div>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>Továbbjutók/csoport</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>Hányan jutnak tovább a főszakaszra</div>
            </div>
            <div style={{ display:\'flex\', alignItems:\'center\', gap:8 }}>
              <button onClick={() => setConfig(c => ({...c, groupAdvance: Math.max(1,(c.groupAdvance??1)-1)}))} style={{ width:33, height:33, borderRadius:10, background:T.surfaceMuted, border:\'none\', cursor:\'pointer\', display:\'grid\', placeItems:\'center\', fontSize:20, fontWeight:900, color:\'#D85F5C\' }}>-</button>
              <span style={{ fontFamily:\'monospace\', fontWeight:900, fontSize:18, color:T.ink, minWidth:30, textAlign:\'center\' }}>{groupAdvance}</span>
              <button onClick={() => setConfig(c => ({...c, groupAdvance: Math.min(3,(c.groupAdvance??1)+1)}))} style={{ width:33, height:33, borderRadius:10, background:T.surfaceMuted, border:\'none\', cursor:\'pointer\', display:\'grid\', placeItems:\'center\', fontSize:20, fontWeight:900, color:T.mintDeep }}>+</button>
            </div>
          </div>
          </>
        )}'''

assert OLD_GROUP_ADV_UI in html, 'group advance UI not found'
html = html.replace(OLD_GROUP_ADV_UI, NEW_GROUP_ADV_UI, 1)

# ── 3. Use playersPerGroup in initTournament group building ───────────────
OLD_GROUP_CONST = '''  const GROUP_ADVANCE = bpCfg.groupAdvance ?? 1;'''
NEW_GROUP_CONST = '''  const GROUP_ADVANCE = bpCfg.groupAdvance ?? 1;
  const PLAYERS_PER_GROUP = bpCfg.playersPerGroup ?? 4;'''
assert OLD_GROUP_CONST in html, 'GROUP_ADVANCE const not found'
html = html.replace(OLD_GROUP_CONST, NEW_GROUP_CONST, 1)

# Replace fixed 2-group split in initTournament with dynamic grouping
OLD_INIT_GROUPS = '''      const sh = [...tp].sort(() => Math.random() - 0.5);
      const half = Math.ceil(sh.length / 2);
      const gPlayers = [sh.slice(0, half), sh.slice(half)];
      const groupType = TOURNAMENT.startsWith(\'grp_rr\') ? \'rr\' : \'se\';
      const groups = gPlayers.map((gp, gi) => ({
        id: gi, label: \'A B C D\'.split(\' \')[gi] + \' csoport\',
        players: gp,
        matches: groupType === \'rr\' ? buildRRMatches(gp) : buildSEBracket(gp).flat(),
        seRounds: groupType === \'se\' ? buildSEBracket(gp) : null,
        seCurRound: 0,
        curIdx: 0, done: false,
      }));
      setTsGroups(groups); setTsCurGroup(0); setTsPhase(\'groups\');'''

NEW_INIT_GROUPS = '''      const sh = [...tp].sort(() => Math.random() - 0.5);
      const numGroups = Math.max(2, Math.ceil(sh.length / PLAYERS_PER_GROUP));
      const gPlayers = Array.from({ length: numGroups }, (_, gi) => {
        const start = Math.floor(gi * sh.length / numGroups);
        const end = Math.floor((gi + 1) * sh.length / numGroups);
        return sh.slice(start, end);
      }).filter(g => g.length > 0);
      const groupType = TOURNAMENT.startsWith(\'grp_rr\') ? \'rr\' : \'se\';
      const groups = gPlayers.map((gp, gi) => ({
        id: gi, label: \'A B C D E F G H\'.split(\' \')[gi] + \' csoport\',
        players: gp,
        matches: groupType === \'rr\' ? buildRRMatches(gp) : buildSEBracket(gp).flat(),
        seRounds: groupType === \'se\' ? buildSEBracket(gp) : null,
        seCurRound: 0,
        curIdx: 0, done: false,
      }));
      setTsGroups(groups); setTsCurGroup(0); setTsPhase(\'groups\');'''

assert OLD_INIT_GROUPS in html, 'initTournament groups not found'
html = html.replace(OLD_INIT_GROUPS, NEW_INIT_GROUPS, 1)

# Also fix the second occurrence of same group building (line ~36171 — the "restart" path)
OLD_INIT_GROUPS2 = '''      const sh = [...ep].sort(() => Math.random() - 0.5);
      const half = Math.ceil(sh.length / 2);
      const gPlayers = [sh.slice(0, half), sh.slice(half)];
      const groupType = TOURNAMENT.startsWith(\'grp_rr\') ? \'rr\' : \'se\';
      const groups = gPlayers.map((gp, gi) => ({
        id: gi, label: \'A B C D\'.split(\' \')[gi] + \' csoport\',
        players: gp,
        matches: groupType === \'rr\' ? buildRRMatches(gp) : buildSEBracket(gp).flat(),
        seRounds: groupType === \'se\' ? buildSEBracket(gp) : null,
        seCurRound: 0, curIdx: 0, done: false,
      }));
      setTsGroups(groups); setTsCurGroup(0); setTsPhase(\'groups\');
      setSeRounds([]); setRrMatches([]); setRrDone(false); setViewGroup(0);'''

NEW_INIT_GROUPS2 = '''      const sh = [...ep].sort(() => Math.random() - 0.5);
      const numGroups2 = Math.max(2, Math.ceil(sh.length / PLAYERS_PER_GROUP));
      const gPlayers = Array.from({ length: numGroups2 }, (_, gi) => {
        const start = Math.floor(gi * sh.length / numGroups2);
        const end = Math.floor((gi + 1) * sh.length / numGroups2);
        return sh.slice(start, end);
      }).filter(g => g.length > 0);
      const groupType = TOURNAMENT.startsWith(\'grp_rr\') ? \'rr\' : \'se\';
      const groups = gPlayers.map((gp, gi) => ({
        id: gi, label: \'A B C D E F G H\'.split(\' \')[gi] + \' csoport\',
        players: gp,
        matches: groupType === \'rr\' ? buildRRMatches(gp) : buildSEBracket(gp).flat(),
        seRounds: groupType === \'se\' ? buildSEBracket(gp) : null,
        seCurRound: 0, curIdx: 0, done: false,
      }));
      setTsGroups(groups); setTsCurGroup(0); setTsPhase(\'groups\');
      setSeRounds([]); setRrMatches([]); setRrDone(false); setViewGroup(0);'''

assert OLD_INIT_GROUPS2 in html, 'initTournament groups2 not found'
html = html.replace(OLD_INIT_GROUPS2, NEW_INIT_GROUPS2, 1)

# ── 4. Version bump ───────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v7.27'"
NEW_VER = "const APP_VERSION = 'v7.28'"
assert OLD_VER in html, 'version not found'
html = html.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("done")
