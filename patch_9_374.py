#!/usr/bin/env python3
"""v9.374 — Menu add player: input always visible, profile button at end opens chip row"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_block = """                {/* Add player — single row: profile chips + expand button */}
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

new_block = """                {/* Add player — input always visible, profile button opens chip picker */}
                <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
                  {/* Row: input + optional add btn + profile toggle btn */}
                  <div style={{ display:'flex', gap:8, alignItems:'center' }}>
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
                    {menuAddName.trim() ? (
                      <button onClick={() => {
                        const newP = { id:Date.now().toString(), name:menuAddName.trim(), drinks:0, points:0, color:PLAYER_COLORS[players.length%PLAYER_COLORS.length] };
                        setPlayers(prev => { const next=[...prev,newP]; if (roomCode && typeof syncRoom==='function') syncRoom(roomCode,{players:next}); return next; });
                        setPendingCommit(null); setMenuAddName(''); setMenuTab('állás');
                      }} style={{ flexShrink:0, padding:'0 18px', height:46, borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>➕</button>
                    ) : menuProfiles.filter(pr => !players.some(p => p.profileId === pr.id)).length > 0 && (
                      <button onClick={() => setMenuAddOpen(o => !o)} style={{ flexShrink:0, width:46, height:46, borderRadius:14, border:'none', background:menuAddOpen ? T.mint : T.bgSoft, color: menuAddOpen ? '#fff' : T.ink, fontSize:20, display:'grid', placeItems:'center', cursor:'pointer' }}>👤</button>
                    )}
                  </div>
                  {/* Profile chip picker — slides open */}
                  {menuAddOpen && !menuAddName.trim() && (
                    <div style={{ display:'flex', gap:6, overflowX:'auto', WebkitOverflowScrolling:'touch', paddingBottom:2 }}>
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
                    </div>
                  )}
                </div>"""

assert old_block in html, "FAIL: add player block not found"
html = html.replace(old_block, new_block, 1)

html = html.replace("const APP_VERSION = 'v9.373';", "const APP_VERSION = 'v9.374';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.374 — Input always visible, 👤 profile btn at end opens chip row")
