#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v9.796 — event share deeplink, announcement clamp + push notif,
# persistent locator sharing, Blackjack cash-out distribution + dealer picker
import io, re

PATH = '/home/user/bottle-of-heroes/index.html'
c = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global c
    assert old in c, 'OLD not found: %r...' % old[:90]
    assert c.count(old) == count, 'OLD not unique (%d): %r...' % (c.count(old), old[:90])
    c = c.replace(old, new, count)

# ═══════════ ITEM 3a — announcement push helper (next to _bohShowNotif) ═══════════
OLD = """window._bohShowNotif = function(title, body) {
  if (!('Notification' in window) || Notification.permission !== 'granted') return;
  try { new Notification(title, { body }); } catch(e) {}
};"""
NEW = """window._bohShowNotif = function(title, body) {
  if (!('Notification' in window) || Notification.permission !== 'granted') return;
  try { new Notification(title, { body }); } catch(e) {}
};
// Hirdetmény push: csak akkor szól, ha a tartalom eltér az utoljára látottól
window._bohAnnounceNotif = function(d) {
  if (!d || !d.active || !d.title) return;
  var key = (d.title || '') + '|' + (d.body || '');
  try {
    if (localStorage.getItem('boh_last_announcement') === key) return;
    localStorage.setItem('boh_last_announcement', key);
  } catch(e) { return; }
  window._bohShowNotif(d.title, d.body || '');
};"""
rep(OLD, NEW)

# ═══════════ ITEM 2+3b — HomeScreen announcement: notif + clamp ═══════════
OLD = """      const unsub = window.onAnnouncement(d => setAnnouncement(d && d.active && d.title && (!d.until || new Date(d.until + 'T23:59:59') >= new Date()) ? d : null));
      return () => unsub();"""
NEW = """      const unsub = window.onAnnouncement(d => {
        const ok = d && d.active && d.title && (!d.until || new Date(d.until + 'T23:59:59') >= new Date()) ? d : null;
        if (ok && typeof window._bohAnnounceNotif === 'function') window._bohAnnounceNotif(ok);
        setAnnouncement(ok);
      });
      return () => unsub();"""
rep(OLD, NEW)

OLD = """          <div style={{ position:'absolute', top:56, left:18, zIndex:20, pointerEvents:'none', maxWidth:'55vw' }}>
            <div style={{ background:'#E8631A', borderRadius:14, padding:'8px 14px', boxShadow:'0 4px 16px rgba(232,99,26,0.4)', display:'inline-block' }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', lineHeight:1.3 }}>{announcement.title}</div>
              {announcement.body && <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:'rgba(255,255,255,0.9)', marginTop:3 }}>{announcement.body}</div>}
            </div>
          </div>"""
NEW = """          <div style={{ position:'absolute', top:56, left:18, zIndex:20, pointerEvents:'none', maxWidth:'55vw' }}>
            <div style={{ background:'#E8631A', borderRadius:14, padding:'8px 14px', boxShadow:'0 4px 16px rgba(232,99,26,0.4)', display:'inline-block', maxHeight:'30vh', overflowY:'auto' }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', lineHeight:1.3, display:'-webkit-box', WebkitLineClamp:1, WebkitBoxOrient:'vertical', overflow:'hidden', wordBreak:'break-word' }}>{announcement.title}</div>
              {announcement.body && <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:'rgba(255,255,255,0.9)', marginTop:3, display:'-webkit-box', WebkitLineClamp:3, WebkitBoxOrient:'vertical', overflow:'hidden', wordBreak:'break-word' }}>{announcement.body}</div>}
            </div>
          </div>"""
rep(OLD, NEW)

# home content container: safe-area padding bottom so nothing sits under the bottom bar
OLD = """      gap:28px; padding:52px 22px 44px;"""
NEW = """      gap:28px; padding:52px 22px calc(44px + env(safe-area-inset-bottom));"""
rep(OLD, NEW)

# ═══════════ ITEM 3c — EventLogScreen: announcement notif subscription ═══════════
OLD = """  // Subscribe to Firestore events collection, ordered by createdAt desc
  React.useEffect(() => {
    const col = evDb();
    if (!col) { setLoading(false); return; }"""
NEW = """  // Hirdetmény push az events módban is (birthday notifok mellett)
  React.useEffect(() => {
    if (typeof window.onAnnouncement !== 'function') return;
    const unsub = window.onAnnouncement(d => {
      if (d && d.active && d.title && (!d.until || new Date(d.until + 'T23:59:59') >= new Date()) && typeof window._bohAnnounceNotif === 'function') window._bohAnnounceNotif(d);
    });
    return () => unsub();
  }, []);

  // Subscribe to Firestore events collection, ordered by createdAt desc
  React.useEffect(() => {
    const col = evDb();
    if (!col) { setLoading(false); return; }"""
rep(OLD, NEW)

# ═══════════ ITEM 1a — deep-link ?event=<id> auto-open ═══════════
OLD = """  React.useEffect(() => {
    if (typeof window.getProfiles === 'function') window.getProfiles().then(p => setProfiles(p || []));
  }, []);

  function formatDate(iso) {"""
NEW = """  React.useEffect(() => {
    if (typeof window.getProfiles === 'function') window.getProfiles().then(p => setProfiles(p || []));
  }, []);

  // Deep link: ?screen=events&event=<id> — az adott esemény részleteinek megnyitása
  const evDeepOpenedRef = React.useRef(false);
  React.useEffect(() => {
    if (evDeepOpenedRef.current || !events.length) return;
    let eid = null;
    try { eid = new URLSearchParams(window.location.search).get('event'); } catch(e) {}
    if (!eid) { evDeepOpenedRef.current = true; return; }
    const found = events.find(e => String(e.id) === String(eid));
    if (found) { evDeepOpenedRef.current = true; setDetail(found.id); }
  }, [events]);

  const [shareCopied, setShareCopied] = React.useState(false);
  function shareEvent(sev) {
    const url = location.origin + location.pathname + '?screen=events&event=' + sev.id;
    if (navigator.share) {
      navigator.share({ title: sev.title, url }).catch(() => {});
    } else if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(() => { setShareCopied(true); setTimeout(() => setShareCopied(false), 2000); }).catch(() => {});
    }
  }

  function formatDate(iso) {"""
rep(OLD, NEW)

# ═══════════ ITEM 1b — Megosztás button in detail view ═══════════
OLD = """              )}
            </div>
          </div>
          {/* RSVP list */}"""
NEW = """              )}
            </div>
          </div>
          {/* Share */}
          <button onClick={() => shareEvent(ev)} style={{ width:'100%', padding:'13px', borderRadius:14, border:'none', background: shareCopied ? T.mint : T.surface, boxShadow:T.shadow, fontFamily:T.font, fontWeight:800, fontSize:14, color: shareCopied ? '#fff' : T.ink, cursor:'pointer', marginBottom:12, display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
            {shareCopied ? 'Link másolva ✓' : '📤 Megosztás'}
          </button>
          {/* RSVP list */}"""
rep(OLD, NEW)

# ═══════════ ITEM 4 — Locator: window-level sharing singleton ═══════════
OLD = """function LocatorScreen({ T, profiles, onClose }) {
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

  React.useEffect(() => { const iv = setInterval(() => setNow(Date.now()), 5000); return () => clearInterval(iv); }, []);"""
NEW = """// Ablak-szintű helymegosztó motor — a LocatorScreen bezárása után is fut,
// csak a felhasználó kikapcsolására áll le.
window._bohLocShare = window._bohLocShare || { watchId: null, myId: null, on: false, err: null, lastPos: null, lastWrite: { t: 0, lat: null, lng: null } };
function bohStartLocShare(me) {
  const S = window._bohLocShare;
  if (!me) return;
  if (S.on && String(S.myId) === String(me.id)) return;
  bohStopLocShare();
  if (!navigator.geolocation) { S.err = 'unsupported'; return; }
  S.myId = String(me.id); S.on = true; S.err = null; S.lastWrite = { t: 0, lat: null, lng: null };
  S.watchId = navigator.geolocation.watchPosition(
    pos => {
      const { latitude: lat, longitude: lng, accuracy: acc } = pos.coords;
      S.lastPos = { lat, lng };
      const lw = S.lastWrite;
      if (lw.lat !== null) {
        const moved = locHaversineM({ lat: lw.lat, lng: lw.lng }, { lat, lng });
        if (moved < 15 && Date.now() - lw.t < 20000) return;
      }
      S.lastWrite = { t: Date.now(), lat, lng };
      const col = locDb();
      if (!col) return;
      const doc = { name: me.name || '?', nickname: me.nickname || null, color: me.color || null, lat, lng, acc: Math.round(acc || 0), ts: Date.now() };
      if (me.img && !(typeof me.img === 'string' && me.img.startsWith('data:') && me.img.length > 500)) doc.img = me.img;
      col.doc(String(me.id)).set(doc).catch(() => {});
    },
    err => { S.err = err.code === 1 ? 'denied' : 'error'; bohStopLocShare(); },
    { enableHighAccuracy: true, maximumAge: 5000, timeout: 20000 }
  );
}
function bohStopLocShare() {
  const S = window._bohLocShare;
  if (S.watchId !== null && navigator.geolocation) { try { navigator.geolocation.clearWatch(S.watchId); } catch(e) {} }
  S.watchId = null;
  if (S.on && S.myId) { const col = locDb(); if (col) col.doc(String(S.myId)).delete().catch(() => {}); }
  S.on = false; S.lastPos = null; S.lastWrite = { t: 0, lat: null, lng: null };
}

function LocatorScreen({ T, profiles, onClose }) {
  const LOC_MAX_AGE = 20 * 60 * 1000;
  const [meId, setMeId] = React.useState(() => localStorage.getItem('boh_locator_me') || null);
  const me = profiles.find(p => String(p.id) === String(meId)) || null;
  const [sharing, setSharing] = React.useState(() => !!(window._bohLocShare && window._bohLocShare.on));
  const [myPos, setMyPos] = React.useState(() => (window._bohLocShare && window._bohLocShare.on) ? window._bohLocShare.lastPos : null);
  const [geoErr, setGeoErr] = React.useState(null);
  const [entries, setEntries] = React.useState([]);
  const [now, setNow] = React.useState(Date.now());

  // Tükrözi a singleton állapotát (pozíció, hiba, on/off) — leállítás NÉLKÜL unmountkor
  React.useEffect(() => {
    const iv = setInterval(() => {
      setNow(Date.now());
      const S = window._bohLocShare;
      setSharing(S.on);
      setMyPos(S.on ? S.lastPos : null);
      if (S.err) setGeoErr(S.err);
    }, 5000);
    return () => clearInterval(iv);
  }, []);"""
rep(OLD, NEW)

OLD = """  function pickMe(p) { localStorage.setItem('boh_locator_me', String(p.id)); setMeId(String(p.id)); }

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
  }, [sharing, meId]);"""
NEW = """  function pickMe(p) { localStorage.setItem('boh_locator_me', String(p.id)); setMeId(String(p.id)); }

  function toggleSharing() {
    const S = window._bohLocShare;
    if (S.on) {
      bohStopLocShare();
      setSharing(false); setMyPos(null);
    } else {
      setGeoErr(null);
      bohStartLocShare(me);
      setSharing(S.on);
      if (S.err) setGeoErr(S.err);
    }
  }"""
rep(OLD, NEW)

OLD = """                <button onClick={() => { setSharing(false); localStorage.removeItem('boh_locator_me'); setMeId(null); }} style={{ border:'none', background:'transparent', padding:0, fontFamily:T.font, fontSize:12, color:T.sub, cursor:'pointer', textDecoration:'underline' }}>Nem te vagy?</button>
              </div>
              <button onClick={() => { if (sharing) { setSharing(false); } else { setGeoErr(null); setSharing(true); } }} style={{ width:56, height:32, borderRadius:999, border:'none', background: sharing ? T.mint : T.border, position:'relative', cursor:'pointer', WebkitTapHighlightColor:'transparent', transition:'background .2s', flexShrink:0 }}>"""
NEW = """                <button onClick={() => { bohStopLocShare(); setSharing(false); setMyPos(null); localStorage.removeItem('boh_locator_me'); setMeId(null); }} style={{ border:'none', background:'transparent', padding:0, fontFamily:T.font, fontSize:12, color:T.sub, cursor:'pointer', textDecoration:'underline' }}>Nem te vagy?</button>
              </div>
              <button onClick={toggleSharing} style={{ width:56, height:32, borderRadius:999, border:'none', background: sharing ? T.mint : T.border, position:'relative', cursor:'pointer', WebkitTapHighlightColor:'transparent', transition:'background .2s', flexShrink:0 }}>"""
rep(OLD, NEW)

OLD = """              {sharing ? (myPos ? '🟢 Helyzetmegosztás aktív.' : '🛰 Helymeghatározás folyamatban…') : 'Helyzetmegosztás kikapcsolva.'} A helyzeted csak addig frissül, amíg az app nyitva van. A megosztás kikapcsolásával azonnal törlődik."""
NEW = """              {sharing ? (myPos ? '🟢 Helyzetmegosztás aktív — akkor is, ha bezárod ezt a nézetet.' : '🛰 Helymeghatározás folyamatban…') : 'Helyzetmegosztás kikapcsolva.'} A helyzeted csak addig frissül, amíg az app nyitva van. A megosztás kikapcsolásával azonnal törlődik."""
rep(OLD, NEW)

# ═══════════ ITEM 5a — bjBookDrinksRemoteMulti helper ═══════════
OLD = """function bjWrite(code, ns) {
  try { firebase.firestore().collection('rooms').doc(code).update({ bjState: ns }); } catch(e) { console.warn('bjWrite', e); }
}"""
NEW = """// Több címzett kortyainak jóváírása EGY read-modify-write körben (+ opcionális extra mezők)
function bjBookDrinksRemoteMulti(code, assigned, extraUpdate) {
  const total = Object.values(assigned || {}).reduce((s, n) => s + (n || 0), 0);
  if (!code || (total <= 0 && !extraUpdate)) return;
  try {
    const dbb = firebase.firestore();
    dbb.collection('rooms').doc(code).get().then(snap => {
      const ps = (snap.data() || {}).players || [];
      const upd = { players: ps.map(p => ((assigned || {})[p.id] || 0) > 0 ? { ...p, drinks: (p.drinks || 0) + assigned[p.id] } : p), ...(extraUpdate || {}) };
      return dbb.collection('rooms').doc(code).update(upd);
    }).catch(() => {});
  } catch(e) {}
}
function bjWrite(code, ns) {
  try { firebase.firestore().collection('rooms').doc(code).update({ bjState: ns }); } catch(e) { console.warn('bjWrite', e); }
}"""
rep(OLD, NEW)

# ═══════════ ITEM 5b — BJGiftOverlay component (after BJAvatar) ═══════════
OLD = """// ═══════════════ BLACKJACK — host (osztó) nézet ═══════════════"""
NEW = """// Kiszállási nyereség-kiosztó overlay — kortyok szétosztása a többiek + az osztó közt
function BJGiftOverlay({ pool, recipients, onConfirm, onCancel }) {
  const [assigned, setAssigned] = React.useState({});
  const total = Object.values(assigned).reduce((s, n) => s + (n || 0), 0);
  const remaining = pool - total;
  return (
    <div style={{ position:'fixed', inset:0, zIndex:600, background:'rgba(0,0,0,0.55)', display:'flex', alignItems:'flex-end', justifyContent:'center' }} onClick={e => { if (e.target === e.currentTarget) onCancel(); }}>
      <div style={{ width:'100%', maxWidth:480, background:T.bg, borderTopLeftRadius:24, borderTopRightRadius:24, padding:'18px', paddingBottom:'max(18px, env(safe-area-inset-bottom))', maxHeight:'80vh', overflowY:'auto', animation:'popIn .25s' }}>
        <div style={{ textAlign:'center', marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink }}>🍺 Oszd ki a nyereséged!</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:4 }}>Még kiosztandó: <b style={{ color: remaining > 0 ? T.coral : T.mint }}>{remaining}</b> / {pool} korty</div>
        </div>
        {recipients.map(r => {
          const n = assigned[r.id] || 0;
          return (
            <div key={r.id} style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:14, padding:'10px 12px', marginBottom:8, boxShadow:T.shadow }}>
              <BJAvatar p={r.p} size={30} />
              <span style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{r.isDealer ? `🎩 Osztó — ${r.p?.name || '?'}` : (r.p?.name || r.id)}</span>
              <button onClick={() => setAssigned(a => ({ ...a, [r.id]: Math.max(0, (a[r.id] || 0) - 1) }))} disabled={n <= 0} style={{ width:32, height:32, borderRadius:9, border:'none', background:T.surfaceMuted, fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, cursor:'pointer', opacity: n <= 0 ? 0.4 : 1 }}>−</button>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color: n > 0 ? T.mint : T.inkSoft, minWidth:22, textAlign:'center' }}>{n}</span>
              <button onClick={() => remaining > 0 && setAssigned(a => ({ ...a, [r.id]: (a[r.id] || 0) + 1 }))} disabled={remaining <= 0} style={{ width:32, height:32, borderRadius:9, border:'none', background: remaining > 0 ? T.mintSoft : T.surfaceMuted, fontFamily:T.font, fontWeight:900, fontSize:18, color: remaining > 0 ? T.mint : T.inkSoft, cursor:'pointer', opacity: remaining <= 0 ? 0.4 : 1 }}>+</button>
            </div>
          );
        })}
        <button onClick={() => remaining === 0 && onConfirm(assigned)} disabled={remaining !== 0} style={{ width:'100%', padding:'14px', borderRadius:16, border:'none', background: remaining === 0 ? T.mint : T.surfaceMuted, fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor: remaining === 0 ? 'pointer' : 'default', marginTop:6 }}>
          {remaining === 0 ? 'Kiosztom ✓' : `Még ${remaining} korty kiosztandó`}
        </button>
        <button onClick={onCancel} style={{ width:'100%', padding:'10px', border:'none', background:'transparent', fontFamily:T.font, fontSize:13, color:T.inkSoft, cursor:'pointer', marginTop:4 }}>Mégsem</button>
      </div>
    </div>
  );
}

// ═══════════════ BLACKJACK — host (osztó) nézet ═══════════════"""
rep(OLD, NEW)

# ═══════════ ITEM 5c — host: state + lastGift banner effect ═══════════
OLD = """  const bjState = isOnline ? (room?.bjState || null) : localState;
  const takenIds = isOnline ? (room?.bjTakenIds || []) : [];
  const hostPlayer = players && players[0];"""
NEW = """  const bjState = isOnline ? (room?.bjState || null) : localState;
  const takenIds = isOnline ? (room?.bjTakenIds || []) : [];
  const hostPlayer = players && players[0];
  const [giftFor, setGiftFor] = React.useState(null); // { pid, pool } — kiszálló nyereség-kiosztása
  const [hostGiftNotice, setHostGiftNotice] = React.useState(null);
  const hostGiftTsRef = React.useRef(undefined);
  React.useEffect(() => {
    const lg = bjState && bjState.lastGift;
    if (hostGiftTsRef.current === undefined) { hostGiftTsRef.current = lg ? lg.ts : null; return; }
    if (!lg || lg.ts === hostGiftTsRef.current) return;
    hostGiftTsRef.current = lg.ts;
    const ts = lg.ts;
    setHostGiftNotice(lg);
    setTimeout(() => setHostGiftNotice(cur => (cur && cur.ts === ts) ? null : cur), 6000);
  }, [bjState && bjState.lastGift && bjState.lastGift.ts]);"""
rep(OLD, NEW)

# ═══════════ ITEM 5d + 6a — hostCashOut w/ distribution, offline dealer setter ═══════════
OLD = """  function hostCashOut(pid) {
    const startStack = bjState.startStack || 10;
    const ch = (bjState.chips || {})[pid] || 0;
    bookDrinks(pid, Math.max(0, startStack - ch));
    update({ ...bjState, cashedOut: { ...(bjState.cashedOut || {}), [pid]: true } });
  }"""
NEW = """  function hostCashOut(pid) {
    const startStack = bjState.startStack || 10;
    const ch = (bjState.chips || {})[pid] || 0;
    const diff = ch - startStack;
    if (diff > 0) { setGiftFor({ pid, pool: diff }); return; } // nyereség — kiosztó overlay
    bookDrinks(pid, Math.max(0, -diff));
    update({ ...bjState, cashedOut: { ...(bjState.cashedOut || {}), [pid]: true } });
  }
  function hostConfirmGift(assigned) {
    const g = giftFor;
    setGiftFor(null);
    if (!g) return;
    const giver = getPlayer(g.pid);
    const lastGift = { giverId: g.pid, giverName: giver?.name || '?', assigned, ts: Date.now() };
    if (isOnline) {
      bjBookDrinksRemoteMulti(roomCode, assigned, { bjState: { ...bjState, lastGift, cashedOut: { ...(bjState.cashedOut || {}), [g.pid]: true } } });
    } else {
      const deltas = {};
      Object.entries(assigned).forEach(([rpid, n]) => { if (n > 0) deltas[rpid] = n; });
      if (Object.keys(deltas).length && typeof onLiveDrinkUpdate === 'function') onLiveDrinkUpdate(deltas);
      update({ ...bjState, lastGift, cashedOut: { ...(bjState.cashedOut || {}), [g.pid]: true } });
    }
  }
  // Offline osztóváltás az első kör előtt: résztvevők = mindenki, kivéve az osztó
  function setOfflineDealer(did) {
    const parts = players.filter(p => p.id !== did).map(p => p.id);
    const startStack = bjState.startStack || 10;
    const bets = {}; const chips = {};
    parts.forEach(pid => { bets[pid] = 1; chips[pid] = startStack; });
    update({ ...bjState, hostId: did, participants: parts, bets, chips, betsDone: {} });
  }"""
rep(OLD, NEW)

# ═══════════ ITEM 6b — online dealer picker in JoiningView ═══════════
OLD = """        <div style={{ background:T.surface, borderRadius:18, padding:'14px 16px', boxShadow:T.shadow, marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:T.weightTitle, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>Kezdő kortykészlet 🍺</div>"""
NEW = """        <div style={{ background:T.surface, borderRadius:18, padding:'14px 16px', boxShadow:T.shadow, marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:T.weightTitle, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>🎩 Ki az osztó?</div>
          <div style={{ display:'flex', gap:8, overflowX:'auto', paddingBottom:4 }}>
            {players.map(p => {
              const sel = p.id === bjState.hostId;
              return (
                <button key={p.id} onClick={() => update({ ...bjState, hostId: p.id })} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:5, padding:'8px 10px', borderRadius:12, border:`2px solid ${sel ? T.mint : 'transparent'}`, background: sel ? T.mintSoft : T.surfaceMuted, cursor:'pointer', flexShrink:0, minWidth:64, WebkitTapHighlightColor:'transparent' }}>
                  <BJAvatar p={p} size={34} />
                  <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:11, color: sel ? T.mint : T.ink, whiteSpace:'nowrap' }}>{sel ? '🎩 ' : ''}{p.name}</span>
                </button>
              );
            })}
          </div>
        </div>
        <div style={{ background:T.surface, borderRadius:18, padding:'14px 16px', boxShadow:T.shadow, marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:T.weightTitle, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>Kezdő kortykészlet 🍺</div>"""
rep(OLD, NEW)

# ═══════════ ITEM 6c — offline dealer picker at top of first BettingView ═══════════
OLD = """      {!isOnline && (bjState.roundsPlayed || 0) === 0 && (
        <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:12, justifyContent:'center' }}>
          <span style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft }}>Kezdőkészlet:</span>"""
NEW = """      {!isOnline && (bjState.roundsPlayed || 0) === 0 && (
        <div style={{ background:T.surface, borderRadius:18, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:T.weightTitle, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>🎩 Ki az osztó?</div>
          <div style={{ display:'flex', gap:8, overflowX:'auto', paddingBottom:4 }}>
            {players.map(p => {
              const sel = p.id === bjState.hostId;
              return (
                <button key={p.id} onClick={() => setOfflineDealer(p.id)} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:5, padding:'8px 10px', borderRadius:12, border:`2px solid ${sel ? T.mint : 'transparent'}`, background: sel ? T.mintSoft : T.surfaceMuted, cursor:'pointer', flexShrink:0, minWidth:64, WebkitTapHighlightColor:'transparent' }}>
                  <BJAvatar p={p} size={34} />
                  <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:11, color: sel ? T.mint : T.ink, whiteSpace:'nowrap' }}>{sel ? '🎩 ' : ''}{p.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
      {!isOnline && (bjState.roundsPlayed || 0) === 0 && (
        <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:12, justifyContent:'center' }}>
          <span style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft }}>Kezdőkészlet:</span>"""
rep(OLD, NEW)

# ═══════════ ITEM 5e — host render: overlay + gift banner ═══════════
OLD = """      {bjState.phase === 'joining' && <JoiningView />}
      {bjState.phase === 'betting' && <BettingView />}
      {(bjState.phase === 'playing' || bjState.phase === 'dealer') && <PlayingView />}
      {bjState.phase === 'results' && <ResultsView />}
    </div>
  );
}"""
NEW = """      {bjState.phase === 'joining' && <JoiningView />}
      {bjState.phase === 'betting' && <BettingView />}
      {(bjState.phase === 'playing' || bjState.phase === 'dealer') && <PlayingView />}
      {bjState.phase === 'results' && <ResultsView />}
      {hostGiftNotice && (
        <div style={{ position:'fixed', top:'max(14px, env(safe-area-inset-top))', left:'50%', transform:'translateX(-50%)', zIndex:610, background:T.coral, color:'#fff', borderRadius:16, padding:'10px 16px', fontFamily:T.font, fontWeight:700, fontSize:13, boxShadow:'0 6px 20px rgba(0,0,0,0.3)', animation:'popIn .25s', maxWidth:'88vw' }}>
          <div style={{ fontWeight:900, marginBottom:2 }}>🍺 {hostGiftNotice.giverName} kiosztotta a nyereségét!</div>
          {Object.entries(hostGiftNotice.assigned || {}).filter(([, n]) => n > 0).map(([rpid, n]) => {
            const rp = getPlayer(rpid) || players.find(pp => String(pp.id) === String(rpid));
            const isDealer = String(rpid) === String(bjState.hostId);
            return <div key={rpid} style={{ fontSize:12 }}>{isDealer ? `🎩 Osztó — ${rp?.name || '?'}` : (rp?.name || rpid)}: +{n} korty</div>;
          })}
        </div>
      )}
      {giftFor && (() => {
        const dealer = getPlayer(bjState.hostId) || hostPlayer;
        const recips = (bjState.participants || []).filter(pid => pid !== giftFor.pid).map(pid => ({ id: pid, p: getPlayer(pid), isDealer: false }));
        if (dealer && !recips.some(r => r.id === dealer.id)) recips.push({ id: dealer.id, p: dealer, isDealer: true });
        return <BJGiftOverlay pool={giftFor.pool} recipients={recips} onConfirm={hostConfirmGift} onCancel={() => setGiftFor(null)} />;
      })()}
    </div>
  );
}"""
rep(OLD, NEW)

# ═══════════ ITEM 5f — observer: gift toast effect + state ═══════════
OLD = """  const playerIdRef = React.useRef(playerId);
  React.useEffect(() => { playerIdRef.current = playerId; }, [playerId]);

  const releasePlayer = React.useCallback((pid) => {"""
NEW = """  const playerIdRef = React.useRef(playerId);
  React.useEffect(() => { playerIdRef.current = playerId; }, [playerId]);
  const [giftPool, setGiftPool] = React.useState(null); // kiszállási nyereség kiosztása
  const [giftNotice, setGiftNotice] = React.useState(null); // { name, n, ts } — ki adott nekem kortyot
  const bjGiftTsRef = React.useRef(undefined);
  React.useEffect(() => {
    const lg = bj && bj.lastGift;
    if (bjGiftTsRef.current === undefined) { bjGiftTsRef.current = lg ? lg.ts : null; return; }
    if (!lg || lg.ts === bjGiftTsRef.current) return;
    bjGiftTsRef.current = lg.ts;
    if (!playerId) return;
    const n = (lg.assigned || {})[playerId] || 0;
    if (n > 0 && lg.giverId !== playerId) {
      const ts = lg.ts;
      setGiftNotice({ name: lg.giverName || '?', n, ts });
      setTimeout(() => setGiftNotice(cur => (cur && cur.ts === ts) ? null : cur), 4500);
    }
  }, [bj && bj.lastGift && bj.lastGift.ts, playerId]);

  const releasePlayer = React.useCallback((pid) => {"""
rep(OLD, NEW)

# ═══════════ ITEM 5g — observer: guestCashOut w/ distribution ═══════════
OLD = """  const guestCashOut = () => {
    const deficit = Math.max(0, startStack - myChips);
    if (deficit > 0) bjBookDrinksRemote(code, playerId, deficit);
    bjWrite(code, { ...bj, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true } });
  };"""
NEW = """  const guestCashOut = () => {
    const surplus = Math.max(0, myChips - startStack);
    if (surplus > 0) { setGiftPool(surplus); return; } // nyereség — kiosztó overlay
    const deficit = Math.max(0, startStack - myChips);
    if (deficit > 0) bjBookDrinksRemote(code, playerId, deficit);
    bjWrite(code, { ...bj, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true } });
  };
  const guestConfirmGift = (assigned) => {
    setGiftPool(null);
    bjBookDrinksRemoteMulti(code, assigned, {
      bjState: { ...bj, lastGift: { giverId: playerId, giverName: me?.name || '?', assigned, ts: Date.now() }, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true } }
    });
  };"""
rep(OLD, NEW)

# ═══════════ ITEM 5h — observer render: toast + overlay ═══════════
OLD = """  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, minHeight:0, overflow:'hidden' }}>
      {Header}
      <div style={{ flex:1, minHeight:0, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'12px 16px 24px' }}>

        {/* Én sáv */}"""
NEW = """  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, minHeight:0, overflow:'hidden' }}>
      {Header}
      {giftNotice && (
        <div style={{ position:'fixed', top:'max(14px, env(safe-area-inset-top))', left:'50%', transform:'translateX(-50%)', zIndex:620, background:T.coral, color:'#fff', borderRadius:999, padding:'10px 18px', fontFamily:T.font, fontWeight:700, fontSize:14, boxShadow:'0 6px 20px rgba(0,0,0,0.3)', animation:'popIn .25s', whiteSpace:'nowrap' }}>
          {giftNotice.name} adott {giftNotice.n} kortyot 🍺
        </div>
      )}
      {giftPool !== null && (() => {
        const dealer = players.find(p => p.id === bj.hostId);
        const recips = (bj.participants || []).filter(pid => pid !== playerId).map(pid => ({ id: pid, p: players.find(pp => pp.id === pid), isDealer: false }));
        if (dealer && !recips.some(r => r.id === dealer.id)) recips.push({ id: dealer.id, p: dealer, isDealer: true });
        return <BJGiftOverlay pool={giftPool} recipients={recips} onConfirm={guestConfirmGift} onCancel={() => setGiftPool(null)} />;
      })()}
      <div style={{ flex:1, minHeight:0, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'12px 16px 24px' }}>

        {/* Én sáv */}"""
rep(OLD, NEW)

# ═══════════ Version bump ═══════════
assert len(re.findall(r"9\.795", c)) == 1, 'expected exactly 1 occurrence of 9.795'
OLD = "const APP_VERSION = 'v9.795';"
NEW = "const APP_VERSION = 'v9.796';"
rep(OLD, NEW)

io.open(PATH, 'w', encoding='utf-8').write(c)
print('OK — all patches applied, version v9.796')
