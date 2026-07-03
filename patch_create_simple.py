import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = '''function EventCreateScreen({ go }) {
  const [events, setEvents] = React.useState(evLoad);
  const [editingId, setEditingId] = React.useState(null); // null=new form, id=edit form
  const [showNewForm, setShowNewForm] = React.useState(false);
  const [deleteConfirm, setDeleteConfirm] = React.useState(null);

  // Live sync
  React.useEffect(() => {
    const col = evDb();
    if (!col) return;
    const unsub = col.orderBy('createdAt','desc').onSnapshot(snap => {
      const docs = snap.docs.map(d => ({ id: d.id, ...d.data() }));
      setEvents(docs);
    });
    return () => unsub();
  }, []);

  function saveNew(data, done) {
    const col = evDb();
    const entry = { ...data, rsvp: {}, createdAt: new Date().toISOString() };
    if (col) { col.add(entry).finally(() => { done(); setShowNewForm(false); }); }
    else { evSave([{ id: Date.now(), ...entry }, ...evLoad()]); done(); setShowNewForm(false); }
  }

  function saveEdit(data, done) {
    const col = evDb();
    if (col) { col.doc(String(editingId)).update(data).finally(() => { done(); setEditingId(null); }); }
    else { evSave(evLoad().map(e => e.id !== editingId ? e : { ...e, ...data })); done(); setEditingId(null); }
  }

  function deleteEvent(id) {
    const col = evDb();
    if (col) col.doc(String(id)).delete();
    else evSave(evLoad().filter(e => e.id !== id));
    setDeleteConfirm(null);
  }

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <div style={{ display:'flex', alignItems:'center', padding:'16px 16px 12px', gap:10 }}>
        <button onClick={() => go('home')} style={{ width:40, height:40, borderRadius:12, border:'none', background:T.surface, display:'grid', placeItems:'center', cursor:'pointer', boxShadow:T.shadow, flexShrink:0 }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink }}>Események kezelése</div>
      </div>
      <div style={{ flex:1, overflowY:'auto', padding:'0 16px 32px' }}>

        {/* Existing events */}
        {events.length > 0 && (
          <div style={{ marginBottom:20 }}>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>Meglévő események</div>
            {events.map(ev => (
              <div key={ev.id}>
                {editingId === ev.id ? (
                  <div style={{ background:T.surface, borderRadius:16, padding:'16px', marginBottom:10, boxShadow:T.shadow }}>
                    <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, marginBottom:12 }}>✏️ {ev.title}</div>
                    <EventForm initial={ev} onSave={saveEdit} onCancel={() => setEditingId(null)} />
                  </div>
                ) : (
                  <div style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:14, padding:'12px 14px', marginBottom:8, boxShadow:T.shadow }}>
                    <div style={{ flex:1, minWidth:0 }}>
                      <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.title}</div>
                      {ev.date && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:2 }}>{new Date(ev.date).toLocaleDateString('hu-HU',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})}</div>}
                    </div>
                    <button onClick={() => { setEditingId(ev.id); setShowNewForm(false); }} style={{ width:34, height:34, borderRadius:10, border:'none', background:'#E8631A18', display:'grid', placeItems:'center', cursor:'pointer', flexShrink:0 }}>
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#E8631A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                    </button>
                    <button onClick={() => setDeleteConfirm(ev.id)} style={{ width:34, height:34, borderRadius:10, border:'none', background:'#e8404018', display:'grid', placeItems:'center', cursor:'pointer', flexShrink:0 }}>
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#e84040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/></svg>
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* New event form */}
        <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>Új esemény</div>
        {showNewForm ? (
          <div style={{ background:T.surface, borderRadius:16, padding:'16px', boxShadow:T.shadow }}>
            <EventForm onSave={saveNew} onCancel={() => setShowNewForm(false)} />
          </div>
        ) : (
          <button onClick={() => { setShowNewForm(true); setEditingId(null); }} style={{ width:'100%', padding:'14px', borderRadius:14, border:`2px dashed ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:800, fontSize:15, color:'#E8631A', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#E8631A" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Új esemény hozzáadása
          </button>
        )}
      </div>

      {/* Delete confirm */}
      {deleteConfirm && (
        <div style={{ position:'fixed', inset:0, background:'rgba(0,0,0,0.45)', zIndex:300, display:'flex', alignItems:'center', justifyContent:'center', padding:24 }}>
          <div style={{ background:T.surface, borderRadius:24, padding:'24px', maxWidth:300, width:'100%', textAlign:'center' }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, marginBottom:8 }}>Törlöd az eseményt?</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.sub, marginBottom:20 }}>Ez nem visszavonható.</div>
            <div style={{ display:'flex', gap:8 }}>
              <button onClick={() => setDeleteConfirm(null)} style={{ flex:1, padding:'12px', borderRadius:12, border:'none', background:T.border, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, cursor:'pointer' }}>Mégse</button>
              <button onClick={() => deleteEvent(deleteConfirm)} style={{ flex:1, padding:'12px', borderRadius:12, border:'none', background:'#e84040', fontFamily:T.font, fontWeight:800, fontSize:14, color:'#fff', cursor:'pointer' }}>Törlés</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}'''

NEW = '''function EventCreateScreen({ go }) {
  const [saving, setSaving] = React.useState(false);

  function saveNew(data, done) {
    setSaving(true);
    const col = evDb();
    const entry = { ...data, rsvp: {}, createdAt: new Date().toISOString() };
    if (col) { col.add(entry).finally(() => { done(); setSaving(false); go('log'); }); }
    else { evSave([{ id: Date.now(), ...entry }, ...evLoad()]); done(); setSaving(false); go('log'); }
  }

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Új esemény" onBack={() => go('log')} />
      <div style={{ flex:1, overflowY:'auto', padding:'16px 16px 32px' }}>
        <EventForm onSave={saveNew} onCancel={() => go('log')} />
      </div>
    </div>
  );
}'''

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

content = re.sub(r'v9\.711', 'v9.712', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.712")
