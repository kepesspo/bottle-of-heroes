import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Firestore helpers for rooms + announcement ────────────────────────────
OLD1 = "  window.getHiddenProfiles = function() {"
NEW1 = """  window.getRooms = function() {
    return db.collection('rooms').get().then(function(snap) {
      return snap.docs.map(function(d) { return Object.assign({ id: d.id }, d.data()); });
    }).catch(function() { return []; });
  };
  window.deleteRoom = function(code) {
    return db.collection('rooms').doc(code).delete().catch(function(e) { console.warn('deleteRoom', e); });
  };

  window.getAnnouncement = function() {
    return db.collection('config').doc('announcement').get().then(function(d) {
      return d.exists ? d.data() : null;
    }).catch(function() { return null; });
  };
  window.setAnnouncement = function(data) {
    return db.collection('config').doc('announcement').set(data).catch(function(e) { console.warn('setAnnouncement', e); });
  };
  window.onAnnouncement = function(cb) {
    return db.collection('config').doc('announcement').onSnapshot(function(d) {
      cb(d.exists ? d.data() : null);
    });
  };

  window.getHiddenProfiles = function() {"""
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# ── 2. Admin tabs: add rooms + message, make scrollable ──────────────────────
OLD2 = "  const TABS = [['profiles','Profilok'],['events','Események'],['db','Adatbázis'],['games','Játékok']];"
NEW2 = "  const TABS = [['profiles','Profilok'],['events','Események'],['db','Adatbázis'],['games','Játékok'],['rooms','Szobák'],['message','Hirdetmény']];"
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# Make tab bar scrollable
OLD3 = "        <div style={{ display:'flex', background:T.surface, borderRadius:18, padding:4, boxShadow:T.shadow }}>"
NEW3 = "        <div style={{ display:'flex', background:T.surface, borderRadius:18, padding:4, boxShadow:T.shadow, overflowX:'auto' }}>"
assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# Add new tab renders
OLD4 = "        {tab === 'games'    && <AdminGames />}\n      </div>"
NEW4 = "        {tab === 'games'    && <AdminGames />}\n        {tab === 'rooms'    && <AdminRooms />}\n        {tab === 'message'  && <AdminMessage />}\n      </div>"
assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

# ── 3. AdminRooms + AdminMessage components (before AdminDatabase) ───────────
ADMIN_NEW_COMPONENTS = '''// ── Admin: Rooms tab ──────────────────────────────────────────────────────────
function AdminRooms() {
  const [rooms, setRooms] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [deleting, setDeleting] = React.useState(null);

  function load() {
    setLoading(true);
    window.getRooms && window.getRooms().then(r => { setRooms(r); setLoading(false); });
  }
  React.useEffect(() => { load(); }, []);

  function deleteRoom(id) {
    setDeleting(id);
    window.deleteRoom && window.deleteRoom(id).then(() => { setDeleting(null); load(); });
  }

  const fmt = ts => {
    if (!ts) return '—';
    try {
      const d = ts.toDate ? ts.toDate() : new Date(ts);
      return d.toLocaleString('hu-HU', { month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' });
    } catch(e) { return '—'; }
  };

  return (
    <div style={{ padding:'16px' }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12 }}>
        <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em' }}>
          Aktív szobák ({rooms.length})
        </div>
        <button onClick={load} style={{ padding:'6px 12px', borderRadius:10, border:'none', background:T.surface, fontFamily:T.font, fontWeight:700, fontSize:12, color:T.mint, cursor:'pointer', boxShadow:T.shadow }}>
          Frissítés
        </button>
      </div>
      {loading ? (
        <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font }}>Betöltés…</div>
      ) : rooms.length === 0 ? (
        <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font, fontSize:14 }}>Nincs aktív szoba</div>
      ) : rooms.map(r => (
        <div key={r.id} style={{ background:T.surface, borderRadius:14, padding:'12px 14px', marginBottom:8, boxShadow:T.shadow }}>
          <div style={{ display:'flex', alignItems:'center', gap:10 }}>
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.mint, letterSpacing:2 }}>{r.id}</div>
                {r.players && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>{r.players.length} játékos</div>}
              </div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:2 }}>
                {fmt(r.createdAt)}{r.players && r.players.length > 0 ? ' · ' + r.players.map(p=>p.name||p).join(', ') : ''}
              </div>
            </div>
            <button onClick={() => deleteRoom(r.id)} disabled={deleting===r.id} style={{ width:34, height:34, borderRadius:9, border:'none', background:'#fef2f2', display:'grid', placeItems:'center', cursor:'pointer', opacity:deleting===r.id?0.5:1 }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Admin: Message/Announcement tab ───────────────────────────────────────────
function AdminMessage() {
  const [title, setTitle] = React.useState('');
  const [body, setBody] = React.useState('');
  const [active, setActive] = React.useState(false);
  const [loading, setLoading] = React.useState(true);
  const [saving, setSaving] = React.useState(false);
  const [saved, setSaved] = React.useState(false);

  React.useEffect(() => {
    if (typeof window.onAnnouncement === 'function') {
      const unsub = window.onAnnouncement(d => {
        if (d) { setTitle(d.title || ''); setBody(d.body || ''); setActive(d.active !== false); }
        else { setTitle(''); setBody(''); setActive(false); }
        setLoading(false);
      });
      return () => unsub();
    }
  }, []);

  function save() {
    if (saving) return;
    setSaving(true);
    window.setAnnouncement({ title, body, active }).then(() => {
      setSaving(false); setSaved(true); setTimeout(() => setSaved(false), 2000);
    }).catch(() => setSaving(false));
  }

  const label = s => <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:6 }}>{s}</div>;

  if (loading) return <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font }}>Betöltés…</div>;

  return (
    <div style={{ padding:'16px' }}>
      <div style={{ background:T.surface, borderRadius:16, padding:'16px', boxShadow:T.shadow }}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:16 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Hirdetmény a főoldalon</div>
          <div style={{ display:'flex', alignItems:'center', gap:8 }}>
            <div style={{ fontFamily:T.font, fontSize:12, color: active ? T.mint : T.sub, fontWeight:700 }}>{active ? 'Aktív' : 'Inaktív'}</div>
            <div onClick={() => setActive(v => !v)} style={{ width:44, height:26, borderRadius:13, background: active ? T.mint : T.inkSoft, cursor:'pointer', position:'relative', transition:'background .2s', flexShrink:0 }}>
              <div style={{ position:'absolute', top:3, left: active ? 21 : 3, width:20, height:20, borderRadius:'50%', background:'#fff', transition:'left .2s', boxShadow:'0 1px 4px rgba(0,0,0,0.2)' }} />
            </div>
          </div>
        </div>
        {label('Cím')}
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="pl. 🎉 Új funkció!" style={{ width:'100%', boxSizing:'border-box', padding:'12px', borderRadius:12, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none', marginBottom:12 }} />
        {label('Szöveg')}
        <input value={body} onChange={e => setBody(e.target.value)} placeholder="pl. Már elérhető az Ország-Város játék!" style={{ width:'100%', boxSizing:'border-box', padding:'12px', borderRadius:12, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none', marginBottom:16 }} />
        {active && title && (
          <div style={{ background:'rgba(232,99,26,0.1)', borderRadius:12, padding:'10px 14px', marginBottom:16, border:'1.5px solid rgba(232,99,26,0.3)' }}>
            <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, marginBottom:6, textTransform:'uppercase', letterSpacing:'0.05em' }}>Előnézet</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:'#E8631A' }}>{title}</div>
            {body && <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.ink, marginTop:2 }}>{body}</div>}
          </div>
        )}
        <button onClick={save} disabled={saving} style={{ width:'100%', padding:'13px', borderRadius:12, border:'none', background: saved ? T.mint : '#E8631A', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer', transition:'background .3s' }}>
          {saved ? '✓ Mentve!' : saving ? 'Mentés…' : 'Mentés'}
        </button>
      </div>
    </div>
  );
}

'''

OLD5 = "// ── Admin: Database tab ──────────────────────────────────────────────────────"
assert OLD5 in content, "OLD5 not found"
content = content.replace(OLD5, ADMIN_NEW_COMPONENTS + OLD5, 1)

# ── 4. HomeScreen: dynamic announcement instead of hardcoded callout ─────────
# Add announcement state to HomeScreen
OLD6 = "  const [splashOn, setSplashOn] = React.useState(() => localStorage.getItem('boh_splash') !== '0');"
NEW6 = """  const [splashOn, setSplashOn] = React.useState(() => localStorage.getItem('boh_splash') !== '0');
  const [announcement, setAnnouncement] = React.useState(null);
  React.useEffect(() => {
    if (typeof window.onAnnouncement === 'function') {
      const unsub = window.onAnnouncement(d => setAnnouncement(d && d.active && d.title ? d : null));
      return () => unsub();
    }
  }, []);"""
assert OLD6 in content, "OLD6 not found"
content = content.replace(OLD6, NEW6, 1)

# Replace hardcoded callout with dynamic one
OLD7 = """        {/* Callout — left side, arrow curves up-right to the pill button */}
        <div style={{ position:'absolute', top:56, left:18, zIndex:20, pointerEvents:'none' }}>
          <div style={{ background:'#E8631A', borderRadius:14, padding:'8px 14px', boxShadow:'0 4px 16px rgba(232,99,26,0.4)', textAlign:'center', display:'inline-block' }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', lineHeight:1.3 }}>🎉 Új funkció!</div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:'rgba(255,255,255,0.9)', marginTop:3 }}>DNR események</div>
          </div>
          {/* Arrow from top-right of box curving up-right to the orange pill button */}
          <svg width="130" height="75" viewBox="0 0 130 75" fill="none"
            style={{ position:'absolute', top:-55, left:110, pointerEvents:'none' }}>
            <path d="M5 70 C5 35, 60 5, 112 22" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" fill="none" strokeDasharray="5 3"/>
            <polyline points="104,16 112,22 106,28" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
          </svg>
        </div>"""
NEW7 = """        {/* Callout — dynamic announcement from Firestore */}
        {announcement && (
          <div style={{ position:'absolute', top:56, left:18, zIndex:20, pointerEvents:'none', maxWidth:'55vw' }}>
            <div style={{ background:'#E8631A', borderRadius:14, padding:'8px 14px', boxShadow:'0 4px 16px rgba(232,99,26,0.4)', display:'inline-block' }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', lineHeight:1.3 }}>{announcement.title}</div>
              {announcement.body && <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:'rgba(255,255,255,0.9)', marginTop:3 }}>{announcement.body}</div>}
            </div>
          </div>
        )}"""
assert OLD7 in content, "OLD7 not found"
content = content.replace(OLD7, NEW7, 1)

# ── 5. Version bump ──────────────────────────────────────────────────────────
content = re.sub(r'v9\.707', 'v9.708', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.708")
