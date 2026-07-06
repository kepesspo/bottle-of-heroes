#!/usr/bin/env python3
# v9.794 — Lokátor: festival friend locator (live location sharing)
import io

P = '/home/user/bottle-of-heroes/index.html'
c = io.open(P, encoding='utf-8').read()

def rep(old, new, count=1):
    global c
    assert c.count(old) == count, 'OLD not found or not unique (%d): %r' % (c.count(old), old[:80])
    c = c.replace(old, new, count)

# ── 1. LocatorScreen component + helpers, inserted before EventLogScreen ──
OLD1 = "function EventLogScreen({ go, goEdit, deepLink }) {"
NEW1 = r"""// ── Lokátor: festival friend locator ──────────────────────────────────────────
function locDb() { return typeof firebase !== 'undefined' ? firebase.firestore().collection('locations') : null; }
function locHaversineM(a, b) {
  const R = 6371000, toR = x => x * Math.PI / 180;
  const dLat = toR(b.lat - a.lat), dLng = toR(b.lng - a.lng);
  const s = Math.sin(dLat/2)*Math.sin(dLat/2) + Math.cos(toR(a.lat))*Math.cos(toR(b.lat))*Math.sin(dLng/2)*Math.sin(dLng/2);
  return 2 * R * Math.asin(Math.sqrt(s));
}
function locBearingDeg(a, b) {
  const toR = x => x * Math.PI / 180;
  const y = Math.sin(toR(b.lng - a.lng)) * Math.cos(toR(b.lat));
  const x = Math.cos(toR(a.lat)) * Math.sin(toR(b.lat)) - Math.sin(toR(a.lat)) * Math.cos(toR(b.lat)) * Math.cos(toR(b.lng - a.lng));
  return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
}
function locFmtDist(m) { return m < 1000 ? Math.round(m) + ' m' : (m/1000).toFixed(1).replace('.', ',') + ' km'; }
function locFmtAgo(ms) {
  const s = Math.max(0, Math.round(ms / 1000));
  if (s < 60) return 'frissítve ' + s + ' másodperce';
  return 'frissítve ' + Math.round(s / 60) + ' perce';
}

function LocatorScreen({ T, profiles, onClose }) {
  const LOC_MAX_AGE = 20 * 60 * 1000;
  const [meId, setMeId] = React.useState(() => localStorage.getItem('boh_locator_me') || null);
  const me = profiles.find(p => String(p.id) === String(meId)) || null;
  const [sharing, setSharing] = React.useState(false);
  const [myPos, setMyPos] = React.useState(null);
  const [geoErr, setGeoErr] = React.useState(null);
  const [entries, setEntries] = React.useState([]);
  const [now, setNow] = React.useState(Date.now());
  const watchRef = React.useRef(null);
  const lastWriteRef = React.useRef({ t: 0, lat: null, lng: null });

  React.useEffect(() => { const iv = setInterval(() => setNow(Date.now()), 5000); return () => clearInterval(iv); }, []);

  // Live list of everyone sharing
  React.useEffect(() => {
    const col = locDb();
    if (!col) return;
    const unsub = col.onSnapshot(snap => setEntries(snap.docs.map(d => ({ id: d.id, ...d.data() }))), () => {});
    return () => unsub();
  }, []);

  function pickMe(p) { localStorage.setItem('boh_locator_me', String(p.id)); setMeId(String(p.id)); }

  function writeMyLoc(pos, force) {
    const col = locDb();
    if (!col || !me) return;
    const { latitude: lat, longitude: lng, accuracy: acc } = pos.coords;
    const lw = lastWriteRef.current;
    if (!force && lw.lat !== null) {
      const moved = locHaversineM({ lat: lw.lat, lng: lw.lng }, { lat, lng });
      if (moved < 15 && Date.now() - lw.t < 20000) return;
    }
    lastWriteRef.current = { t: Date.now(), lat, lng };
    const doc = { name: me.name || '?', nickname: me.nickname || null, color: me.color || null, lat, lng, acc: Math.round(acc || 0), ts: Date.now() };
    if (me.img && !(typeof me.img === 'string' && me.img.startsWith('data:') && me.img.length > 500)) doc.img = me.img;
    col.doc(String(me.id)).set(doc).catch(() => {});
  }

  function stopSharing() {
    if (watchRef.current !== null && navigator.geolocation) { navigator.geolocation.clearWatch(watchRef.current); watchRef.current = null; }
    lastWriteRef.current = { t: 0, lat: null, lng: null };
    const col = locDb();
    if (col && me) col.doc(String(me.id)).delete().catch(() => {});
  }

  React.useEffect(() => {
    if (!sharing || !me) return;
    if (!navigator.geolocation) { setGeoErr('unsupported'); setSharing(false); return; }
    setGeoErr(null);
    watchRef.current = navigator.geolocation.watchPosition(
      pos => { setMyPos({ lat: pos.coords.latitude, lng: pos.coords.longitude }); writeMyLoc(pos, lastWriteRef.current.lat === null); },
      err => { setGeoErr(err.code === 1 ? 'denied' : 'error'); setSharing(false); },
      { enableHighAccuracy: true, maximumAge: 5000, timeout: 20000 }
    );
    return () => stopSharing();
  }, [sharing, meId]);

  const fresh = entries.filter(e => e.ts && (now - e.ts) < LOC_MAX_AGE);
  const others = fresh.filter(e => !me || String(e.id) !== String(me.id)).map(e => {
    const dist = myPos ? locHaversineM(myPos, e) : null;
    const brg = myPos ? locBearingDeg(myPos, e) : null;
    return { ...e, _dist: dist, _brg: brg };
  }).sort((a, b) => (a._dist === null ? Infinity : a._dist) - (b._dist === null ? Infinity : b._dist));

  const card = { background: T.surface, borderRadius: 18, boxShadow: T.shadow };

  return (
    <div style={{ position:'fixed', inset:0, zIndex:450, background:T.bg, display:'flex', flexDirection:'column', overflow:'hidden' }}>
      {/* Header */}
      <div style={{ display:'flex', alignItems:'center', padding:'16px 16px 12px', gap:10 }}>
        <button onClick={onClose} style={{ width:40, height:40, borderRadius:12, border:'none', background:T.surface, display:'grid', placeItems:'center', cursor:'pointer', boxShadow:T.shadow, flexShrink:0, WebkitTapHighlightColor:'transparent' }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>📍 Lokátor</div>
      </div>
      <div style={{ flex:1, overflowY:'auto', padding:'0 16px 32px' }}>
        {!me ? (
          <div style={{ ...card, padding:18 }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink, marginBottom:4, textAlign:'center' }}>Ki vagy?</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.sub, marginBottom:16, textAlign:'center' }}>Válaszd ki a profilod a helymegosztáshoz</div>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:12 }}>
              {profiles.map(p => (
                <button key={p.id} onClick={() => pickMe(p)} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:8, padding:'14px 8px', borderRadius:16, border:`2px solid ${T.border}`, background:T.bg, cursor:'pointer', WebkitTapHighlightColor:'transparent' }}>
                  <div style={{ width:52, height:52, borderRadius:'50%', background:p.color||'#888', overflow:'hidden', display:'grid', placeItems:'center' }}>
                    {p.img ? <img src={p.img} style={{ width:52, height:52, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:'#fff' }}>{(p.name||'?').charAt(0).toUpperCase()}</span>}
                  </div>
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink, textAlign:'center', lineHeight:1.2 }}>{p.name}</span>
                </button>
              ))}
            </div>
            {profiles.length === 0 && <div style={{ fontFamily:T.font, fontSize:14, color:T.sub, textAlign:'center' }}>Nincsenek profilok.</div>}
          </div>
        ) : (
          <>
            {/* Sharing toggle card */}
            <div style={{ ...card, padding:'14px 16px', marginBottom:12, display:'flex', alignItems:'center', gap:12 }}>
              <div style={{ width:40, height:40, borderRadius:'50%', background:me.color||'#888', overflow:'hidden', display:'grid', placeItems:'center', flexShrink:0 }}>
                {me.img ? <img src={me.img} style={{ width:40, height:40, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff' }}>{(me.name||'?').charAt(0).toUpperCase()}</span>}
              </div>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{me.nickname || me.name}</div>
                <button onClick={() => { setSharing(false); localStorage.removeItem('boh_locator_me'); setMeId(null); }} style={{ border:'none', background:'transparent', padding:0, fontFamily:T.font, fontSize:12, color:T.sub, cursor:'pointer', textDecoration:'underline' }}>Nem te vagy?</button>
              </div>
              <button onClick={() => { if (sharing) { setSharing(false); } else { setGeoErr(null); setSharing(true); } }} style={{ width:56, height:32, borderRadius:999, border:'none', background: sharing ? T.mint : T.border, position:'relative', cursor:'pointer', WebkitTapHighlightColor:'transparent', transition:'background .2s', flexShrink:0 }}>
                <div style={{ position:'absolute', top:3, left: sharing ? 27 : 3, width:26, height:26, borderRadius:'50%', background:'#fff', boxShadow:'0 1px 4px rgba(0,0,0,0.25)', transition:'left .2s' }} />
              </button>
            </div>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, lineHeight:1.5, margin:'0 4px 12px' }}>
              {sharing ? (myPos ? '🟢 Helyzetmegosztás aktív.' : '🛰 Helymeghatározás folyamatban…') : 'Helyzetmegosztás kikapcsolva.'} A helyzeted csak addig frissül, amíg az app nyitva van. A megosztás kikapcsolásával azonnal törlődik.
            </div>
            {geoErr && (
              <div style={{ background:'#e8404018', borderRadius:14, padding:'12px 16px', marginBottom:12, fontFamily:T.font, fontSize:13, color:'#e84040', fontWeight:700, lineHeight:1.4 }}>
                {geoErr === 'denied' ? '🚫 A helymeghatározás le van tiltva. Engedélyezd a böngésző beállításaiban (Webhely beállítások → Helyadatok), majd próbáld újra.' : geoErr === 'unsupported' ? 'Ez az eszköz nem támogatja a helymeghatározást.' : 'Nem sikerült meghatározni a helyzeted. Próbáld újra.'}
              </div>
            )}
            {/* Others */}
            <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.sub, textTransform:'uppercase', letterSpacing:'0.07em', margin:'4px 4px 8px' }}>Többiek ({others.length})</div>
            {others.length === 0 && (
              <div style={{ textAlign:'center', padding:'40px 24px', color:T.sub, fontFamily:T.font, fontSize:14, lineHeight:1.6 }}>
                <div style={{ fontSize:44, marginBottom:12 }}>🧭</div>
                Még senki nem osztja meg a helyzetét
              </div>
            )}
            {others.map(o => (
              <div key={o.id} style={{ ...card, borderRadius:16, padding:'12px 14px', marginBottom:8, display:'flex', alignItems:'center', gap:12 }}>
                <div style={{ width:40, height:40, borderRadius:'50%', background:o.color||'#888', overflow:'hidden', display:'grid', placeItems:'center', flexShrink:0 }}>
                  {o.img ? <img src={o.img} style={{ width:40, height:40, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff' }}>{(o.name||'?').charAt(0).toUpperCase()}</span>}
                </div>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{o.nickname || o.name}</div>
                  <div style={{ display:'flex', alignItems:'center', gap:6, marginTop:2 }}>
                    {o._dist !== null && (
                      <span style={{ display:'inline-flex', alignItems:'center', gap:4, fontFamily:T.font, fontSize:13, fontWeight:800, color:T.mint }}>
                        <svg width="13" height="13" viewBox="0 0 24 24" style={{ transform:`rotate(${Math.round(o._brg)}deg)` }} fill={T.mint}><path d="M12 2L19 21l-7-5-7 5L12 2z"/></svg>
                        {locFmtDist(o._dist)}
                      </span>
                    )}
                    <span style={{ fontFamily:T.font, fontSize:11, color:T.sub }}>{locFmtAgo(now - o.ts)}</span>
                  </div>
                </div>
                <a href={`https://www.google.com/maps/dir/?api=1&destination=${o.lat},${o.lng}`} target="_blank" rel="noopener noreferrer" style={{ display:'flex', alignItems:'center', gap:5, background:T.mint+'22', borderRadius:10, padding:'8px 11px', textDecoration:'none', flexShrink:0 }}>
                  <span style={{ fontSize:14 }}>🗺</span>
                  <span style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.mint }}>Útvonal</span>
                </a>
              </div>
            ))}
            {others.length > 0 && !myPos && (
              <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, textAlign:'center', marginTop:8, lineHeight:1.5 }}>Kapcsold be a helyzetmegosztást, hogy lásd a távolságot és az irányt.</div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function EventLogScreen({ go, goEdit, deepLink }) {"""
rep(OLD1, NEW1)

# ── 2. locOpen state in EventLogScreen ──
OLD2 = """  const [evView, setEvView] = React.useState('list'); // 'list' | 'calendar'"""
NEW2 = """  const [evView, setEvView] = React.useState('list'); // 'list' | 'calendar'
  const [locOpen, setLocOpen] = React.useState(false);"""
rep(OLD2, NEW2)

# ── 3. Entry button under the view switcher + overlay mount ──
OLD3 = """        </div>
      </div>
      {(() => {
        const now = new Date(); now.setHours(0,0,0,0);"""
NEW3 = """        </div>
      </div>
      {/* Lokátor entry */}
      <div style={{ padding:'10px 16px 0' }}>
        <button onClick={() => setLocOpen(true)} style={{ width:'100%', display:'flex', alignItems:'center', gap:12, background:T.surface, border:'none', borderRadius:18, padding:'13px 16px', boxShadow:T.shadow, cursor:'pointer', WebkitTapHighlightColor:'transparent', textAlign:'left' }}>
          <span style={{ fontSize:22, flexShrink:0 }}>📍</span>
          <span style={{ flex:1, minWidth:0 }}>
            <span style={{ display:'block', fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>Lokátor</span>
            <span style={{ display:'block', fontFamily:T.font, fontSize:12, color:T.sub, marginTop:1 }}>Hol vannak a többiek a fesztiválon?</span>
          </span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={T.sub} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink:0 }}><polyline points="9 18 15 12 9 6"/></svg>
        </button>
      </div>
      {locOpen && <LocatorScreen T={T} profiles={profiles} onClose={() => setLocOpen(false)} />}
      {(() => {
        const now = new Date(); now.setHours(0,0,0,0);"""
rep(OLD3, NEW3)

# ── 4. Version bump ──
rep("const APP_VERSION = 'v9.793';", "const APP_VERSION = 'v9.794';")

io.open(P, 'w', encoding='utf-8').write(c)
print('patch_locator OK')
