with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove 'db' tab from AdminScreen TABS array
OLD1 = """  const TABS = [['profiles','Profilok'],['events','Események'],['db','Adatbázis'],['games','Játékok'],['rooms','Szobák'],['message','Hirdetmény'],['settings','Beállítások']];"""
NEW1 = """  const TABS = [['profiles','Profilok'],['events','Események'],['games','Játékok'],['rooms','Szobák'],['message','Hirdetmény'],['settings','Beállítások']];"""
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Remove AdminDatabase render line
OLD2 = """        {tab === 'events'   && <AdminEvents go={go} />}
        {tab === 'db'       && <AdminDatabase />}
        {tab === 'games'    && <AdminGames />}"""
NEW2 = """        {tab === 'events'   && <AdminEvents go={go} />}
        {tab === 'games'    && <AdminGames />}"""
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. Add stats state + load + functions to AdminProfiles (after eventsRsvp state)
OLD3 = """  const [eventsRsvp, setEventsRsvp] = React.useState(evLoad());

  React.useEffect(() => {
    const col = evDb();
    if (!col) return;
    const unsub = col.onSnapshot(snap => { setEventsRsvp(snap.docs.map(d=>({id:d.id,...d.data()}))); });
    return () => unsub();
  }, []);

  function load() {"""
NEW3 = """  const [eventsRsvp, setEventsRsvp] = React.useState(evLoad());
  const [allStats, setAllStats] = React.useState({});
  const [editingStats, setEditingStats] = React.useState(null);
  const [editVals, setEditVals] = React.useState({});
  const [savingStats, setSavingStats] = React.useState(false);
  const [savedStats, setSavedStats] = React.useState(null);

  const STAT_FIELDS = [
    { key:'totalDrinks', label:'Ital', type:'number' },
    { key:'gamesPlayed', label:'Meccs', type:'number' },
    { key:'wins', label:'Győzelem', type:'number' },
    { key:'totalPoints', label:'Pont', type:'number' },
  ];

  React.useEffect(() => {
    const col = evDb();
    if (!col) return;
    const unsub = col.onSnapshot(snap => { setEventsRsvp(snap.docs.map(d=>({id:d.id,...d.data()}))); });
    return () => unsub();
  }, []);

  React.useEffect(() => {
    if (typeof window.getAllStats === 'function') window.getAllStats().then(s => setAllStats(s || {}));
  }, []);

  function startEditStats(p) {
    const st = allStats[p.id] || {};
    const vals = {};
    STAT_FIELDS.forEach(f => { vals[f.key] = st[f.key] !== undefined ? String(st[f.key]) : '0'; });
    setEditVals(vals);
    setEditingStats(editingStats === p.id ? null : p.id);
  }

  function saveStats() {
    if (savingStats) return;
    setSavingStats(true);
    const updates = {};
    STAT_FIELDS.forEach(f => { updates[f.key] = Number(editVals[f.key]) || 0; });
    window.updateStats(editingStats, updates).then(() => {
      setAllStats(prev => ({ ...prev, [editingStats]: { ...(prev[editingStats]||{}), ...updates } }));
      setSavingStats(false); setSavedStats(editingStats); setEditingStats(null);
      setTimeout(() => setSavedStats(null), 2000);
    }).catch(() => setSavingStats(false));
  }

  function load() {"""
assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# 4. Replace the entire profile card rendering with stats-enabled version
OLD4 = """      ) : profiles.map(p => (
        <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:14, padding:'12px 14px', marginBottom:8, boxShadow:T.shadow }}>
          {p.img ? (
            <div style={{ width:38, height:38, borderRadius:10, overflow:'hidden', flexShrink:0 }}>
              <img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
            </div>
          ) : (
            <div style={{ width:12, height:12, borderRadius:'50%', background:p.color||'#888', flexShrink:0 }} />
          )}
          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
            {p.nickname && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>{p.nickname}</div>}
            {(()=>{ const cnt=eventsRsvp.filter(e=>(e.rsvp||{})[p.name]==='yes').length; return cnt>0?<div style={{fontFamily:T.font,fontSize:11,color:T.mint,fontWeight:700,marginTop:2}}>✓ {cnt} eseményre jelentkezett</div>:null; })()}
          </div>
          <button onClick={() => toggleHideProfile(p.id)} style={{ width:36, height:36, borderRadius:10, border:`1.5px solid ${hiddenProfs.includes(p.id) ? '#ef4444' : T.mint}`, background: hiddenProfs.includes(p.id) ? '#fef2f2' : 'rgba(37,181,114,0.08)', display:'grid', placeItems:'center', cursor:'pointer' }}>
            {hiddenProfs.includes(p.id) ? (
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            ) : (
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={T.mint} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            )}
          </button>
          <button onClick={() => deleteProfile(p.id)} disabled={deleting===p.id} style={{ width:36, height:36, borderRadius:10, border:'none', background:'#fef2f2', display:'grid', placeItems:'center', cursor:'pointer', opacity:deleting===p.id?0.5:1 }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
          </button>
        </div>
      ))}"""

NEW4 = """      ) : profiles.map(p => {
        const st = allStats[p.id] || {};
        const isEd = editingStats === p.id;
        const rsvpCnt = eventsRsvp.filter(e=>(e.rsvp||{})[p.name]==='yes').length;
        return (
          <div key={p.id} style={{ background:T.surface, borderRadius:14, marginBottom:8, boxShadow:T.shadow, overflow:'hidden' }}>
            {/* Main row */}
            <div style={{ display:'flex', alignItems:'center', gap:10, padding:'12px 14px' }}>
              {p.img ? (
                <div style={{ width:38, height:38, borderRadius:10, overflow:'hidden', flexShrink:0 }}>
                  <img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
                </div>
              ) : (
                <div style={{ width:38, height:38, borderRadius:10, background:p.color||'#888', display:'grid', placeItems:'center', flexShrink:0 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff' }}>{(p.name||'?')[0].toUpperCase()}</span>
                </div>
              )}
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
                {p.nickname && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>{p.nickname}</div>}
                <div style={{ display:'flex', gap:10, marginTop:2, flexWrap:'wrap' }}>
                  {rsvpCnt>0 && <span style={{fontFamily:T.font,fontSize:11,color:T.mint,fontWeight:700}}>✓ {rsvpCnt} esemény</span>}
                  {(st.totalDrinks||st.gamesPlayed||st.wins) ? <span style={{fontFamily:T.font,fontSize:11,color:T.sub}}>{st.totalDrinks||0} ital · {st.gamesPlayed||0} meccs · {st.wins||0} győz</span> : null}
                </div>
              </div>
              {savedStats === p.id && <span style={{ fontSize:18 }}>✅</span>}
              <button onClick={() => startEditStats(p)} style={{ width:34, height:34, borderRadius:9, border:'none', background: isEd ? T.mint+'22' : T.border, display:'grid', placeItems:'center', cursor:'pointer' }} title="Statisztika szerkesztése">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke={isEd ? T.mint : T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
              </button>
              <button onClick={() => toggleHideProfile(p.id)} style={{ width:34, height:34, borderRadius:9, border:`1.5px solid ${hiddenProfs.includes(p.id) ? '#ef4444' : T.mint}`, background: hiddenProfs.includes(p.id) ? '#fef2f2' : 'rgba(37,181,114,0.08)', display:'grid', placeItems:'center', cursor:'pointer' }}>
                {hiddenProfs.includes(p.id) ? (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                ) : (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.mint} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                )}
              </button>
              <button onClick={() => deleteProfile(p.id)} disabled={deleting===p.id} style={{ width:34, height:34, borderRadius:9, border:'none', background:'#fef2f2', display:'grid', placeItems:'center', cursor:'pointer', opacity:deleting===p.id?0.5:1 }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
              </button>
            </div>
            {/* Inline stats editor */}
            {isEd && (
              <div style={{ padding:'0 14px 14px', borderTop:`1px solid ${T.border}` }}>
                <div style={{ fontFamily:T.font, fontSize:10, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', margin:'10px 0 8px' }}>Statisztika szerkesztése</div>
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginBottom:10 }}>
                  {STAT_FIELDS.map(f => (
                    <div key={f.key}>
                      <div style={{ fontFamily:T.font, fontSize:10, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:4 }}>{f.label}</div>
                      <input type="number" value={editVals[f.key]||'0'} onChange={e => setEditVals(prev => ({...prev,[f.key]:e.target.value}))}
                        style={{ width:'100%', boxSizing:'border-box', padding:'9px 10px', borderRadius:10, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />
                    </div>
                  ))}
                </div>
                <div style={{ display:'flex', gap:8 }}>
                  <button onClick={() => setEditingStats(null)} style={{ flex:1, padding:'10px', borderRadius:11, border:`1.5px solid ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:700, fontSize:13, color:T.sub, cursor:'pointer' }}>Mégsem</button>
                  <button onClick={saveStats} disabled={savingStats} style={{ flex:2, padding:'10px', borderRadius:11, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer', opacity:savingStats?0.6:1 }}>{savingStats?'Mentés…':'Mentés'}</button>
                </div>
              </div>
            )}
          </div>
        );
      })}"""

assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

import re
content = re.sub(r'v9\.763', 'v9.764', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.764")
