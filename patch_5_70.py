with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add gameResult state to PlayScreen
OLD_STATE = "  const [csapatLosers, setCsapatLosers] = useState(new Set());\n  const transRef = React.useRef(false);\n  useEffect(() => { setCsapatLosers(new Set()); setPendingCommit(null); }, [gameIdx]);"
NEW_STATE = "  const [csapatLosers, setCsapatLosers] = useState(new Set());\n  const [gameResult, setGameResult] = useState(null); // { correct, playerName }\n  const transRef = React.useRef(false);\n  useEffect(() => { setCsapatLosers(new Set()); setPendingCommit(null); setGameResult(null); }, [gameIdx]);"
assert OLD_STATE in content, 'PlayScreen state block not found'
content = content.replace(OLD_STATE, NEW_STATE, 1)

# 2. Pass onResult to GameContent in PlayScreen
OLD_GC_CALL = "<GameContent key={currentGameId + gameIdx} gameId={currentGameId} gameIdx={gameIdx} players={players} onAdvance={advanceLoverseny} roomCode={roomCode} mode={mode} gameMeta={gameMeta} challenger={currentPlayer} opponent={selectedOpponent} />"
NEW_GC_CALL = "<GameContent key={currentGameId + gameIdx} gameId={currentGameId} gameIdx={gameIdx} players={players} onAdvance={advanceLoverseny} onResult={setGameResult} roomCode={roomCode} mode={mode} gameMeta={gameMeta} challenger={currentPlayer} opponent={selectedOpponent} />"
assert OLD_GC_CALL in content, 'GameContent call not found'
content = content.replace(OLD_GC_CALL, NEW_GC_CALL, 1)

# 3. Add ResultBanner just above footer
OLD_FOOTER = "      {/* footer */}\n      <div style={{ background:T.surface, boxShadow:'0 -6px 24px rgba(20,30,50,0.08)', padding:'12px 18px 22px', borderTopLeftRadius:24, borderTopRightRadius:24 }}>"
NEW_FOOTER = """      {/* ResultBanner */}
      {gameResult && (
        <div style={{ flexShrink:0, padding:'0 18px 8px', maxWidth:680, margin:'0 auto', width:'100%', boxSizing:'border-box' }}>
          <div style={{ borderRadius:16, padding:'12px 16px', display:'flex', alignItems:'center', gap:12, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)', background: gameResult.correct ? 'rgba(80,168,130,0.12)' : 'rgba(232,160,144,0.18)', border:`2px solid ${gameResult.correct ? '#50A882' : '#E8A090'}` }}>
            <div style={{ fontSize:26 }}>{gameResult.correct ? '🎉' : '🍺'}</div>
            <div>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color: gameResult.correct ? '#50A882' : '#C05050' }}>
                {gameResult.correct ? 'Helyes! Nem kell innod.' : 'Rossz tipp — inni kell!'}
              </div>
              {gameResult.playerName && !gameResult.correct && (
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:1 }}>{gameResult.playerName} iszik egyet</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* footer */}
      <div style={{ background:T.surface, boxShadow:'0 -6px 24px rgba(20,30,50,0.08)', padding:'12px 18px 22px', borderTopLeftRadius:24, borderTopRightRadius:24 }}>"""
assert OLD_FOOTER in content, 'Footer not found'
content = content.replace(OLD_FOOTER, NEW_FOOTER, 1)

# 4. Update GameContent to accept and pass onResult
OLD_GC_DEF = "function GameContent({ gameId, gameIdx, players, onAdvance, roomCode, mode, gameMeta, challenger, opponent }) {"
NEW_GC_DEF = "function GameContent({ gameId, gameIdx, players, onAdvance, onResult, roomCode, mode, gameMeta, challenger, opponent }) {"
assert OLD_GC_DEF in content, 'GameContent def not found'
content = content.replace(OLD_GC_DEF, NEW_GC_DEF, 1)

# 5. Pass onResult to IgazHamisGame
OLD_IH_CALL = "if (gameId === 'igazhamis') return <IgazHamisGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} />;"
NEW_IH_CALL = "if (gameId === 'igazhamis') return <IgazHamisGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;"
assert OLD_IH_CALL in content, 'IgazHamis GameContent call not found'
content = content.replace(OLD_IH_CALL, NEW_IH_CALL, 1)

# 6. Update IgazHamisGame: accept onResult, remove internal banner, call onResult
OLD_IH_SIG = "function IgazHamisGame({ gameIdx, challenger, onAdvance }) {"
NEW_IH_SIG = "function IgazHamisGame({ gameIdx, challenger, onAdvance, onResult }) {"
assert OLD_IH_SIG in content, 'IgazHamis signature not found'
content = content.replace(OLD_IH_SIG, NEW_IH_SIG, 1)

# 7. Update the useEffect that calls onAdvance to also call onResult
OLD_EFFECT = """  useEffect(() => {
    if (decided === null || advancedRef.current) return;
    advancedRef.current = true;
    const dm = {};
    if (!correct && challenger) dm[challenger.id] = 1;
    onAdvance && onAdvance(dm);
  }, [decided]);"""
NEW_EFFECT = """  useEffect(() => {
    if (decided === null || advancedRef.current) return;
    advancedRef.current = true;
    const dm = {};
    if (!correct && challenger) dm[challenger.id] = 1;
    onAdvance && onAdvance(dm);
    onResult && onResult({ correct, playerName: (!correct && challenger) ? challenger.name : null });
  }, [decided]);"""
assert OLD_EFFECT in content, 'IgazHamis useEffect not found'
content = content.replace(OLD_EFFECT, NEW_EFFECT, 1)

# 8. Remove the internal result banner from IgazHamisGame
OLD_BANNER = """
      {/* Result banner */}
      {decided && (
        <div style={{ width:'100%', borderRadius:16, padding:'14px 18px', display:'flex', alignItems:'center', gap:12, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)', background: correct ? 'rgba(80,168,130,0.12)' : 'rgba(232,160,144,0.18)', border:`2px solid ${correct ? '#50A882' : '#E8A090'}` }}>
          <div style={{ fontSize:28 }}>{correct ? '🎉' : '🍺'}</div>
          <div>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color: correct ? '#50A882' : '#C05050' }}>
              {correct ? 'Helyes! Nem kell innod.' : 'Rossz tipp — inni kell!'}
            </div>
            {challenger && !correct && (
              <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>{challenger.name} iszik egyet</div>
            )}
          </div>
        </div>
      )}"""
assert OLD_BANNER in content, 'Internal result banner not found'
content = content.replace(OLD_BANNER, '', 1)

# Version bump
assert 'Verzió 5.69' in content
content = content.replace('Verzió 5.69', 'Verzió 5.70', 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('OK — ResultBanner kiemelve PlayScreen szintjére, v5.70')
