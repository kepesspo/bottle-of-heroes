with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Lista nézet — kártya: cancelled esetén piros keret + áthúzott cím + ELMARAD badge
OLD1 = """            <div key={ev.id} onClick={() => setDetail(ev.id)} style={{ background:T.surface, borderRadius:16, marginBottom:8, boxShadow:T.shadow, cursor:'pointer', WebkitTapHighlightColor:'transparent', overflow:'hidden' }}>
              {/* Top row */}
              <div style={{ display:'flex', alignItems:'center', gap:12, padding:'12px 12px 10px' }}>
                {/* Date badge */}
                <div style={{ width:44, height:44, borderRadius:12, background:'#E8631A', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', flexShrink:0 }}>"""

NEW1 = """            <div key={ev.id} onClick={() => setDetail(ev.id)} style={{ background: ev.cancelled ? '#fef2f2' : T.surface, borderRadius:16, marginBottom:8, boxShadow:T.shadow, cursor:'pointer', WebkitTapHighlightColor:'transparent', overflow:'hidden', border: ev.cancelled ? '1.5px solid #ef4444' : '1.5px solid transparent' }}>
              {ev.cancelled && <div style={{ background:'#ef4444', padding:'4px 14px', fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', letterSpacing:'0.08em', textAlign:'center' }}>ELMARAD</div>}
              {/* Top row */}
              <div style={{ display:'flex', alignItems:'center', gap:12, padding:'12px 12px 10px' }}>
                {/* Date badge */}
                <div style={{ width:44, height:44, borderRadius:12, background: ev.cancelled ? '#ef4444' : '#E8631A', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', flexShrink:0 }}>"""

assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Lista nézet — cím áthúzva ha cancelled
OLD2 = """                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink, lineHeight:1.2, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.title}</div>"""

NEW2 = """                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color: ev.cancelled ? '#ef4444' : T.ink, lineHeight:1.2, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', textDecoration: ev.cancelled ? 'line-through' : 'none' }}>{ev.title}</div>"""

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. Naptár havi lista — cancelled jelzés
OLD3 = """              <div key={ev.id} onClick={() => setDetail(ev.id)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 12px', background:T.surface, borderRadius:12, marginBottom:6, boxShadow:T.shadow, cursor:'pointer' }}>
                <div style={{ width:4, alignSelf:'stretch', borderRadius:4, background:col, flexShrink:0 }} />
                <div style={{ width:34, height:34, borderRadius:8, background:col, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', lineHeight:1 }}>{new Date(ev.date).getDate()}</span>
                </div>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.title}</div>"""

NEW3 = """              <div key={ev.id} onClick={() => setDetail(ev.id)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 12px', background: ev.cancelled ? '#fef2f2' : T.surface, borderRadius:12, marginBottom:6, boxShadow:T.shadow, cursor:'pointer', border: ev.cancelled ? '1.5px solid #ef4444' : '1.5px solid transparent' }}>
                <div style={{ width:4, alignSelf:'stretch', borderRadius:4, background: ev.cancelled ? '#ef4444' : col, flexShrink:0 }} />
                <div style={{ width:34, height:34, borderRadius:8, background: ev.cancelled ? '#ef4444' : col, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', lineHeight:1 }}>{ev.cancelled ? '✕' : new Date(ev.date).getDate()}</span>
                </div>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ display:'flex', alignItems:'center', gap:6 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color: ev.cancelled ? '#ef4444' : T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', textDecoration: ev.cancelled ? 'line-through' : 'none', flex:1, minWidth:0 }}>{ev.title}</div>
                    {ev.cancelled && <div style={{ fontFamily:T.font, fontWeight:900, fontSize:9, color:'#fff', background:'#ef4444', borderRadius:5, padding:'2px 5px', flexShrink:0 }}>ELMARAD</div>}
                  </div>"""

assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# Need to close the extra div we opened in the title row — find and patch the dateLabel line
OLD4 = """                  <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:1 }}>{dateLabel}{ev.location?' · '+ev.location.split(',')[0]:''}</div>"""
NEW4 = """                  </div>
                  <div style={{ fontFamily:T.font, fontSize:11, color: ev.cancelled ? '#ef4444' : T.sub, marginTop:1 }}>{dateLabel}{ev.location?' · '+ev.location.split(',')[0]:''}</div>"""
assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

import re
content = re.sub(r'v9\.752', 'v9.753', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.753")
