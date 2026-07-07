#!/usr/bin/env python3
# patch_bug_report.py — v9.815 -> v9.816: bug report feature
import io

PATH = 'index.html'
with io.open(PATH, encoding='utf-8') as f:
    c = f.read()

# ── 1. Firebase helpers ──────────────────────────────────────────────
OLD1 = """  window.setAnnouncement = function(data) {
    return db.collection('config').doc('announcement').set(data).catch(function(e) { console.warn('setAnnouncement', e); });
  };
"""
NEW1 = OLD1 + """  window.sendBugReport = function(data){ return db.collection('bug_reports').add(Object.assign({}, data, { createdAt: firebase.firestore.FieldValue.serverTimestamp() })); };
  window.getBugReports = function(){ return db.collection('bug_reports').orderBy('createdAt','desc').limit(50).get().then(function(snap){ return snap.docs.map(function(d){ return Object.assign({ id:d.id }, d.data()); }); }).catch(function(){ return []; }); };
  window.updateBugReport = function(id, patch){ return db.collection('bug_reports').doc(id).set(patch, { merge:true }); };
  window.deleteBugReport = function(id){ return db.collection('bug_reports').doc(id).delete(); };
"""
assert OLD1 in c, 'anchor 1 (firebase helpers) not found'
c = c.replace(OLD1, NEW1, 1)

# ── 2. Shared components (before EventLogScreen) ─────────────────────
OLD2 = "function EventLogScreen({ go, goEdit, deepLink }) {"
NEW2 = """function BugReportSheet({ T, onClose }) {
  const [text, setText] = React.useState('');
  const [sent, setSent] = React.useState(false);
  const [sending, setSending] = React.useState(false);
  const send = () => {
    if (!text.trim() || sending) return;
    setSending(true);
    Promise.resolve(window.sendBugReport && window.sendBugReport({ text: text.trim(), version: APP_VERSION, screen: (window.location.search || '-'), ua: navigator.userAgent.slice(0,120) }))
      .then(() => { setSent(true); setTimeout(() => { onClose && onClose(); }, 1500); })
      .catch(() => { setSent(true); setTimeout(() => { onClose && onClose(); }, 1500); });
  };
  return (
    <div onClick={onClose} style={{ position:'fixed', inset:0, zIndex:9999, background:'rgba(0,0,0,0.5)', display:'flex', alignItems:'flex-end', justifyContent:'center' }}>
      <div onClick={e => e.stopPropagation()} style={{ width:'100%', maxWidth:520, background:T.surface, borderRadius:'24px 24px 0 0', padding:'24px 20px 32px', boxShadow:'0 -8px 40px rgba(0,0,0,0.25)' }}>
        {sent ? (
          <div style={{ textAlign:'center', padding:'24px 0', fontFamily:T.font, fontWeight:900, fontSize:18, color:T.mint }}>✓ Köszi, megkaptuk!</div>
        ) : (
          <>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, marginBottom:14 }}>🐞 Hiba bejelentése</div>
            <textarea value={text} onChange={e => setText(e.target.value)} placeholder="Mi történt? Melyik játékban?" rows={4} style={{ width:'100%', boxSizing:'border-box', padding:'13px 14px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none', resize:'vertical', marginBottom:14 }} />
            <button onClick={send} disabled={!text.trim() || sending} style={{ width:'100%', padding:'14px', borderRadius:14, border:'none', background: text.trim() ? T.mint : T.surfaceMuted, fontFamily:T.font, fontWeight:900, fontSize:15, color: text.trim() ? '#fff' : T.sub, cursor: text.trim() ? 'pointer' : 'default' }}>Küldés</button>
          </>
        )}
      </div>
    </div>
  );
}

function BugReportEntry({ T, variant }) {
  const [open, setOpen] = React.useState(false);
  const btn = variant === 'text'
    ? <button onClick={() => setOpen(true)} style={{ display:'block', margin:'8px auto 0', padding:'10px 16px', border:'none', background:'transparent', fontFamily:T.font, fontWeight:700, fontSize:13, color:T.sub, cursor:'pointer', textDecoration:'underline', textUnderlineOffset:3 }}>🐞 Hiba bejelentése</button>
    : <button onClick={() => setOpen(true)} style={{ width:'100%', marginTop:8, padding:'14px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.surfaceMuted, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft, cursor:'pointer' }}>🐞 Hiba bejelentése</button>;
  return <>{btn}{open && <BugReportSheet T={T} onClose={() => setOpen(false)} />}</>;
}

function BugReportsCard() {
  const [reports, setReports] = React.useState(null);
  const [confirmDel, setConfirmDel] = React.useState(null);
  const load = () => { setReports(null); (window.getBugReports ? window.getBugReports() : Promise.resolve([])).then(setReports); };
  React.useEffect(() => { load(); }, []);
  const toggle = (r) => { window.updateBugReport && window.updateBugReport(r.id, { done: !r.done }).then(load); };
  const del = (id) => { window.deleteBugReport && window.deleteBugReport(id).then(load); };
  return (
    <div style={{ background:T.surface, borderRadius:16, padding:16, boxShadow:T.shadow, marginTop:14 }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12 }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>🐞 Hibabejelentések</div>
        <button onClick={load} style={{ padding:'6px 12px', borderRadius:10, border:'none', background:T.surfaceMuted, fontFamily:T.font, fontWeight:700, fontSize:12, color:T.mint, cursor:'pointer' }}>Frissítés</button>
      </div>
      {reports === null && <div style={{ fontFamily:T.font, fontSize:13, color:T.sub, textAlign:'center', padding:'12px 0' }}>Betöltés…</div>}
      {reports !== null && reports.length === 0 && <div style={{ fontFamily:T.font, fontSize:14, color:T.sub, textAlign:'center', padding:'20px 0' }}>Nincs bejelentés 🎉</div>}
      {reports !== null && reports.map(r => (
        <div key={r.id} style={{ borderTop:`1px solid ${T.border}`, padding:'12px 0', opacity: r.done ? 0.55 : 1 }}>
          <div style={{ fontFamily:T.font, fontSize:14, color:T.ink, whiteSpace:'pre-wrap', wordBreak:'break-word' }}>{r.text}</div>
          <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:6 }}>{r.version} · {r.screen} · {r.createdAt && r.createdAt.toDate ? r.createdAt.toDate().toLocaleString('hu-HU') : ''}</div>
          <div style={{ display:'flex', gap:8, marginTop:8 }}>
            <button onClick={() => toggle(r)} style={{ padding:'6px 12px', borderRadius:10, border:'none', background: r.done ? T.surfaceMuted : T.mintSoft, fontFamily:T.font, fontWeight:700, fontSize:12, color: r.done ? T.sub : T.mint, cursor:'pointer' }}>{r.done ? 'Nyitott' : 'Kész ✓'}</button>
            <button onClick={() => { if (confirmDel === r.id) { del(r.id); setConfirmDel(null); } else setConfirmDel(r.id); }} style={{ padding:'6px 12px', borderRadius:10, border:'none', background: confirmDel === r.id ? '#ef4444' : '#fef2f2', fontFamily:T.font, fontWeight:700, fontSize:12, color: confirmDel === r.id ? '#fff' : '#ef4444', cursor:'pointer' }}>{confirmDel === r.id ? 'Biztos?' : '🗑'}</button>
          </div>
        </div>
      ))}
    </div>
  );
}

function EventLogScreen({ go, goEdit, deepLink }) {"""
assert OLD2 in c, 'anchor 2 (EventLogScreen) not found'
c = c.replace(OLD2, NEW2, 1)

# ── 3. Events screen entry ───────────────────────────────────────────
OLD3 = """      </div>; })()}
    </div>
  );
}

// ── Shared event form"""
NEW3 = """      </div>; })()}
      <BugReportEntry T={T} variant="text" />
    </div>
  );
}

// ── Shared event form"""
assert OLD3 in c, 'anchor 3 (events return) not found'
c = c.replace(OLD3, NEW3, 1)

# ── 4. Settings sheet entry ──────────────────────────────────────────
OLD4 = """                <Toggle on={splashOn} onChange={toggleSplash} />
              </div>

            </div>
          </SheetOverlay>"""
NEW4 = """                <Toggle on={splashOn} onChange={toggleSplash} />
              </div>

              <div style={{ height:1, background:T.inkMute+'25', margin:'20px 0' }} />
              <BugReportEntry T={T} />

            </div>
          </SheetOverlay>"""
assert OLD4 in c, 'anchor 4 (settings sheet) not found'
c = c.replace(OLD4, NEW4, 1)

# ── 5. Admin card ────────────────────────────────────────────────────
OLD5 = """        <ForceReloadButton />
      </div>
    </div>
  );
}

function ForceReloadButton() {"""
NEW5 = """        <ForceReloadButton />
      </div>

      <BugReportsCard />
    </div>
  );
}

function ForceReloadButton() {"""
assert OLD5 in c, 'anchor 5 (admin card) not found'
c = c.replace(OLD5, NEW5, 1)

# ── 6. Version bump ──────────────────────────────────────────────────
OLD6 = "const APP_VERSION = 'v9.815';"
NEW6 = "const APP_VERSION = 'v9.816';"
assert c.count(OLD6) == 1, 'version anchor count != 1'
c = c.replace(OLD6, NEW6, 1)

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(c)
print('patch applied OK')
