import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Switch: remove icons ──
OLD1 = '''          {[['list','☰','Lista'],['calendar','📅','Naptár']].map(([key,icon,label]) => (
            <button key={key} onClick={() => setEvView(key)} style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', gap:7, padding:'13px 0', borderRadius:14, border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer', background: evView===key ? T.mint : 'transparent', color: evView===key ? '#fff' : T.sub, transition:'all .2s', WebkitTapHighlightColor:'transparent' }}>
              <span style={{ fontSize:16 }}>{icon}</span>{label}
            </button>
          ))}'''

NEW1 = '''          {[['list','Lista'],['calendar','Naptár']].map(([key,label]) => (
            <button key={key} onClick={() => setEvView(key)} style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', padding:'13px 0', borderRadius:14, border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer', background: evView===key ? T.mint : 'transparent', color: evView===key ? '#fff' : T.sub, transition:'all .2s', WebkitTapHighlightColor:'transparent' }}>
              {label}
            </button>
          ))}'''

assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# ── 2. Card: compact + fix multi-day time + "0 nap" instead of "Ma!" ──
OLD2 = '''          return (
            <div key={ev.id} onClick={() => setDetail(ev.id)} style={{ background:T.surface, borderRadius:20, marginBottom:12, boxShadow:T.shadow, cursor:'pointer', WebkitTapHighlightColor:'transparent', overflow:'hidden' }}>
              {/* Top row */}
              <div style={{ display:'flex', alignItems:'center', gap:14, padding:'16px 16px 12px' }}>
                {/* Date badge */}
                <div style={{ width:52, height:52, borderRadius:14, background:'#E8631A', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
                  {d ? (
                    <>
                      <span style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff', lineHeight:1 }}>{d.getDate()}</span>
                      <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10, color:'rgba(255,255,255,0.85)', textTransform:'uppercase' }}>{d.toLocaleDateString('hu-HU',{month:'short'})}</span>
                    </>
                  ) : (
                    <span style={{ fontSize:24 }}>📅</span>
                  )}
                </div>
                {/* Title + meta */}
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, lineHeight:1.2, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.title}</div>
                  <div style={{ display:'flex', gap:8, marginTop:4, flexWrap:'wrap', alignItems:'center' }}>
                    {timeStr && <span style={{ fontFamily:T.font, fontSize:13, color:T.sub, display:'flex', alignItems:'center', gap:3 }}>🕐 {timeStr}{ev.dateTo ? (() => { const te=new Date(ev.dateTo); return '–'+te.toLocaleTimeString('hu-HU',{hour:'2-digit',minute:'2-digit'}); })() : ''}</span>}
                    {ev.location
                      ? <span style={{ fontFamily:T.font, fontSize:13, color:T.sub, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>📍 {ev.location.split(',')[0]}</span>
                      : <span style={{ fontFamily:T.font, fontSize:13, color:T.sub, fontStyle:'italic' }}>📍 Még nem tudjuk</span>}
                  </div>
                </div>
                {/* Right column: days only */}
                {daysLabel && (
                  <div style={{ background: daysLeft === 0 ? '#E8631A' : daysLeft <= 3 ? '#c07a10' : '#25b572', borderRadius:14, padding:'8px 14px', textAlign:'center', flexShrink:0, minWidth:62, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
                    {daysLeft === 0 ? (
                      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:32, color:'#fff', lineHeight:1 }}>Ma!</div>
                    ) : daysLeft === 1 ? (
                      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:19, color:'#fff', lineHeight:1 }}>Holnap</div>
                    ) : (
                      <React.Fragment>
                        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:32, color:'#fff', lineHeight:1 }}>{daysLeft}</div>
                        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:'rgba(255,255,255,0.85)', lineHeight:1, marginTop:3 }}>nap</div>
                      </React.Fragment>
                    )}
                  </div>
                )}
              </div>'''

NEW2 = '''          const isMultiDay = ev.dateTo && (() => { const s=new Date(ev.date); const e=new Date(ev.dateTo); s.setHours(0,0,0,0); e.setHours(0,0,0,0); return e>s; })();
          const metaLine = isMultiDay
            ? (() => { const s=new Date(ev.date); const e=new Date(ev.dateTo); return s.toLocaleDateString('hu-HU',{month:'short',day:'numeric'})+' – '+e.toLocaleDateString('hu-HU',{month:'short',day:'numeric'}); })()
            : ev.allDay ? 'Egész nap' : timeStr || '';
          return (
            <div key={ev.id} onClick={() => setDetail(ev.id)} style={{ background:T.surface, borderRadius:16, marginBottom:8, boxShadow:T.shadow, cursor:'pointer', WebkitTapHighlightColor:'transparent', overflow:'hidden' }}>
              {/* Top row */}
              <div style={{ display:'flex', alignItems:'center', gap:12, padding:'12px 12px 10px' }}>
                {/* Date badge */}
                <div style={{ width:44, height:44, borderRadius:12, background:'#E8631A', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
                  {d ? (
                    <>
                      <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', lineHeight:1 }}>{d.getDate()}</span>
                      <span style={{ fontFamily:T.font, fontWeight:700, fontSize:9, color:'rgba(255,255,255,0.85)', textTransform:'uppercase' }}>{d.toLocaleDateString('hu-HU',{month:'short'})}</span>
                    </>
                  ) : (
                    <span style={{ fontSize:20 }}>📅</span>
                  )}
                </div>
                {/* Title + meta */}
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink, lineHeight:1.2, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.title}</div>
                  <div style={{ display:'flex', gap:6, marginTop:3, flexWrap:'wrap', alignItems:'center' }}>
                    {metaLine && <span style={{ fontFamily:T.font, fontSize:12, color:T.sub, display:'flex', alignItems:'center', gap:2 }}>🕐 {metaLine}</span>}
                    {ev.location
                      ? <span style={{ fontFamily:T.font, fontSize:12, color:T.sub, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>📍 {ev.location.split(',')[0]}</span>
                      : <span style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontStyle:'italic' }}>📍 Még nem tudjuk</span>}
                  </div>
                </div>
                {/* Right column: days badge */}
                {daysLeft !== null && daysLeft >= 0 && (
                  <div style={{ background: daysLeft === 0 ? '#E8631A' : daysLeft <= 3 ? '#c07a10' : '#25b572', borderRadius:12, padding:'6px 10px', textAlign:'center', flexShrink:0, minWidth:54, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:28, color:'#fff', lineHeight:1 }}>{daysLeft}</div>
                    <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:'rgba(255,255,255,0.85)', lineHeight:1, marginTop:2 }}>nap</div>
                  </div>
                )}
              </div>'''

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# ── 3. Calendar: all events orange (remove SPAN_COLORS rotation) ──
OLD3 = "  const SPAN_COLORS = ['#E8631A','#25b572','#5b7cf6','#c07a10','#d63884'];\n  // assign stable color index per event id\n  const colorMap = {};\n  let ci = 0;\n  monthEvs.forEach(ev => { if(colorMap[ev.id]===undefined) colorMap[ev.id]=ci++; });"
NEW3 = "  const EV_COLOR = '#E8631A';\n  const colorMap = {};\n  monthEvs.forEach(ev => { colorMap[ev.id] = 0; });"
assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

OLD4 = "                  const col = SPAN_COLORS[colorMap[ev.id] % SPAN_COLORS.length];"
NEW4 = "                  const col = EV_COLOR;"
assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

OLD5 = "            const col = SPAN_COLORS[colorMap[ev.id] % SPAN_COLORS.length];"
NEW5 = "            const col = EV_COLOR;"
assert OLD5 in content, "OLD5 not found"
content = content.replace(OLD5, NEW5, 1)

# fix daysLabel — remove the old text-based label, keep numeric
OLD6 = "          const daysLabel = daysLeft === null ? null : daysLeft < 0 ? null : daysLeft === 0 ? 'Ma!' : daysLeft === 1 ? 'Holnap' : `${daysLeft} nap`;"
NEW6 = "          const daysLabel = daysLeft === null ? null : daysLeft < 0 ? null : `${daysLeft} nap`;"
assert OLD6 in content, "OLD6 not found"
content = content.replace(OLD6, NEW6, 1)

# version bump
content = re.sub(r'v9\.687', 'v9.688', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.688")
