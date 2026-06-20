#!/usr/bin/env python3
"""v9.373 — Menu Add Player: collapse to 1 row (profile chips + '+' expand button)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_add_player = """                {/* Add player */}
                <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
                  <div style={{ display:'flex', gap:8 }}>
                    <input
                      value={menuAddName}
                      onChange={e => setMenuAddName(e.target.value)}
                      onKeyDown={e => {
                        if (e.key==='Enter' && menuAddName.trim()) {
                          const newP = { id:Date.now().toString(), name:menuAddName.trim(), drinks:0, points:0, color:PLAYER_COLORS[players.length%PLAYER_COLORS.length] };
                          setPlayers(prev => { const next=[...prev,newP]; if (roomCode && typeof syncRoom==='function') syncRoom(roomCode,{players:next}); return next; });
                          setPendingCommit(null); setMenuAddName(''); setMenuTab('állás');
                        }
                      }}
                      placeholder="+ Név beírása"
                      style={{ flex:1, padding:'13px 16px', border:'none', borderRadius:14, fontFamily:T.font, fontSize:14, color:T.ink, background:T.bgSoft, outline:'none' }}
                    />
                    {menuAddName.trim() && (
                      <button onClick={() => {
                        const newP = { id:Date.now().toString(), name:menuAddName.trim(), drinks:0, points:0, color:PLAYER_COLORS[players.length%PLAYER_COLORS.length] };
                        setPlayers(prev => { const next=[...prev,newP]; if (roomCode && typeof syncRoom==='function') syncRoom(roomCode,{players:next}); return next; });
                        setPendingCommit(null); setMenuAddName(''); setMenuTab('állás');
                      }} style={{ padding:'0 18px', borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>➕</button>
                    )}
                  </div>
                  {/* Profil picker */}
                  {menuProfiles.filter(pr => !players.some(p => p.profileId === pr.id)).length > 0 && (
                    <div style={{ display:'flex', gap:6, overflowX:'auto', WebkitOverflowScrolling:'touch', paddingBottom:2 }}>
                      {menuProfiles.filter(pr => !players.some(p => p.profileId === pr.id)).map(pr => (
                        <button key={pr.id} onClick={() => {
                          const newP = { id:Date.now().toString(), name:pr.nickname||pr.name, drinks:0, points:0, color:pr.color||PLAYER_COLORS[players.length%PLAYER_COLORS.length], profileId:pr.id, img:pr.img||null };
                          setPlayers(prev => {
                            const next = [...prev, newP];
                            if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: next });
                            return next;
                          });
                          setPendingCommit(null); setMenuTab('állás');
                        }} style={{ display:'flex', alignItems:'center', gap:6, padding:'6px 10px', borderRadius:10, border:'none', background:T.bgSoft, cursor:'pointer', flexShrink:0 }}>
                          <div style={{ width:24, height:24, borderRadius:'50%', background:pr.color||T.mint, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>
                            {pr.img ? <img src={pr.img} style={{ width:24, height:24, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>{(pr.name||'?').charAt(0).toUpperCase()}</span>}
                          </div>
                          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.ink, whiteSpace:'nowrap' }}>{pr.name}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>"""

new_add_player = """                {/* Add player — single row: profile chips + expand button */}
                <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
                  <div style={{ display:'flex', alignItems:'center', gap:6, overflowX:'auto', WebkitOverflowScrolling:'touch' }}>
                    {menuProfiles.filter(pr => !players.some(p => p.profileId === pr.id)).map(pr => (
                      <button key={pr.id} onClick={() => {
                        const newP = { id:Date.now().toString(), name:pr.nickname||pr.name, drinks:0, points:0, color:pr.color||PLAYER_COLORS[players.length%PLAYER_COLORS.length], profileId:pr.id, img:pr.img||null };
                        setPlayers(prev => { const next=[...prev,newP]; if (roomCode && typeof syncRoom==='function') syncRoom(roomCode,{players:next}); return next; });
                        setPendingCommit(null); setMenuTab('állás');
                      }} style={{ display:'flex', alignItems:'center', gap:6, padding:'7px 12px 7px 7px', borderRadius:20, border:'none', background:T.bgSoft, cursor:'pointer', flexShrink:0 }}>
                        <div style={{ width:26, height:26, borderRadius:'50%', background:pr.color||T.mint, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>
                          {pr.img ? <img src={pr.img} style={{ width:26, height:26, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>{(pr.name||'?').charAt(0).toUpperCase()}</span>}
                        </div>
                        <span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink, whiteSpace:'nowrap' }}>{pr.name}</span>
                      </button>
                    ))}
                    {/* Expand button — always at end */}
                    <button onClick={() => setMenuAddOpen(o => !o)} style={{ flexShrink:0, width:36, height:36, borderRadius:'50%', border:'none', background:T.mint, color:'#fff', fontSize:20, display:'grid', placeItems:'center', cursor:'pointer', marginLeft:'auto' }}>＋</button>
                  </div>
                  {/* Expanded: text input */}
                  {menuAddOpen && (
                    <div style={{ display:'flex', gap:8 }}>
                      <input
                        autoFocus
                        value={menuAddName}
                        onChange={e => setMenuAddName(e.target.value)}
                        onKeyDown={e => {
                          if (e.key==='Enter' && menuAddName.trim()) {
                            const newP = { id:Date.now().toString(), name:menuAddName.trim(), drinks:0, points:0, color:PLAYER_COLORS[players.length%PLAYER_COLORS.length] };
                            setPlayers(prev => { const next=[...prev,newP]; if (roomCode && typeof syncRoom==='function') syncRoom(roomCode,{players:next}); return next; });
                            setPendingCommit(null); setMenuAddName(''); setMenuAddOpen(false); setMenuTab('állás');
                          }
                        }}
                        placeholder="+ Név beírása"
                        style={{ flex:1, padding:'13px 16px', border:'none', borderRadius:14, fontFamily:T.font, fontSize:14, color:T.ink, background:T.bgSoft, outline:'none' }}
                      />
                      {menuAddName.trim() && (
                        <button onClick={() => {
                          const newP = { id:Date.now().toString(), name:menuAddName.trim(), drinks:0, points:0, color:PLAYER_COLORS[players.length%PLAYER_COLORS.length] };
                          setPlayers(prev => { const next=[...prev,newP]; if (roomCode && typeof syncRoom==='function') syncRoom(roomCode,{players:next}); return next; });
                          setPendingCommit(null); setMenuAddName(''); setMenuAddOpen(false); setMenuTab('állás');
                        }} style={{ padding:'0 18px', borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>➕</button>
                      )}
                    </div>
                  )}
                </div>"""

assert old_add_player in html, "FAIL: add player section not found"
html = html.replace(old_add_player, new_add_player, 1)

# Add menuAddOpen state after menuAddName state
old_state = "  const [menuAddName, setMenuAddName] = useState('');"
new_state = "  const [menuAddName, setMenuAddName] = useState('');\n  const [menuAddOpen, setMenuAddOpen] = React.useState(false);"

assert old_state in html, "FAIL: menuAddName state not found"
html = html.replace(old_state, new_state, 1)

# Version bump
html = html.replace("const APP_VERSION = 'v9.372';", "const APP_VERSION = 'v9.373';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.373 — Menu add player collapsed to 1 row with expand button")
