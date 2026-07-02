#!/usr/bin/env python3
"""Patch: EventLog v2 — view-only screen + 5s long-press to create (v9.656 → v9.657)"""
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

# ── 1. Replace EventLogScreen with view-only + EventCreateScreen ──────────────
replace_once(
    """function EventLogScreen({ go }) {
  const LOG_KEY = 'boh_event_log';
  function loadLogs() {
    try { return JSON.parse(localStorage.getItem(LOG_KEY) || '[]'); } catch(e) { return []; }
  }
  function saveLogs(logs) {
    try { localStorage.setItem(LOG_KEY, JSON.stringify(logs)); } catch(e) {}
  }

  const [logs, setLogs] = React.useState(loadLogs);
  const [input, setInput] = React.useState('');
  const [showClearConfirm, setShowClearConfirm] = React.useState(false);
  const inputRef = React.useRef(null);

  function addEvent() {
    const text = input.trim();
    if (!text) return;
    const entry = { id: Date.now(), text, ts: new Date().toISOString() };
    const next = [entry, ...logs];
    setLogs(next);
    saveLogs(next);
    setInput('');
    inputRef.current?.focus();
  }

  function deleteEvent(id) {
    const next = logs.filter(l => l.id !== id);
    setLogs(next);
    saveLogs(next);
  }

  function clearAll() {
    setLogs([]);
    saveLogs([]);
    setShowClearConfirm(false);
  }

  function formatTs(iso) {
    const d = new Date(iso);
    const pad = n => String(n).padStart(2, '0');
    return `${pad(d.getMonth()+1)}.${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      {/* Header */}
      <div style={{ display:'flex', alignItems:'center', padding:'16px 16px 8px', gap:10 }}>
        <button onClick={() => go('home')} style={{ width:40, height:40, borderRadius:12, border:'none', background:T.surface, display:'grid', placeItems:'center', cursor:'pointer', boxShadow:T.shadow, flexShrink:0 }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div style={{ flex:1 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink, lineHeight:1 }}>Esemény napló</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:2 }}>{logs.length} bejegyzés</div>
        </div>
        {logs.length > 0 && (
          <button onClick={() => setShowClearConfirm(true)} style={{ padding:'8px 14px', borderRadius:10, border:'none', background:T.surface, fontFamily:T.font, fontWeight:700, fontSize:13, color:'#e84040', cursor:'pointer' }}>
            Törlés
          </button>
        )}
      </div>

      {/* Input */}
      <div style={{ padding:'8px 16px 12px', display:'flex', gap:8 }}>
        <input
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && addEvent()}
          placeholder="Új esemény leírása…"
          style={{ flex:1, padding:'12px 14px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.surface, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none' }}
        />
        <button onClick={addEvent} disabled={!input.trim()} style={{ width:48, height:48, borderRadius:14, border:'none', background: input.trim() ? '#E8631A' : T.border, display:'grid', placeItems:'center', cursor: input.trim() ? 'pointer' : 'default', flexShrink:0, transition:'background .15s' }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        </button>
      </div>

      {/* Log list */}
      <div style={{ flex:1, overflowY:'auto', padding:'0 16px 32px' }}>
        {logs.length === 0 && (
          <div style={{ textAlign:'center', padding:'48px 16px', color:T.sub, fontFamily:T.font, fontSize:15 }}>
            <div style={{ fontSize:40, marginBottom:12 }}>📋</div>
            Még nincsenek bejegyzések.<br/>Írj be egy eseményt fent!
          </div>
        )}
        {logs.map((log, idx) => (
          <div key={log.id} style={{ display:'flex', alignItems:'flex-start', gap:12, padding:'12px 14px', background:T.surface, borderRadius:14, marginBottom:8, boxShadow:T.shadow }}>
            <div style={{ width:36, height:36, borderRadius:10, background:'#E8631A22', display:'grid', placeItems:'center', flexShrink:0 }}>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:'#E8631A' }}>#{logs.length - idx}</span>
            </div>
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink, lineHeight:1.3, wordBreak:'break-word' }}>{log.text}</div>
              <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:3 }}>{formatTs(log.ts)}</div>
            </div>
            <button onClick={() => deleteEvent(log.id)} style={{ width:32, height:32, borderRadius:8, border:'none', background:'transparent', display:'grid', placeItems:'center', cursor:'pointer', flexShrink:0, opacity:0.5 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
        ))}
      </div>

      {/* Clear confirm */}
      {showClearConfirm && (
        <div style={{ position:'fixed', inset:0, background:'rgba(0,0,0,0.45)', zIndex:300, display:'flex', alignItems:'center', justifyContent:'center', padding:24 }}>
          <div style={{ background:T.surface, borderRadius:24, padding:'28px 24px', maxWidth:320, width:'100%', textAlign:'center' }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, marginBottom:8 }}>Minden törlése?</div>
            <div style={{ fontFamily:T.font, fontSize:14, color:T.sub, marginBottom:24 }}>Ez a művelet nem visszavonható.</div>
            <div style={{ display:'flex', gap:10 }}>
              <button onClick={() => setShowClearConfirm(false)} style={{ flex:1, padding:'13px', borderRadius:14, border:'none', background:T.border, fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink, cursor:'pointer' }}>Mégse</button>
              <button onClick={clearAll} style={{ flex:1, padding:'13px', borderRadius:14, border:'none', background:'#e84040', fontFamily:T.font, fontWeight:800, fontSize:15, color:'#fff', cursor:'pointer' }}>Törlés</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}""",
    r"""// ── Shared event storage ──────────────────────────────────────────────────────
const EV_KEY = 'boh_event_log';
function evLoad() { try { return JSON.parse(localStorage.getItem(EV_KEY) || '[]'); } catch(e) { return []; } }
function evSave(logs) { try { localStorage.setItem(EV_KEY, JSON.stringify(logs)); } catch(e) {} }

function EventLogScreen({ go }) {
  const [events, setEvents] = React.useState(evLoad);
  const [detail, setDetail] = React.useState(null); // event object

  function formatDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    const pad = n => String(n).padStart(2,'0');
    return `${d.getFullYear()}.${pad(d.getMonth()+1)}.${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  if (detail) {
    return (
      <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
        <div style={{ display:'flex', alignItems:'center', padding:'16px 16px 12px', gap:10 }}>
          <button onClick={() => setDetail(null)} style={{ width:40, height:40, borderRadius:12, border:'none', background:T.surface, display:'grid', placeItems:'center', cursor:'pointer', boxShadow:T.shadow, flexShrink:0 }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          </button>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>Esemény részletei</div>
        </div>
        <div style={{ flex:1, overflowY:'auto', padding:'0 16px 32px' }}>
          {/* Title */}
          <div style={{ background:T.surface, borderRadius:18, padding:'18px 18px', marginBottom:12, boxShadow:T.shadow }}>
            <div style={{ fontFamily:T.font, fontSize:12, color:'#E8631A', fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:6 }}>Esemény neve</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink }}>{detail.title}</div>
          </div>
          {/* Description */}
          {detail.desc && (
            <div style={{ background:T.surface, borderRadius:18, padding:'18px 18px', marginBottom:12, boxShadow:T.shadow }}>
              <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:6 }}>Leírás</div>
              <div style={{ fontFamily:T.font, fontSize:15, color:T.ink, lineHeight:1.5 }}>{detail.desc}</div>
            </div>
          )}
          {/* Date + Location row */}
          <div style={{ display:'flex', gap:10, marginBottom:12 }}>
            <div style={{ flex:1, background:T.surface, borderRadius:18, padding:'16px', boxShadow:T.shadow }}>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:5 }}>📅 Időpont</div>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>{detail.date ? formatDate(detail.date) : '—'}</div>
            </div>
            <div style={{ flex:1, background:T.surface, borderRadius:18, padding:'16px', boxShadow:T.shadow }}>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:5 }}>📍 Helyszín</div>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>{detail.location || '—'}</div>
            </div>
          </div>
          {/* RSVP */}
          {detail.rsvp && Object.keys(detail.rsvp).length > 0 && (
            <div style={{ background:T.surface, borderRadius:18, padding:'18px', boxShadow:T.shadow }}>
              <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:12 }}>Ki jön?</div>
              {Object.entries(detail.rsvp).map(([name, status]) => (
                <div key={name} style={{ display:'flex', alignItems:'center', gap:10, marginBottom:8 }}>
                  <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>{name}</div>
                  <div style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color: status==='yes'?'#25b572':status==='maybe'?'#c07a10':'#e84040' }}>
                    {status==='yes' ? '✅ Jövök' : status==='maybe' ? '🤔 Talán' : '❌ Nem tudok'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <div style={{ display:'flex', alignItems:'center', padding:'16px 16px 12px', gap:10 }}>
        <button onClick={() => go('home')} style={{ width:40, height:40, borderRadius:12, border:'none', background:T.surface, display:'grid', placeItems:'center', cursor:'pointer', boxShadow:T.shadow, flexShrink:0 }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div style={{ flex:1 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink, lineHeight:1 }}>Esemény napló</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:2 }}>{events.length} esemény</div>
        </div>
      </div>
      <div style={{ flex:1, overflowY:'auto', padding:'0 16px 32px' }}>
        {events.length === 0 && (
          <div style={{ textAlign:'center', padding:'64px 24px', color:T.sub, fontFamily:T.font, fontSize:15, lineHeight:1.6 }}>
            <div style={{ fontSize:48, marginBottom:14 }}>📋</div>
            Még nincsenek események.<br/>
            <span style={{ fontSize:13 }}>Tartsd nyomva 5 másodpercig a főoldalon<br/>a napló ikont új esemény létrehozásához.</span>
          </div>
        )}
        {events.map((ev, idx) => (
          <div key={ev.id} onClick={() => setDetail(ev)} style={{ display:'flex', alignItems:'center', gap:14, padding:'14px 16px', background:T.surface, borderRadius:16, marginBottom:10, boxShadow:T.shadow, cursor:'pointer', WebkitTapHighlightColor:'transparent' }}>
            <div style={{ width:42, height:42, borderRadius:12, background:'#E8631A18', display:'grid', placeItems:'center', flexShrink:0 }}>
              <span style={{ fontSize:20 }}>📅</span>
            </div>
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink, lineHeight:1.2, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.title}</div>
              <div style={{ display:'flex', gap:10, marginTop:3 }}>
                {ev.date && <span style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>{new Date(ev.date).toLocaleDateString('hu-HU',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})}</span>}
                {ev.location && <span style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>📍 {ev.location}</span>}
              </div>
            </div>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={T.sub} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
          </div>
        ))}
      </div>
    </div>
  );
}

function EventCreateScreen({ go }) {
  const [title, setTitle] = React.useState('');
  const [desc, setDesc] = React.useState('');
  const [date, setDate] = React.useState('');
  const [location, setLocation] = React.useState('');
  const [profiles, setProfiles] = React.useState([]);
  const [rsvp, setRsvp] = React.useState({}); // name → 'yes'|'maybe'|'no'

  React.useEffect(() => {
    if (typeof window.getProfiles === 'function') {
      window.getProfiles().then(p => setProfiles(p || []));
    }
  }, []);

  function toggleRsvp(name, status) {
    setRsvp(r => ({ ...r, [name]: r[name] === status ? undefined : status }));
  }

  function save() {
    if (!title.trim()) return;
    const events = evLoad();
    const entry = { id: Date.now(), title: title.trim(), desc: desc.trim(), date: date || null, location: location.trim(), rsvp, createdAt: new Date().toISOString() };
    evSave([entry, ...events]);
    go('log');
  }

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <div style={{ display:'flex', alignItems:'center', padding:'16px 16px 12px', gap:10 }}>
        <button onClick={() => go('home')} style={{ width:40, height:40, borderRadius:12, border:'none', background:T.surface, display:'grid', placeItems:'center', cursor:'pointer', boxShadow:T.shadow, flexShrink:0 }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink }}>Új esemény</div>
        <button onClick={save} disabled={!title.trim()} style={{ padding:'9px 18px', borderRadius:12, border:'none', background: title.trim() ? '#E8631A' : T.border, fontFamily:T.font, fontWeight:800, fontSize:14, color:'#fff', cursor: title.trim() ? 'pointer' : 'default' }}>
          Mentés
        </button>
      </div>
      <div style={{ flex:1, overflowY:'auto', padding:'0 16px 32px' }}>
        {/* Title */}
        <div style={{ marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:6 }}>Esemény neve *</div>
          <input value={title} onChange={e => setTitle(e.target.value)} placeholder="pl. Pénteki parti" style={{ width:'100%', boxSizing:'border-box', padding:'13px 14px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.surface, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none' }} />
        </div>
        {/* Description */}
        <div style={{ marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:6 }}>Leírás</div>
          <textarea value={desc} onChange={e => setDesc(e.target.value)} placeholder="Mit kell tudni az eseményről?" rows={3} style={{ width:'100%', boxSizing:'border-box', padding:'13px 14px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.surface, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none', resize:'none' }} />
        </div>
        {/* Date + Location */}
        <div style={{ display:'flex', gap:10, marginBottom:12 }}>
          <div style={{ flex:1 }}>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:6 }}>📅 Időpont</div>
            <input type="datetime-local" value={date} onChange={e => setDate(e.target.value)} style={{ width:'100%', boxSizing:'border-box', padding:'12px 10px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.surface, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />
          </div>
          <div style={{ flex:1 }}>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:6 }}>📍 Helyszín</div>
            <input value={location} onChange={e => setLocation(e.target.value)} placeholder="pl. Jani háza" style={{ width:'100%', boxSizing:'border-box', padding:'13px 10px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.surface, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />
          </div>
        </div>
        {/* RSVP from profiles */}
        {profiles.length > 0 && (
          <div>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>Ki jön?</div>
            {profiles.map(p => (
              <div key={p.name} style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:14, padding:'10px 14px', marginBottom:8, boxShadow:T.shadow }}>
                <div style={{ width:34, height:34, borderRadius:'50%', background:p.color||'#555', overflow:'hidden', display:'grid', placeItems:'center', flexShrink:0 }}>
                  {p.img ? <img src={p.img} style={{ width:34, height:34, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff' }}>{(p.name||'?').charAt(0).toUpperCase()}</span>}
                </div>
                <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>{p.name}</div>
                <div style={{ display:'flex', gap:6 }}>
                  {[['yes','✅'],['maybe','🤔'],['no','❌']].map(([val, emoji]) => (
                    <button key={val} onClick={() => toggleRsvp(p.name, val)} style={{ width:34, height:34, borderRadius:10, border:'none', background: rsvp[p.name]===val ? (val==='yes'?'#25b57222':val==='maybe'?'#c07a1022':'#e8404022') : T.border, fontSize:16, cursor:'pointer', transition:'background .1s' }}>
                      {emoji}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}""",
    "EventLogScreen v2 + EventCreateScreen"
)

# ── 2. Replace pill button with long-press logic (5s) ────────────────────────
replace_once(
    """          <button onClick={() => go('log')} style={{ display:'flex', alignItems:'center', justifyContent:'center', width:52, height:52, border:'none', background:'#E8631A', cursor:'pointer' }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="9" y1="7" x2="15" y2="7"/><line x1="9" y1="11" x2="15" y2="11"/><line x1="9" y1="15" x2="12" y2="15"/></svg>
          </button>
          <div style={{ width:1, background:'rgba(255,255,255,0.25)', margin:'12px 0' }} />""",
    r"""          {(() => {
            const [lpPct, setLpPct] = React.useState(0); // 0-100
            const lpRef = React.useRef(null);
            const lpStart = React.useRef(null);
            const DURATION = 5000;
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
          })()}
          <div style={{ width:1, background:'rgba(255,255,255,0.25)', margin:'12px 0' }} />""",
    "Pill: long-press 5s button with SVG progress ring"
)

# ── 3. Screen routing: add 'create' screen ────────────────────────────────────
replace_once(
    "{screen==='log'      && <EventLogScreen go={go} />}",
    """{screen==='log'      && <EventLogScreen go={go} />}
        {screen==='create'   && <EventCreateScreen go={go} />}""",
    "screen routing: create"
)

# ── Version bump ──────────────────────────────────────────────────────────────
replace_once(
    "const APP_VERSION = 'v9.656';",
    "const APP_VERSION = 'v9.657';",
    "version bump 9.656 → 9.657"
)

assert src != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)
print("\nAll patches applied.")
