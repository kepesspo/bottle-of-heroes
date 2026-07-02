import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Events pill button: remove long-press, keep click ──
OLD1 = '''          {(() => {
            const [lpPct, setLpPct] = React.useState(0); // 0-100
            const lpRef = React.useRef(null);
            const lpStart = React.useRef(null);
            const DURATION = 3000;
            const R = 18, CIRC = 2 * Math.PI * R;
            function startPress() {
              lpStart.current = Date.now();
              lpRef.current = setInterval(() => {
                const elapsed = Date.now() - lpStart.current;
                const pct = Math.min(100, (elapsed / DURATION) * 100);
                setLpPct(pct);
                if (pct >= 100) {
                  clearInterval(lpRef.current);
                  setLpPct(0);
                  go('create');
                }
              }, 30);
            }
            function endPress() {
              clearInterval(lpRef.current);
              if (lpPct < 100) setLpPct(0);
            }
            return (
              <button
                onMouseDown={startPress} onMouseUp={endPress} onMouseLeave={endPress}
                onTouchStart={e => { e.preventDefault(); startPress(); }} onTouchEnd={endPress} onTouchCancel={endPress}
                onClick={() => { if (lpPct === 0) go('log'); }}
                style={{ position:'relative', display:'flex', alignItems:'center', justifyContent:'center', width:52, height:52, border:'none', background:'#E8631A', cursor:'pointer', WebkitTapHighlightColor:'transparent', userSelect:'none' }}>
                {lpPct > 0 ? (
                  <svg width="40" height="40" viewBox="0 0 40 40" style={{ position:'absolute' }}>
                    <circle cx="20" cy="20" r={R} fill="none" stroke="rgba(255,255,255,0.25)" strokeWidth="3"/>
                    <circle cx="20" cy="20" r={R} fill="none" stroke="#fff" strokeWidth="3"
                      strokeDasharray={CIRC} strokeDashoffset={CIRC * (1 - lpPct/100)}
                      strokeLinecap="round" transform="rotate(-90 20 20)" style={{ transition:'stroke-dashoffset 0.03s linear' }}/>
                  </svg>
                ) : null}
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" style={{ position:'relative', zIndex:1 }}><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="9" y1="7" x2="15" y2="7"/><line x1="9" y1="11" x2="15" y2="11"/><line x1="9" y1="15" x2="12" y2="15"/></svg>
              </button>
            );
          })()}'''

NEW1 = '''          <button onClick={() => go('log')}
              style={{ display:'flex', alignItems:'center', justifyContent:'center', width:52, height:52, border:'none', background:'#E8631A', cursor:'pointer', WebkitTapHighlightColor:'transparent' }}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="9" y1="7" x2="15" y2="7"/><line x1="9" y1="11" x2="15" y2="11"/><line x1="9" y1="15" x2="12" y2="15"/></svg>
            </button>'''

assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# ── 2. Settings gear: add 3s long-press → PIN → admin ──
OLD2 = '''          <button onClick={() => setShowSettings(true)} style={{ display:'flex', alignItems:'center', justifyContent:'center', width:52, height:52, border:'none', background:'transparent', cursor:'pointer' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
          </button>'''

NEW2 = '''          {(() => {
            const [gPct, setGPct] = React.useState(0);
            const [showPin, setShowPin] = React.useState(false);
            const [pinVal, setPinVal] = React.useState('');
            const [pinErr, setPinErr] = React.useState(false);
            const gRef = React.useRef(null);
            const gStart = React.useRef(null);
            const GDUR = 3000;
            function gStartPress() {
              gStart.current = Date.now();
              gRef.current = setInterval(() => {
                const e = Date.now() - gStart.current;
                const p = Math.min(100, (e / GDUR) * 100);
                setGPct(p);
                if (p >= 100) { clearInterval(gRef.current); setGPct(0); setShowPin(true); setPinVal(''); setPinErr(false); }
              }, 30);
            }
            function gEndPress() { clearInterval(gRef.current); if (gPct < 100) setGPct(0); }
            function submitPin() {
              if (pinVal === '199509') { setShowPin(false); setPinVal(''); go('admin'); }
              else { setPinErr(true); setPinVal(''); }
            }
            const GCIRC = 2 * Math.PI * 16;
            return (
              <React.Fragment>
                <button onClick={() => setShowSettings(true)}
                  onMouseDown={gStartPress} onMouseUp={gEndPress} onMouseLeave={gEndPress}
                  onTouchStart={e2 => { e2.preventDefault(); gStartPress(); }} onTouchEnd={gEndPress} onTouchCancel={gEndPress}
                  style={{ position:'relative', display:'flex', alignItems:'center', justifyContent:'center', width:52, height:52, border:'none', background:'transparent', cursor:'pointer', WebkitTapHighlightColor:'transparent', userSelect:'none' }}>
                  {gPct > 0 && (
                    <svg width="36" height="36" viewBox="0 0 36 36" style={{ position:'absolute' }}>
                      <circle cx="18" cy="18" r="16" fill="none" stroke={T.border} strokeWidth="2.5"/>
                      <circle cx="18" cy="18" r="16" fill="none" stroke={T.mint} strokeWidth="2.5"
                        strokeDasharray={GCIRC} strokeDashoffset={GCIRC*(1-gPct/100)}
                        strokeLinecap="round" transform="rotate(-90 18 18)" style={{transition:'stroke-dashoffset 0.03s linear'}}/>
                    </svg>
                  )}
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" style={{position:'relative',zIndex:1}}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
                </button>
                {showPin && (
                  <div style={{position:'fixed',inset:0,zIndex:9000,background:'rgba(0,0,0,0.55)',display:'flex',alignItems:'center',justifyContent:'center'}} onClick={e2=>{if(e2.target===e2.currentTarget){setShowPin(false);setPinVal('');}}}>
                    <div style={{background:T.surface,borderRadius:24,padding:'32px 28px',width:280,boxShadow:'0 20px 60px rgba(0,0,0,0.3)',display:'flex',flexDirection:'column',alignItems:'center',gap:16}}>
                      <div style={{fontFamily:T.font,fontWeight:900,fontSize:20,color:T.ink}}>🔐 Admin belépés</div>
                      <div style={{fontFamily:T.font,fontSize:14,color:T.sub,textAlign:'center'}}>Add meg a PIN kódot</div>
                      <input
                        type="password" inputMode="numeric" maxLength={6}
                        value={pinVal} onChange={e2=>{setPinVal(e2.target.value);setPinErr(false);}}
                        onKeyDown={e2=>{if(e2.key==='Enter')submitPin();}}
                        autoFocus
                        style={{width:'100%',boxSizing:'border-box',padding:'14px 16px',borderRadius:14,border:`2px solid ${pinErr?'#ef4444':T.border}`,background:T.bg,fontFamily:T.font,fontSize:22,color:T.ink,textAlign:'center',letterSpacing:8,outline:'none'}}
                        placeholder="······"
                      />
                      {pinErr && <div style={{fontFamily:T.font,fontSize:13,color:'#ef4444',fontWeight:700}}>Helytelen PIN</div>}
                      <button onClick={submitPin} style={{width:'100%',padding:'14px',borderRadius:14,border:'none',background:T.mint,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer'}}>Belépés</button>
                    </div>
                  </div>
                )}
              </React.Fragment>
            );
          })()}'''

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# ── 3. Add AdminScreen component before EventLogScreen ──
ADMIN_COMPONENT = '''
// ── AdminScreen ────────────────────────────────────────────────────────────────
function AdminScreen({ go }) {
  const [tab, setTab] = React.useState('profiles');
  const TABS = [['profiles','👤','Profilok'],['events','📅','Események'],['db','🗄️','Adatbázis']];

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Admin" onBack={() => go('home')} />
      {/* Tab switcher */}
      <div style={{ padding:'10px 16px 0' }}>
        <div style={{ display:'flex', background:T.surface, borderRadius:18, padding:4, boxShadow:T.shadow }}>
          {TABS.map(([k,icon,label]) => (
            <button key={k} onClick={() => setTab(k)} style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', gap:5, padding:'10px 0', borderRadius:14, border:'none', fontFamily:T.font, fontWeight:900, fontSize:12, cursor:'pointer', background: tab===k ? T.mint : 'transparent', color: tab===k ? '#fff' : T.inkSoft, transition:'all .2s', WebkitTapHighlightColor:'transparent' }}>
              <span>{icon}</span>{label}
            </button>
          ))}
        </div>
      </div>
      <div style={{ flex:1, overflowY:'auto' }}>
        {tab === 'profiles' && <AdminProfiles />}
        {tab === 'events'   && <AdminEvents go={go} />}
        {tab === 'db'       && <AdminDatabase />}
      </div>
    </div>
  );
}

// ── Admin: Profiles tab ────────────────────────────────────────────────────────
const AVATAR_COLORS = ['#E8631A','#25b572','#5b7cf6','#c07a10','#d63884','#0ea5e9','#8b5cf6','#ef4444'];
function AdminProfiles() {
  const [profiles, setProfiles] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [showForm, setShowForm] = React.useState(false);
  const [name, setName] = React.useState('');
  const [color, setColor] = React.useState('#E8631A');
  const [saving, setSaving] = React.useState(false);
  const [deleting, setDeleting] = React.useState(null);

  function load() {
    setLoading(true);
    if (typeof window.getProfiles === 'function') {
      window.getProfiles().then(p => { setProfiles(p || []); setLoading(false); });
    } else { setLoading(false); }
  }
  React.useEffect(() => { load(); }, []);

  function save() {
    if (!name.trim() || saving) return;
    setSaving(true);
    window.saveProfile({ name: name.trim(), color }).then(() => {
      setSaving(false); setShowForm(false); setName(''); setColor('#E8631A'); load();
    }).catch(() => setSaving(false));
  }

  function deleteProfile(id) {
    if (typeof firebase === 'undefined') return;
    setDeleting(id);
    firebase.firestore().collection('profiles').doc(id).delete().then(() => { setDeleting(null); load(); }).catch(() => setDeleting(null));
  }

  return (
    <div style={{ padding:'16px' }}>
      <button onClick={() => setShowForm(s => !s)} style={{ width:'100%', padding:'13px', borderRadius:14, border:`2px dashed ${T.mint}`, background:'transparent', fontFamily:T.font, fontWeight:900, fontSize:14, color:T.mint, cursor:'pointer', marginBottom:14 }}>
        + Új profil hozzáadása
      </button>
      {showForm && (
        <div style={{ background:T.surface, borderRadius:16, padding:'16px', marginBottom:16, boxShadow:T.shadow }}>
          <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:6 }}>Név</div>
          <input value={name} onChange={e => setName(e.target.value)} placeholder="pl. Kovács Péter" style={{ width:'100%', boxSizing:'border-box', padding:'12px', borderRadius:12, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none', marginBottom:12 }} />
          <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>Szín</div>
          <div style={{ display:'flex', gap:8, flexWrap:'wrap', marginBottom:14 }}>
            {AVATAR_COLORS.map(c => (
              <div key={c} onClick={() => setColor(c)} style={{ width:32, height:32, borderRadius:'50%', background:c, cursor:'pointer', boxShadow: color===c ? `0 0 0 3px ${T.bg}, 0 0 0 5px ${c}` : 'none', transition:'box-shadow .15s' }} />
            ))}
          </div>
          <div style={{ display:'flex', gap:8 }}>
            <button onClick={() => setShowForm(false)} style={{ flex:1, padding:'11px', borderRadius:12, border:`1.5px solid ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:700, fontSize:14, color:T.sub, cursor:'pointer' }}>Mégsem</button>
            <button onClick={save} disabled={saving||!name.trim()} style={{ flex:2, padding:'11px', borderRadius:12, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer', opacity:saving||!name.trim()?0.6:1 }}>
              {saving ? 'Mentés…' : 'Mentés'}
            </button>
          </div>
        </div>
      )}
      {loading ? (
        <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font }}>Betöltés…</div>
      ) : profiles.length === 0 ? (
        <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font, fontSize:14 }}>Még nincs profil</div>
      ) : profiles.map(p => (
        <div key={p.id} style={{ display:'flex', alignItems:'center', gap:12, background:T.surface, borderRadius:14, padding:'12px 14px', marginBottom:8, boxShadow:T.shadow }}>
          <div style={{ width:40, height:40, borderRadius:'50%', background:p.color||'#888', flexShrink:0, display:'grid', placeItems:'center', overflow:'hidden' }}>
            {p.img ? <img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff' }}>{(p.name||'?')[0].toUpperCase()}</span>}
          </div>
          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
            {p.nickname && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>{p.nickname}</div>}
          </div>
          <button onClick={() => deleteProfile(p.id)} disabled={deleting===p.id} style={{ width:36, height:36, borderRadius:10, border:'none', background:'#fef2f2', display:'grid', placeItems:'center', cursor:'pointer', opacity:deleting===p.id?0.5:1 }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
          </button>
        </div>
      ))}
    </div>
  );
}

// ── Admin: Events tab (EventCreateScreen moved here) ──────────────────────────
function AdminEvents({ go }) {
  const [events, setEvents] = React.useState(evLoad());
  const [editingId, setEditingId] = React.useState(null);
  const [showNewForm, setShowNewForm] = React.useState(false);
  const [deleteConfirm, setDeleteConfirm] = React.useState(null);

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
    <div style={{ padding:'16px' }}>
      {!showNewForm && (
        <button onClick={() => setShowNewForm(true)} style={{ width:'100%', padding:'13px', borderRadius:14, border:`2px dashed ${T.mint}`, background:'transparent', fontFamily:T.font, fontWeight:900, fontSize:14, color:T.mint, cursor:'pointer', marginBottom:14 }}>
          + Új esemény létrehozása
        </button>
      )}
      {showNewForm && (
        <div style={{ background:T.surface, borderRadius:16, padding:'16px', marginBottom:14, boxShadow:T.shadow }}>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, marginBottom:12 }}>✨ Új esemény</div>
          <EventForm onSave={saveNew} onCancel={() => setShowNewForm(false)} />
        </div>
      )}
      {events.length > 0 && (
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
                <div style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:14, padding:'12px 14px', marginBottom:8, boxShadow:T.shadow }}>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.title}</div>
                    {ev.date && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:2 }}>{new Date(ev.date).toLocaleDateString('hu-HU',{year:'numeric',month:'short',day:'numeric'})}</div>}
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
      )}
    </div>
  );
}

// ── Admin: Database tab ────────────────────────────────────────────────────────
function AdminDatabase() {
  const [profiles, setProfiles] = React.useState([]);
  const [allStats, setAllStats] = React.useState({});
  const [loading, setLoading] = React.useState(true);
  const [editing, setEditing] = React.useState(null); // profileId
  const [editVals, setEditVals] = React.useState({});
  const [saving, setSaving] = React.useState(false);
  const [saved, setSaved] = React.useState(null);

  function load() {
    setLoading(true);
    Promise.all([
      typeof window.getProfiles === 'function' ? window.getProfiles() : Promise.resolve([]),
      typeof window.getAllStats === 'function' ? window.getAllStats() : Promise.resolve({}),
    ]).then(([profs, stats]) => {
      setProfiles(profs || []);
      setAllStats(stats || {});
      setLoading(false);
    });
  }
  React.useEffect(() => { load(); }, []);

  const STAT_FIELDS = [
    { key:'totalDrinks', label:'Összes ital', type:'number' },
    { key:'gamesPlayed', label:'Játszott meccsek', type:'number' },
    { key:'wins', label:'Győzelmek', type:'number' },
    { key:'totalPoints', label:'Összes pont', type:'number' },
  ];

  function startEdit(p) {
    const st = allStats[p.id] || {};
    const vals = {};
    STAT_FIELDS.forEach(f => { vals[f.key] = st[f.key] !== undefined ? String(st[f.key]) : '0'; });
    setEditVals(vals);
    setEditing(p.id);
  }

  function saveEdit() {
    if (saving) return;
    setSaving(true);
    const updates = {};
    STAT_FIELDS.forEach(f => { updates[f.key] = Number(editVals[f.key]) || 0; });
    window.updateStats(editing, updates).then(() => {
      setAllStats(prev => ({ ...prev, [editing]: { ...(prev[editing]||{}), ...updates } }));
      setSaving(false); setSaved(editing); setEditing(null);
      setTimeout(() => setSaved(null), 2000);
    }).catch(() => setSaving(false));
  }

  if (loading) return <div style={{ textAlign:'center', padding:48, color:T.sub, fontFamily:T.font }}>Betöltés…</div>;

  return (
    <div style={{ padding:'16px' }}>
      <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>Játékos statisztikák</div>
      {profiles.map(p => {
        const st = allStats[p.id] || {};
        const isEd = editing === p.id;
        return (
          <div key={p.id} style={{ background:T.surface, borderRadius:16, padding:'14px', marginBottom:10, boxShadow:T.shadow }}>
            <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom: isEd ? 12 : 0 }}>
              <div style={{ width:36, height:36, borderRadius:'50%', background:p.color||'#888', display:'grid', placeItems:'center', flexShrink:0, overflow:'hidden' }}>
                {p.img ? <img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff' }}>{(p.name||'?')[0].toUpperCase()}</span>}
              </div>
              <div style={{ flex:1 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>{p.name}</div>
                {!isEd && <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:1 }}>
                  {st.totalDrinks||0} ital · {st.gamesPlayed||0} meccs · {st.wins||0} győz · {st.totalPoints||0} pt
                </div>}
              </div>
              {saved === p.id && <span style={{ fontSize:18 }}>✅</span>}
              {!isEd && (
                <button onClick={() => startEdit(p)} style={{ width:34, height:34, borderRadius:9, border:'none', background:T.border, display:'grid', placeItems:'center', cursor:'pointer' }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                </button>
              )}
            </div>
            {isEd && (
              <React.Fragment>
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginBottom:12 }}>
                  {STAT_FIELDS.map(f => (
                    <div key={f.key}>
                      <div style={{ fontFamily:T.font, fontSize:10, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:4 }}>{f.label}</div>
                      <input type="number" value={editVals[f.key]||'0'} onChange={e => setEditVals(prev => ({...prev,[f.key]:e.target.value}))}
                        style={{ width:'100%', boxSizing:'border-box', padding:'9px 10px', borderRadius:10, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />
                    </div>
                  ))}
                </div>
                <div style={{ display:'flex', gap:8 }}>
                  <button onClick={() => setEditing(null)} style={{ flex:1, padding:'10px', borderRadius:11, border:`1.5px solid ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:700, fontSize:13, color:T.sub, cursor:'pointer' }}>Mégsem</button>
                  <button onClick={saveEdit} disabled={saving} style={{ flex:2, padding:'10px', borderRadius:11, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer', opacity:saving?0.6:1 }}>{saving?'Mentés…':'Mentés'}</button>
                </div>
              </React.Fragment>
            )}
          </div>
        );
      })}
    </div>
  );
}

'''

# Insert AdminScreen before EventLogScreen function
assert 'function EventLogScreen' in content, "EventLogScreen not found"
content = content.replace('function EventLogScreen', ADMIN_COMPONENT + 'function EventLogScreen', 1)

# ── 4. Add admin screen to router ──
OLD4 = "        {screen==='log'      && <EventLogScreen go={go} goEdit={goEdit} />}"
NEW4 = "        {screen==='log'      && <EventLogScreen go={go} goEdit={goEdit} />}\n        {screen==='admin'    && <AdminScreen go={go} />}"
assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

# ── 5. Version bump ──
content = re.sub(r'v9\.700', 'v9.701', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.701")
