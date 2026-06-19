#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. PlayerProfileStats: remove currentStreak, keep bestStreak
old1 = """    { emoji:'🔥', label:'Jelenlegi streak', value: stats.currentStreak ? `${stats.currentStreak}×` : '—' },
    { emoji:'🏅', label:'Legjobb streak', value: stats.bestStreak ? `${stats.bestStreak}×` : '—' },"""
new1 = """    { emoji:'🏅', label:'Legjobb streak', value: stats.bestStreak ? `${stats.bestStreak}×` : '—' },"""
assert old1 in html, "FAIL: PlayerProfileStats streak"
html = html.replace(old1, new1, 1)

# ── 2. StatsScreen profil kártyán: streak mini stat — remove currentStreak
old2 = """                        { emoji:'🔥', val: s.currentStreak ? s.currentStreak+'×' : '—', label:'streak' },"""
new2 = """                        { emoji:'🏅', val: s.bestStreak ? s.bestStreak+'×' : '—', label:'best streak' },"""
assert old2 in html, "FAIL: StatsScreen streak"
html = html.replace(old2, new2, 1)

# ── 3. Profil picker: nickname megjelenítés + Firestore sync hozzáadáskor
old3 = """                      {menuProfiles.filter(pr => !players.some(p => p.profileId === pr.id)).map(pr => (
                        <button key={pr.id} onClick={() => {
                          const newP = { id:Date.now().toString(), name:pr.name, drinks:0, points:0, color:pr.color||PLAYER_COLORS[players.length%PLAYER_COLORS.length], profileId:pr.id, img:pr.img||null };
                          setPlayers(prev=>[...prev,newP]); setPendingCommit(null); setMenuTab('állás');
                        }} style={{ display:'flex', alignItems:'center', gap:6, padding:'6px 10px', borderRadius:10, border:'none', background:T.bgSoft, cursor:'pointer', flexShrink:0 }}>
                          <div style={{ width:24, height:24, borderRadius:'50%', background:pr.color||T.mint, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>
                            {pr.img ? <img src={pr.img} style={{ width:24, height:24, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff' }}>{(pr.name||'?').charAt(0).toUpperCase()}</span>}
                          </div>
                          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.ink, whiteSpace:'nowrap' }}>{pr.name}</span>
                        </button>
                      ))}"""
new3 = """                      {menuProfiles.filter(pr => !players.some(p => p.profileId === pr.id)).map(pr => (
                        <button key={pr.id} onClick={() => {
                          const newP = { id:Date.now().toString(), name:pr.name, drinks:0, points:0, color:pr.color||PLAYER_COLORS[players.length%PLAYER_COLORS.length], profileId:pr.id, img:pr.img||null };
                          setPlayers(prev => {
                            const next = [...prev, newP];
                            if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: next });
                            return next;
                          });
                          setPendingCommit(null); setMenuTab('állás');
                        }} style={{ display:'flex', alignItems:'center', gap:6, padding:'6px 10px', borderRadius:10, border:'none', background:T.bgSoft, cursor:'pointer', flexShrink:0 }}>
                          <div style={{ width:24, height:24, borderRadius:'50%', background:pr.color||T.mint, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>
                            {pr.img ? <img src={pr.img} style={{ width:24, height:24, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff' }}>{(pr.name||'?').charAt(0).toUpperCase()}</span>}
                          </div>
                          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.ink, whiteSpace:'nowrap' }}>{pr.nickname || pr.name}</span>
                        </button>
                      ))}"""
assert old3 in html, "FAIL: profil picker"
html = html.replace(old3, new3, 1)

# ── 4. Név beírása + hozzáadás — Firestore sync
old4 = """                      if (e.key==='Enter' && menuAddName.trim()) {
                          const newP = { id:Date.now().toString(), name:menuAddName.trim(), drinks:0, points:0, color:PLAYER_COLORS[players.length%PLAYER_COLORS.length] };
                          setPlayers(prev=>[...prev,newP]); setPendingCommit(null); setMenuAddName(''); setMenuTab('állás');
                        }"""
new4 = """                      if (e.key==='Enter' && menuAddName.trim()) {
                          const newP = { id:Date.now().toString(), name:menuAddName.trim(), drinks:0, points:0, color:PLAYER_COLORS[players.length%PLAYER_COLORS.length] };
                          setPlayers(prev => { const next=[...prev,newP]; if (roomCode && typeof syncRoom==='function') syncRoom(roomCode,{players:next}); return next; });
                          setPendingCommit(null); setMenuAddName(''); setMenuTab('állás');
                        }"""
assert old4 in html, "FAIL: Enter add"
html = html.replace(old4, new4, 1)

old5 = """                      const newP = { id:Date.now().toString(), name:menuAddName.trim(), drinks:0, points:0, color:PLAYER_COLORS[players.length%PLAYER_COLORS.length] };
                        setPlayers(prev=>[...prev,newP]); setPendingCommit(null); setMenuAddName(''); setMenuTab('állás');"""
new5 = """                      const newP = { id:Date.now().toString(), name:menuAddName.trim(), drinks:0, points:0, color:PLAYER_COLORS[players.length%PLAYER_COLORS.length] };
                        setPlayers(prev => { const next=[...prev,newP]; if (roomCode && typeof syncRoom==='function') syncRoom(roomCode,{players:next}); return next; });
                        setPendingCommit(null); setMenuAddName(''); setMenuTab('állás');"""
assert old5 in html, "FAIL: button add"
html = html.replace(old5, new5, 1)

html = html.replace("const APP_VERSION = 'v9.297';", "const APP_VERSION = 'v9.298';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.298 — currentStreak ki, profil picker becenév, Firestore sync hozzáadáskor")
