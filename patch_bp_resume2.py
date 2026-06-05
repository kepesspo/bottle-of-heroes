with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Remove bad resume code from BeerPongGame ───────────────────────────────
OLD_BAD_RESUME = '''\n\n  // Resume from Firestore state\n  const [resumePrompt, setResumePrompt] = React.useState(\'checking\'); // \'checking\' | \'show\' | \'done\'\n  const [savedBpState, setSavedBpState] = React.useState(null);\n\n  React.useEffect(() => {\n    if (!roomCode || mode !== \'Online\' || typeof checkRoom !== \'function\') {\n      setResumePrompt(\'done\'); return;\n    }\n    checkRoom(roomCode).then(room => {\n      const bp = room?.bpState;\n      if (!bp || bp.tournament !== TOURNAMENT) { setResumePrompt(\'done\'); return; }\n      const seArr = bp.seRounds ? (Array.isArray(bp.seRounds) ? bp.seRounds : Object.values(bp.seRounds)) : [];\n      const rrArr = bp.rrMatches ? (Array.isArray(bp.rrMatches) ? bp.rrMatches : Object.values(bp.rrMatches)) : [];\n      const grpArr = bp.tsGroups ? (Array.isArray(bp.tsGroups) ? bp.tsGroups : Object.values(bp.tsGroups)) : [];\n      const hasData = seArr.length > 0 || rrArr.length > 0 || grpArr.length > 0;\n      if (!hasData) { setResumePrompt(\'done\'); return; }\n      setSavedBpState(bp);\n      setResumePrompt(\'show\');\n    }).catch(() => setResumePrompt(\'done\'));\n  }, []);\n\n  const resumeFromState = (bp) => {\n    const norm = (v) => v ? (Array.isArray(v) ? v : Object.values(v)) : [];\n    setSeRounds(norm(bp.seRounds));\n    setSeCurRound(bp.seCurRound ?? 0);\n    setSeCurMatch(bp.seCurMatch ?? 0);\n    setRrMatches(norm(bp.rrMatches));\n    setRrIdx(bp.rrIdx ?? 0);\n    setRrDone(bp.rrDone ?? false);\n    const groups = norm(bp.tsGroups).map(g => ({\n      ...g,\n      matches: norm(g.matches),\n      seRounds: g.seRounds ? norm(g.seRounds) : null,\n    }));\n    setTsGroups(groups);\n    setTsPhase(bp.phase || \'groups\');\n    setDrinkMap(bp.drinkMap || {});\n    setChampion(bp.champion || null);\n    setViewGroup(0);\n    setCups1(MAX_CUPS); setCups2(MAX_CUPS);\n    doneRef.current = !!bp.champion;\n    if (MODE === \'csapat\') setTeamsReady(true);\n    setResumePrompt(\'done\');\n  };'''

assert OLD_BAD_RESUME in html, 'bad resume code not found'
html = html.replace(OLD_BAD_RESUME, '', 1)

# Remove bad render guard
OLD_BAD_RENDER = '''  if (resumePrompt === \'checking\') {
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

NEW_TEAM_CLEAN = '''  if (MODE === 'csapat' && !teamsReady) {'''
assert OLD_BAD_RENDER in html, 'bad render guard not found'
html = html.replace(OLD_BAD_RENDER, NEW_TEAM_CLEAN, 1)

# ── 2. Add initialBpState prop + resumeFromBpState to BeerPongGame ────────────
OLD_BP_FUNC = '''function BeerPongGame({ gameIdx, players, onAdvance, onResult, gameMeta, roomCode, mode }) {'''
NEW_BP_FUNC = '''function BeerPongGame({ gameIdx, players, onAdvance, onResult, gameMeta, roomCode, mode, initialBpState }) {'''
assert OLD_BP_FUNC in html, 'BeerPongGame func not found'
html = html.replace(OLD_BP_FUNC, NEW_BP_FUNC, 1)

OLD_TIMER_EFFECT = '''  React.useEffect(() => {
    if (timerRunning) {'''
NEW_TIMER_EFFECT = '''  const resumeFromBpState = (bp) => {
    if (!bp) return;
    const norm = (v) => v ? (Array.isArray(v) ? v : Object.values(v)) : [];
    setSeRounds(norm(bp.seRounds));
    setSeCurRound(bp.seCurRound ?? 0);
    setSeCurMatch(bp.seCurMatch ?? 0);
    setRrMatches(norm(bp.rrMatches));
    setRrIdx(bp.rrIdx ?? 0);
    setRrDone(bp.rrDone ?? false);
    setTsGroups(norm(bp.tsGroups).map(g => ({
      ...g,
      matches: norm(g.matches),
      seRounds: g.seRounds ? norm(g.seRounds) : null,
    })));
    setTsPhase(bp.phase || 'groups');
    setDrinkMap(bp.drinkMap || {});
    setChampion(bp.champion || null);
    setViewGroup(0);
    setCups1(MAX_CUPS); setCups2(MAX_CUPS);
    doneRef.current = !!bp.champion;
    if (MODE === 'csapat') setTeamsReady(true);
  };

  React.useEffect(() => { if (initialBpState) resumeFromBpState(initialBpState); }, []);

  React.useEffect(() => {
    if (timerRunning) {'''
assert OLD_TIMER_EFFECT in html, 'timer effect not found'
html = html.replace(OLD_TIMER_EFFECT, NEW_TIMER_EFFECT, 1)

# ── 3. Pass initialBpState from PlayScreen ────────────────────────────────────
OLD_BP_CALL = '''  if (gameId === 'beerpong') return <BeerPongGame key={gameIdx + '_' + (gameMeta?.beerpongConfig?.tournamentType||'se')} gameIdx={gameIdx} players={players} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} roomCode={roomCode} mode={mode} />;'''
NEW_BP_CALL = '''  if (gameId === 'beerpong') return <BeerPongGame key={gameIdx + '_' + (gameMeta?.beerpongConfig?.tournamentType||'se')} gameIdx={gameIdx} players={players} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} roomCode={roomCode} mode={mode} initialBpState={gameMeta?._resumeBpState || null} />;'''
assert OLD_BP_CALL in html, 'BeerPongGame call not found'
html = html.replace(OLD_BP_CALL, NEW_BP_CALL, 1)

# ── 4. Save resume data to localStorage when host creates a room ──────────────
OLD_CREATE_ROOM = '''      const code = generateRoomCode();
      setCreatingRoom(true);
      createRoom(code, players.map(p=>({...p})), selectedGames, gameMeta)
        .then(() => {'''
NEW_CREATE_ROOM = '''      const code = generateRoomCode();
      setCreatingRoom(true);
      if ((selectedGames || []).includes('beerpong')) {
        try { localStorage.setItem('boh_bp_resume', JSON.stringify({ code, players: players.map(p=>({...p})), selectedGames, gameMeta: {...gameMeta, _resumeBpState: null} })); } catch(e) {}
      }
      createRoom(code, players.map(p=>({...p})), selectedGames, gameMeta)
        .then(() => {'''
assert OLD_CREATE_ROOM in html, 'createRoom not found'
html = html.replace(OLD_CREATE_ROOM, NEW_CREATE_ROOM, 1)

# ── 5. Add goResume + resumeRoomData state to App ─────────────────────────────
OLD_HANDLE_THEME = '''  const handleSetTheme = (name) => {
    localStorage.setItem('boh_theme', name);
    T = THEMES[name];
    setAppTheme(name);
  };

  React.useEffect(() => {
    document.body.style.background = T.bg;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = T.bg;
  }, [appTheme]);'''

NEW_HANDLE_THEME = '''  const handleSetTheme = (name) => {
    localStorage.setItem('boh_theme', name);
    T = THEMES[name];
    setAppTheme(name);
  };

  React.useEffect(() => {
    document.body.style.background = T.bg;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = T.bg;
  }, [appTheme]);

  const [resumeRoomData, setResumeRoomData] = React.useState(null);

  React.useEffect(() => {
    try {
      const saved = localStorage.getItem('boh_bp_resume');
      if (!saved || typeof checkRoom !== 'function') return;
      const data = JSON.parse(saved);
      if (!data?.code) return;
      checkRoom(data.code).then(room => {
        if (!room?.bpState) return;
        const bp = room.bpState;
        const norm = (v) => v ? (Array.isArray(v) ? v : Object.values(v)) : [];
        const hasData = norm(bp.seRounds).length > 0 || norm(bp.rrMatches).length > 0 || norm(bp.tsGroups).length > 0;
        if (!hasData) return;
        setResumeRoomData({ ...data, bpState: bp });
      }).catch(() => {});
    } catch(e) {}
  }, []);

  const goResume = (data) => {
    setPlayers(data.players);
    setSelectedGames(data.selectedGames);
    setGameMeta({ ...data.gameMeta, _resumeBpState: data.bpState });
    setRoomCode(data.code);
    if (typeof subscribeRoom === 'function') {
      if (roomUnsubRef.current) roomUnsubRef.current();
      roomUnsubRef.current = subscribeRoom(data.code, roomData => {
        if (roomData) setPlayers(roomData.players || data.players);
      });
    }
    setResumeRoomData(null);
    localStorage.removeItem('boh_bp_resume');
    setScreen('play');
  };'''

assert OLD_HANDLE_THEME in html, 'handleSetTheme not found'
html = html.replace(OLD_HANDLE_THEME, NEW_HANDLE_THEME, 1)

# ── 6. Pass resumeRoomData + goResume to HomeScreen ──────────────────────────
OLD_HOME_CALL = '''        {screen===\'home\'     && <HomeScreen     go={go} mode={mode} setMode={setMode} onStartGame={onStartGame} setTheme={handleSetTheme} currentTheme={appTheme} />}'''
NEW_HOME_CALL = '''        {screen===\'home\'     && <HomeScreen     go={go} mode={mode} setMode={setMode} onStartGame={onStartGame} setTheme={handleSetTheme} currentTheme={appTheme} resumeRoomData={resumeRoomData} onResume={goResume} />}'''
assert OLD_HOME_CALL in html, 'HomeScreen call not found'
html = html.replace(OLD_HOME_CALL, NEW_HOME_CALL, 1)

# ── 7. Update HomeScreen signature + add resume button ───────────────────────
OLD_HOME_FUNC = '''function HomeScreen({ go, mode, setMode, onStartGame, setTheme, currentTheme }) {'''
NEW_HOME_FUNC = '''function HomeScreen({ go, mode, setMode, onStartGame, setTheme, currentTheme, resumeRoomData, onResume }) {'''
assert OLD_HOME_FUNC in html, 'HomeScreen func not found'
html = html.replace(OLD_HOME_FUNC, NEW_HOME_FUNC, 1)

OLD_THEME_BTN = '''        <div style={{ position:\'absolute\', top:14, right:18, zIndex:10 }}>
          <button onClick={() => setTheme && setTheme(currentTheme === \'warm\' ? \'sky\' : currentTheme === \'sky\' ? \'dark\' : \'warm\')}'''
NEW_THEME_BTN = '''        {resumeRoomData && onResume && (
          <div style={{ position:\'absolute\', top:14, left:18, zIndex:10 }}>
            <button onClick={() => onResume(resumeRoomData)} style={{ display:\'flex\', alignItems:\'center\', gap:7, padding:\'8px 14px\', borderRadius:999, border:\'none\', background:T.mint, color:\'#fff\', fontFamily:T.font, fontWeight:800, fontSize:13, cursor:\'pointer\', boxShadow:T.shadowLift, animation:\'pulse 2s infinite\' }}>
              <span style={{ fontSize:16 }}>🏓</span> Folytatás
            </button>
          </div>
        )}
        <div style={{ position:\'absolute\', top:14, right:18, zIndex:10 }}>
          <button onClick={() => setTheme && setTheme(currentTheme === \'warm\' ? \'sky\' : currentTheme === \'sky\' ? \'dark\' : \'warm\')}'''
assert OLD_THEME_BTN in html, 'theme button not found'
html = html.replace(OLD_THEME_BTN, NEW_THEME_BTN, 1)

# ── 8. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v7.45'"
NEW_VER = "const APP_VERSION = 'v7.46'"
assert OLD_VER in html, 'version not found'
html = html.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("done")
