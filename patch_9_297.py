#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Reakció eltávolítása a PlayerProfileStats-ból (player edit sheet alján)
old1 = """    { emoji:'⚡', label:'Legjobb reakció', value: stats.bestReactionTime != null ? `${stats.bestReactionTime}ms` : '—' },"""
new1 = """"""
assert old1 in html, "FAIL: reakció PlayerProfileStats"
html = html.replace(old1, new1, 1)

# ── 2. Reakció eltávolítása a PlayerCard mini statból (játékos lista)
old2 = """                        { emoji:'⚡', val: s.bestReactionTime != null ? s.bestReactionTime+'ms' : '—', label:'reakció' },"""
new2 = """"""
assert old2 in html, "FAIL: reakció PlayerCard"
html = html.replace(old2, new2, 1)

# ── 3. Menü VEZÉRLÉS: add player section — profil picker + névjegy hozzáadás
#    PlayScreen-ben load profiles és state
old3 = """  const [menuAddName, setMenuAddName] = useState('');"""
new3 = """  const [menuAddName, setMenuAddName] = useState('');
  const [menuProfiles, setMenuProfiles] = React.useState([]);
  React.useEffect(() => {
    if (typeof window.getProfiles === 'function') window.getProfiles().then(p => setMenuProfiles(p || []));
  }, []);"""
assert old3 in html, "FAIL: menuAddName state"
html = html.replace(old3, new3, 1)

# ── 4. Add player input section — add profile picker below input
old4 = """                {/* Add player */}
                <div style={{ display:'flex', gap:8 }}>
                  <input
                    value={menuAddName}
                    onChange={e => setMenuAddName(e.target.value)}
                    onKeyDown={e => {
                      if (e.key==='Enter' && menuAddName.trim()) {
                        const newP = { id:Date.now().toString(), name:menuAddName.trim(), drinks:0, points:0, color:PLAYER_COLORS[players.length%PLAYER_COLORS.length] };
                        setPlayers(prev=>[...prev,newP]); setPendingCommit(null); setMenuAddName('');
                      }
                    }}
                    placeholder="+ Játékos hozzáadása"
                    style={{ flex:1, padding:'13px 16px', border:'none', borderRadius:14, fontFamily:T.font, fontSize:14, color:T.ink, background:T.bgSoft, outline:'none' }}
                  />
                  {menuAddName.trim() && (
                    <button onClick={() => {
                      const newP = { id:Date.now().toString(), name:menuAddName.trim(), drinks:0, points:0, color:PLAYER_COLORS[players.length%PLAYER_COLORS.length] };
                      setPlayers(prev=>[...prev,newP]); setPendingCommit(null); setMenuAddName('');
                    }} style={{ padding:'0 18px', borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>➕</button>
                  )}
                </div>"""
new4 = """                {/* Add player */}
                <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
                  <div style={{ display:'flex', gap:8 }}>
                    <input
                      value={menuAddName}
                      onChange={e => setMenuAddName(e.target.value)}
                      onKeyDown={e => {
                        if (e.key==='Enter' && menuAddName.trim()) {
                          const newP = { id:Date.now().toString(), name:menuAddName.trim(), drinks:0, points:0, color:PLAYER_COLORS[players.length%PLAYER_COLORS.length] };
                          setPlayers(prev=>[...prev,newP]); setPendingCommit(null); setMenuAddName(''); setMenuTab('állás');
                        }
                      }}
                      placeholder="+ Név beírása"
                      style={{ flex:1, padding:'13px 16px', border:'none', borderRadius:14, fontFamily:T.font, fontSize:14, color:T.ink, background:T.bgSoft, outline:'none' }}
                    />
                    {menuAddName.trim() && (
                      <button onClick={() => {
                        const newP = { id:Date.now().toString(), name:menuAddName.trim(), drinks:0, points:0, color:PLAYER_COLORS[players.length%PLAYER_COLORS.length] };
                        setPlayers(prev=>[...prev,newP]); setPendingCommit(null); setMenuAddName(''); setMenuTab('állás');
                      }} style={{ padding:'0 18px', borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>➕</button>
                    )}
                  </div>
                  {/* Profil picker */}
                  {menuProfiles.filter(pr => !players.some(p => p.profileId === pr.id)).length > 0 && (
                    <div style={{ display:'flex', gap:6, overflowX:'auto', WebkitOverflowScrolling:'touch', paddingBottom:2 }}>
                      {menuProfiles.filter(pr => !players.some(p => p.profileId === pr.id)).map(pr => (
                        <button key={pr.id} onClick={() => {
                          const newP = { id:Date.now().toString(), name:pr.name, drinks:0, points:0, color:pr.color||PLAYER_COLORS[players.length%PLAYER_COLORS.length], profileId:pr.id, img:pr.img||null };
                          setPlayers(prev=>[...prev,newP]); setPendingCommit(null); setMenuTab('állás');
                        }} style={{ display:'flex', alignItems:'center', gap:6, padding:'6px 10px', borderRadius:10, border:'none', background:T.bgSoft, cursor:'pointer', flexShrink:0 }}>
                          <div style={{ width:24, height:24, borderRadius:'50%', background:pr.color||T.mint, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>
                            {pr.img ? <img src={pr.img} style={{ width:24, height:24, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff' }}>{(pr.name||'?').charAt(0).toUpperCase()}</span>}
                          </div>
                          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.ink, whiteSpace:'nowrap' }}>{pr.name}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>"""
assert old4 in html, "FAIL: add player section"
html = html.replace(old4, new4, 1)

html = html.replace("const APP_VERSION = 'v9.296';", "const APP_VERSION = 'v9.297';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.297 — reakció ki, menü profil picker + állás tab switch hozzáadáskor")
