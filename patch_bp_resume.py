with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Add resumePrompt state + checkRoom useEffect after existing state ──────
OLD_STATE_END = '''  const [timerSecs, setTimerSecs] = React.useState(0);
  const [timerRunning, setTimerRunning] = React.useState(false);
  const timerRef = React.useRef(null);'''

NEW_STATE_END = '''  const [timerSecs, setTimerSecs] = React.useState(0);
  const [timerRunning, setTimerRunning] = React.useState(false);
  const timerRef = React.useRef(null);

  // Resume from Firestore state
  const [resumePrompt, setResumePrompt] = React.useState('checking'); // 'checking' | 'show' | 'done'
  const [savedBpState, setSavedBpState] = React.useState(null);

  React.useEffect(() => {
    if (!roomCode || mode !== 'Online' || typeof checkRoom !== 'function') {
      setResumePrompt('done'); return;
    }
    checkRoom(roomCode).then(room => {
      const bp = room?.bpState;
      if (!bp || bp.tournament !== TOURNAMENT) { setResumePrompt('done'); return; }
      const seArr = bp.seRounds ? (Array.isArray(bp.seRounds) ? bp.seRounds : Object.values(bp.seRounds)) : [];
      const rrArr = bp.rrMatches ? (Array.isArray(bp.rrMatches) ? bp.rrMatches : Object.values(bp.rrMatches)) : [];
      const grpArr = bp.tsGroups ? (Array.isArray(bp.tsGroups) ? bp.tsGroups : Object.values(bp.tsGroups)) : [];
      const hasData = seArr.length > 0 || rrArr.length > 0 || grpArr.length > 0;
      if (!hasData) { setResumePrompt('done'); return; }
      setSavedBpState(bp);
      setResumePrompt('show');
    }).catch(() => setResumePrompt('done'));
  }, []);

  const resumeFromState = (bp) => {
    const norm = (v) => v ? (Array.isArray(v) ? v : Object.values(v)) : [];
    setSeRounds(norm(bp.seRounds));
    setSeCurRound(bp.seCurRound ?? 0);
    setSeCurMatch(bp.seCurMatch ?? 0);
    setRrMatches(norm(bp.rrMatches));
    setRrIdx(bp.rrIdx ?? 0);
    setRrDone(bp.rrDone ?? false);
    const groups = norm(bp.tsGroups).map(g => ({
      ...g,
      matches: norm(g.matches),
      seRounds: g.seRounds ? norm(g.seRounds) : null,
    }));
    setTsGroups(groups);
    setTsPhase(bp.phase || 'groups');
    setDrinkMap(bp.drinkMap || {});
    setChampion(bp.champion || null);
    setViewGroup(0);
    setCups1(MAX_CUPS); setCups2(MAX_CUPS);
    doneRef.current = !!bp.champion;
    if (MODE === 'csapat') setTeamsReady(true);
    setResumePrompt('done');
  };'''

assert OLD_STATE_END in html, 'state end not found'
html = html.replace(OLD_STATE_END, NEW_STATE_END, 1)

# ── 2. Add resume prompt render guard before team assignment screen ──────────
OLD_TEAM_CHECK = '''  if (MODE === 'csapat' && !teamsReady) {'''

NEW_TEAM_CHECK = '''  if (resumePrompt === 'checking') {
    return (
      <div style={{ flex:1, display:\'flex\', flexDirection:\'column\', alignItems:\'center\', justifyContent:\'center\', gap:16, padding:32 }}>
        <div style={{ display:\'flex\', gap:6 }}>{[0,1,2].map(i => <span key={i} style={{ width:10, height:10, borderRadius:\'50%\', background:T.mint, animation:`dotBounce 1.2s ${i*0.15}s infinite ease-in-out` }}/>)}</div>
      </div>
    );
  }

  if (resumePrompt === \'show\' && savedBpState) {
    const bp = savedBpState;
    const norm = (v) => v ? (Array.isArray(v) ? v : Object.values(v)) : [];
    const seArr = norm(bp.seRounds);
    const rrArr = norm(bp.rrMatches);
    const grpArr = norm(bp.tsGroups);
    const totalMatches = seArr.flatMap(r => r).filter(m => m.score).length
      + rrArr.filter(m => m.score).length
      + grpArr.flatMap(g => norm(g.matches)).filter(m => m.score).length;
    const phaseText = bp.phase === \'finals\' ? \'Főszakasz\' : bp.tournament?.startsWith(\'grp_\') ? \'Csoportkör\' : null;
    return (
      <div style={{ flex:1, display:\'flex\', flexDirection:\'column\', alignItems:\'center\', justifyContent:\'center\', gap:20, padding:28 }}>
        <div style={{ fontSize:52 }}>🏓</div>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink, textAlign:\'center\' }}>Folytatod az előző bajnokságot?</div>
        <div style={{ background:T.surface, borderRadius:16, padding:\'14px 18px\', boxShadow:T.shadow, display:\'flex\', flexDirection:\'column\', gap:6, width:\'100%\', maxWidth:320 }}>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft }}>
            {totalMatches > 0 ? `${totalMatches} meccs már lejátszva` : \'Sorsolás kész, játék nem kezdődött\'}
          </div>
          {phaseText && <div style={{ fontFamily:T.font, fontSize:13, color:T.mint, fontWeight:700 }}>{phaseText}</div>}
          {bp.champion && <div style={{ fontFamily:T.font, fontSize:13, color:T.yellow, fontWeight:700 }}>🏆 Bajnok: {bp.champion.name}</div>}
        </div>
        <button onClick={() => resumeFromState(savedBpState)} style={{ width:\'100%\', maxWidth:320, padding:\'15px 0\', borderRadius:16, background:T.mint, border:\'none\', color:\'#fff\', fontFamily:T.font, fontWeight:900, fontSize:16, cursor:\'pointer\', boxShadow:T.shadowLift }}>
          ▶ Folytatás
        </button>
        <button onClick={() => setResumePrompt(\'done\')} style={{ width:\'100%\', maxWidth:320, padding:\'13px 0\', borderRadius:16, background:T.surfaceMuted, border:\'none\', color:T.inkSoft, fontFamily:T.font, fontWeight:700, fontSize:15, cursor:\'pointer\' }}>
          Új bajnokság indítása
        </button>
      </div>
    );
  }

  if (MODE === 'csapat' && !teamsReady) {'''

assert OLD_TEAM_CHECK in html, 'team check not found'
html = html.replace(OLD_TEAM_CHECK, NEW_TEAM_CHECK, 1)

# ── 3. Version bump ────────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v7.44'"
NEW_VER = "const APP_VERSION = 'v7.45'"
assert OLD_VER in html, 'version not found'
html = html.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("done")
