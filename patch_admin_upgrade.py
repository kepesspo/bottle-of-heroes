import re
with open('index.html', encoding='utf-8') as f:
    c = f.read()

# ═══ 0. Firebase helperek: admin PIN + force reload ═══════════════════════════
OLD = """  // Load blacklist eagerly on startup
  window.loadZeneBadList();"""
NEW = """  // Load blacklist eagerly on startup
  window.loadZeneBadList();
  // ── Admin PIN + kényszerített frissítés ──
  window.getAdminPin = function() {
    return db.collection('config').doc('adminPin').get().then(function(d) {
      return d.exists ? (d.data().pin || '') : '';
    }).catch(function() { return ''; });
  };
  window.setAdminPin = function(pin) {
    return db.collection('config').doc('adminPin').set({ pin: pin || '' });
  };
  window.triggerForceReload = function() {
    return db.collection('config').doc('forceReload').set({ ts: Date.now() });
  };
  window._bohLoadTs = Date.now();
  try {
    db.collection('config').doc('forceReload').onSnapshot(function(d) {
      var ts = d.exists && d.data().ts;
      if (ts && ts > window._bohLoadTs) { location.reload(); }
    });
  } catch(e) {}"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 1. AdminDatabase (halott kód) törlése ════════════════════════════════════
si = c.index("// ── Admin: Database tab ─")
ei = c.index("\nfunction EventLogScreen(", si)
c = c[:si] + c[ei+1:]

# ═══ 2. AdminScreen: új tabok + PIN kapu ══════════════════════════════════════
OLD = """function AdminScreen({ go }) {
  const [tab, setTab] = React.useState('profiles');
  const TABS = [['profiles','Profilok'],['events','Események'],['games','Játékok'],['rooms','Szobák'],['message','Hirdetmény'],['settings','Beállítások']];"""
NEW = """function AdminScreen({ go }) {
  const [tab, setTab] = React.useState('profiles');
  const TABS = [['profiles','Profilok'],['events','Események'],['games','Játékok'],['stats','Statisztika'],['zene','Zene'],['rooms','Szobák'],['message','Hirdetmény'],['settings','Beállítások']];
  const [pinOk, setPinOk] = React.useState(null);
  const [reqPin, setReqPin] = React.useState('');
  const [pinInput, setPinInput] = React.useState('');
  const [pinErr, setPinErr] = React.useState(false);

  React.useEffect(() => {
    (window.getAdminPin ? window.getAdminPin() : Promise.resolve('')).then(p => {
      setReqPin(p || '');
      let ok = !p;
      try { if (p && localStorage.getItem('boh_admin_ok') === p) ok = true; } catch(e) {}
      setPinOk(ok);
    }).catch(() => setPinOk(true));
  }, []);

  if (pinOk === null) return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg }}>
      <AppBar title="Admin" onBack={() => go('home')} />
      <div style={{ flex:1, display:'grid', placeItems:'center', fontFamily:T.font, color:T.sub }}>Betöltés…</div>
    </div>
  );
  if (!pinOk) return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg }}>
      <AppBar title="Admin" onBack={() => go('home')} />
      <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:14, padding:24 }}>
        <div style={{ fontSize:42 }}>🔐</div>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink }}>Admin PIN szükséges</div>
        <input type="password" inputMode="numeric" value={pinInput} onChange={e => { setPinInput(e.target.value); setPinErr(false); }}
          onKeyDown={e => { if (e.key === 'Enter' && pinInput === reqPin) { try { localStorage.setItem('boh_admin_ok', reqPin); } catch(err) {} setPinOk(true); } }}
          placeholder="PIN kód" style={{ width:180, boxSizing:'border-box', padding:'13px', borderRadius:14, border:`2px solid ${pinErr ? '#ef4444' : T.border}`, background:T.surface, fontFamily:T.font, fontSize:18, textAlign:'center', letterSpacing:4, color:T.ink, outline:'none' }} />
        {pinErr && <div style={{ fontFamily:T.font, fontSize:12, color:'#ef4444', fontWeight:700 }}>Hibás PIN</div>}
        <button onClick={() => { if (pinInput === reqPin) { try { localStorage.setItem('boh_admin_ok', reqPin); } catch(e) {} setPinOk(true); } else setPinErr(true); }}
          style={{ width:180, padding:'13px', borderRadius:14, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>Belépés</button>
      </div>
    </div>
  );"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

OLD = """        {tab === 'rooms'    && <AdminRooms />}"""
NEW = """        {tab === 'stats'    && <AdminStats />}
        {tab === 'zene'     && <AdminZene />}
        {tab === 'rooms'    && <AdminRooms />}"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 3. Új komponensek: AdminStats, AdminZene, ProfileMergeCard ══════════════
OLD = """// ── Admin: Games tab ──────────────────────────────────────────────────────────
function AdminGames() {"""
NEW = """// ── Admin: Statisztika tab ────────────────────────────────────────────────────
function AdminStats() {
  const [profiles, setProfiles] = React.useState([]);
  const [stats, setStats] = React.useState({});
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    Promise.all([
      window.getProfiles ? window.getProfiles() : Promise.resolve([]),
      window.getAllStats ? window.getAllStats() : Promise.resolve({}),
    ]).then(([ps, st]) => { setProfiles(ps || []); setStats(st || {}); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font }}>Betöltés…</div>;

  const rows = profiles.map(p => ({ p, s: stats[p.id] || {} }));
  const sum = key => rows.reduce((a, r) => a + (r.s[key] || 0), 0);
  const Board = ({ title, emoji, valFn, fmt }) => {
    const top = [...rows].filter(r => (valFn(r.s) || 0) > 0).sort((a, b) => valFn(b.s) - valFn(a.s)).slice(0, 5);
    return (
      <div style={{ background:T.surface, borderRadius:16, padding:'14px 16px', boxShadow:T.shadow, marginBottom:12 }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, marginBottom:10 }}>{emoji} {title}</div>
        {top.length === 0 && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>Még nincs adat</div>}
        {top.map((r, i) => (
          <div key={r.p.id} style={{ display:'flex', alignItems:'center', gap:10, padding:'5px 0', borderBottom: i < top.length-1 ? `1px solid ${T.border}` : 'none' }}>
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color: i===0 ? '#F59E0B' : T.sub, width:22 }}>{i===0?'🥇':i===1?'🥈':i===2?'🥉':(i+1)+'.'}</span>
            {r.p.img ? <img src={r.p.img} style={{ width:26, height:26, borderRadius:'50%', objectFit:'cover' }} /> : <div style={{ width:26, height:26, borderRadius:'50%', background:r.p.color||'#888', display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff' }}>{(r.p.name||'?')[0].toUpperCase()}</div>}
            <span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink, flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{r.p.nickname || r.p.name}</span>
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.mint }}>{fmt ? fmt(valFn(r.s)) : valFn(r.s)}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div style={{ padding:'16px' }}>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:10, marginBottom:14 }}>
        {[
          { emoji:'👤', label:'Profil', val: profiles.length },
          { emoji:'⭐', label:'Össz pont', val: sum('totalPoints') },
          { emoji:'🍺', label:'Össz korty', val: sum('totalDrinks') },
        ].map((it, i) => (
          <div key={i} style={{ background:T.surface, borderRadius:14, padding:'12px 8px', boxShadow:T.shadow, textAlign:'center' }}>
            <div style={{ fontSize:20 }}>{it.emoji}</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink, marginTop:2 }}>{it.val}</div>
            <div style={{ fontFamily:T.font, fontSize:10, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.05em' }}>{it.label}</div>
          </div>
        ))}
      </div>
      <Board title="Toplista — pontok" emoji="⭐" valFn={s => s.totalPoints || 0} />
      <Board title="Toplista — kortyok" emoji="🍺" valFn={s => s.totalDrinks || 0} />
      <Board title="Beer Pong győzelmek" emoji="🏓" valFn={s => s.bp_match_wins || 0} />
      <Board title="Busz — teljesítések" emoji="🚌" valFn={s => s.busz_completions || 0} />
    </div>
  );
}

// ── Admin: Zene (tiltólista) tab ──────────────────────────────────────────────
function AdminZene() {
  const [items, setItems] = React.useState(null);
  const [busy, setBusy] = React.useState(false);
  const [confirmAll, setConfirmAll] = React.useState(false);

  const load = () => {
    firebase.firestore().collection('zene_blacklist').get().then(snap => {
      setItems(snap.docs.map(d => ({ id: d.id, ...d.data() })));
    }).catch(() => setItems([]));
  };
  React.useEffect(load, []);

  const songOf = id => (typeof ZENE_SONGS !== 'undefined' ? ZENE_SONGS.find(s => s.spotifyId === id) : null);
  const localClear = id => {
    window._zeneBadIds && window._zeneBadIds.delete(id);
    try { localStorage.removeItem('znobad_' + id); } catch(e) {}
  };
  const unban = id => {
    if (busy) return; setBusy(true);
    firebase.firestore().collection('zene_blacklist').doc(id).delete()
      .then(() => { localClear(id); load(); }).finally(() => setBusy(false));
  };
  const clearAll = () => {
    if (busy || !items || !items.length) return; setBusy(true); setConfirmAll(false);
    const db2 = firebase.firestore();
    const batch = db2.batch();
    items.forEach(it => batch.delete(db2.collection('zene_blacklist').doc(it.id)));
    batch.commit().then(() => { items.forEach(it => localClear(it.id)); load(); }).finally(() => setBusy(false));
  };
  const fmt = ts => { try { const d = ts && ts.toDate ? ts.toDate() : null; return d ? d.toLocaleDateString('hu-HU', { month:'short', day:'numeric' }) : ''; } catch(e) { return ''; } };

  if (items === null) return <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font }}>Betöltés…</div>;

  return (
    <div style={{ padding:'16px' }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12 }}>
        <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em' }}>
          Tiltott számok ({items.length} / {typeof ZENE_SONGS !== 'undefined' ? ZENE_SONGS.length : '?'})
        </div>
        <div style={{ display:'flex', gap:8 }}>
          <button onClick={load} style={{ padding:'6px 12px', borderRadius:10, border:'none', background:T.surface, fontFamily:T.font, fontWeight:700, fontSize:12, color:T.mint, cursor:'pointer', boxShadow:T.shadow }}>Frissítés</button>
          {items.length > 0 && (confirmAll ? (
            <button onClick={clearAll} style={{ padding:'6px 12px', borderRadius:10, border:'none', background:'#ef4444', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#fff', cursor:'pointer' }}>Biztos? Mind törlése</button>
          ) : (
            <button onClick={() => setConfirmAll(true)} style={{ padding:'6px 12px', borderRadius:10, border:'none', background:'#fef2f2', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#ef4444', cursor:'pointer' }}>Összes visszaengedése</button>
          ))}
        </div>
      </div>
      {items.length === 0 && (
        <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font, fontSize:14 }}>🎉 A tiltólista üres — minden szám játszható</div>
      )}
      {items.map(it => {
        const s = songOf(it.id);
        return (
          <div key={it.id} style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:14, padding:'10px 14px', marginBottom:8, boxShadow:T.shadow }}>
            <span style={{ fontSize:18, flexShrink:0 }}>🎵</span>
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{s ? `${s.artist} — ${s.title}` : it.id}</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:1 }}>{s ? `${s.era || ''} ${s.genre || ''}` : 'ismeretlen szám'}{it.ts ? ' · tiltva: ' + fmt(it.ts) : ''}</div>
            </div>
            <button onClick={() => unban(it.id)} disabled={busy} style={{ padding:'7px 12px', borderRadius:10, border:'none', background:'rgba(37,181,114,0.1)', fontFamily:T.font, fontWeight:800, fontSize:12, color:T.mint, cursor:'pointer', flexShrink:0, opacity:busy?0.5:1 }}>↩ Vissza</button>
          </div>
        );
      })}
    </div>
  );
}

// ── Admin: profil összevonás kártya ───────────────────────────────────────────
function ProfileMergeCard({ profiles, onDone }) {
  const [open, setOpen] = React.useState(false);
  const [srcId, setSrcId] = React.useState('');
  const [dstId, setDstId] = React.useState('');
  const [busy, setBusy] = React.useState(false);

  const doMerge = () => {
    if (!srcId || !dstId || srcId === dstId || busy) return;
    setBusy(true);
    const db2 = firebase.firestore();
    Promise.all([
      db2.collection('stats').doc(srcId).get(), db2.collection('stats').doc(dstId).get(),
      db2.collection('profiles').doc(srcId).get(), db2.collection('profiles').doc(dstId).get(),
    ]).then(([ss, ds, sp, dp]) => {
      const s = ss.exists ? ss.data() : {}, d = ds.exists ? ds.data() : {};
      const merged = { ...d };
      Object.keys(s).forEach(k => {
        if (typeof s[k] === 'number') merged[k] = k.indexOf('best') === 0 ? Math.max(d[k] || 0, s[k]) : ((typeof d[k] === 'number' ? d[k] : 0) + s[k]);
        else if (merged[k] === undefined) merged[k] = s[k];
      });
      const spd = sp.exists ? sp.data() : {}, dpd = dp.exists ? dp.data() : {};
      const profPatch = {};
      ['nickname', 'phone', 'birthday', 'img'].forEach(k => { if (!dpd[k] && spd[k]) profPatch[k] = spd[k]; });
      const batch = db2.batch();
      batch.set(db2.collection('stats').doc(dstId), merged);
      if (Object.keys(profPatch).length) batch.set(db2.collection('profiles').doc(dstId), profPatch, { merge: true });
      batch.delete(db2.collection('profiles').doc(srcId));
      batch.delete(db2.collection('stats').doc(srcId));
      return batch.commit();
    }).then(() => { setSrcId(''); setDstId(''); setOpen(false); onDone && onDone(); }).finally(() => setBusy(false));
  };

  const selStyle = { width:'100%', boxSizing:'border-box', padding:'11px', borderRadius:11, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' };
  return (
    <div style={{ background:T.surface, borderRadius:16, padding:'12px 16px', marginBottom:14, boxShadow:T.shadow }}>
      <div onClick={() => setOpen(o => !o)} style={{ display:'flex', alignItems:'center', justifyContent:'space-between', cursor:'pointer' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.ink }}>🔀 Duplikált profilok összevonása</div>
        <span style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>{open ? '▲' : '▼'}</span>
      </div>
      {open && (
        <div style={{ marginTop:12, display:'flex', flexDirection:'column', gap:10 }}>
          <div>
            <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, marginBottom:4 }}>EZT olvasztjuk be (törlődik):</div>
            <select value={srcId} onChange={e => setSrcId(e.target.value)} style={selStyle}>
              <option value="">— válassz —</option>
              {profiles.filter(p => p.id !== dstId).map(p => <option key={p.id} value={p.id}>{p.name}{p.nickname ? ` (${p.nickname})` : ''}</option>)}
            </select>
          </div>
          <div>
            <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, marginBottom:4 }}>EBBE (megmarad, statok összeadódnak):</div>
            <select value={dstId} onChange={e => setDstId(e.target.value)} style={selStyle}>
              <option value="">— válassz —</option>
              {profiles.filter(p => p.id !== srcId).map(p => <option key={p.id} value={p.id}>{p.name}{p.nickname ? ` (${p.nickname})` : ''}</option>)}
            </select>
          </div>
          <button onClick={doMerge} disabled={!srcId || !dstId || busy} style={{ padding:'12px', borderRadius:12, border:'none', background: (!srcId || !dstId) ? T.border : '#E8631A', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer', opacity: busy ? 0.6 : 1 }}>
            {busy ? 'Összevonás…' : 'Összevonás'}
          </button>
        </div>
      )}
    </div>
  );
}

// ── Admin: Games tab ──────────────────────────────────────────────────────────
function AdminGames() {"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 4. AdminProfiles: merge kártya beszúrása ═════════════════════════════════
OLD = """  return (
    <div style={{ padding:'16px' }}>
      {birthdayToday.length > 0 && ("""
NEW = """  return (
    <div style={{ padding:'16px' }}>
      {profiles.length >= 2 && <ProfileMergeCard profiles={profiles} onDone={load} />}
      {birthdayToday.length > 0 && ("""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 5. AdminRooms: régi szobák törlése + observer belépés ════════════════════
OLD = """        <button onClick={load} style={{ padding:'6px 12px', borderRadius:10, border:'none', background:T.surface, fontFamily:T.font, fontWeight:700, fontSize:12, color:T.mint, cursor:'pointer', boxShadow:T.shadow }}>
          Frissítés
        </button>
      </div>"""
NEW = """        <button onClick={load} style={{ padding:'6px 12px', borderRadius:10, border:'none', background:T.surface, fontFamily:T.font, fontWeight:700, fontSize:12, color:T.mint, cursor:'pointer', boxShadow:T.shadow }}>
          Frissítés
        </button>
      </div>
      {(() => {
        const weekAgo = Date.now() - 7 * 86400000;
        const old = rooms.filter(r => { try { const d = r.createdAt && (r.createdAt.toDate ? r.createdAt.toDate() : new Date(r.createdAt)); return d && d.getTime() < weekAgo; } catch(e) { return false; } });
        if (!old.length) return null;
        return (
          <button onClick={() => { setLoading(true); Promise.all(old.map(r => window.deleteRoom(r.id))).finally(load); }}
            style={{ width:'100%', padding:'11px', borderRadius:12, border:'none', background:'#fef2f2', fontFamily:T.font, fontWeight:800, fontSize:13, color:'#ef4444', cursor:'pointer', marginBottom:12 }}>
            🧹 {old.length} db 1 hétnél régebbi szoba törlése
          </button>
        );
      })()}"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

OLD = """            <button onClick={() => deleteRoom(r.id)} disabled={deleting===r.id} style={{ width:34, height:34, borderRadius:9, border:'none', background:'#fef2f2', display:'grid', placeItems:'center', cursor:'pointer', opacity:deleting===r.id?0.5:1 }}>"""
NEW = """            <button onClick={() => window.open(window.location.pathname + '?room=' + r.id, '_blank')} title="Belépés observerként" style={{ width:34, height:34, borderRadius:9, border:'none', background:'rgba(37,181,114,0.1)', display:'grid', placeItems:'center', cursor:'pointer', flexShrink:0 }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={T.mint} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
            <button onClick={() => deleteRoom(r.id)} disabled={deleting===r.id} style={{ width:34, height:34, borderRadius:9, border:'none', background:'#fef2f2', display:'grid', placeItems:'center', cursor:'pointer', opacity:deleting===r.id?0.5:1 }}>"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 6. AdminMessage: lejárati dátum ══════════════════════════════════════════
OLD = """        if (d) { setTitle(d.title || ''); setBody(d.body || ''); setActive(d.active !== false); }
        else { setTitle(''); setBody(''); setActive(false); }"""
NEW = """        if (d) { setTitle(d.title || ''); setBody(d.body || ''); setActive(d.active !== false); setUntil(d.until || ''); }
        else { setTitle(''); setBody(''); setActive(false); setUntil(''); }"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

OLD = """  const [saved, setSaved] = React.useState(false);

  React.useEffect(() => {
    if (typeof window.onAnnouncement === 'function') {"""
NEW = """  const [saved, setSaved] = React.useState(false);
  const [until, setUntil] = React.useState('');

  React.useEffect(() => {
    if (typeof window.onAnnouncement === 'function') {"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

OLD = """    window.setAnnouncement({ title, body, active }).then(() => {"""
NEW = """    window.setAnnouncement({ title, body, active, until: until || null }).then(() => {"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

OLD = """        {label('Szöveg')}
        <input value={body} onChange={e => setBody(e.target.value)} placeholder="pl. Már elérhető az Ország-Város játék!" style={{ width:'100%', boxSizing:'border-box', padding:'12px', borderRadius:12, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none', marginBottom:16 }} />"""
NEW = """        {label('Szöveg')}
        <input value={body} onChange={e => setBody(e.target.value)} placeholder="pl. Már elérhető az Ország-Város játék!" style={{ width:'100%', boxSizing:'border-box', padding:'12px', borderRadius:12, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none', marginBottom:12 }} />
        {label('Lejárat (opcionális — eddig a napig látszik)')}
        <input type="date" value={until} onChange={e => setUntil(e.target.value)} style={{ width:'100%', boxSizing:'border-box', padding:'12px', borderRadius:12, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none', marginBottom:16 }} />"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# fogyasztó: lejárt hirdetmény nem jelenik meg
OLD = """      const unsub = window.onAnnouncement(d => setAnnouncement(d && d.active && d.title ? d : null));"""
NEW = """      const unsub = window.onAnnouncement(d => setAnnouncement(d && d.active && d.title && (!d.until || new Date(d.until + 'T23:59:59') >= new Date()) ? d : null));"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 7. AdminEvents: esemény duplikálás gomb ══════════════════════════════════
OLD = """                    <button onClick={() => setEditingId(ev.id)} style={{ width:34, height:34, borderRadius:9, border:'none', background:T.border, display:'grid', placeItems:'center', cursor:'pointer', flexShrink:0 }}>"""
NEW = """                    <button onClick={() => { const col = evDb(); if (!col) return; const copy = { ...ev, title: (ev.title || '') + ' (másolat)', rsvp: {}, createdAt: new Date().toISOString() }; delete copy.id; delete copy.sortOrder; col.add(copy); }} title="Duplikálás" style={{ width:34, height:34, borderRadius:9, border:'none', background:'rgba(37,181,114,0.1)', display:'grid', placeItems:'center', cursor:'pointer', flexShrink:0 }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.mint} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
                    </button>
                    <button onClick={() => setEditingId(ev.id)} style={{ width:34, height:34, borderRadius:9, border:'none', background:T.border, display:'grid', placeItems:'center', cursor:'pointer', flexShrink:0 }}>"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 8. AdminSettings: PIN beállítás + force refresh ══════════════════════════
OLD = """        {saving && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, textAlign:'center', marginTop:10 }}>Mentés…</div>}
      </div>
    </div>
  );
}"""
NEW = """        {saving && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, textAlign:'center', marginTop:10 }}>Mentés…</div>}
      </div>

      <AdminPinCard />

      <div style={{ background:T.surface, borderRadius:16, padding:16, boxShadow:T.shadow, marginTop:14 }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink, marginBottom:4 }}>Kényszerített frissítés</div>
        <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginBottom:12 }}>Minden megnyitott app azonnal újratölt — deploy után hasznos, ha valakinél régi verzió ragadt be.</div>
        <ForceReloadButton />
      </div>
    </div>
  );
}

function ForceReloadButton() {
  const [confirm, setConfirm] = React.useState(false);
  const [done, setDone] = React.useState(false);
  if (done) return <div style={{ fontFamily:T.font, fontSize:13, color:T.mint, fontWeight:800, textAlign:'center', padding:'8px 0' }}>✓ Frissítés kiküldve (ez az eszköz is újratölt…)</div>;
  return confirm ? (
    <div style={{ display:'flex', gap:8 }}>
      <button onClick={() => { setDone(true); window.triggerForceReload && window.triggerForceReload(); }} style={{ flex:1, padding:'12px', borderRadius:12, border:'none', background:'#ef4444', fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>Biztos — frissítés most</button>
      <button onClick={() => setConfirm(false)} style={{ flex:1, padding:'12px', borderRadius:12, border:`1.5px solid ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:700, fontSize:13, color:T.sub, cursor:'pointer' }}>Mégsem</button>
    </div>
  ) : (
    <button onClick={() => setConfirm(true)} style={{ width:'100%', padding:'12px', borderRadius:12, border:'none', background:'#E8631A', fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>🔄 Mindenki frissítése</button>
  );
}

function AdminPinCard() {
  const [pin, setPin] = React.useState('');
  const [cur, setCur] = React.useState(null);
  const [saving, setSaving] = React.useState(false);
  const [saved, setSaved] = React.useState(false);

  React.useEffect(() => {
    (window.getAdminPin ? window.getAdminPin() : Promise.resolve('')).then(p => { setCur(p || ''); setPin(p || ''); });
  }, []);

  function save() {
    if (saving) return; setSaving(true);
    window.setAdminPin(pin.trim()).then(() => {
      setCur(pin.trim());
      try { if (pin.trim()) localStorage.setItem('boh_admin_ok', pin.trim()); else localStorage.removeItem('boh_admin_ok'); } catch(e) {}
      setSaved(true); setTimeout(() => setSaved(false), 2000);
    }).finally(() => setSaving(false));
  }

  if (cur === null) return null;
  return (
    <div style={{ background:T.surface, borderRadius:16, padding:16, boxShadow:T.shadow, marginTop:14 }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink, marginBottom:4 }}>Admin PIN</div>
      <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginBottom:12 }}>{cur ? 'A belépéshez PIN kell. Üresen hagyva kikapcsolod.' : 'Nincs PIN — az admin felület bárkinek elérhető.'}</div>
      <div style={{ display:'flex', gap:8 }}>
        <input value={pin} onChange={e => setPin(e.target.value)} placeholder="pl. 1234" inputMode="numeric" style={{ flex:1, boxSizing:'border-box', padding:'12px', borderRadius:12, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none' }} />
        <button onClick={save} disabled={saving} style={{ padding:'12px 18px', borderRadius:12, border:'none', background: saved ? T.mint : '#E8631A', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>{saved ? '✓' : 'Mentés'}</button>
      </div>
    </div>
  );
}"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

c = re.sub(r'v9\.787', 'v9.788', c, count=2)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Done v9.788")
