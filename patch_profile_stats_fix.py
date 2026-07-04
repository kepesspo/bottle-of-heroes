with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix STAT_FIELDS — correct field names + add missing fields
OLD1 = """  const STAT_FIELDS = [
    { key:'totalDrinks', label:'Ital', type:'number' },
    { key:'gamesPlayed', label:'Meccs', type:'number' },
    { key:'wins', label:'Győzelem', type:'number' },
    { key:'totalPoints', label:'Pont', type:'number' },
  ];"""

NEW1 = """  const STAT_FIELDS = [
    { key:'totalDrinks',  label:'Összes korty',  type:'number' },
    { key:'totalPoints',  label:'Összesített pont', type:'number' },
    { key:'totalSessions',label:'Játszott meccs', type:'number' },
    { key:'totalWins',    label:'Győzelem',       type:'number' },
    { key:'totalRounds',  label:'Körök',          type:'number' },
    { key:'bestStreak',   label:'Legjobb streak', type:'number' },
  ];"""

assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Replace profile card: whole row clickable + bigger/cleaner stat summary
OLD2 = """            {/* Main row */}
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
            </div>"""

NEW2 = """            {/* Main row — clicking opens stats */}
            <div onClick={() => startEditStats(p)} style={{ display:'flex', alignItems:'center', gap:10, padding:'12px 14px', cursor:'pointer', WebkitTapHighlightColor:'transparent' }}>
              {p.img ? (
                <div style={{ width:42, height:42, borderRadius:10, overflow:'hidden', flexShrink:0 }}>
                  <img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
                </div>
              ) : (
                <div style={{ width:42, height:42, borderRadius:10, background:p.color||'#888', display:'grid', placeItems:'center', flexShrink:0 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff' }}>{(p.name||'?')[0].toUpperCase()}</span>
                </div>
              )}
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
                {p.nickname && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>{p.nickname}</div>}
                <div style={{ display:'flex', gap:8, marginTop:2, flexWrap:'wrap' }}>
                  {rsvpCnt>0 && <span style={{fontFamily:T.font,fontSize:11,color:T.mint,fontWeight:700}}>✓ {rsvpCnt} esemény</span>}
                  {(st.totalDrinks!=null||st.totalSessions!=null) ? <span style={{fontFamily:T.font,fontSize:11,color:T.sub}}>🍺 {st.totalDrinks||0} · ⭐ {st.totalPoints||0} · 🏆 {st.totalSessions>0?Math.round((st.totalWins||0)/st.totalSessions*100)+'%':'—'}</span> : null}
                </div>
              </div>
              {savedStats === p.id ? <span style={{ fontSize:18, flexShrink:0 }}>✅</span> : (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.sub} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink:0, transform: isEd ? 'rotate(180deg)' : 'none', transition:'transform .2s' }}><polyline points="6 9 12 15 18 9"/></svg>
              )}
              <div onClick={e => { e.stopPropagation(); toggleHideProfile(p.id); }} style={{ width:34, height:34, borderRadius:9, border:`1.5px solid ${hiddenProfs.includes(p.id) ? '#ef4444' : T.mint}`, background: hiddenProfs.includes(p.id) ? '#fef2f2' : 'rgba(37,181,114,0.08)', display:'grid', placeItems:'center', cursor:'pointer', flexShrink:0 }}>
                {hiddenProfs.includes(p.id) ? (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                ) : (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.mint} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                )}
              </div>
              <div onClick={e => { e.stopPropagation(); deleteProfile(p.id); }} style={{ width:34, height:34, borderRadius:9, border:'none', background:'#fef2f2', display:'grid', placeItems:'center', cursor:'pointer', opacity:deleting===p.id?0.5:1, flexShrink:0 }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
              </div>
            </div>"""

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

import re
content = re.sub(r'v9\.764', 'v9.765', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.765")
