with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. EventForm: add image state after cancelled state
OLD1 = """  const [cancelled, setCancelled] = React.useState(initial?.cancelled || false);

  function submit() {
    if (!title.trim() || saving) { setTitleTouched(true); return; }
    setSaving(true);
    onSave({ title: title.trim(), desc: desc.trim(), date: date || null, dateTo: dateTo || null, allDay, location: locationUnknown ? '' : location.trim(), creator: creator || null, cancelled }, () => setSaving(false));
  }"""

NEW1 = """  const [cancelled, setCancelled] = React.useState(initial?.cancelled || false);
  const [image, setImage] = React.useState(initial?.image || null);
  const imgInputRef = React.useRef(null);

  function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = evt => {
      const img = new Image();
      img.onload = () => {
        const MAX = 900;
        let w = img.width, h = img.height;
        if (w > MAX) { h = Math.round(h * MAX / w); w = MAX; }
        const canvas = document.createElement('canvas');
        canvas.width = w; canvas.height = h;
        canvas.getContext('2d').drawImage(img, 0, 0, w, h);
        setImage(canvas.toDataURL('image/jpeg', 0.72));
      };
      img.src = evt.target.result;
    };
    reader.readAsDataURL(file);
  }

  function submit() {
    if (!title.trim() || saving) { setTitleTouched(true); return; }
    setSaving(true);
    onSave({ title: title.trim(), desc: desc.trim(), date: date || null, dateTo: dateTo || null, allDay, location: locationUnknown ? '' : location.trim(), creator: creator || null, cancelled, image: image || null }, () => setSaving(false));
  }"""

assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. EventForm: add image upload card after Leírás card
OLD2 = """      {/* Időpont */}
      <div style={card}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:14 }}>
          {label('Időpont')}"""

NEW2 = """      {/* Borítókép */}
      <div style={card}>
        {label('Borítókép (opcionális)')}
        {image ? (
          <div style={{ position:'relative', marginBottom:8, borderRadius:12, overflow:'hidden' }}>
            <img src={image} style={{ width:'100%', objectFit:'cover', maxHeight:160, display:'block' }} />
            <button onClick={() => { setImage(null); if(imgInputRef.current) imgInputRef.current.value=''; }} style={{ position:'absolute', top:8, right:8, width:30, height:30, borderRadius:'50%', border:'none', background:'rgba(0,0,0,0.55)', color:'#fff', fontSize:16, cursor:'pointer', display:'grid', placeItems:'center', lineHeight:1 }}>✕</button>
          </div>
        ) : null}
        <label style={{ display:'flex', alignItems:'center', gap:10, background:T.bg, borderRadius:13, padding:'12px 14px', cursor:'pointer', WebkitTapHighlightColor:'transparent' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={T.sub} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
          <span style={{ fontFamily:T.font, fontSize:14, color:T.sub }}>{ image ? 'Kép cseréje…' : 'Kép kiválasztása…' }</span>
          <input ref={imgInputRef} type="file" accept="image/*" onChange={handleImageUpload} style={{ display:'none' }} />
        </label>
      </div>

      {/* Időpont */}
      <div style={card}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:14 }}>
          {label('Időpont')}"""

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. Event detail: add cover image after cancelled banner and before title block
OLD3 = """          {/* Title */}
          <div style={{ background:T.surface, borderRadius:18, padding:'18px', marginBottom:12, boxShadow:T.shadow }}>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.mint, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:6 }}>Esemény neve</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color: ev.cancelled ? '#ef4444' : T.ink, textDecoration: ev.cancelled ? 'line-through' : 'none' }}>{ev.title}</div>
          </div>"""

NEW3 = """          {/* Cover image */}
          {ev.image && (
            <div style={{ borderRadius:16, overflow:'hidden', marginBottom:12, boxShadow:T.shadow }}>
              <img src={ev.image} style={{ width:'100%', objectFit:'cover', maxHeight:200, display:'block' }} />
            </div>
          )}
          {/* Title */}
          <div style={{ background:T.surface, borderRadius:18, padding:'18px', marginBottom:12, boxShadow:T.shadow }}>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.mint, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:6 }}>Esemény neve</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color: ev.cancelled ? '#ef4444' : T.ink, textDecoration: ev.cancelled ? 'line-through' : 'none' }}>{ev.title}</div>
          </div>"""

assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# 4. Event detail: add Google Maps button in location section
OLD4 = """            <div style={{ display:'flex', alignItems:'center', gap:10 }}>
              <span style={{ fontSize:18, flexShrink:0 }}>📍</span>
              <div style={{ minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.06em' }}>Helyszín</div>
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.location ? ev.location.split(',')[0] : '—'}</div>
              </div>
            </div>"""

NEW4 = """            <div style={{ display:'flex', alignItems:'center', gap:10 }}>
              <span style={{ fontSize:18, flexShrink:0 }}>📍</span>
              <div style={{ minWidth:0, flex:1 }}>
                <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.06em' }}>Helyszín</div>
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.location ? ev.location.split(',')[0] : '—'}</div>
              </div>
              {ev.location && (
                <a href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(ev.location)}`} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()} style={{ display:'flex', alignItems:'center', gap:5, background:T.mint+'22', borderRadius:10, padding:'7px 11px', textDecoration:'none', flexShrink:0 }}>
                  <span style={{ fontSize:14 }}>🗺</span>
                  <span style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.mint }}>Térkép</span>
                </a>
              )}
            </div>"""

assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

# 5. Event list card: add thin cover image strip at the top (after ELMARAD badge, before Top row)
OLD5 = """              {ev.cancelled && <div style={{ background:'#ef4444', padding:'4px 14px', fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', letterSpacing:'0.08em', textAlign:'center' }}>ELMARAD</div>}
              {/* Top row */}"""

NEW5 = """              {ev.cancelled && <div style={{ background:'#ef4444', padding:'4px 14px', fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', letterSpacing:'0.08em', textAlign:'center' }}>ELMARAD</div>}
              {ev.image && !ev.cancelled && <div style={{ height:90, overflow:'hidden' }}><img src={ev.image} style={{ width:'100%', height:'100%', objectFit:'cover', display:'block' }} /></div>}
              {/* Top row */}"""

assert OLD5 in content, "OLD5 not found"
content = content.replace(OLD5, NEW5, 1)

import re
content = re.sub(r'v9\.766', 'v9.767', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.767")
