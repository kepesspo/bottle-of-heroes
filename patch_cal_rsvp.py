import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = '''          {monthEvs.map(ev => {
            const col = EV_COLOR;
            const isMulti = ev.dateTo && new Date(ev.dateTo).toDateString()!==new Date(ev.date).toDateString();
            const dateLabel = isMulti
              ? `${new Date(ev.date).toLocaleDateString('hu-HU',{month:'short',day:'numeric'})} – ${new Date(ev.dateTo).toLocaleDateString('hu-HU',{month:'short',day:'numeric'})}`
              : `${new Date(ev.date).getDate()}. ${ev.allDay?'Egész nap':new Date(ev.date).toLocaleTimeString('hu-HU',{hour:'2-digit',minute:'2-digit'})}`;
            return (
              <div key={ev.id} onClick={() => setDetail(ev.id)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 12px', background:T.surface, borderRadius:12, marginBottom:6, boxShadow:T.shadow, cursor:'pointer' }}>
                <div style={{ width:4, alignSelf:'stretch', borderRadius:4, background:col, flexShrink:0 }} />
                <div style={{ width:34, height:34, borderRadius:8, background:col, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', lineHeight:1 }}>{new Date(ev.date).getDate()}</span>
                </div>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.title}</div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:1 }}>{dateLabel}{ev.location?' · '+ev.location.split(',')[0]:''}</div>
                </div>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={T.sub} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
              </div>
            );
          })}'''

NEW = '''          {monthEvs.map(ev => {
            const col = EV_COLOR;
            const isMulti = ev.dateTo && new Date(ev.dateTo).toDateString()!==new Date(ev.date).toDateString();
            const dateLabel = isMulti
              ? `${new Date(ev.date).toLocaleDateString('hu-HU',{month:'short',day:'numeric'})} – ${new Date(ev.dateTo).toLocaleDateString('hu-HU',{month:'short',day:'numeric'})}`
              : `${new Date(ev.date).getDate()}. ${ev.allDay?'Egész nap':new Date(ev.date).toLocaleTimeString('hu-HU',{hour:'2-digit',minute:'2-digit'})}`;
            const yesCount = ev.rsvp ? Object.values(ev.rsvp).filter(s=>s==='yes').length : 0;
            return (
              <div key={ev.id} onClick={() => setDetail(ev.id)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 12px', background:T.surface, borderRadius:12, marginBottom:6, boxShadow:T.shadow, cursor:'pointer' }}>
                <div style={{ width:4, alignSelf:'stretch', borderRadius:4, background:col, flexShrink:0 }} />
                <div style={{ width:34, height:34, borderRadius:8, background:col, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', lineHeight:1 }}>{new Date(ev.date).getDate()}</span>
                </div>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.title}</div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:1 }}>{dateLabel}{ev.location?' · '+ev.location.split(',')[0]:''}</div>
                  <div style={{ fontFamily:T.font, fontSize:11, marginTop:3 }}>
                    {yesCount > 0
                      ? <span style={{ color:'#25b572', fontWeight:700 }}>✓ {yesCount} jön</span>
                      : <span style={{ color:T.sub, fontStyle:'italic' }}>Még senki nem jelentkezett</span>}
                  </div>
                </div>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={T.sub} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
              </div>
            );
          })}'''

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

content = re.sub(r'v9\.689', 'v9.690', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.690")
