with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Add hostPin state to ObserverScreen ────────────────────────────────────
OLD_OBS_STATE = '''  const [joinMode, setJoinMode] = useState('observer'); // 'observer' | 'host'
  const [hostLoading, setHostLoading] = useState(false);'''
NEW_OBS_STATE = '''  const [joinMode, setJoinMode] = useState('observer'); // 'observer' | 'host'
  const [hostLoading, setHostLoading] = useState(false);
  const [hostPin, setHostPin] = useState('');'''
assert OLD_OBS_STATE in html, 'obs state not found'
html = html.replace(OLD_OBS_STATE, NEW_OBS_STATE, 1)

# ── 2. Check PIN in submitHost ────────────────────────────────────────────────
OLD_SUBMIT_HOST = '''  const submitHost = () => {
    if (code.length < CODE_LEN) return;
    setHostLoading(true);'''
NEW_SUBMIT_HOST = '''  const submitHost = () => {
    if (code.length < CODE_LEN) return;
    if (hostPin !== '2026') { setErrorMsg('Helytelen PIN kód.'); return; }
    setHostLoading(true);'''
assert OLD_SUBMIT_HOST in html, 'submitHost not found'
html = html.replace(OLD_SUBMIT_HOST, NEW_SUBMIT_HOST, 1)

# ── 3. Pass hostPin/setHostPin to ObserverEnter ───────────────────────────────
OLD_OBS_ENTER_CALL = '''      {status==='enter' && <ObserverEnter code={code} codeLen={CODE_LEN} onDigit={push} onBack={back} onSubmit={submit} onPaste={v => setCode(v.replace(/\D/g,'').slice(0,CODE_LEN))} joinMode={joinMode} setJoinMode={setJoinMode} hostLoading={hostLoading} errorMsg={errorMsg} />}'''
NEW_OBS_ENTER_CALL = '''      {status==='enter' && <ObserverEnter code={code} codeLen={CODE_LEN} onDigit={push} onBack={back} onSubmit={submit} onPaste={v => setCode(v.replace(/\D/g,'').slice(0,CODE_LEN))} joinMode={joinMode} setJoinMode={setJoinMode} hostLoading={hostLoading} errorMsg={errorMsg} hostPin={hostPin} setHostPin={setHostPin} />}'''
assert OLD_OBS_ENTER_CALL in html, 'ObserverEnter call not found'
html = html.replace(OLD_OBS_ENTER_CALL, NEW_OBS_ENTER_CALL, 1)

# ── 4. Update ObserverEnter signature ─────────────────────────────────────────
OLD_OBS_ENTER_FUNC = '''function ObserverEnter({ code, codeLen, onDigit, onBack, onSubmit, onPaste, joinMode, setJoinMode, hostLoading, errorMsg }) {
  const ready = code.length === codeLen;'''
NEW_OBS_ENTER_FUNC = '''function ObserverEnter({ code, codeLen, onDigit, onBack, onSubmit, onPaste, joinMode, setJoinMode, hostLoading, errorMsg, hostPin, setHostPin }) {
  const PIN_LEN = 4;
  const ready = code.length === codeLen;
  const pinReady = hostPin.length === PIN_LEN;'''
assert OLD_OBS_ENTER_FUNC in html, 'ObserverEnter func not found'
html = html.replace(OLD_OBS_ENTER_FUNC, NEW_OBS_ENTER_FUNC, 1)

# ── 5. Add PIN input UI after the room code digits, before the hint text ──────
OLD_HINT = '''        <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, fontWeight:600, opacity:0.7 }}>Tipp: a házigazda osztja meg a szoba kódját</div>
      </div>
      <NumberPad onDigit={onDigit} onBack={onBack} />
      <PrimaryButton disabled={!ready || hostLoading} onClick={onSubmit} style={{ marginTop:14 }}>{hostLoading ? 'Betöltés…' : joinMode==='host' ? '🎮 Belépés Hostként' : 'Csatlakozás'}</PrimaryButton>'''
NEW_HINT = '''        <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, fontWeight:600, opacity:0.7 }}>Tipp: a házigazda osztja meg a szoba kódját</div>
        {joinMode==='host' && (
          <div style={{ width:'100%', maxWidth:280 }}>
            <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft, marginBottom:6, textAlign:'center' }}>🔐 Host PIN</div>
            <div style={{ display:'flex', gap:8, justifyContent:'center' }}>
              {Array.from({ length:PIN_LEN }).map((_,i) => {
                const filled = i < hostPin.length;
                const active = i === hostPin.length;
                return (
                  <div key={i} style={{
                    width:38, height:52,
                    background: filled ? T.surface : 'rgba(255,255,255,0.5)',
                    borderRadius:12,
                    border: active ? `2px solid ${T.mint}` : `2px solid ${filled ? 'transparent' : 'rgba(20,30,50,0.08)'}`,
                    boxShadow: filled ? T.shadow : 'none',
                    display:'grid', placeItems:'center',
                    fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:24,
                    color:T.ink, fontVariantNumeric:'tabular-nums',
                    transition:'all .15s',
                  }}>
                    {filled ? '•' : (active ? <span style={{ width:2, height:22, background:T.mint, opacity:0.7, animation:'caretBlink 1s infinite' }}/> : '')}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
      <NumberPad onDigit={joinMode==='host' && pinReady ? onDigit : joinMode==='host' ? (d => setHostPin && hostPin.length < PIN_LEN ? setHostPin(hostPin+d) : null) : onDigit} onBack={joinMode==='host' && !pinReady ? (() => setHostPin && setHostPin(hostPin.slice(0,-1))) : onBack} />
      <PrimaryButton disabled={joinMode==='host' ? (!ready || !pinReady || hostLoading) : !ready} onClick={onSubmit} style={{ marginTop:14 }}>{hostLoading ? 'Betöltés…' : joinMode==='host' ? '🎮 Belépés Hostként' : 'Csatlakozás'}</PrimaryButton>'''
assert OLD_HINT in html, 'hint not found'
html = html.replace(OLD_HINT, NEW_HINT, 1)

# ── 6. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v7.48'"
NEW_VER = "const APP_VERSION = 'v7.49'"
assert OLD_VER in html, 'version not found'
html = html.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("done")
