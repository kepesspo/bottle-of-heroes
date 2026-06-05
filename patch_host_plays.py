with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. BuszConfigSheet: add "Host is játszik" toggle ─────────────────────────
OLD_BUSZ_CONFIG_CLOSE = '''        <button onClick={onClose} style={{ width:'100%', padding:'15px', borderRadius:16, background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:'0 5px 16px -5px rgba(79,194,160,0.6)', marginTop:16 }}>Kész</button>
      </div>
    </SheetOverlay>
  );
}

function KisebbConfigSheet'''

NEW_BUSZ_CONFIG_CLOSE = '''        {(() => { const hostPlaysOn = config.hostPlays === true; return (
          <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'13px 0', borderTop:'1px solid rgba(26,42,74,0.10)' }}>
            <div>
              <span style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>🎮 Host is játszik</span>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>A host a saját telefonján kártyázik is</div>
            </div>
            <button onClick={() => setConfig(c => ({...c, hostPlays: !hostPlaysOn}))} style={{ width:50, height:30, borderRadius:15, background:hostPlaysOn?T.mint:'rgba(26,42,74,0.12)', border:'none', cursor:'pointer', position:'relative', transition:'background .2s', flexShrink:0 }}>
              <div style={{ position:'absolute', top:3, left:hostPlaysOn?23:3, width:24, height:24, borderRadius:'50%', background:'#fff', boxShadow:'0 1px 3px rgba(0,0,0,0.22)', transition:'left .2s' }}/>
            </button>
          </div>
        ); })()}
        <button onClick={onClose} style={{ width:'100%', padding:'15px', borderRadius:16, background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:'0 5px 16px -5px rgba(79,194,160,0.6)', marginTop:16 }}>Kész</button>
      </div>
    </SheetOverlay>
  );
}

function KisebbConfigSheet'''

assert OLD_BUSZ_CONFIG_CLOSE in html, 'BuszConfigSheet close button not found'
html = html.replace(OLD_BUSZ_CONFIG_CLOSE, NEW_BUSZ_CONFIG_CLOSE, 1)

# ── 2. BuszGame: add hostPlayerId + hostViewMode state ────────────────────────
OLD_BUSZ_GAME_STATE = '''function BuszGame({ players, roomCode, mode, gameIdx, gameMeta, onAdvance }) {
  const isOnline = mode === 'Online' && !!roomCode;
  const [buszState, setBuszState] = useState(null);
  const [zsulliAnim, setZsulliAnim] = useState(null);
  const [ready, setReady] = useState(false);
  const [guessResult, setGuessResult] = useState(null);
  const [takenIds, setTakenIds] = useState([]);
  const [showQR, setShowQR] = useState(false);
  const stRef = useRef(null);
  const autoStartRef = useRef(false);'''

NEW_BUSZ_GAME_STATE = '''function BuszGame({ players, roomCode, mode, gameIdx, gameMeta, onAdvance }) {
  const isOnline = mode === 'Online' && !!roomCode;
  const [buszState, setBuszState] = useState(null);
  const [zsulliAnim, setZsulliAnim] = useState(null);
  const [ready, setReady] = useState(false);
  const [guessResult, setGuessResult] = useState(null);
  const [takenIds, setTakenIds] = useState([]);
  const [showQR, setShowQR] = useState(false);
  const [hostPlayerId, setHostPlayerId] = useState(null);
  const [hostViewMode, setHostViewMode] = useState('host'); // 'host' | 'player'
  const hostPlaysEnabled = !!(gameMeta?.buszConfig?.hostPlays);
  const stRef = useRef(null);
  const autoStartRef = useRef(false);'''

assert OLD_BUSZ_GAME_STATE in html, 'BuszGame state not found'
html = html.replace(OLD_BUSZ_GAME_STATE, NEW_BUSZ_GAME_STATE, 1)

# ── 3. After game starts (buszState exists), show identity picker if needed ───
# Insert before "// ── Pyramid phase" block
OLD_PYRAMID_PHASE_COMMENT = '''  // ── Pyramid phase ────────────────────────────────────────────────────────
  if (buszState.phase === 'pyramid') {'''

NEW_PYRAMID_PHASE_COMMENT = '''  // ── Host identity picker (if hostPlays ON and not yet selected) ─────────────
  if (hostPlaysEnabled && !hostPlayerId) {
    return (
      <div style={{ flex:1, display:'flex', flexDirection:'column', padding:'20px 18px', gap:16, minHeight:0 }}>
        <div style={{ textAlign:'center', flexShrink:0 }}>
          <div style={{ fontSize:52 }}>🎮</div>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, marginTop:8 }}>Te ki vagy?</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:6 }}>Válaszd ki a neved — te is játszol</div>
        </div>
        <div style={{ display:'flex', flexDirection:'column', gap:8, overflowY:'auto', WebkitOverflowScrolling:'touch', flex:1, minHeight:0 }}>
          {players.map(p => (
            <button key={p.id} onClick={() => setHostPlayerId(p.id)} style={{ display:'flex', alignItems:'center', gap:12, padding:'14px 16px', background:T.surface, border:'2px solid transparent', borderRadius:16, cursor:'pointer', boxShadow:T.shadow, textAlign:'left', width:'100%' }}>
              <div style={{ width:42, height:42, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:18, color:'#fff', flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>
              <div style={{ flex:1, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, color:T.ink }}>{p.name}</div>
              <div style={{ width:10, height:10, borderRadius:'50%', background:p.color, opacity:0.5, flexShrink:0 }}/>
            </button>
          ))}
        </div>
      </div>
    );
  }

  // ── Host view mode toggle button (shown in both views) ────────────────────
  const hostViewToggle = hostPlaysEnabled && hostPlayerId ? (
    <button
      onClick={() => setHostViewMode(m => m === 'host' ? 'player' : 'host')}
      style={{ position:'fixed', bottom:90, right:14, zIndex:50, display:'flex', alignItems:'center', gap:6, padding:'9px 14px', borderRadius:999, border:'none', background: hostViewMode === 'player' ? T.coral : T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer', boxShadow:T.shadowLift }}
    >
      {hostViewMode === 'host' ? '👤 Játékos nézet' : '🎮 Host nézet'}
    </button>
  ) : null;

  // ── Player view mode: render BuszPlayerView ───────────────────────────────
  if (hostPlaysEnabled && hostPlayerId && hostViewMode === 'player' && buszState && isOnline) {
    const fakeRoom = { ...buszState, buszState, players, buszTakenIds: [hostPlayerId] };
    return (
      <div style={{ flex:1, display:'flex', flexDirection:'column', minHeight:0, position:'relative' }}>
        <BuszPlayerView room={{ buszState, players, buszTakenIds: [hostPlayerId] }} roomCode={roomCode} forcedPlayerId={hostPlayerId} />
        {hostViewToggle}
      </div>
    );
  }

  // ── Pyramid phase ────────────────────────────────────────────────────────
  if (buszState.phase === 'pyramid') {'''

assert OLD_PYRAMID_PHASE_COMMENT in html, 'pyramid phase comment not found'
html = html.replace(OLD_PYRAMID_PHASE_COMMENT, NEW_PYRAMID_PHASE_COMMENT, 1)

# ── 4. Add hostViewToggle to host pyramid view (sticky bottom area) ───────────
OLD_PYRAMID_BUTTONS = '''        {allDone ? (
          <PrimaryButton onClick={endPyramid} tone="coral" style={{ position:'sticky', bottom:12, zIndex:5 }}>🚌 Buszra szállás →</PrimaryButton>
        ) : (
          <PrimaryButton onClick={flipCard} style={{ position:'sticky', bottom:12, zIndex:5 }}>Következő lap →</PrimaryButton>
        )}
      </div>
    );
  }

  // ── Done phase ───────────────────────────────────────────────────────────'''

NEW_PYRAMID_BUTTONS = '''        {allDone ? (
          <PrimaryButton onClick={endPyramid} tone="coral" style={{ position:'sticky', bottom:12, zIndex:5 }}>🚌 Buszra szállás →</PrimaryButton>
        ) : (
          <PrimaryButton onClick={flipCard} style={{ position:'sticky', bottom:12, zIndex:5 }}>Következő lap →</PrimaryButton>
        )}
      </div>
      {hostViewToggle}
    );
  }

  // ── Done phase ───────────────────────────────────────────────────────────'''

assert OLD_PYRAMID_BUTTONS in html, 'pyramid buttons not found'
html = html.replace(OLD_PYRAMID_BUTTONS, NEW_PYRAMID_BUTTONS, 1)

# ── 5. Add hostViewToggle to host bus view ─────────────────────────────────────
OLD_BUS_RETURN_CLOSE = '''      </div>
    );
  }

  return null;
}


function RulettGame'''

NEW_BUS_RETURN_CLOSE = '''      {hostViewToggle}
      </div>
    );
  }

  return null;
}


function RulettGame'''

assert OLD_BUS_RETURN_CLOSE in html, 'bus return close not found'
html = html.replace(OLD_BUS_RETURN_CLOSE, NEW_BUS_RETURN_CLOSE, 1)

# ── 6. BuszPlayerView: support forcedPlayerId prop ────────────────────────────
OLD_BUSZ_PLAYER_VIEW_FUNC = '''function BuszPlayerView({ room, roomCode }) {
  const buszState = room.buszState;
  const players = room.players || [];

  const [playerId, setPlayerId] = useState(null);'''

NEW_BUSZ_PLAYER_VIEW_FUNC = '''function BuszPlayerView({ room, roomCode, forcedPlayerId }) {
  const buszState = room.buszState;
  const players = room.players || [];

  const [playerId, setPlayerId] = useState(forcedPlayerId || null);'''

assert OLD_BUSZ_PLAYER_VIEW_FUNC in html, 'BuszPlayerView func not found'
html = html.replace(OLD_BUSZ_PLAYER_VIEW_FUNC, NEW_BUSZ_PLAYER_VIEW_FUNC, 1)

# ── 7. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v7.51'"
NEW_VER = "const APP_VERSION = 'v7.52'"
assert OLD_VER in html, 'version not found'
html = html.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("done")
