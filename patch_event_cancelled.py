with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add cancelled state to EventForm (after titleTouched state)
OLD1 = """  const [titleTouched, setTitleTouched] = React.useState(false);
  const titleErr = titleTouched && !title.trim();

  function submit() {
    if (!title.trim() || saving) { setTitleTouched(true); return; }
    setSaving(true);
    onSave({ title: title.trim(), desc: desc.trim(), date: date || null, dateTo: dateTo || null, allDay, location: locationUnknown ? '' : location.trim(), creator: creator || null }, () => setSaving(false));
  }"""

NEW1 = """  const [titleTouched, setTitleTouched] = React.useState(false);
  const titleErr = titleTouched && !title.trim();
  const [cancelled, setCancelled] = React.useState(initial?.cancelled || false);

  function submit() {
    if (!title.trim() || saving) { setTitleTouched(true); return; }
    setSaving(true);
    onSave({ title: title.trim(), desc: desc.trim(), date: date || null, dateTo: dateTo || null, allDay, location: locationUnknown ? '' : location.trim(), creator: creator || null, cancelled }, () => setSaving(false));
  }"""

assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Add cancelled toggle before the Gombok section
OLD2 = """      {/* Gombok */}
      <div style={{ display:'flex', gap:10, marginTop:4 }}>"""

NEW2 = """      {/* Elmarad toggle — only show when editing */}
      {initial && (
        <div onClick={() => setCancelled(c => !c)} style={{ display:'flex', alignItems:'center', justifyContent:'space-between', background: cancelled ? '#fef2f2' : T.surface, borderRadius:16, padding:'14px 16px', marginBottom:12, boxShadow:T.shadow, cursor:'pointer', border: cancelled ? '1.5px solid #ef4444' : '1.5px solid transparent', transition:'all .2s' }}>
          <div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color: cancelled ? '#ef4444' : T.ink }}>Esemény elmarad</div>
            <div style={{ fontFamily:T.font, fontSize:12, color: cancelled ? '#ef4444' : T.sub, marginTop:2 }}>{cancelled ? 'Az esemény törölve / elmarad' : 'Kattints ha az esemény elmarad'}</div>
          </div>
          <div style={{ width:44, height:26, borderRadius:13, background: cancelled ? '#ef4444' : T.border, position:'relative', transition:'background .2s', flexShrink:0 }}>
            <div style={{ position:'absolute', top:3, left: cancelled ? 21 : 3, width:20, height:20, borderRadius:'50%', background:'#fff', transition:'left .2s', boxShadow:'0 1px 4px rgba(0,0,0,0.2)' }} />
          </div>
        </div>
      )}

      {/* Gombok */}
      <div style={{ display:'flex', gap:10, marginTop:4 }}>"""

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. AdminEvents list: show cancelled events with strikethrough + "Elmarad" badge
OLD3 = """                <div style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:14, padding:'12px 14px', marginBottom:8, boxShadow:T.shadow }}>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.title}</div>
                    {ev.date && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:2 }}>{new Date(ev.date).toLocaleDateString('hu-HU',{year:'numeric',month:'short',day:'numeric'})}</div>}
                  </div>"""

NEW3 = """                <div style={{ display:'flex', alignItems:'center', gap:10, background: ev.cancelled ? '#fef2f2' : T.surface, borderRadius:14, padding:'12px 14px', marginBottom:8, boxShadow:T.shadow, border: ev.cancelled ? '1.5px solid #ef4444' : '1.5px solid transparent' }}>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color: ev.cancelled ? '#ef4444' : T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', textDecoration: ev.cancelled ? 'line-through' : 'none' }}>{ev.title}</div>
                      {ev.cancelled && <div style={{ fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff', background:'#ef4444', borderRadius:6, padding:'2px 6px', flexShrink:0 }}>ELMARAD</div>}
                    </div>
                    {ev.date && <div style={{ fontFamily:T.font, fontSize:12, color: ev.cancelled ? '#ef4444' : T.sub, marginTop:2, textDecoration: ev.cancelled ? 'line-through' : 'none' }}>{new Date(ev.date).toLocaleDateString('hu-HU',{year:'numeric',month:'short',day:'numeric'})}</div>}
                  </div>"""

assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

import re
content = re.sub(r'v9\.749', 'v9.750', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.750")
