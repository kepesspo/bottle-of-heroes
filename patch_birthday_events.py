with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = """        return <div style={{ flex:1, overflowY:'auto', padding:'16px 16px 32px' }}>
        {shown.length === 0 && (
          <div style={{ textAlign:'center', padding:'64px 24px', color:T.sub, fontFamily:T.font, fontSize:15, lineHeight:1.6 }}>
            <div style={{ fontSize:48, marginBottom:14 }}>{evView === 'past' ? '🕰️' : '📋'}</div>
            {evView === 'past' ? 'Még nincs elmúlt esemény.' : 'Még nincsenek közelgő események.'}
          </div>
        )}
        {shown.map((ev) => {"""

NEW = """        const todayMD2 = new Date().toISOString().slice(5,10);
        const upcomingBdays = evView === 'list' ? profiles.filter(p => p.birthday).map(p => {
          const bd = p.birthday.slice(5,10);
          const thisYear = new Date().getFullYear();
          let next = new Date(thisYear + '-' + bd);
          if (next.toISOString().slice(5,10) < todayMD2) next = new Date((thisYear+1) + '-' + bd);
          const diff = Math.round((next - new Date(new Date().toDateString())) / 86400000);
          return { ...p, _bdDiff: diff, _bdMD: bd };
        }).filter(p => p._bdDiff <= 30).sort((a,b) => a._bdDiff - b._bdDiff) : [];
        return <div style={{ flex:1, overflowY:'auto', padding:'16px 16px 32px' }}>
        {upcomingBdays.length > 0 && (
          <div style={{ marginBottom:16 }}>
            <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.sub, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>🎂 Közelgő születésnapok</div>
            <div style={{ display:'flex', gap:10, overflowX:'auto', paddingBottom:4 }}>
              {upcomingBdays.map(p => (
                <div key={p.id} style={{ flexShrink:0, background:T.surface, borderRadius:16, padding:'12px 14px', boxShadow:T.shadow, display:'flex', flexDirection:'column', alignItems:'center', gap:6, minWidth:90 }}>
                  {p.img ? (
                    <div style={{ width:44, height:44, borderRadius:'50%', overflow:'hidden' }}><img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} /></div>
                  ) : (
                    <div style={{ width:44, height:44, borderRadius:'50%', background:p.color||'#888', display:'grid', placeItems:'center' }}>
                      <span style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff' }}>{(p.name||'?')[0].toUpperCase()}</span>
                    </div>
                  )}
                  <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.ink, textAlign:'center', maxWidth:80, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.nickname || p.name}</div>
                  <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color: p._bdDiff===0 ? '#e91e8c' : p._bdDiff===1 ? T.mint : T.sub, textAlign:'center' }}>
                    {p._bdDiff === 0 ? 'Ma! 🎂' : p._bdDiff === 1 ? 'Holnap 🎈' : p._bdDiff + ' nap'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {shown.length === 0 && (
          <div style={{ textAlign:'center', padding:'64px 24px', color:T.sub, fontFamily:T.font, fontSize:15, lineHeight:1.6 }}>
            <div style={{ fontSize:48, marginBottom:14 }}>{evView === 'past' ? '🕰️' : '📋'}</div>
            {evView === 'past' ? 'Még nincs elmúlt esemény.' : 'Még nincsenek közelgő események.'}
          </div>
        )}
        {shown.map((ev) => {"""

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

import re
content = re.sub(r'v9\.768', 'v9.769', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.769")
