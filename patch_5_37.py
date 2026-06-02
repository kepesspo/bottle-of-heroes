# -*- coding: utf-8 -*-
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. pendingCommit state ─────────────────────────────────────────────────
old1 = "  const [showMenu, setShowMenu] = useState(false);"
new1 = (
    "  const [showMenu, setShowMenu] = useState(false);\n"
    "  const [pendingCommit, setPendingCommit] = useState(null);"
)
assert old1 in html, "Fix 1 not found"
html = html.replace(old1, new1, 1)

# ── 2. gameIdx useEffect: reset pendingCommit + auto-select Páros opponent ──
old2 = "  useEffect(() => { setCsapatLosers(new Set()); }, [gameIdx]);"
new2 = (
    "  useEffect(() => { setCsapatLosers(new Set()); setPendingCommit(null); }, [gameIdx]);\n"
    "\n"
    "  useEffect(() => {\n"
    "    if (currentGame.category !== 'Páros') { setSelectedOpponent(null); return; }\n"
    "    const others = players.filter((_,i) => i !== turn);\n"
    "    if (others.length === 0) return;\n"
    "    setSelectedOpponent(others[Math.floor(Math.random() * others.length)]);\n"
    "  }, [turn, gameIdx]);"
)
assert old2 in html, "Fix 2 not found"
html = html.replace(old2, new2, 1)

# ── 3. Add commitPending function after commitRound ────────────────────────
old3 = (
    "  // Egyéni: current player wins or loses\n"
    "  const advance = success => {"
)
new3 = (
    "  const commitPending = () => {\n"
    "    if (!pendingCommit || transitioning) return;\n"
    "    const {newPlayers, fb, newTurn, newGameIdx, newRound} = pendingCommit;\n"
    "    setPendingCommit(null);\n"
    "    commitRound(newPlayers, fb, newTurn, newGameIdx, newRound);\n"
    "  };\n"
    "\n"
    "  // Egyéni: current player wins or loses\n"
    "  const advance = success => {"
)
assert old3 in html, "Fix 3 not found"
html = html.replace(old3, new3, 1)

# ── 4. advance → setPendingCommit ─────────────────────────────────────────
old4 = "    commitRound(newPlayers, success?'win':'lose', (turn+1)%players.length, gameIdx+1, round+1);\n  };\n\n  // Csapat"
new4 = "    setPendingCommit({ newPlayers, fb:success?'win':'lose', newTurn:(turn+1)%players.length, newGameIdx:gameIdx+1, newRound:round+1 });\n  };\n\n  // Csapat"
assert old4 in html, "Fix 4 not found"
html = html.replace(old4, new4, 1)

# ── 5. advancePaired → setPendingCommit ───────────────────────────────────
old5 = (
    "    setSelectedOpponent(null);\n"
    "    commitRound(newPlayers, currentPlayerWon?'win':'lose', (turn+1)%players.length, gameIdx+1, round+1);\n"
    "  };"
)
new5 = (
    "    setSelectedOpponent(null);\n"
    "    setPendingCommit({ newPlayers, fb:currentPlayerWon?'win':'lose', newTurn:(turn+1)%players.length, newGameIdx:gameIdx+1, newRound:round+1 });\n"
    "  };"
)
assert old5 in html, "Fix 5 not found"
html = html.replace(old5, new5, 1)

# ── 6. advanceLoverseny → setPendingCommit ────────────────────────────────
old6 = "    commitRound(newPlayers, null, (turn+1)%players.length, gameIdx+1, round+1);\n  };"
new6 = "    setPendingCommit({ newPlayers, fb:null, newTurn:(turn+1)%players.length, newGameIdx:gameIdx+1, newRound:round+1 });\n  };"
assert old6 in html, "Fix 6 not found"
html = html.replace(old6, new6, 1)

# ── 7. Remove Páros picker (auto-select handles it now) ───────────────────
old7 = (
    "      {currentGame.category === 'Páros' && !selectedOpponent && (\n"
    "        <div style={{ padding:'0 18px 14px', display:'flex', flexDirection:'column', gap:10, alignItems:'center' }}>\n"
    "          <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em' }}>Válassz ellenfelet</div>\n"
    "          <div style={{ display:'flex', gap:8, overflowX:'auto', WebkitOverflowScrolling:'touch', paddingBottom:4, width:'100%' }}>\n"
    "            {players.filter((_,i) => i!==turn).map(p => (\n"
    "              <button key={p.id} onClick={() => !transitioning && setSelectedOpponent(p)} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:4, padding:'8px 12px', border:'none', background:T.surface, borderRadius:14, boxShadow:T.shadow, cursor:'pointer', flexShrink:0 }}>\n"
    "                <div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</div>\n"
    "                <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:11, color:T.ink, maxWidth:60, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>\n"
    "              </button>\n"
    "            ))}\n"
    "          </div>\n"
    "        </div>\n"
    "      )}"
)
new7 = ""
assert old7 in html, "Fix 7 not found"
html = html.replace(old7, new7, 1)

# ── 8. Páros VS display → just CTA buttons ────────────────────────────────
old8 = (
    "      {currentGame.category === 'Páros' && selectedOpponent && (\n"
    "        <div style={{ padding:'0 18px 0' }}>\n"
    "          <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:18, padding:'0 0 10px' }}>\n"
    "            <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>\n"
    "              <div style={{ width:46, height:46, borderRadius:'50%', background:currentPlayer.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:18, color:'#fff' }}>{currentPlayer.name.charAt(0).toUpperCase()}</div>\n"
    "              <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:11, color:T.ink, maxWidth:64, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', textAlign:'center' }}>{currentPlayer.name}</div>\n"
    "            </div>\n"
    "            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:T.inkSoft }}>VS</div>\n"
    "            <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>\n"
    "              <div style={{ width:46, height:46, borderRadius:'50%', background:selectedOpponent.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:18, color:'#fff' }}>{selectedOpponent.name.charAt(0).toUpperCase()}</div>\n"
    "              <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:11, color:T.ink, maxWidth:64, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', textAlign:'center' }}>{selectedOpponent.name}</div>\n"
    "            </div>\n"
    "          </div>\n"
    "          {scenario.cta.length > 0 && (\n"
    "          <div className='play-actions'>\n"
    "            <button onClick={() => advancePaired(false)} disabled={transitioning} style={{ flex:1, minHeight:60, border:'none', background:T.coral, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:17, borderRadius:16, cursor:'pointer', boxShadow:T.shadow }}>Vesztettem \U0001f614</button>\n"
    "            <button onClick={() => advancePaired(true)} disabled={transitioning} style={{ flex:1, minHeight:60, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:17, borderRadius:16, cursor:'pointer', boxShadow:T.shadow }}>Nyertem! \U0001f389</button>\n"
    "          </div>\n"
    "          )}\n"
    "        </div>\n"
    "      )}"
)
new8 = (
    "      {currentGame.category === 'Páros' && selectedOpponent && scenario.cta.length > 0 && (\n"
    "        <div className='play-actions' style={{ padding:'0 18px 0' }}>\n"
    "          <button onClick={() => advancePaired(false)} disabled={transitioning} style={{ flex:1, minHeight:60, border:'none', background:T.coral, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:17, borderRadius:16, cursor:'pointer', boxShadow:T.shadow }}>Vesztettem \U0001f614</button>\n"
    "          <button onClick={() => advancePaired(true)} disabled={transitioning} style={{ flex:1, minHeight:60, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:17, borderRadius:16, cursor:'pointer', boxShadow:T.shadow }}>Nyertem! \U0001f389</button>\n"
    "        </div>\n"
    "      )}"
)
assert old8 in html, "Fix 8 not found"
html = html.replace(old8, new8, 1)

# ── 9. Csapat "következő" buttons → set pendingCommit-friendly text ────────
old9a = (
    "          {csapatLosers.size > 0 ? (\n"
    "            <button onClick={() => { if(transitioning) return; const dm={}; csapatLosers.forEach(pid=>{dm[pid]=1;}); setCsapatLosers(new Set()); advanceLoverseny(dm); }} style={{ width:'100%', padding:'14px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow, animation:'popIn .2s' }}>\n"
    "              {csapatLosers.size===1 ? `${players.find(p=>csapatLosers.has(p.id))?.name} iszik — következő játék →` : `${csapatLosers.size} ember iszik — következő játék →`}\n"
    "            </button>\n"
    "          ) : (\n"
    "            <button onClick={() => { if(transitioning) return; advanceLoverseny({}); }} style={{ width:'100%', padding:'14px', background:'rgba(255,255,255,0.6)', color:T.inkSoft, fontFamily:T.font, fontWeight:600, fontSize:15, borderRadius:16, border:`2px solid rgba(0,0,0,0.1)`, cursor:'pointer' }}>\n"
    "              Senki nem rontott — következő játék →\n"
    "            </button>"
)
new9a = (
    "          {csapatLosers.size > 0 ? (\n"
    "            <button onClick={() => { if(transitioning) return; const dm={}; csapatLosers.forEach(pid=>{dm[pid]=1;}); setCsapatLosers(new Set()); advanceLoverseny(dm); }} style={{ width:'100%', padding:'14px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow, animation:'popIn .2s' }}>\n"
    "              {csapatLosers.size===1 ? `${players.find(p=>csapatLosers.has(p.id))?.name} iszik ✔` : `${csapatLosers.size} ember iszik ✔`}\n"
    "            </button>\n"
    "          ) : (\n"
    "            <button onClick={() => { if(transitioning) return; advanceLoverseny({}); }} style={{ width:'100%', padding:'14px', background:'rgba(255,255,255,0.6)', color:T.inkSoft, fontFamily:T.font, fontWeight:600, fontSize:15, borderRadius:16, border:`2px solid rgba(0,0,0,0.1)`, cursor:'pointer' }}>\n"
    "              Senki nem rontott ✔\n"
    "            </button>"
)
assert old9a in html, "Fix 9a not found"
html = html.replace(old9a, new9a, 1)

# ── 10. Footer: rounded top corners + player pill variants + next game btn ──
old10 = (
    "      {/* footer */}\n"
    "      <div style={{ background:T.surface, boxShadow:'0 -4px 18px rgba(20,30,50,0.05)', padding:'12px 18px 22px' }}>\n"
    "      <div className=\"play-footer-inner\">\n"
    "        {currentGame.category === 'Csapat' ? (\n"
    "          <div style={{ flex:1, display:'flex', alignItems:'center', gap:10, background:'rgba(0,0,0,0.04)', borderRadius:18, padding:'10px 14px' }}>\n"
    "            <div style={{ width:40, height:40, borderRadius:'50%', background:T.surfaceMuted, display:'grid', placeItems:'center', fontSize:20, flexShrink:0 }}>\U0001f465</div>\n"
    "            <div style={{ flex:1, minWidth:0 }}>\n"
    "              <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, letterSpacing:'0.06em', textTransform:'uppercase', lineHeight:1 }}>MOST ŐK JÖNNEK</div>\n"
    "              <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, color:T.ink }}>Csapat</div>\n"
    "            </div>\n"
    "          </div>\n"
    "        ) : (\n"
    "          <div key={currentPlayer.id} style={{\n"
    "            flex:1, display:'flex', alignItems:'center', gap:10,\n"
    "            background:`${currentPlayer.color}18`, borderRadius:18, padding:'10px 14px',\n"
    "            border:`1.5px solid ${currentPlayer.color}35`,\n"
    "            animation:'popIn .35s cubic-bezier(.2,.9,.3,1.4)',\n"
    "          }}>\n"
    "            <div style={{\n"
    "              width:40, height:40, borderRadius:'50%', background:currentPlayer.color,\n"
    "              display:'grid', placeItems:'center',\n"
    "              fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:'#fff',\n"
    "              boxShadow: scorePulse ? `0 0 0 5px ${currentPlayer.color}44` : `0 0 0 3px ${currentPlayer.color}30`,\n"
    "              transition:'box-shadow .3s', flexShrink:0,\n"
    "            }}>{currentPlayer.name.charAt(0).toUpperCase()||'?'}</div>\n"
    "            <div style={{ flex:1, minWidth:0 }}>\n"
    "              <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:`${currentPlayer.color}cc`, letterSpacing:'0.06em', textTransform:'uppercase', lineHeight:1 }}>MOST Ő JÖN</div>\n"
    "              <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{currentPlayer.name}</div>\n"
    "            </div>\n"
    "          </div>\n"
    "        )}\n"
    "        <button onClick={() => setShowMenu(true)} style={{ width:48, height:48, borderRadius:'50%', border:`2px solid ${T.inkMute}40`, background:'transparent', cursor:'pointer', display:'grid', placeItems:'center', color:T.inkSoft, padding:0, flexShrink:0 }}>{Icon.menu(T.inkSoft)}</button>\n"
    "      </div>\n"
    "\n"
    "      </div>"
)
new10 = (
    "      {/* footer */}\n"
    "      <div style={{ background:T.surface, boxShadow:'0 -6px 24px rgba(20,30,50,0.08)', padding:'12px 18px 22px', borderTopLeftRadius:24, borderTopRightRadius:24 }}>\n"
    "      <div className=\"play-footer-inner\">\n"
    "        {/* Player pill */}\n"
    "        {currentGame.category === 'Csapat' ? (() => {\n"
    "          const vis = players.slice(0,4);\n"
    "          const extra = players.length - vis.length;\n"
    "          const aw = 36 + (vis.length - 1 + (extra>0?1:0)) * 20;\n"
    "          return (\n"
    "            <div style={{ flex:1, display:'flex', alignItems:'center', gap:10, background:'rgba(0,0,0,0.04)', borderRadius:18, padding:'10px 14px' }}>\n"
    "              <div style={{ position:'relative', width:aw, height:40, flexShrink:0 }}>\n"
    "                {vis.map((p,i) => (\n"
    "                  <div key={p.id} style={{ position:'absolute', left:i*20, top:2, width:36, height:36, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', color:'#fff', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:13, border:`2.5px solid ${T.surface}`, zIndex:i }}>{p.name.charAt(0).toUpperCase()}</div>\n"
    "                ))}\n"
    "                {extra > 0 && <div style={{ position:'absolute', left:vis.length*20, top:2, width:36, height:36, borderRadius:'50%', background:`${T.inkMute}40`, display:'grid', placeItems:'center', color:T.inkSoft, fontSize:10, fontWeight:700, border:`2.5px solid ${T.surface}`, zIndex:vis.length }}>+{extra}</div>}\n"
    "              </div>\n"
    "              <div style={{ flex:1, minWidth:0 }}>\n"
    "                <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, letterSpacing:'0.06em', textTransform:'uppercase', lineHeight:1 }}>MOST ŐK JÖNNEK</div>\n"
    "                <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, color:T.ink }}>Csapat</div>\n"
    "              </div>\n"
    "            </div>\n"
    "          );\n"
    "        })() : currentGame.category === 'Páros' && selectedOpponent ? (\n"
    "          <div key={currentPlayer.id + (selectedOpponent?.id||'')} style={{ flex:1, display:'flex', alignItems:'center', gap:7, background:`${currentPlayer.color}14`, borderRadius:18, padding:'8px 12px', border:`1.5px solid ${currentPlayer.color}30`, animation:'popIn .35s cubic-bezier(.2,.9,.3,1.4)', overflow:'hidden' }}>\n"
    "            <div style={{ width:38, height:38, borderRadius:'50%', background:currentPlayer.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, color:'#fff', boxShadow:`0 0 0 3px ${T.coral}55`, flexShrink:0 }}>{currentPlayer.name.charAt(0).toUpperCase()}</div>\n"
    "            <div style={{ color:T.inkSoft, fontSize:14, flexShrink:0 }}>→</div>\n"
    "            <div style={{ width:38, height:38, borderRadius:'50%', background:selectedOpponent.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, color:'#fff', opacity:0.65, flexShrink:0 }}>{selectedOpponent.name.charAt(0).toUpperCase()}</div>\n"
    "            <div style={{ flex:1, minWidth:0 }}>\n"
    "              <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.coral, letterSpacing:'0.06em', textTransform:'uppercase', lineHeight:1 }}>KIHÍVÁS</div>\n"
    "              <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{currentPlayer.name} → {selectedOpponent.name}</div>\n"
    "            </div>\n"
    "          </div>\n"
    "        ) : (\n"
    "          <div key={currentPlayer.id} style={{ flex:1, display:'flex', alignItems:'center', gap:10, background:`${currentPlayer.color}18`, borderRadius:18, padding:'10px 14px', border:`1.5px solid ${currentPlayer.color}35`, animation:'popIn .35s cubic-bezier(.2,.9,.3,1.4)' }}>\n"
    "            <div style={{ width:40, height:40, borderRadius:'50%', background:currentPlayer.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:'#fff', boxShadow: scorePulse ? `0 0 0 5px ${currentPlayer.color}44` : `0 0 0 3px ${currentPlayer.color}30`, transition:'box-shadow .3s', flexShrink:0 }}>{currentPlayer.name.charAt(0).toUpperCase()||'?'}</div>\n"
    "            <div style={{ flex:1, minWidth:0 }}>\n"
    "              <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:`${currentPlayer.color}cc`, letterSpacing:'0.06em', textTransform:'uppercase', lineHeight:1 }}>MOST Ő JÖN</div>\n"
    "              <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{currentPlayer.name}</div>\n"
    "            </div>\n"
    "          </div>\n"
    "        )}\n"
    "        {/* Menu btn */}\n"
    "        <button onClick={() => setShowMenu(true)} style={{ width:48, height:48, borderRadius:'50%', border:`2px solid ${T.inkMute}40`, background:'transparent', cursor:'pointer', display:'grid', placeItems:'center', color:T.inkSoft, padding:0, flexShrink:0 }}>{Icon.menu(T.inkSoft)}</button>\n"
    "        {/* Next game btn */}\n"
    "        {(() => {\n"
    "          const nextGameId = games[(gameIdx + 1) % games.length];\n"
    "          const nextGame = GAMES.find(g => g.id === nextGameId) || GAMES[0];\n"
    "          const active = !!pendingCommit && !transitioning;\n"
    "          return (\n"
    "            <button onClick={commitPending} disabled={!active} style={{\n"
    "              height:56, padding:'0 14px', borderRadius:18, border:'none',\n"
    "              cursor: active ? 'pointer' : 'default',\n"
    "              background: active ? T.mint : `${T.inkMute}18`,\n"
    "              display:'flex', alignItems:'center', justifyContent:'center', gap:6,\n"
    "              flexShrink:0, transition:'background .25s, box-shadow .25s, opacity .25s',\n"
    "              boxShadow: active ? T.shadow : 'none', opacity: active ? 1 : 0.45,\n"
    "            }}>\n"
    "              <div style={{ width:34, height:34, borderRadius:11, background: active ? 'rgba(255,255,255,0.22)' : `${nextGame.color}22`, display:'grid', placeItems:'center', padding:5, overflow:'hidden', flexShrink:0 }}>\n"
    "                <GameImg g={nextGame} size=\"full\" />\n"
    "              </div>\n"
    "              <span style={{ color: active ? '#fff' : T.inkSoft, fontSize:18, lineHeight:1 }}>→</span>\n"
    "            </button>\n"
    "          );\n"
    "        })()}\n"
    "      </div>\n"
    "\n"
    "      </div>"
)
assert old10 in html, "Fix 10 not found"
html = html.replace(old10, new10, 1)

# ── 11. Version bump ──────────────────────────────────────────────────────
assert 'Verzió 5.36 · DNR · 2026.06.01 10:30' in html, "Version not found"
html = html.replace(
    'Verzió 5.36 · DNR · 2026.06.01 10:30',
    'Verzió 5.37 · DNR · 2026.06.01 11:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done — v5.37")
