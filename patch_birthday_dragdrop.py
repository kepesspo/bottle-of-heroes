with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ════════════════════════════════════════════════════════════
# 1. BIRTHDAY — AdminProfiles: add birthday banner + card badge
# ════════════════════════════════════════════════════════════

OLD1 = """  return (
    <div style={{ padding:'16px' }}>
      <button onClick={() => setShowForm(s => !s)} style={{ width:'100%', padding:'13px', borderRadius:14, border:`2px dashed ${T.mint}`, background:'transparent', fontFamily:T.font, fontWeight:900, fontSize:14, color:T.mint, cursor:'pointer', marginBottom:14 }}>
        + Új profil hozzáadása
      </button>"""

NEW1 = """  const todayMD = new Date().toISOString().slice(5, 10);
  const birthdayToday = profiles.filter(p => p.birthday && p.birthday.slice(5, 10) === todayMD);

  React.useEffect(() => {
    if (birthdayToday.length > 0) {
      if (typeof window._bohShowNotif === 'function') {
        birthdayToday.forEach(p => {
          window._bohShowNotif('🎂 Születésnap!', `Ma van ${p.nickname || p.name} születésnapja!`);
        });
      }
    }
  }, [profiles.length]);

  return (
    <div style={{ padding:'16px' }}>
      {birthdayToday.length > 0 && (
        <div style={{ background:'linear-gradient(135deg,#f472b6,#a855f7)', borderRadius:16, padding:'14px 16px', marginBottom:14, display:'flex', alignItems:'center', gap:12 }}>
          <span style={{ fontSize:28 }}>🎂</span>
          <div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff' }}>
              Ma van {birthdayToday.map(p => p.nickname || p.name).join(' és ')} születésnapja!
            </div>
            <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.85)', marginTop:2 }}>🎉 Ne felejtsd el köszönteni!</div>
          </div>
        </div>
      )}
      <button onClick={() => setShowForm(s => !s)} style={{ width:'100%', padding:'13px', borderRadius:14, border:`2px dashed ${T.mint}`, background:'transparent', fontFamily:T.font, fontWeight:900, fontSize:14, color:T.mint, cursor:'pointer', marginBottom:14 }}>
        + Új profil hozzáadása
      </button>"""

assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Birthday badge on matching profile card name row
OLD2 = """              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
                {p.nickname && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>{p.nickname}</div>}"""

NEW2 = """              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ display:'flex', alignItems:'center', gap:6 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
                  {p.birthday && p.birthday.slice(5,10) === todayMD && <span style={{ fontSize:16 }}>🎂</span>}
                </div>
                {p.nickname && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>{p.nickname}</div>}"""

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# ════════════════════════════════════════════════════════════
# 3. DRAG & DROP — AdminEvents: add drag state + listRef
# ════════════════════════════════════════════════════════════

OLD3 = """function AdminEvents({ go }) {
  const [events, setEvents] = React.useState(evLoad());
  const [editingId, setEditingId] = React.useState(null);
  const [showNewForm, setShowNewForm] = React.useState(false);
  const [deleteConfirm, setDeleteConfirm] = React.useState(null);"""

NEW3 = """function AdminEvents({ go }) {
  const [events, setEvents] = React.useState(evLoad());
  const [editingId, setEditingId] = React.useState(null);
  const [showNewForm, setShowNewForm] = React.useState(false);
  const [deleteConfirm, setDeleteConfirm] = React.useState(null);
  const [dragState, setDragState] = React.useState({ from: null, to: null });
  const dragRef = React.useRef({ active: false, from: null, to: null });
  const listRef = React.useRef(null);"""

assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# 4. Add sortedEvents + reorderEvents after deleteEvent function
OLD4 = """  function deleteEvent(id) {
    const col = evDb();
    if (col) col.doc(String(id)).delete();
    else evSave(evLoad().filter(e => e.id !== id));
    setDeleteConfirm(null);
  }

  return ("""

NEW4 = """  function deleteEvent(id) {
    const col = evDb();
    if (col) col.doc(String(id)).delete();
    else evSave(evLoad().filter(e => e.id !== id));
    setDeleteConfirm(null);
  }

  const sortedEvents = React.useMemo(() => [...events].sort((a, b) => {
    if (a.sortOrder != null && b.sortOrder != null) return a.sortOrder - b.sortOrder;
    if (a.sortOrder != null) return -1;
    if (b.sortOrder != null) return 1;
    if (!a.date) return 1; if (!b.date) return -1;
    return new Date(a.date) - new Date(b.date);
  }), [events]);

  function reorderEvents(fromIdx, toIdx) {
    if (fromIdx === toIdx) return;
    const next = [...sortedEvents];
    const [moved] = next.splice(fromIdx, 1);
    next.splice(toIdx, 0, moved);
    // optimistic local update
    setEvents(prev => {
      const idxMap = {};
      next.forEach((ev, i) => { idxMap[ev.id] = i; });
      return prev.map(ev => idxMap[ev.id] !== undefined ? { ...ev, sortOrder: idxMap[ev.id] } : ev);
    });
    // persist to Firestore
    const col = evDb();
    if (col && typeof firebase !== 'undefined') {
      const batch = firebase.firestore().batch();
      next.forEach((ev, i) => { batch.update(col.doc(String(ev.id)), { sortOrder: i }); });
      batch.commit().catch(() => {});
    }
  }

  function startDrag(e, idx) {
    e.preventDefault();
    dragRef.current = { active: true, from: idx, to: idx };
    setDragState({ from: idx, to: idx });

    function onMove(ev) {
      ev.preventDefault();
      const clientY = ev.touches ? ev.touches[0].clientY : ev.clientY;
      if (!listRef.current) return;
      const items = listRef.current.querySelectorAll('[data-drag-item]');
      let newTo = dragRef.current.from;
      for (let i = 0; i < items.length; i++) {
        const rect = items[i].getBoundingClientRect();
        if (clientY < rect.top + rect.height * 0.5) { newTo = i; break; }
        newTo = i;
      }
      if (newTo !== dragRef.current.to) {
        dragRef.current.to = newTo;
        setDragState({ from: dragRef.current.from, to: newTo });
      }
    }

    function onEnd() {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('touchmove', onMove);
      document.removeEventListener('mouseup', onEnd);
      document.removeEventListener('touchend', onEnd);
      reorderEvents(dragRef.current.from, dragRef.current.to);
      dragRef.current.active = false;
      setDragState({ from: null, to: null });
    }

    document.addEventListener('mousemove', onMove, { passive: false });
    document.addEventListener('touchmove', onMove, { passive: false });
    document.addEventListener('mouseup', onEnd);
    document.addEventListener('touchend', onEnd);
  }

  return ("""

assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

# 5. Replace the events list render to use sortedEvents + drag handles
OLD5 = """      {events.length > 0 && (
        <div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>Meglévő események</div>
          {events.map(ev => (
            <div key={ev.id}>
              {editingId === ev.id ? (
                <div style={{ background:T.surface, borderRadius:16, padding:'16px', marginBottom:10, boxShadow:T.shadow }}>
                  <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, marginBottom:12 }}>✏️ {ev.title}</div>
                  <EventForm initial={ev} onSave={saveEdit} onCancel={() => setEditingId(null)} />
                </div>
              ) : (
                <div style={{ display:'flex', alignItems:'center', gap:10, background: ev.cancelled ? '#fef2f2' : T.surface, borderRadius:14, padding:'12px 14px', marginBottom:8, boxShadow:T.shadow, border: ev.cancelled ? '1.5px solid #ef4444' : '1.5px solid transparent' }}>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color: ev.cancelled ? '#ef4444' : T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', textDecoration: ev.cancelled ? 'line-through' : 'none' }}>{ev.title}</div>
                      {ev.cancelled && <div style={{ fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff', background:'#ef4444', borderRadius:6, padding:'2px 6px', flexShrink:0 }}>ELMARAD</div>}
                    </div>
                    {ev.date && <div style={{ fontFamily:T.font, fontSize:12, color: ev.cancelled ? '#ef4444' : T.sub, marginTop:2, textDecoration: ev.cancelled ? 'line-through' : 'none' }}>{new Date(ev.date).toLocaleDateString('hu-HU',{year:'numeric',month:'short',day:'numeric'})}</div>}
                    {(()=>{ const r=ev.rsvp||{},en=Object.entries(r),yn=en.filter(([,s])=>s==='yes').map(([n])=>n),mc=en.filter(([,s])=>s==='maybe').length,nc=en.filter(([,s])=>s==='no').length; if(!en.length)return null; return(<div style={{display:'flex',gap:8,marginTop:4,alignItems:'center',flexWrap:'wrap'}}>{yn.length>0&&<span style={{fontFamily:T.font,fontSize:11,color:'#22c55e',fontWeight:700}}>✓ {yn.length}</span>}{mc>0&&<span style={{fontFamily:T.font,fontSize:11,color:'#f59e0b',fontWeight:700}}>? {mc}</span>}{nc>0&&<span style={{fontFamily:T.font,fontSize:11,color:'#ef4444',fontWeight:700}}>✗ {nc}</span>}{yn.length>0&&<span style={{fontFamily:T.font,fontSize:10,color:T.sub,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',maxWidth:120}}>{yn.join(', ')}</span>}</div>); })()}
                  </div>
                  <button onClick={() => setEditingId(ev.id)} style={{ width:34, height:34, borderRadius:9, border:'none', background:T.border, display:'grid', placeItems:'center', cursor:'pointer' }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  </button>
                  {deleteConfirm === ev.id ? (
                    <React.Fragment>
                      <button onClick={() => deleteEvent(ev.id)} style={{ padding:'6px 10px', borderRadius:9, border:'none', background:'#ef4444', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#fff', cursor:'pointer' }}>Törlés</button>
                      <button onClick={() => setDeleteConfirm(null)} style={{ padding:'6px 10px', borderRadius:9, border:`1px solid ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:700, fontSize:12, color:T.sub, cursor:'pointer' }}>Mégsem</button>
                    </React.Fragment>
                  ) : (
                    <button onClick={() => setDeleteConfirm(ev.id)} style={{ width:34, height:34, borderRadius:9, border:'none', background:'#fef2f2', display:'grid', placeItems:'center', cursor:'pointer' }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}"""

NEW5 = """      {sortedEvents.length > 0 && (
        <div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>Meglévő események</div>
          <div ref={listRef}>
          {sortedEvents.map((ev, idx) => {
            const isDragging = dragState.from === idx;
            const isTarget = dragState.to === idx && dragState.from !== null && dragState.from !== idx;
            return (
              <div key={ev.id} data-drag-item style={{ marginBottom:8, opacity: isDragging ? 0.45 : 1, transition:'opacity .15s', borderTop: isTarget && dragState.to < dragState.from ? `2.5px solid ${T.mint}` : 'none', borderBottom: isTarget && dragState.to >= dragState.from ? `2.5px solid ${T.mint}` : 'none' }}>
                {editingId === ev.id ? (
                  <div style={{ background:T.surface, borderRadius:16, padding:'16px', boxShadow:T.shadow }}>
                    <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, marginBottom:12 }}>✏️ {ev.title}</div>
                    <EventForm initial={ev} onSave={saveEdit} onCancel={() => setEditingId(null)} />
                  </div>
                ) : (
                  <div style={{ display:'flex', alignItems:'center', gap:8, background: ev.cancelled ? '#fef2f2' : T.surface, borderRadius:14, padding:'10px 12px', boxShadow:T.shadow, border: ev.cancelled ? '1.5px solid #ef4444' : '1.5px solid transparent' }}>
                    {/* Drag handle */}
                    <div onMouseDown={e => startDrag(e, idx)} onTouchStart={e => startDrag(e, idx)}
                      style={{ display:'flex', flexDirection:'column', gap:3, padding:'4px 6px', cursor:'grab', flexShrink:0, touchAction:'none', WebkitTapHighlightColor:'transparent' }}>
                      <div style={{ width:14, height:1.5, background:T.sub, borderRadius:1 }} />
                      <div style={{ width:14, height:1.5, background:T.sub, borderRadius:1 }} />
                      <div style={{ width:14, height:1.5, background:T.sub, borderRadius:1 }} />
                    </div>
                    <div style={{ flex:1, minWidth:0 }}>
                      <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color: ev.cancelled ? '#ef4444' : T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', textDecoration: ev.cancelled ? 'line-through' : 'none' }}>{ev.title}</div>
                        {ev.cancelled && <div style={{ fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff', background:'#ef4444', borderRadius:6, padding:'2px 6px', flexShrink:0 }}>ELMARAD</div>}
                      </div>
                      {ev.date && <div style={{ fontFamily:T.font, fontSize:12, color: ev.cancelled ? '#ef4444' : T.sub, marginTop:2, textDecoration: ev.cancelled ? 'line-through' : 'none' }}>{new Date(ev.date).toLocaleDateString('hu-HU',{year:'numeric',month:'short',day:'numeric'})}</div>}
                      {(()=>{ const r=ev.rsvp||{},en=Object.entries(r),yn=en.filter(([,s])=>s==='yes').map(([n])=>n),mc=en.filter(([,s])=>s==='maybe').length,nc=en.filter(([,s])=>s==='no').length; if(!en.length)return null; return(<div style={{display:'flex',gap:8,marginTop:4,alignItems:'center',flexWrap:'wrap'}}>{yn.length>0&&<span style={{fontFamily:T.font,fontSize:11,color:'#22c55e',fontWeight:700}}>✓ {yn.length}</span>}{mc>0&&<span style={{fontFamily:T.font,fontSize:11,color:'#f59e0b',fontWeight:700}}>? {mc}</span>}{nc>0&&<span style={{fontFamily:T.font,fontSize:11,color:'#ef4444',fontWeight:700}}>✗ {nc}</span>}{yn.length>0&&<span style={{fontFamily:T.font,fontSize:10,color:T.sub,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',maxWidth:100}}>{yn.join(', ')}</span>}</div>); })()}
                    </div>
                    <button onClick={() => setEditingId(ev.id)} style={{ width:34, height:34, borderRadius:9, border:'none', background:T.border, display:'grid', placeItems:'center', cursor:'pointer', flexShrink:0 }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                    </button>
                    {deleteConfirm === ev.id ? (
                      <React.Fragment>
                        <button onClick={() => deleteEvent(ev.id)} style={{ padding:'6px 10px', borderRadius:9, border:'none', background:'#ef4444', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#fff', cursor:'pointer' }}>Törlés</button>
                        <button onClick={() => setDeleteConfirm(null)} style={{ padding:'6px 10px', borderRadius:9, border:`1px solid ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:700, fontSize:12, color:T.sub, cursor:'pointer' }}>Mégsem</button>
                      </React.Fragment>
                    ) : (
                      <button onClick={() => setDeleteConfirm(ev.id)} style={{ width:34, height:34, borderRadius:9, border:'none', background:'#fef2f2', display:'grid', placeItems:'center', cursor:'pointer', flexShrink:0 }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
                      </button>
                    )}
                  </div>
                )}
              </div>
            );
          })}
          </div>
        </div>
      )}"""

assert OLD5 in content, "OLD5 not found"
content = content.replace(OLD5, NEW5, 1)

import re
content = re.sub(r'v9\.767', 'v9.768', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.768")
