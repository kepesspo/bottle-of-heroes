import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = '''  return (
    <div>
      <div style={{ marginBottom:10 }}>
        <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:5 }}>Esemény neve *</div>
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="pl. Pénteki parti" style={{ width:'100%', boxSizing:'border-box', padding:'12px 13px', borderRadius:13, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none' }} />
      </div>
      <div style={{ marginBottom:10 }}>
        <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:5 }}>Leírás</div>
        <textarea value={desc} onChange={e => setDesc(e.target.value)} placeholder="Mit kell tudni az eseményről?" rows={2} style={{ width:'100%', boxSizing:'border-box', padding:'12px 13px', borderRadius:13, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none', resize:'none' }} />
      </div>
      <div style={{ marginBottom:10 }}>
        <div style={{ display:'flex', alignItems:'center', marginBottom:8, gap:10 }}>
          <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em' }}>📅 Időpont</div>
          <button onClick={() => setAllDay(a=>!a)} style={{ display:'flex', alignItems:'center', gap:6, padding:'5px 11px', borderRadius:999, border:`1.5px solid ${allDay ? T.mint : T.border}`, background: allDay ? T.mint+'22' : 'transparent', cursor:'pointer', fontFamily:T.font, fontWeight:700, fontSize:12, color: allDay ? T.mint : T.sub, WebkitTapHighlightColor:'transparent' }}>
            {allDay ? '✓' : '○'} Egész nap
          </button>
        </div>
        <div style={{ display:'flex', gap:8, alignItems:'center', marginBottom:6 }}>
          <span style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, flexShrink:0, width:28 }}>Től</span>
          <input type="date" value={date ? date.slice(0,10) : ''} onChange={e => setDate(prev => e.target.value + (prev && prev.length>10 ? prev.slice(10) : 'T00:00'))} style={{ flex:1, minWidth:0, boxSizing:'border-box', padding:'10px 10px', borderRadius:13, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />
          {!allDay && <input type="time" value={date ? date.slice(11,16) : ''} onChange={e => setDate(prev => (prev ? prev.slice(0,10) : new Date().toISOString().slice(0,10)) + 'T' + e.target.value)} style={{ width:90, boxSizing:'border-box', padding:'10px 10px', borderRadius:13, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />}
        </div>
        <div style={{ display:'flex', gap:8, alignItems:'center' }}>
          <span style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, flexShrink:0, width:28 }}>Ig</span>
          <input type="date" value={dateTo ? dateTo.slice(0,10) : ''} onChange={e => setDateTo(prev => e.target.value + (prev && prev.length>10 ? prev.slice(10) : 'T00:00'))} style={{ flex:1, minWidth:0, boxSizing:'border-box', padding:'10px 10px', borderRadius:13, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />
          {!allDay && <input type="time" value={dateTo ? dateTo.slice(11,16) : ''} onChange={e => setDateTo(prev => (prev ? prev.slice(0,10) : (date ? date.slice(0,10) : new Date().toISOString().slice(0,10))) + 'T' + e.target.value)} style={{ width:90, boxSizing:'border-box', padding:'10px 10px', borderRadius:13, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />}
        </div>
      </div>
      <div style={{ marginBottom:14 }}>
        <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:5 }}>📍 Helyszín</div>
        {!locationUnknown && (
          <div style={{ position:'relative', marginBottom:7 }}>
            <div style={{ display:'flex', alignItems:'center', background:T.bg, borderRadius:13, border:`1.5px solid ${T.border}`, overflow:'hidden' }}>
              <span style={{ padding:'0 9px', fontSize:15 }}>🔍</span>
              <input value={locationQuery} onChange={e => searchLocation(e.target.value)} placeholder="Keress helyszínt…" style={{ flex:1, padding:'11px 10px 11px 0', border:'none', background:'transparent', fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />
              {locationSearching && <span style={{ padding:'0 10px', fontSize:12, color:T.sub }}>…</span>}
            </div>
            {locationSuggestions.length > 0 && (
              <div style={{ position:'absolute', top:'100%', left:0, right:0, zIndex:50, background:T.surface, borderRadius:13, boxShadow:'0 8px 24px rgba(0,0,0,0.18)', marginTop:4, overflow:'hidden' }}>
                {locationSuggestions.map((s, i) => (
                  <div key={i} onClick={() => pickLocation(s)} style={{ padding:'11px 13px', borderBottom: i < locationSuggestions.length-1 ? `1px solid ${T.border}` : 'none', cursor:'pointer', fontFamily:T.font, fontSize:13, color:T.ink, lineHeight:1.3 }}>
                    <div style={{ fontWeight:700 }}>{s.short}</div>
                    <div style={{ fontSize:11, color:T.sub, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{s.label}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        <button onClick={() => { setLocationUnknown(u => !u); setLocationSuggestions([]); }} style={{ display:'flex', alignItems:'center', gap:7, padding:'9px 13px', borderRadius:11, border:`1.5px solid ${locationUnknown ? '#E8631A' : T.border}`, background: locationUnknown ? '#E8631A18' : 'transparent', cursor:'pointer', fontFamily:T.font, fontWeight:700, fontSize:13, color: locationUnknown ? '#E8631A' : T.sub }}>
          <div style={{ width:16, height:16, borderRadius:4, border:`2px solid ${locationUnknown ? '#E8631A' : T.sub}`, background: locationUnknown ? '#E8631A' : 'transparent', display:'grid', placeItems:'center', flexShrink:0 }}>
            {locationUnknown && <svg width="10" height="10" viewBox="0 0 12 12"><polyline points="2,6 5,9 10,3" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>}
          </div>
          Még nem tudjuk a helyszínt
        </button>
      </div>
      <div style={{ display:'flex', gap:8 }}>
        {onCancel && <button onClick={onCancel} style={{ flex:1, padding:'13px', borderRadius:13, border:'none', background:T.border, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, cursor:'pointer' }}>Mégse</button>}
        <button onClick={submit} disabled={!title.trim() || saving} style={{ flex:2, padding:'13px', borderRadius:13, border:'none', background: title.trim() && !saving ? '#E8631A' : T.border, fontFamily:T.font, fontWeight:800, fontSize:14, color:'#fff', cursor: title.trim() && !saving ? 'pointer' : 'default' }}>
          {saving ? '…' : (initial ? 'Mentés' : 'Létrehozás')}
        </button>
      </div>
    </div>'''

NEW = '''  const inpStyle = { width:'100%', boxSizing:'border-box', padding:'13px 14px', borderRadius:13, border:'none', background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none' };
  const label = txt => <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:8 }}>{txt}</div>;
  const card = { background:T.surface, borderRadius:18, padding:'16px', boxShadow:T.shadow, marginBottom:12 };

  return (
    <div>
      {/* Név */}
      <div style={card}>
        {label('Esemény neve')}
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="pl. Pénteki parti" style={inpStyle} />
      </div>

      {/* Leírás */}
      <div style={card}>
        {label('Leírás')}
        <textarea value={desc} onChange={e => setDesc(e.target.value)} placeholder="Mit kell tudni az eseményről?" rows={3} style={{ ...inpStyle, resize:'none' }} />
      </div>

      {/* Időpont */}
      <div style={card}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:14 }}>
          {label('Időpont')}
          <div onClick={() => setAllDay(a=>!a)} style={{ display:'flex', alignItems:'center', gap:8, cursor:'pointer' }}>
            <div style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color: allDay ? T.mint : T.sub }}>Egész nap</div>
            <div style={{ width:44, height:26, borderRadius:13, background: allDay ? T.mint : T.inkSoft, position:'relative', transition:'background .2s', flexShrink:0 }}>
              <div style={{ position:'absolute', top:3, left: allDay ? 21 : 3, width:20, height:20, borderRadius:'50%', background:'#fff', transition:'left .2s', boxShadow:'0 1px 4px rgba(0,0,0,0.2)' }} />
            </div>
          </div>
        </div>
        <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
          <div style={{ display:'flex', gap:8, alignItems:'center' }}>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, width:24, flexShrink:0 }}>Től</div>
            <input type="date" value={date ? date.slice(0,10) : ''} onChange={e => setDate(prev => e.target.value + (prev && prev.length>10 ? prev.slice(10) : 'T00:00'))} style={{ ...inpStyle, flex:1, minWidth:0, padding:'11px 12px' }} />
            {!allDay && <input type="time" value={date ? date.slice(11,16) : ''} onChange={e => setDate(prev => (prev ? prev.slice(0,10) : new Date().toISOString().slice(0,10)) + 'T' + e.target.value)} style={{ ...inpStyle, width:88, padding:'11px 10px' }} />}
          </div>
          <div style={{ display:'flex', gap:8, alignItems:'center' }}>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, width:24, flexShrink:0 }}>Ig</div>
            <input type="date" value={dateTo ? dateTo.slice(0,10) : ''} onChange={e => setDateTo(prev => e.target.value + (prev && prev.length>10 ? prev.slice(10) : 'T00:00'))} style={{ ...inpStyle, flex:1, minWidth:0, padding:'11px 12px' }} />
            {!allDay && <input type="time" value={dateTo ? dateTo.slice(11,16) : ''} onChange={e => setDateTo(prev => (prev ? prev.slice(0,10) : (date ? date.slice(0,10) : new Date().toISOString().slice(0,10))) + 'T' + e.target.value)} style={{ ...inpStyle, width:88, padding:'11px 10px' }} />}
          </div>
        </div>
      </div>

      {/* Helyszín */}
      <div style={card}>
        {label('Helyszín')}
        {!locationUnknown && (
          <div style={{ position:'relative', marginBottom:10 }}>
            <div style={{ display:'flex', alignItems:'center', background:T.bg, borderRadius:13, overflow:'hidden' }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={T.sub} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft:13, flexShrink:0 }}><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input value={locationQuery} onChange={e => searchLocation(e.target.value)} placeholder="Keress helyszínt…" style={{ flex:1, padding:'13px 10px', border:'none', background:'transparent', fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />
              {locationSearching && <span style={{ padding:'0 12px', fontSize:12, color:T.sub }}>…</span>}
            </div>
            {locationSuggestions.length > 0 && (
              <div style={{ position:'absolute', top:'100%', left:0, right:0, zIndex:50, background:T.surface, borderRadius:13, boxShadow:'0 8px 24px rgba(0,0,0,0.18)', marginTop:4, overflow:'hidden' }}>
                {locationSuggestions.map((s, i) => (
                  <div key={i} onClick={() => pickLocation(s)} style={{ padding:'11px 14px', borderBottom: i < locationSuggestions.length-1 ? `1px solid ${T.border}` : 'none', cursor:'pointer', fontFamily:T.font, fontSize:13, color:T.ink, lineHeight:1.3 }}>
                    <div style={{ fontWeight:700 }}>{s.short}</div>
                    <div style={{ fontSize:11, color:T.sub, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{s.label}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        <div onClick={() => { setLocationUnknown(u => !u); setLocationSuggestions([]); }} style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'12px 14px', borderRadius:13, background:T.bg, cursor:'pointer' }}>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color: locationUnknown ? '#E8631A' : T.sub }}>Még nem tudjuk a helyszínt</div>
          <div style={{ width:44, height:26, borderRadius:13, background: locationUnknown ? '#E8631A' : T.inkSoft, position:'relative', transition:'background .2s', flexShrink:0 }}>
            <div style={{ position:'absolute', top:3, left: locationUnknown ? 21 : 3, width:20, height:20, borderRadius:'50%', background:'#fff', transition:'left .2s', boxShadow:'0 1px 4px rgba(0,0,0,0.2)' }} />
          </div>
        </div>
      </div>

      {/* Gombok */}
      <div style={{ display:'flex', gap:10, marginTop:4 }}>
        {onCancel && <button onClick={onCancel} style={{ flex:1, padding:'15px', borderRadius:16, border:'none', background:T.surface, fontFamily:T.font, fontWeight:800, fontSize:15, color:T.sub, cursor:'pointer', boxShadow:T.shadow }}>Mégse</button>}
        <button onClick={submit} disabled={!title.trim() || saving} style={{ flex:2, padding:'15px', borderRadius:16, border:'none', background: title.trim() && !saving ? '#E8631A' : T.border, fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor: title.trim() && !saving ? 'pointer' : 'default', boxShadow: title.trim() ? '0 4px 14px rgba(232,99,26,0.4)' : 'none', transition:'all .2s' }}>
          {saving ? '…' : (initial ? 'Mentés' : 'Létrehozás')}
        </button>
      </div>
    </div>'''

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

content = re.sub(r'v9\.712', 'v9.713', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.713")
