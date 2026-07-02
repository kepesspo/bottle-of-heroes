#!/usr/bin/env python3
"""Patch: Esemény napló gomb + EventLogScreen (v9.655 → v9.656)"""
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

# ── 1. EventLogScreen component (before HomeScreen) ──────────────────────────
replace_once(
    "function HomeScreen({ go, onStartGame, onQuickGame, setTheme, currentTheme, setLang, currentLang, resumeRoomData, onResume }) {",
    r"""function EventLogScreen({ go }) {
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
}

function HomeScreen({ go, onStartGame, onQuickGame, setTheme, currentTheme, setLang, currentLang, resumeRoomData, onResume }) {""",
    "EventLogScreen component"
)

# ── 2. Pill: add event log button to the LEFT ─────────────────────────────────
replace_once(
    """        {/* Top-right: grouped pill */}
        <div style={{ position:'absolute', top:14, right:18, zIndex:10, display:'flex', background:T.surface, borderRadius:18, boxShadow:T.shadow, overflow:'hidden' }}>
          <button onClick={() => setShowSettings(true)} style={{ display:'flex', alignItems:'center', justifyContent:'center', width:52, height:52, border:'none', background:'transparent', cursor:'pointer' }}>""",
    """        {/* Top-right: grouped pill */}
        <div style={{ position:'absolute', top:14, right:18, zIndex:10, display:'flex', background:T.surface, borderRadius:18, boxShadow:T.shadow, overflow:'hidden' }}>
          <button onClick={() => go('log')} style={{ display:'flex', alignItems:'center', justifyContent:'center', width:52, height:52, border:'none', background:'#E8631A', cursor:'pointer' }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="9" y1="7" x2="15" y2="7"/><line x1="9" y1="11" x2="15" y2="11"/><line x1="9" y1="15" x2="12" y2="15"/></svg>
          </button>
          <div style={{ width:1, background:'rgba(255,255,255,0.25)', margin:'12px 0' }} />
          <button onClick={() => setShowSettings(true)} style={{ display:'flex', alignItems:'center', justifyContent:'center', width:52, height:52, border:'none', background:'transparent', cursor:'pointer' }}>""",
    "Pill: event log button left"
)

# ── 3. Screen routing: add 'log' screen ──────────────────────────────────────
replace_once(
    "{screen==='stats'    && <StatsScreen    go={go} onOpenObserver={openObserver} />}",
    """{screen==='stats'    && <StatsScreen    go={go} onOpenObserver={openObserver} />}
        {screen==='log'      && <EventLogScreen go={go} />}""",
    "screen routing: log"
)

# ── Version bump ──────────────────────────────────────────────────────────────
replace_once(
    "const APP_VERSION = 'v9.655';",
    "const APP_VERSION = 'v9.656';",
    "version bump 9.655 → 9.656"
)

assert src != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)
print("\nAll patches applied.")
