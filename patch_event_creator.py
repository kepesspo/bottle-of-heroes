import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add creator state + profiles loading to EventForm
OLD1 = """function EventForm({ initial, onSave, onCancel }) {
  const [title, setTitle] = React.useState(initial?.title || '');
  const [desc, setDesc] = React.useState(initial?.desc || '');
  const [date, setDate] = React.useState(initial?.date ? initial.date.slice(0,16) : '');
  const [dateTo, setDateTo] = React.useState(initial?.dateTo ? initial.dateTo.slice(0,16) : '');
  const [allDay, setAllDay] = React.useState(initial?.allDay || false);
  const [locationUnknown, setLocationUnknown] = React.useState(initial ? !initial.location : false);
  const [location, setLocation] = React.useState(initial?.location || '');
  const [locationQuery, setLocationQuery] = React.useState(initial?.location || '');
  const [locationSuggestions, setLocationSuggestions] = React.useState([]);
  const [locationSearching, setLocationSearching] = React.useState(false);
  const locationDebounce = React.useRef(null);
  const [saving, setSaving] = React.useState(false);"""

NEW1 = """function EventForm({ initial, onSave, onCancel }) {
  const [title, setTitle] = React.useState(initial?.title || '');
  const [desc, setDesc] = React.useState(initial?.desc || '');
  const [date, setDate] = React.useState(initial?.date ? initial.date.slice(0,16) : '');
  const [dateTo, setDateTo] = React.useState(initial?.dateTo ? initial.dateTo.slice(0,16) : '');
  const [allDay, setAllDay] = React.useState(initial?.allDay || false);
  const [locationUnknown, setLocationUnknown] = React.useState(initial ? !initial.location : false);
  const [location, setLocation] = React.useState(initial?.location || '');
  const [locationQuery, setLocationQuery] = React.useState(initial?.location || '');
  const [locationSuggestions, setLocationSuggestions] = React.useState([]);
  const [locationSearching, setLocationSearching] = React.useState(false);
  const locationDebounce = React.useRef(null);
  const [saving, setSaving] = React.useState(false);
  const [creator, setCreator] = React.useState(initial?.creator || null);
  const [profiles, setProfiles] = React.useState([]);
  React.useEffect(() => {
    if (typeof window.getProfiles === 'function') window.getProfiles().then(p => setProfiles(p || []));
  }, []);"""

assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Include creator in submit data
OLD2 = "    onSave({ title: title.trim(), desc: desc.trim(), date: date || null, dateTo: dateTo || null, allDay, location: locationUnknown ? '' : location.trim() }, () => setSaving(false));"
NEW2 = "    onSave({ title: title.trim(), desc: desc.trim(), date: date || null, dateTo: dateTo || null, allDay, location: locationUnknown ? '' : location.trim(), creator: creator || null }, () => setSaving(false));"
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. Add creator card UI at the top of the form (before the Név card)
OLD3 = """      {/* Név */}
      <div style={card}>
        {label('Esemény neve')}
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="pl. Pénteki parti" style={inpStyle} />
      </div>"""

NEW3 = """      {/* Létrehozó */}
      {profiles.length > 0 && (
        <div style={card}>
          {label('Létrehozó')}
          <div style={{ display:'flex', flexWrap:'wrap', gap:8 }}>
            {profiles.map(p => {
              const sel = creator && creator.id === p.id;
              return (
                <div key={p.id} onClick={() => setCreator(sel ? null : { id: p.id, name: p.name, color: p.color, img: p.img || null })}
                  style={{ display:'flex', alignItems:'center', gap:8, padding:'8px 12px', borderRadius:12, background: sel ? (p.color || T.mint) + '22' : T.bg, border:`2px solid ${sel ? (p.color || T.mint) : 'transparent'}`, cursor:'pointer', transition:'all .15s', WebkitTapHighlightColor:'transparent' }}>
                  <div style={{ width:28, height:28, borderRadius:'50%', background: p.color || '#888', flexShrink:0, display:'grid', placeItems:'center', overflow:'hidden' }}>
                    {p.img ? <img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff' }}>{(p.name||'?')[0].toUpperCase()}</span>}
                  </div>
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color: sel ? (p.color || T.mint) : T.ink }}>{p.name}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Név */}
      <div style={card}>
        {label('Esemény neve')}
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="pl. Pénteki parti" style={inpStyle} />
      </div>"""

assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# 4. Version bump
content = re.sub(r'v9\.713', 'v9.714', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.714")
