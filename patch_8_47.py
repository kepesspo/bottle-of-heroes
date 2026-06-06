#!/usr/bin/env python3
"""v8.47: Beer Pong visszavágó — on/off switch, SE finals only"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. BeerPongConfigSheet: add visszavago toggle before close button ─────────
OLD_CLOSE_BTN = """        <button onClick={onClose} style={{ width:'100%', padding:'15px', borderRadius:16, background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:'0 5px 16px -5px rgba(79,194,160,0.6)', marginTop:16 }}>Kész</button>"""

NEW_CLOSE_BTN = """        {/* Visszavágó toggle — only for SE or grp→SE finals */}
        {(!tournament.startsWith('grp_') ? tournament === 'se' : tournament.endsWith('_se')) && (
          <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'13px 0', borderTop:'1px solid rgba(26,42,74,0.10)' }}>
            <div>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>Visszavágó</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>Egyenes kiesésnél a vesztes kérhet visszavágót (1x/meccs)</div>
            </div>
            <div onClick={() => setConfig(c => ({...c, visszavago: !(c.visszavago ?? false)}))}
              style={{ width:48, height:28, borderRadius:14, background:(config.visszavago??false)?T.mint:T.surfaceMuted, cursor:'pointer', position:'relative', transition:'background .2s', flexShrink:0 }}>
              <div style={{ position:'absolute', top:3, left:(config.visszavago??false)?22:3, width:22, height:22, borderRadius:'50%', background:'#fff', boxShadow:'0 1px 4px rgba(0,0,0,0.2)', transition:'left .2s' }} />
            </div>
          </div>
        )}

        <button onClick={onClose} style={{ width:'100%', padding:'15px', borderRadius:16, background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:'0 5px 16px -5px rgba(79,194,160,0.6)', marginTop:16 }}>Kész</button>"""

assert OLD_CLOSE_BTN in content, "close button not found"
content = content.replace(OLD_CLOSE_BTN, NEW_CLOSE_BTN, 1)
print("✓ BeerPongConfigSheet: visszavágó toggle added")

# ── 2. BeerpongGame: read visszavago config ───────────────────────────────────
OLD_CFG_READ = """  const MAX_CUPS = bpCfg.maxCups ?? 10;"""
NEW_CFG_READ = """  const MAX_CUPS = bpCfg.maxCups ?? 10;
  const VISSZAVAGO   = !!(bpCfg.visszavago);"""

assert OLD_CFG_READ in content, "MAX_CUPS line not found"
content = content.replace(OLD_CFG_READ, NEW_CFG_READ, 1)
print("✓ VISSZAVAGO config read")

# ── 3. Add visszavagoOffer state ──────────────────────────────────────────────
OLD_CHAMPION_STATE = """  const [champion, setChampion] = React.useState(null);"""
NEW_CHAMPION_STATE = """  const [champion, setChampion] = React.useState(null);
  const [visszavagoOffer, setVissszavagoOffer] = React.useState(null);
  const visszavagoUsedRef = React.useRef(new Set());"""

assert OLD_CHAMPION_STATE in content, "champion state not found"
content = content.replace(OLD_CHAMPION_STATE, NEW_CHAMPION_STATE, 1)
print("✓ visszavagoOffer state added")

# ── 4. isSEFinals computed var ────────────────────────────────────────────────
OLD_TOTAL_SE = """  const totalSERounds = seRounds.length > 1"""
NEW_TOTAL_SE = """  const isSEFinals = VISSZAVAGO && (
    TOURNAMENT === 'se' ||
    (TOURNAMENT.startsWith('grp_') && tsPhase === 'finals' && finalsType === 'se')
  );
  const totalSERounds = seRounds.length > 1"""

assert OLD_TOTAL_SE in content, "totalSERounds not found"
content = content.replace(OLD_TOTAL_SE, NEW_TOTAL_SE, 1)
print("✓ isSEFinals computed")

# ── 5. Modify confirm button: intercept for visszavágó ────────────────────────
OLD_CONFIRM_BTN = """        {/* Confirm button */}
        <button onClick={confirmHandler} disabled={!canConfirm} style={{ width:'100%', marginTop:16, minHeight:52, border:'none', borderRadius:16, cursor: canConfirm ? 'pointer' : 'default', fontFamily:T.font, fontWeight:800, fontSize:16, color:'#fff', background: !canConfirm ? 'rgba(0,0,0,0.07)' : winnerP ? T.mint : T.inkSoft, boxShadow: canConfirm && winnerP ? '0 4px 0 ' + T.mintDeep : 'none', transition:'background .2s', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
          {!canConfirm ? <span style={{ color:T.inkMute }}>Állítsd be az eredményt</span>
            : cups1 === cups2 ? '🤝 Döntetlen megerősítése'
            : <><span>🏆</span><span>{winnerP?.name} nyert — tovább</span></>
          }
        </button>"""

NEW_CONFIRM_BTN = """        {/* Visszavágó offer overlay */}
        {visszavagoOffer && (
          <div style={{ marginTop:16, background:'rgba(14,14,24,0.05)', borderRadius:16, padding:'16px', display:'flex', flexDirection:'column', gap:10 }}>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink, textAlign:'center' }}>⚔️ Visszavágó?</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}><b>{visszavagoOffer.loser?.name}</b> kérhet visszavágót!</div>
            <div style={{ display:'flex', gap:8 }}>
              <button onClick={() => {
                visszavagoUsedRef.current.add(visszavagoOffer.matchKey);
                setVissszavagoOffer(null);
                setCups1(MAX_CUPS); setCups2(MAX_CUPS); resetTimer();
              }} style={{ flex:1, padding:'13px', borderRadius:14, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:14, background:T.coral, color:'#fff', boxShadow:'0 4px 12px rgba(240,100,80,0.35)' }}>
                🔄 Visszavágó!
              </button>
              <button onClick={() => { setVissszavagoOffer(null); confirmHandler && confirmHandler(); }} style={{ flex:1, padding:'13px', borderRadius:14, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:14, background:T.mint, color:'#fff', boxShadow:'0 4px 12px rgba(79,194,160,0.35)' }}>
                Nem, tovább →
              </button>
            </div>
          </div>
        )}

        {/* Confirm button */}
        {!visszavagoOffer && (
          <button onClick={() => {
            if (!canConfirm) return;
            const matchKey = seCurRound + '_' + seCurMatch;
            const loserP = cups1 < cups2 ? currentMatch?.p2 : currentMatch?.p1;
            if (isSEFinals && loserP && !visszavagoUsedRef.current.has(matchKey)) {
              setVissszavagoOffer({ loser: loserP, winner: winnerP, matchKey });
              return;
            }
            confirmHandler && confirmHandler();
          }} disabled={!canConfirm} style={{ width:'100%', marginTop:16, minHeight:52, border:'none', borderRadius:16, cursor: canConfirm ? 'pointer' : 'default', fontFamily:T.font, fontWeight:800, fontSize:16, color:'#fff', background: !canConfirm ? 'rgba(0,0,0,0.07)' : winnerP ? T.mint : T.inkSoft, boxShadow: canConfirm && winnerP ? '0 4px 0 ' + T.mintDeep : 'none', transition:'background .2s', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
            {!canConfirm ? <span style={{ color:T.inkMute }}>Állítsd be az eredményt</span>
              : cups1 === cups2 ? '🤝 Döntetlen megerősítése'
              : <><span>🏆</span><span>{winnerP?.name} nyert — tovább</span></>
            }
          </button>
        )}"""

assert OLD_CONFIRM_BTN in content, "confirm button not found"
content = content.replace(OLD_CONFIRM_BTN, NEW_CONFIRM_BTN, 1)
print("✓ Confirm button: visszavágó intercept added")

# ── 6. Reset visszavagoOffer when match changes ───────────────────────────────
OLD_RESHUFFLE = """  const handleReshuffle = () => {"""
NEW_RESHUFFLE = """  React.useEffect(() => { setVissszavagoOffer(null); }, [seCurRound, seCurMatch]);

  const handleReshuffle = () => {"""

assert OLD_RESHUFFLE in content, "handleReshuffle not found"
content = content.replace(OLD_RESHUFFLE, NEW_RESHUFFLE, 1)
print("✓ visszavagoOffer reset on match change")

# ── 7. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.46';"
NEW_VER = "const APP_VERSION = 'v8.47';"
assert OLD_VER in content, "version not found"
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.47 saved")
