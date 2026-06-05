with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. ObserverScreen: add onJoinAsHost prop + host mode ─────────────────────
OLD_OBS_FUNC = '''function ObserverScreen({ go, initialCode }) {
  const CODE_LEN = 6;
  const [code, setCode] = useState(() => (initialCode||'').slice(0,6));
  const [name, setName] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [observerId] = useState(() => 'obs_' + Date.now());
  const [status, setStatus] = useState('enter');'''

NEW_OBS_FUNC = '''function ObserverScreen({ go, initialCode, onJoinAsHost }) {
  const CODE_LEN = 6;
  const [code, setCode] = useState(() => (initialCode||'').slice(0,6));
  const [name, setName] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [observerId] = useState(() => 'obs_' + Date.now());
  const [status, setStatus] = useState('enter');
  const [joinMode, setJoinMode] = useState('observer'); // 'observer' | 'host'
  const [hostLoading, setHostLoading] = useState(false);'''

assert OLD_OBS_FUNC in html, 'ObserverScreen func not found'
html = html.replace(OLD_OBS_FUNC, NEW_OBS_FUNC, 1)

# ── 2. Add host submit logic before existing submit ──────────────────────────
OLD_SUBMIT = '''  const submit = () => {
    if (code.length < CODE_LEN) return;
    setStatus('connecting');
    checkRoom(code)
      .then(room => {
        if (!room || !room.active) { setErrorMsg(`A ${code} kód nem érvényes, vagy a szoba bezárult.`); setStatus('error'); return; }
        const isBuszRoom = !!(room.buszState || (room.selectedGames||[]).includes('busz'));
        if (!isBuszRoom) {
          if (!room.observerAllowed) { setErrorMsg('A házigazda nem engedélyezte a megfigyelőket ennél a szobánál.'); setStatus('error'); return; }
          const obs = room.observers || [];
          if (obs.length >= 3) { setErrorMsg('A szoba tele van – már 3 vendég csatlakozott.'); setStatus('error'); return; }
        }
        return (typeof joinRoom==='function' && !isBuszRoom ? joinRoom(code, { id:observerId, name:name.trim() }) : Promise.resolve())
          .then(() => setStatus('watching'));
      })
      .catch(() => { setErrorMsg('Hálózati hiba – próbáld újra.'); setStatus('error'); });
  };'''

NEW_SUBMIT = '''  const submitHost = () => {
    if (code.length < CODE_LEN) return;
    setHostLoading(true);
    checkRoom(code)
      .then(room => {
        setHostLoading(false);
        if (!room || !room.active) { setErrorMsg(`A ${code} kód nem érvényes, vagy a szoba bezárult.`); return; }
        if (onJoinAsHost) onJoinAsHost(code, room);
      })
      .catch(() => { setHostLoading(false); setErrorMsg('Hálózati hiba – próbáld újra.'); });
  };

  const submit = () => {
    if (code.length < CODE_LEN) return;
    if (joinMode === 'host') { submitHost(); return; }
    setStatus('connecting');
    checkRoom(code)
      .then(room => {
        if (!room || !room.active) { setErrorMsg(`A ${code} kód nem érvényes, vagy a szoba bezárult.`); setStatus('error'); return; }
        const isBuszRoom = !!(room.buszState || (room.selectedGames||[]).includes('busz'));
        if (!isBuszRoom) {
          if (!room.observerAllowed) { setErrorMsg('A házigazda nem engedélyezte a megfigyelőket ennél a szobánál.'); setStatus('error'); return; }
          const obs = room.observers || [];
          if (obs.length >= 3) { setErrorMsg('A szoba tele van – már 3 vendég csatlakozott.'); setStatus('error'); return; }
        }
        return (typeof joinRoom==='function' && !isBuszRoom ? joinRoom(code, { id:observerId, name:name.trim() }) : Promise.resolve())
          .then(() => setStatus('watching'));
      })
      .catch(() => { setErrorMsg('Hálózati hiba – próbáld újra.'); setStatus('error'); });
  };'''

assert OLD_SUBMIT in html, 'submit not found'
html = html.replace(OLD_SUBMIT, NEW_SUBMIT, 1)

# ── 3. Pass joinMode/setJoinMode/hostLoading/errorMsg to ObserverEnter ────────
OLD_OBS_ENTER_CALL = '''      {status===\'enter\' && <ObserverEnter code={code} codeLen={CODE_LEN} onDigit={push} onBack={back} onSubmit={submit} onPaste={v => setCode(v.replace(/\D/g,\'\').slice(0,CODE_LEN))} />}'''
NEW_OBS_ENTER_CALL = '''      {status===\'enter\' && <ObserverEnter code={code} codeLen={CODE_LEN} onDigit={push} onBack={back} onSubmit={submit} onPaste={v => setCode(v.replace(/\D/g,\'\').slice(0,CODE_LEN))} joinMode={joinMode} setJoinMode={setJoinMode} hostLoading={hostLoading} errorMsg={errorMsg} />}'''
assert OLD_OBS_ENTER_CALL in html, 'ObserverEnter call not found'
html = html.replace(OLD_OBS_ENTER_CALL, NEW_OBS_ENTER_CALL, 1)

# ── 4. Update ObserverEnter component to show mode toggle + host UI ───────────
OLD_OBS_ENTER_FUNC = '''function ObserverEnter({ code, codeLen, onDigit, onBack, onSubmit, onPaste }) {
  const ready = code.length === codeLen;'''
NEW_OBS_ENTER_FUNC = '''function ObserverEnter({ code, codeLen, onDigit, onBack, onSubmit, onPaste, joinMode, setJoinMode, hostLoading, errorMsg }) {
  const ready = code.length === codeLen;'''
assert OLD_OBS_ENTER_FUNC in html, 'ObserverEnter func not found'
html = html.replace(OLD_OBS_ENTER_FUNC, NEW_OBS_ENTER_FUNC, 1)

# Add mode toggle + update the icon/title/subtitle + button text inside ObserverEnter
OLD_ENTER_ICON = '''        <div style={{ fontSize:52, lineHeight:1, filter:\'drop-shadow(0 4px 10px rgba(20,30,50,0.15))\' }}>👀</div>
        <div style={{ textAlign:\'center\', maxWidth:280 }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:T.ink, textTransform:\'uppercase\', letterSpacing:T.letterDisplay }}>Szoba kód</div>
          <div style={{ marginTop:4, fontFamily:T.font, fontSize:12, fontWeight:600, color:T.inkSoft, lineHeight:1.4 }}>Add meg a házigazda szobakódját.</div>
        </div>'''
NEW_ENTER_ICON = '''        {/* Mode toggle */}
        <div style={{ display:\'flex\', background:T.surfaceMuted, borderRadius:14, padding:3, gap:3, width:\'100%\', maxWidth:280 }}>
          <button onClick={() => setJoinMode && setJoinMode(\'observer\')} style={{ flex:1, padding:\'9px 0\', borderRadius:11, border:\'none\', cursor:\'pointer\', fontFamily:T.font, fontWeight:700, fontSize:13, background: joinMode===\'observer\' ? T.surface : \'transparent\', color: joinMode===\'observer\' ? T.ink : T.inkSoft, boxShadow: joinMode===\'observer\' ? T.shadow : \'none\', transition:\'all .18s\' }}>👀 Megfigyelő</button>
          <button onClick={() => setJoinMode && setJoinMode(\'host\')} style={{ flex:1, padding:\'9px 0\', borderRadius:11, border:\'none\', cursor:\'pointer\', fontFamily:T.font, fontWeight:700, fontSize:13, background: joinMode===\'host\' ? T.mint : \'transparent\', color: joinMode===\'host\' ? \'#fff\' : T.inkSoft, boxShadow: joinMode===\'host\' ? T.shadowLift : \'none\', transition:\'all .18s\' }}>🎮 Host</button>
        </div>
        <div style={{ fontSize:44, lineHeight:1, filter:\'drop-shadow(0 4px 10px rgba(20,30,50,0.15))\' }}>{joinMode===\'host\' ? \'🎮\' : \'👀\'}</div>
        <div style={{ textAlign:\'center\', maxWidth:280 }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:T.ink, textTransform:\'uppercase\', letterSpacing:T.letterDisplay }}>Szoba kód</div>
          <div style={{ marginTop:4, fontFamily:T.font, fontSize:12, fontWeight:600, color:T.inkSoft, lineHeight:1.4 }}>{joinMode===\'host\' ? \'Irányítsd a játékot egy másik készülékről.\' : \'Add meg a házigazda szobakódját.\'}</div>
        </div>
        {errorMsg && <div style={{ fontFamily:T.font, fontSize:12, color:T.coral, fontWeight:700, textAlign:\'center\', maxWidth:280 }}>{errorMsg}</div>}'''
assert OLD_ENTER_ICON in html, 'enter icon not found'
html = html.replace(OLD_ENTER_ICON, NEW_ENTER_ICON, 1)

# Update the connect button text
OLD_CONNECT_BTN = '''      <PrimaryButton disabled={!ready} onClick={onSubmit} style={{ marginTop:14 }}>Csatlakozás</PrimaryButton>'''
NEW_CONNECT_BTN = '''      <PrimaryButton disabled={!ready || hostLoading} onClick={onSubmit} style={{ marginTop:14 }}>{hostLoading ? \'Betöltés…\' : joinMode===\'host\' ? \'🎮 Belépés Hostként\' : \'Csatlakozás\'}</PrimaryButton>'''
assert OLD_CONNECT_BTN in html, 'connect button not found'
html = html.replace(OLD_CONNECT_BTN, NEW_CONNECT_BTN, 1)

# ── 5. Add goJoinAsHost to App + pass to ObserverScreen ──────────────────────
OLD_GO_RESUME_END = '''  const goResume = (data) => {
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

NEW_GO_RESUME_END = '''  const goResume = (data) => {
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
  };

  const goJoinAsHost = (code, room) => {
    const bp = room.bpState || null;
    setPlayers(room.players || []);
    setSelectedGames(room.selectedGames || []);
    setGameMeta({ ...(room.gameMeta || {}), _resumeBpState: bp });
    setRoomCode(code);
    if (typeof subscribeRoom === 'function') {
      if (roomUnsubRef.current) roomUnsubRef.current();
      roomUnsubRef.current = subscribeRoom(code, roomData => {
        if (roomData) setPlayers(roomData.players || room.players);
      });
    }
    setScreen('play');
  };'''

assert OLD_GO_RESUME_END in html, 'goResume not found'
html = html.replace(OLD_GO_RESUME_END, NEW_GO_RESUME_END, 1)

# Pass onJoinAsHost to ObserverScreen in render
OLD_OBS_RENDER = '''        {screen===\'observer\' && <ObserverScreen go={go} initialCode={_initRoom} />}'''
NEW_OBS_RENDER = '''        {screen===\'observer\' && <ObserverScreen go={go} initialCode={_initRoom} onJoinAsHost={goJoinAsHost} />}'''
assert OLD_OBS_RENDER in html, 'ObserverScreen render not found'
html = html.replace(OLD_OBS_RENDER, NEW_OBS_RENDER, 1)

# ── 6. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v7.47'"
NEW_VER = "const APP_VERSION = 'v7.48'"
assert OLD_VER in html, 'version not found'
html = html.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("done")
