import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Admin tabs: remove emojis ─────────────────────────────────────────────
OLD1 = "  const TABS = [['profiles','👤','Profilok'],['events','📅','Események'],['db','🗄️','Adatbázis'],['games','🎮','Játékok']];"
NEW1 = "  const TABS = [['profiles','Profilok'],['events','Események'],['db','Adatbázis'],['games','Játékok']];"
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# Fix the tab render (it destructures [k, icon, label] → now [k, label])
OLD2 = "          {TABS.map(([k,icon,label]) => (\n            <button key={k} onClick={() => setTab(k)} style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', gap:5, padding:'10px 0', borderRadius:14, border:'none', fontFamily:T.font, fontWeight:900, fontSize:12, cursor:'pointer', background: tab===k ? T.mint : 'transparent', color: tab===k ? '#fff' : T.inkSoft, transition:'all .2s', WebkitTapHighlightColor:'transparent' }}>\n              <span>{icon}</span>{label}\n            </button>\n          ))}"
NEW2 = "          {TABS.map(([k,label]) => (\n            <button key={k} onClick={() => setTab(k)} style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', padding:'10px 0', borderRadius:14, border:'none', fontFamily:T.font, fontWeight:900, fontSize:12, cursor:'pointer', background: tab===k ? T.mint : 'transparent', color: tab===k ? '#fff' : T.inkSoft, transition:'all .2s', WebkitTapHighlightColor:'transparent' }}>\n              {label}\n            </button>\n          ))}"
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# ── 2. Profile hide/show in Firestore ────────────────────────────────────────
# Add hiddenProfiles Firestore helpers alongside hiddenGames helpers
OLD3 = "  window.getHiddenGames = function() {"
NEW3 = """  window.getHiddenProfiles = function() {
    return db.collection('config').doc('hiddenProfiles').get().then(function(d) {
      return d.exists ? (d.data().ids || []) : [];
    }).catch(function() { return []; });
  };
  window.setHiddenProfiles = function(ids) {
    return db.collection('config').doc('hiddenProfiles').set({ ids: ids }).catch(function(e) { console.warn('setHiddenProfiles', e); });
  };
  window.onHiddenProfiles = function(cb) {
    return db.collection('config').doc('hiddenProfiles').onSnapshot(function(d) {
      cb(d.exists ? (d.data().ids || []) : []);
    });
  };

  window.getHiddenGames = function() {"""
assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# ── 3. AdminProfiles: add hide toggle per profile ────────────────────────────
OLD4 = """function AdminProfiles() {
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
  React.useEffect(() => { load(); }, []);"""
NEW4 = """function AdminProfiles() {
  const [profiles, setProfiles] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [showForm, setShowForm] = React.useState(false);
  const [name, setName] = React.useState('');
  const [color, setColor] = React.useState('#E8631A');
  const [saving, setSaving] = React.useState(false);
  const [deleting, setDeleting] = React.useState(null);
  const [hiddenProfs, setHiddenProfs] = React.useState([]);

  function load() {
    setLoading(true);
    if (typeof window.getProfiles === 'function') {
      window.getProfiles().then(p => { setProfiles(p || []); setLoading(false); });
    } else { setLoading(false); }
  }
  React.useEffect(() => { load(); }, []);
  React.useEffect(() => {
    if (typeof window.onHiddenProfiles === 'function') {
      const unsub = window.onHiddenProfiles(ids => setHiddenProfs(ids));
      return () => unsub();
    }
  }, []);

  function toggleHideProfile(id) {
    const next = hiddenProfs.includes(id) ? hiddenProfs.filter(x => x !== id) : [...hiddenProfs, id];
    window.setHiddenProfiles && window.setHiddenProfiles(next);
  }"""
assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

# Add hide button to each profile row (after delete button)
OLD5 = """          <button onClick={() => deleteProfile(p.id)} disabled={deleting===p.id} style={{ width:36, height:36, borderRadius:10, border:'none', background:'#fef2f2', display:'grid', placeItems:'center', cursor:'pointer', opacity:deleting===p.id?0.5:1 }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
          </button>"""
NEW5 = """          <button onClick={() => toggleHideProfile(p.id)} style={{ width:36, height:36, borderRadius:10, border:`1.5px solid ${hiddenProfs.includes(p.id) ? '#ef4444' : T.mint}`, background: hiddenProfs.includes(p.id) ? '#fef2f2' : 'rgba(37,181,114,0.08)', display:'grid', placeItems:'center', cursor:'pointer' }}>
            {hiddenProfs.includes(p.id) ? (
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            ) : (
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={T.mint} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            )}
          </button>
          <button onClick={() => deleteProfile(p.id)} disabled={deleting===p.id} style={{ width:36, height:36, borderRadius:10, border:'none', background:'#fef2f2', display:'grid', placeItems:'center', cursor:'pointer', opacity:deleting===p.id?0.5:1 }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
          </button>"""
assert OLD5 in content, "OLD5 not found"
content = content.replace(OLD5, NEW5, 1)

# ── 4. Calendar: bigger header, bigger buttons, side padding ─────────────────
OLD6 = "    <div style={{ flex:1, overflowY:'auto', padding:'6px 6px 24px' }} onTouchStart={onSwipeStart} onTouchEnd={onSwipeEnd}>\n      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:4 }}>\n        <button onClick={() => setCalMonth(new Date(year, month-1, 1))} style={{ width:26, height:26, borderRadius:7, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>\n          <svg width=\"11\" height=\"11\" viewBox=\"0 0 24 24\" fill=\"none\" stroke={T.ink} strokeWidth=\"2\" strokeLinecap=\"round\" strokeLinejoin=\"round\"><polyline points=\"15 18 9 12 15 6\"/></svg>\n        </button>\n        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.ink }}>{HU_MONTHS[month]} {year}</div>\n        <button onClick={() => setCalMonth(new Date(year, month+1, 1))} style={{ width:26, height:26, borderRadius:7, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>\n          <svg width=\"11\" height=\"11\" viewBox=\"0 0 24 24\" fill=\"none\" stroke={T.ink} strokeWidth=\"2\" strokeLinecap=\"round\" strokeLinejoin=\"round\"><polyline points=\"9 18 15 12 9 6\"/></svg>\n        </button>\n      </div>"
NEW6 = "    <div style={{ flex:1, overflowY:'auto', padding:'8px 12px 24px' }} onTouchStart={onSwipeStart} onTouchEnd={onSwipeEnd}>\n      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:6 }}>\n        <button onClick={() => setCalMonth(new Date(year, month-1, 1))} style={{ width:34, height:34, borderRadius:10, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>\n          <svg width=\"14\" height=\"14\" viewBox=\"0 0 24 24\" fill=\"none\" stroke={T.ink} strokeWidth=\"2.5\" strokeLinecap=\"round\" strokeLinejoin=\"round\"><polyline points=\"15 18 9 12 15 6\"/></svg>\n        </button>\n        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink }}>{HU_MONTHS[month]} {year}</div>\n        <button onClick={() => setCalMonth(new Date(year, month+1, 1))} style={{ width:34, height:34, borderRadius:10, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>\n          <svg width=\"14\" height=\"14\" viewBox=\"0 0 24 24\" fill=\"none\" stroke={T.ink} strokeWidth=\"2.5\" strokeLinecap=\"round\" strokeLinejoin=\"round\"><polyline points=\"9 18 15 12 9 6\"/></svg>\n        </button>\n      </div>"
assert OLD6 in content, "OLD6 not found"
content = content.replace(OLD6, NEW6, 1)

# ── 5. Version bump ──────────────────────────────────────────────────────────
content = re.sub(r'v9\.703', 'v9.704', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.704")
