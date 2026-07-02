#!/usr/bin/env python3
"""Patch: Event log → Firebase Firestore 'events' collection (v9.659 → v9.660)"""
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()
orig = src

def replace_once(old, new, label):
    global src
    if old not in src:
        print(f'MISSING: {label}'); sys.exit(1)
    if src.count(old) != 1:
        print(f'AMBIGUOUS ({src.count(old)}x): {label}'); sys.exit(1)
    src = src.replace(old, new, 1)
    print(f'OK: {label}')

# ── 1. Replace shared storage helpers + EventLogScreen ───────────────────────
replace_once(
    """// ── Shared event storage ──────────────────────────────────────────────────────
const EV_KEY = 'boh_event_log';
function evLoad() { try { return JSON.parse(localStorage.getItem(EV_KEY) || '[]'); } catch(e) { return []; } }
function evSave(logs) { try { localStorage.setItem(EV_KEY, JSON.stringify(logs)); } catch(e) {} }""",
    """// ── Shared event storage (Firebase Firestore 'events' collection) ─────────────
function evDb() { return typeof firebase !== 'undefined' ? firebase.firestore().collection('events') : null; }
// localStorage fallback (offline / no firebase)
const EV_KEY = 'boh_event_log';
function evLoad() { try { return JSON.parse(localStorage.getItem(EV_KEY) || '[]'); } catch(e) { return []; } }
function evSave(logs) { try { localStorage.setItem(EV_KEY, JSON.stringify(logs)); } catch(e) {} }""",
    "evDb helper"
)

# ── 2. Replace EventLogScreen with Firebase-synced version ────────────────────
replace_once(
    """function EventLogScreen({ go, goEdit }) {
  const [events, setEvents] = React.useState(evLoad);
  const [detail, setDetail] = React.useState(null); // event id
  const [rsvpSheet, setRsvpSheet] = React.useState(false); // show profile picker
  const [rsvpStep, setRsvpStep] = React.useState('who'); // 'who' | 'status'
  const [rsvpProfile, setRsvpProfile] = React.useState(null); // chosen profile
  const [profiles, setProfiles] = React.useState([]);

  React.useEffect(() => {
    if (typeof window.getProfiles === 'function') window.getProfiles().then(p => setProfiles(p || []));
  }, []);

  function formatDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    const pad = n => String(n).padStart(2,'0');
    return `${d.getFullYear()}.${pad(d.getMonth()+1)}.${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  function getDetail() { return events.find(e => e.id === detail) || null; }

  function saveRsvp(status) {
    if (!rsvpProfile || !detail) return;
    const next = events.map(ev => ev.id !== detail ? ev : { ...ev, rsvp: { ...(ev.rsvp||{}), [rsvpProfile.name]: status } });
    setEvents(next);
    evSave(next);
    setRsvpSheet(false);
    setRsvpStep('who');
    setRsvpProfile(null);
  }""",
    """function EventLogScreen({ go, goEdit }) {
  const [events, setEvents] = React.useState(evLoad);
  const [loading, setLoading] = React.useState(true);
  const [detail, setDetail] = React.useState(null); // event id
  const [rsvpSheet, setRsvpSheet] = React.useState(false);
  const [rsvpStep, setRsvpStep] = React.useState('who');
  const [rsvpProfile, setRsvpProfile] = React.useState(null);
  const [profiles, setProfiles] = React.useState([]);

  // Subscribe to Firestore events collection, ordered by createdAt desc
  React.useEffect(() => {
    const col = evDb();
    if (!col) { setLoading(false); return; }
    const unsub = col.orderBy('createdAt', 'desc').onSnapshot(snap => {
      const docs = snap.docs.map(d => ({ id: d.id, ...d.data() }));
      setEvents(docs);
      evSave(docs); // keep localStorage in sync as offline cache
      setLoading(false);
    }, () => setLoading(false));
    return () => unsub();
  }, []);

  React.useEffect(() => {
    if (typeof window.getProfiles === 'function') window.getProfiles().then(p => setProfiles(p || []));
  }, []);

  function formatDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    const pad = n => String(n).padStart(2,'0');
    return `${d.getFullYear()}.${pad(d.getMonth()+1)}.${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  function getDetail() { return events.find(e => e.id === detail) || null; }

  function saveRsvp(status) {
    if (!rsvpProfile || !detail) return;
    const col = evDb();
    const patch = { [`rsvp.${rsvpProfile.name}`]: status };
    if (col) {
      col.doc(String(detail)).update(patch).catch(() => {
        // fallback: update locally
        setEvents(ev => ev.map(e => e.id === detail ? { ...e, rsvp: { ...(e.rsvp||{}), [rsvpProfile.name]: status } } : e));
      });
    } else {
      setEvents(ev => { const next = ev.map(e => e.id === detail ? { ...e, rsvp: { ...(e.rsvp||{}), [rsvpProfile.name]: status } } : e); evSave(next); return next; });
    }
    setRsvpSheet(false);
    setRsvpStep('who');
    setRsvpProfile(null);
  }""",
    "EventLogScreen Firebase sync"
)

# ── 3. Replace EventCreateScreen save() to use Firestore ─────────────────────
replace_once(
    """function EventCreateScreen({ go, editId }) {
  const existing = editId ? (evLoad().find(e => e.id === editId) || null) : null;
  const [title, setTitle] = React.useState(existing?.title || '');
  const [desc, setDesc] = React.useState(existing?.desc || '');
  const [date, setDate] = React.useState(existing?.date ? existing.date.slice(0,16) : '');
  const [locationUnknown, setLocationUnknown] = React.useState(existing ? !existing.location : false);
  const [location, setLocation] = React.useState(existing?.location || '');

  function save() {
    if (!title.trim()) return;
    const events = evLoad();
    const loc = locationUnknown ? '' : location.trim();
    if (editId) {
      evSave(events.map(e => e.id !== editId ? e : { ...e, title: title.trim(), desc: desc.trim(), date: date || null, location: loc }));
    } else {
      const entry = { id: Date.now(), title: title.trim(), desc: desc.trim(), date: date || null, location: loc, rsvp: {}, createdAt: new Date().toISOString() };
      evSave([entry, ...events]);
    }
    go('log');
  }""",
    """function EventCreateScreen({ go, editId }) {
  const existing = editId ? (evLoad().find(e => e.id === editId) || null) : null;
  const [title, setTitle] = React.useState(existing?.title || '');
  const [desc, setDesc] = React.useState(existing?.desc || '');
  const [date, setDate] = React.useState(existing?.date ? existing.date.slice(0,16) : '');
  const [locationUnknown, setLocationUnknown] = React.useState(existing ? !existing.location : false);
  const [location, setLocation] = React.useState(existing?.location || '');
  const [saving, setSaving] = React.useState(false);

  function save() {
    if (!title.trim() || saving) return;
    setSaving(true);
    const loc = locationUnknown ? '' : location.trim();
    const col = evDb();
    if (col) {
      if (editId) {
        col.doc(String(editId)).update({ title: title.trim(), desc: desc.trim(), date: date || null, location: loc })
          .finally(() => { setSaving(false); go('log'); });
      } else {
        const entry = { title: title.trim(), desc: desc.trim(), date: date || null, location: loc, rsvp: {}, createdAt: new Date().toISOString() };
        col.add(entry).finally(() => { setSaving(false); go('log'); });
      }
    } else {
      // offline fallback
      const events = evLoad();
      if (editId) {
        evSave(events.map(e => e.id !== editId ? e : { ...e, title: title.trim(), desc: desc.trim(), date: date || null, location: loc }));
      } else {
        const entry = { id: Date.now(), title: title.trim(), desc: desc.trim(), date: date || null, location: loc, rsvp: {}, createdAt: new Date().toISOString() };
        evSave([entry, ...events]);
      }
      setSaving(false);
      go('log');
    }
  }""",
    "EventCreateScreen Firebase save"
)

# ── 4. Mentés gomb: saving state ─────────────────────────────────────────────
replace_once(
    """        <button onClick={save} disabled={!title.trim()} style={{ padding:'9px 18px', borderRadius:12, border:'none', background: title.trim() ? '#E8631A' : T.border, fontFamily:T.font, fontWeight:800, fontSize:14, color:'#fff', cursor: title.trim() ? 'pointer' : 'default' }}>
          Mentés
        </button>""",
    """        <button onClick={save} disabled={!title.trim() || saving} style={{ padding:'9px 18px', borderRadius:12, border:'none', background: title.trim() && !saving ? '#E8631A' : T.border, fontFamily:T.font, fontWeight:800, fontSize:14, color:'#fff', cursor: title.trim() && !saving ? 'pointer' : 'default' }}>
          {saving ? '…' : 'Mentés'}
        </button>""",
    "Mentés gomb saving state"
)

# ── 5. Version bump ────────────────────────────────────────────────────────────
replace_once(
    "const APP_VERSION = 'v9.659';",
    "const APP_VERSION = 'v9.660';",
    "version bump 9.659 → 9.660"
)

assert src != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)
print("\nAll patches applied.")
