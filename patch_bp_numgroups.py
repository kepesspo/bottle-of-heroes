with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Config UI: replace playersPerGroup with numGroups ─────────────────
OLD_CFG_DESTR = '''  const groupAdvance = config.groupAdvance ?? 1;
  const playersPerGroup = config.playersPerGroup ?? 4;'''
NEW_CFG_DESTR = '''  const groupAdvance = config.groupAdvance ?? 1;
  const numGroups = config.numGroups ?? 2;'''
assert OLD_CFG_DESTR in html, 'config destructure not found'
html = html.replace(OLD_CFG_DESTR, NEW_CFG_DESTR, 1)

OLD_PPG_UI = '''          <div style={{ display:\'flex\', alignItems:\'center\', justifyContent:\'space-between\', padding:\'13px 0\', borderTop:\'1px solid rgba(26,42,74,0.10)\' }}>
            <div>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>Játékosok/csoport</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>Hány játékos kerüljön egy csoportba</div>
            </div>
            <div style={{ display:\'flex\', alignItems:\'center\', gap:8 }}>
              <button onClick={() => setConfig(c => ({...c, playersPerGroup: Math.max(3,(c.playersPerGroup??4)-1)}))} style={{ width:33, height:33, borderRadius:10, background:T.surfaceMuted, border:\'none\', cursor:\'pointer\', display:\'grid\', placeItems:\'center\', fontSize:20, fontWeight:900, color:\'#D85F5C\' }}>-</button>
              <span style={{ fontFamily:\'monospace\', fontWeight:900, fontSize:18, color:T.ink, minWidth:30, textAlign:\'center\' }}>{playersPerGroup}</span>
              <button onClick={() => setConfig(c => ({...c, playersPerGroup: Math.min(8,(c.playersPerGroup??4)+1)}))} style={{ width:33, height:33, borderRadius:10, background:T.surfaceMuted, border:\'none\', cursor:\'pointer\', display:\'grid\', placeItems:\'center\', fontSize:20, fontWeight:900, color:T.mintDeep }}>+</button>
            </div>
          </div>'''
NEW_PPG_UI = '''          <div style={{ display:\'flex\', alignItems:\'center\', justifyContent:\'space-between\', padding:\'13px 0\', borderTop:\'1px solid rgba(26,42,74,0.10)\' }}>
            <div>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>Csoportok száma</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>Hány csoportra osztja szét a játékosokat</div>
            </div>
            <div style={{ display:\'flex\', alignItems:\'center\', gap:8 }}>
              <button onClick={() => setConfig(c => ({...c, numGroups: Math.max(2,(c.numGroups??2)-1)}))} style={{ width:33, height:33, borderRadius:10, background:T.surfaceMuted, border:\'none\', cursor:\'pointer\', display:\'grid\', placeItems:\'center\', fontSize:20, fontWeight:900, color:\'#D85F5C\' }}>-</button>
              <span style={{ fontFamily:\'monospace\', fontWeight:900, fontSize:18, color:T.ink, minWidth:30, textAlign:\'center\' }}>{numGroups}</span>
              <button onClick={() => setConfig(c => ({...c, numGroups: Math.min(8,(c.numGroups??2)+1)}))} style={{ width:33, height:33, borderRadius:10, background:T.surfaceMuted, border:\'none\', cursor:\'pointer\', display:\'grid\', placeItems:\'center\', fontSize:20, fontWeight:900, color:T.mintDeep }}>+</button>
            </div>
          </div>'''
assert OLD_PPG_UI in html, 'ppg UI not found'
html = html.replace(OLD_PPG_UI, NEW_PPG_UI, 1)

# ── 2. Game const: replace PLAYERS_PER_GROUP with NUM_GROUPS ─────────────
OLD_CONST = '''  const GROUP_ADVANCE = bpCfg.groupAdvance ?? 1;
  const PLAYERS_PER_GROUP = bpCfg.playersPerGroup ?? 4;'''
NEW_CONST = '''  const GROUP_ADVANCE = bpCfg.groupAdvance ?? 1;
  const NUM_GROUPS = bpCfg.numGroups ?? 2;'''
assert OLD_CONST in html, 'game const not found'
html = html.replace(OLD_CONST, NEW_CONST, 1)

# ── 3. initTournament: use NUM_GROUPS directly ────────────────────────────
OLD_INIT1 = '''      const sh = [...tp].sort(() => Math.random() - 0.5);
      const numGroups = Math.max(2, Math.ceil(sh.length / PLAYERS_PER_GROUP));
      const gPlayers = Array.from({ length: numGroups }, (_, gi) => {
        const start = Math.floor(gi * sh.length / numGroups);
        const end = Math.floor((gi + 1) * sh.length / numGroups);
        return sh.slice(start, end);
      }).filter(g => g.length > 0);'''
NEW_INIT1 = '''      const sh = [...tp].sort(() => Math.random() - 0.5);
      const numGroups = Math.max(2, Math.min(NUM_GROUPS, Math.floor(sh.length / 2)));
      const gPlayers = Array.from({ length: numGroups }, (_, gi) => {
        const start = Math.floor(gi * sh.length / numGroups);
        const end = Math.floor((gi + 1) * sh.length / numGroups);
        return sh.slice(start, end);
      }).filter(g => g.length > 0);'''
assert OLD_INIT1 in html, 'initTournament1 not found'
html = html.replace(OLD_INIT1, NEW_INIT1, 1)

OLD_INIT2 = '''      const sh = [...ep].sort(() => Math.random() - 0.5);
      const numGroups2 = Math.max(2, Math.ceil(sh.length / PLAYERS_PER_GROUP));
      const gPlayers = Array.from({ length: numGroups2 }, (_, gi) => {
        const start = Math.floor(gi * sh.length / numGroups2);
        const end = Math.floor((gi + 1) * sh.length / numGroups2);
        return sh.slice(start, end);
      }).filter(g => g.length > 0);'''
NEW_INIT2 = '''      const sh = [...ep].sort(() => Math.random() - 0.5);
      const numGroups2 = Math.max(2, Math.min(NUM_GROUPS, Math.floor(sh.length / 2)));
      const gPlayers = Array.from({ length: numGroups2 }, (_, gi) => {
        const start = Math.floor(gi * sh.length / numGroups2);
        const end = Math.floor((gi + 1) * sh.length / numGroups2);
        return sh.slice(start, end);
      }).filter(g => g.length > 0);'''
assert OLD_INIT2 in html, 'initTournament2 not found'
html = html.replace(OLD_INIT2, NEW_INIT2, 1)

# ── 4. Version bump ───────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v7.29'"
NEW_VER = "const APP_VERSION = 'v7.30'"
assert OLD_VER in html, 'version not found'
html = html.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("done")
