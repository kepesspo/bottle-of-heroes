with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = """          <div style={{ display:'flex', gap:8, alignItems:'center' }}>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, width:24, flexShrink:0 }}>Től</div>
            <input type="date" value={date ? date.slice(0,10) : ''} onChange={e => setDate(prev => e.target.value + (prev && prev.length>10 ? prev.slice(10) : 'T00:00'))} style={{ ...inpStyle, flex:1, minWidth:0, padding:'11px 12px' }} />
            {!allDay && <input type="time" value={date ? date.slice(11,16) : ''} onChange={e => setDate(prev => (prev ? prev.slice(0,10) : new Date().toISOString().slice(0,10)) + 'T' + e.target.value)} style={{ ...inpStyle, width:88, padding:'11px 10px' }} />}
          </div>
          <div style={{ display:'flex', gap:8, alignItems:'center' }}>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, width:24, flexShrink:0 }}>Ig</div>
            <input type="date" value={dateTo ? dateTo.slice(0,10) : ''} onChange={e => setDateTo(prev => e.target.value + (prev && prev.length>10 ? prev.slice(10) : 'T00:00'))} style={{ ...inpStyle, flex:1, minWidth:0, padding:'11px 12px' }} />
            {!allDay && <input type="time" value={dateTo ? dateTo.slice(11,16) : ''} onChange={e => setDateTo(prev => (prev ? prev.slice(0,10) : (date ? date.slice(0,10) : new Date().toISOString().slice(0,10))) + 'T' + e.target.value)} style={{ ...inpStyle, width:88, padding:'11px 10px' }} />}
          </div>"""

NEW = """          <div style={{ display:'flex', gap:8, alignItems:'center' }}>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, width:24, flexShrink:0 }}>Től</div>
            <input type="date" value={date ? date.slice(0,10) : ''} onChange={e => setDate(prev => e.target.value + (prev && prev.length>10 ? prev.slice(10) : 'T00:00'))} style={{ ...inpStyle, flex:1, minWidth:0, padding:'7px 12px', height:42, boxSizing:'border-box' }} />
            {!allDay && <input type="time" value={date ? date.slice(11,16) : ''} onChange={e => setDate(prev => (prev ? prev.slice(0,10) : new Date().toISOString().slice(0,10)) + 'T' + e.target.value)} style={{ ...inpStyle, width:88, padding:'7px 10px', height:42, boxSizing:'border-box' }} />}
          </div>
          <div style={{ display:'flex', gap:8, alignItems:'center' }}>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, width:24, flexShrink:0 }}>Ig</div>
            <input type="date" value={dateTo ? dateTo.slice(0,10) : ''} onChange={e => setDateTo(prev => e.target.value + (prev && prev.length>10 ? prev.slice(10) : 'T00:00'))} style={{ ...inpStyle, flex:1, minWidth:0, padding:'7px 12px', height:42, boxSizing:'border-box' }} />
            {!allDay && <input type="time" value={dateTo ? dateTo.slice(11,16) : ''} onChange={e => setDateTo(prev => (prev ? prev.slice(0,10) : (date ? date.slice(0,10) : new Date().toISOString().slice(0,10))) + 'T' + e.target.value)} style={{ ...inpStyle, width:88, padding:'7px 10px', height:42, boxSizing:'border-box' }} />}
          </div>"""

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

import re
content = re.sub(r'v9\.742', 'v9.743', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.743")
