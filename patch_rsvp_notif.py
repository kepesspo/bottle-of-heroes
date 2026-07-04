with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. EventLogScreen: add notifPerm state + notifLoadTime ref + notification listener
OLD1 = """  const evT = useEventsTheme();
  // Use events theme only on deep link; otherwise use the app's global theme
  const T = deepLink ? evT : (THEMES[localStorage.getItem('boh_theme')] || THEMES['warm']);
  // Subscribe to Firestore events collection, ordered by createdAt desc"""

NEW1 = """  const evT = useEventsTheme();
  // Use events theme only on deep link; otherwise use the app's global theme
  const T = deepLink ? evT : (THEMES[localStorage.getItem('boh_theme')] || THEMES['warm']);
  const [notifPerm, setNotifPerm] = React.useState(() => { if (!('Notification' in window)) return 'unsupported'; return Notification.permission; });
  const notifLoadTime = React.useRef(new Date().toISOString());

  React.useEffect(() => {
    if (typeof firebase === 'undefined') return;
    const notifCol = firebase.firestore().collection('event_notifications');
    const unsub = notifCol.orderBy('createdAt','desc').limit(10).onSnapshot(snap => {
      if (!('Notification' in window) || Notification.permission !== 'granted') return;
      snap.docChanges().forEach(change => {
        if (change.type !== 'added') return;
        const d = change.doc.data();
        if (d.createdAt <= notifLoadTime.current) return;
        const isNew = d.type === 'new_event';
        const title = isNew ? ('📅 Új esemény: ' + d.title) : ('🚫 Elmarad: ' + d.title);
        const body = isNew && d.date ? new Date(d.date).toLocaleDateString('hu-HU',{month:'long',day:'numeric'}) : '';
        try { new Notification(title, { body, icon: '/bottle-of-heroes/icon-192.png' }); } catch(e) {}
      });
    });
    return () => unsub();
  }, []);

  // Subscribe to Firestore events collection, ordered by createdAt desc"""

assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. EventLogScreen AppBar: add bell button next to + create button
OLD2 = """        <button onClick={() => go('create')} style={{ width:38, height:38, borderRadius:11, border:'none', background:T.mint, display:'grid', placeItems:'center', cursor:'pointer', WebkitTapHighlightColor:'transparent' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        </button>"""

NEW2 = """        <div style={{ display:'flex', gap:6 }}>
          {notifPerm !== 'unsupported' && (
            <button onClick={() => { if (notifPerm==='denied'){alert('Értesítések letiltva. Böngésző Beállítások → Webhelyek → Értesítések → engedélyezd.');return;} Notification.requestPermission().then(p => setNotifPerm(p)); }} style={{ width:38, height:38, borderRadius:11, border:'none', background: notifPerm==='granted' ? T.mint+'33' : T.surface, display:'grid', placeItems:'center', cursor:'pointer', WebkitTapHighlightColor:'transparent', boxShadow:T.shadow }} title="Értesítések">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={notifPerm==='granted' ? T.mint : T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>
            </button>
          )}
          <button onClick={() => go('create')} style={{ width:38, height:38, borderRadius:11, border:'none', background:T.mint, display:'grid', placeItems:'center', cursor:'pointer', WebkitTapHighlightColor:'transparent' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </button>
        </div>"""

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. AdminEvents saveNew: write notification to Firestore after adding event
OLD3 = """  function saveNew(data, done) {
    const col = evDb();
    const entry = { ...data, rsvp: {}, createdAt: new Date().toISOString() };
    if (col) { col.add(entry).finally(() => { done(); setShowNewForm(false); }); }
    else { evSave([{ id: Date.now(), ...entry }, ...evLoad()]); done(); setShowNewForm(false); }
  }"""

NEW3 = """  function saveNew(data, done) {
    const col = evDb();
    const entry = { ...data, rsvp: {}, createdAt: new Date().toISOString() };
    if (col) {
      col.add(entry).then(() => {
        firebase.firestore().collection('event_notifications').add({ type:'new_event', title: data.title, date: data.date||null, createdAt: new Date().toISOString() }).catch(()=>{});
      }).finally(() => { done(); setShowNewForm(false); });
    } else { evSave([{ id: Date.now(), ...entry }, ...evLoad()]); done(); setShowNewForm(false); }
  }"""

assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# 4. AdminEvents saveEdit: write notification when event is newly cancelled
OLD4 = """  function saveEdit(data, done) {
    const col = evDb();
    if (col) { col.doc(String(editingId)).update(data).finally(() => { done(); setEditingId(null); }); }
    else { evSave(evLoad().map(e => e.id !== editingId ? e : { ...e, ...data })); done(); setEditingId(null); }
  }"""

NEW4 = """  function saveEdit(data, done) {
    const col = evDb();
    const prevEv = events.find(e => e.id === editingId);
    if (col) {
      col.doc(String(editingId)).update(data).then(() => {
        if (data.cancelled && !prevEv?.cancelled) {
          firebase.firestore().collection('event_notifications').add({ type:'cancelled', title: data.title, createdAt: new Date().toISOString() }).catch(()=>{});
        }
      }).finally(() => { done(); setEditingId(null); });
    } else { evSave(evLoad().map(e => e.id !== editingId ? e : { ...e, ...data })); done(); setEditingId(null); }
  }"""

assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

# 5. AdminEvents event card: add RSVP counts row after the date line
OLD5 = """                    {ev.date && <div style={{ fontFamily:T.font, fontSize:12, color: ev.cancelled ? '#ef4444' : T.sub, marginTop:2, textDecoration: ev.cancelled ? 'line-through' : 'none' }}>{new Date(ev.date).toLocaleDateString('hu-HU',{year:'numeric',month:'short',day:'numeric'})}</div>}
                  </div>
                  <button onClick={() => setEditingId(ev.id)}"""

NEW5 = """                    {ev.date && <div style={{ fontFamily:T.font, fontSize:12, color: ev.cancelled ? '#ef4444' : T.sub, marginTop:2, textDecoration: ev.cancelled ? 'line-through' : 'none' }}>{new Date(ev.date).toLocaleDateString('hu-HU',{year:'numeric',month:'short',day:'numeric'})}</div>}
                    {(()=>{ const r=ev.rsvp||{},en=Object.entries(r),yn=en.filter(([,s])=>s==='yes').map(([n])=>n),mc=en.filter(([,s])=>s==='maybe').length,nc=en.filter(([,s])=>s==='no').length; if(!en.length)return null; return(<div style={{display:'flex',gap:8,marginTop:4,alignItems:'center',flexWrap:'wrap'}}>{yn.length>0&&<span style={{fontFamily:T.font,fontSize:11,color:'#22c55e',fontWeight:700}}>✓ {yn.length}</span>}{mc>0&&<span style={{fontFamily:T.font,fontSize:11,color:'#f59e0b',fontWeight:700}}>? {mc}</span>}{nc>0&&<span style={{fontFamily:T.font,fontSize:11,color:'#ef4444',fontWeight:700}}>✗ {nc}</span>}{yn.length>0&&<span style={{fontFamily:T.font,fontSize:10,color:T.sub,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',maxWidth:120}}>{yn.join(', ')}</span>}</div>); })()}
                  </div>
                  <button onClick={() => setEditingId(ev.id)}"""

assert OLD5 in content, "OLD5 not found"
content = content.replace(OLD5, NEW5, 1)

# 6. AdminProfiles: add events loading for RSVP count
OLD6 = """  const [avatarId, setAvatarId] = React.useState(null);

  function load() {"""

NEW6 = """  const [avatarId, setAvatarId] = React.useState(null);
  const [eventsRsvp, setEventsRsvp] = React.useState(evLoad());

  React.useEffect(() => {
    const col = evDb();
    if (!col) return;
    const unsub = col.onSnapshot(snap => { setEventsRsvp(snap.docs.map(d=>({id:d.id,...d.data()}))); });
    return () => unsub();
  }, []);

  function load() {"""

assert OLD6 in content, "OLD6 not found"
content = content.replace(OLD6, NEW6, 1)

# 7. AdminProfiles profile card: add RSVP count under nickname
OLD7 = """          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
            {p.nickname && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>{p.nickname}</div>}
          </div>"""

NEW7 = """          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
            {p.nickname && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>{p.nickname}</div>}
            {(()=>{ const cnt=eventsRsvp.filter(e=>(e.rsvp||{})[p.name]==='yes').length; return cnt>0?<div style={{fontFamily:T.font,fontSize:11,color:T.mint,fontWeight:700,marginTop:2}}>✓ {cnt} eseményre jelentkezett</div>:null; })()}
          </div>"""

assert OLD7 in content, "OLD7 not found"
content = content.replace(OLD7, NEW7, 1)

import re
content = re.sub(r'v9\.762', 'v9.763', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.763")
