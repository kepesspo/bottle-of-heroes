#!/usr/bin/env python3
# v9.822: bug report auto-screenshot (html2canvas) + admin preview
import io

PATH = 'index.html'
with io.open(PATH, encoding='utf-8') as f:
    c = f.read()

# 1) html2canvas lazy loader + capture helper near firebase helpers
OLD1 = "  window.sendBugReport = function(data){ return db.collection('bug_reports').add(Object.assign({}, data, { createdAt: firebase.firestore.FieldValue.serverTimestamp() })); };"
NEW1 = (
    "  window._loadHtml2Canvas = function(){ if (window.html2canvas) return Promise.resolve(window.html2canvas); if (window._h2cPromise) return window._h2cPromise; window._h2cPromise = new Promise(function(res, rej){ var s = document.createElement('script'); s.src='https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js'; s.onload=function(){ res(window.html2canvas); }; s.onerror=function(){ rej(new Error('h2c load fail')); }; document.head.appendChild(s); }); return window._h2cPromise; };\n"
    "  window._captureScreenshot = function(){ return window._loadHtml2Canvas().then(function(h2c){ return h2c(document.body, { ignoreElements: function(el){ return el.getAttribute && el.getAttribute('data-noshot') === '1'; }, backgroundColor: null, scale: (window.innerWidth > 700 ? 0.5 : 0.6), logging:false, useCORS:true }); }).then(function(canvas){ var maxW = 540; var scale = Math.min(1, maxW / canvas.width); var out = document.createElement('canvas'); out.width = Math.round(canvas.width*scale); out.height = Math.round(canvas.height*scale); out.getContext('2d').drawImage(canvas, 0, 0, out.width, out.height); return out.toDataURL('image/jpeg', 0.5); }).catch(function(){ return null; }); };\n"
    "  window.sendBugReport = function(data){ return db.collection('bug_reports').add(Object.assign({}, data, { createdAt: firebase.firestore.FieldValue.serverTimestamp() })); };"
)
assert OLD1 in c, 'OLD1 not found'
assert c.count(OLD1) == 1, 'OLD1 not unique'
c = c.replace(OLD1, NEW1)

# 2a) data-noshot on SheetOverlay backdrop
OLD2 = (
    "    <div onClick={dismiss} style={{\n"
    "      position:'fixed', inset:0,\n"
    "      background:'rgba(14,14,24,0.55)',"
)
NEW2 = (
    "    <div onClick={dismiss} data-noshot=\"1\" style={{\n"
    "      position:'fixed', inset:0,\n"
    "      background:'rgba(14,14,24,0.55)',"
)
assert OLD2 in c, 'OLD2 not found'
assert c.count(OLD2) == 1, 'OLD2 not unique'
c = c.replace(OLD2, NEW2)

# 2b) data-noshot on BugReportSheet outer overlay
OLD3 = "    <div onClick={onClose} style={{ position:'fixed', inset:0, zIndex:9999, background:'rgba(0,0,0,0.5)', display:'flex', alignItems:'flex-end', justifyContent:'center' }}>"
NEW3 = "    <div onClick={onClose} data-noshot=\"1\" style={{ position:'fixed', inset:0, zIndex:9999, background:'rgba(0,0,0,0.5)', display:'flex', alignItems:'flex-end', justifyContent:'center' }}>"
assert OLD3 in c, 'OLD3 not found'
assert c.count(OLD3) == 1, 'OLD3 not unique'
c = c.replace(OLD3, NEW3)

# 3) BugReportSheet: accept screenshot prop, show status, include in send
OLD4 = "function BugReportSheet({ T, onClose }) {\n  const [text, setText] = React.useState('');\n  const [sent, setSent] = React.useState(false);\n  const [sending, setSending] = React.useState(false);"
NEW4 = (
    "function BugReportSheet({ T, onClose, shot }) {\n"
    "  const [text, setText] = React.useState('');\n"
    "  const [sent, setSent] = React.useState(false);\n"
    "  const [sending, setSending] = React.useState(false);\n"
    "  const [shotData, setShotData] = React.useState(null);\n"
    "  const [shotPending, setShotPending] = React.useState(true);\n"
    "  React.useEffect(() => {\n"
    "    let alive = true;\n"
    "    Promise.resolve(shot).then(function(d){ if (alive) { setShotData(d || null); setShotPending(false); } }).catch(function(){ if (alive) { setShotData(null); setShotPending(false); } });\n"
    "    return function(){ alive = false; };\n"
    "  }, [shot]);"
)
assert OLD4 in c, 'OLD4 not found'
c = c.replace(OLD4, NEW4)

OLD5 = "    Promise.resolve(window.sendBugReport && window.sendBugReport({ text: text.trim(), version: APP_VERSION, screen: (window.location.search || '-'), ua: navigator.userAgent.slice(0,120) }))"
NEW5 = "    Promise.resolve(window.sendBugReport && window.sendBugReport({ text: text.trim(), version: APP_VERSION, screen: (window.location.search || '-'), ua: navigator.userAgent.slice(0,120), screenshot: shotData || null }))"
assert OLD5 in c, 'OLD5 not found'
c = c.replace(OLD5, NEW5)

# Screenshot status UI: insert after the textarea line inside the form
OLD6 = "            <textarea value={text} onChange={e => setText(e.target.value)} placeholder=\"Mi történt? Melyik játékban?\" rows={4} style={{ width:'100%', boxSizing:'border-box', padding:'13px 14px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none', resize:'vertical', marginBottom:14 }} />"
NEW6 = (
    OLD6 + "\n"
    "            {shotPending && <div style={{ fontFamily:T.font, fontSize:13, color:T.sub, marginBottom:12 }}>📸 Képernyőkép készül…</div>}\n"
    "            {!shotPending && shotData && (\n"
    "              <div style={{ marginBottom:12 }}>\n"
    "                <img src={shotData} alt=\"screenshot\" style={{ maxHeight:120, maxWidth:'100%', borderRadius:10, border:`1.5px solid ${T.border}`, display:'block' }} />\n"
    "                <div style={{ fontFamily:T.font, fontSize:12, color:T.mint, fontWeight:700, marginTop:6 }}>Képernyőkép csatolva ✓</div>\n"
    "              </div>\n"
    "            )}"
)
assert OLD6 in c, 'OLD6 not found'
assert c.count(OLD6) == 1, 'OLD6 not unique'
c = c.replace(OLD6, NEW6)

# 4) BugReportEntry: capture on tap, pass shot prop
OLD7 = (
    "function BugReportEntry({ T, variant }) {\n"
    "  const [open, setOpen] = React.useState(false);"
)
NEW7 = (
    "function BugReportEntry({ T, variant }) {\n"
    "  const [open, setOpen] = React.useState(false);\n"
    "  const [shot, setShot] = React.useState(null);\n"
    "  const openReport = () => { setShot(window._captureScreenshot ? window._captureScreenshot() : Promise.resolve(null)); setOpen(true); };"
)
assert OLD7 in c, 'OLD7 not found'
c = c.replace(OLD7, NEW7)

OLD8 = "  const btn = variant === 'text'\n    ? <button onClick={() => setOpen(true)} style={{ display:'block', margin:'8px auto 0', padding:'10px 16px', border:'none', background:'transparent', fontFamily:T.font, fontWeight:700, fontSize:13, color:T.sub, cursor:'pointer', textDecoration:'underline', textUnderlineOffset:3 }}>🐞 Hiba bejelentése</button>\n    : <button onClick={() => setOpen(true)} style={{ width:'100%', marginTop:8, padding:'14px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.surfaceMuted, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft, cursor:'pointer' }}>🐞 Hiba bejelentése</button>;\n  return <>{btn}{open && <BugReportSheet T={T} onClose={() => setOpen(false)} />}</>;"
NEW8 = "  const btn = variant === 'text'\n    ? <button onClick={openReport} style={{ display:'block', margin:'8px auto 0', padding:'10px 16px', border:'none', background:'transparent', fontFamily:T.font, fontWeight:700, fontSize:13, color:T.sub, cursor:'pointer', textDecoration:'underline', textUnderlineOffset:3 }}>🐞 Hiba bejelentése</button>\n    : <button onClick={openReport} style={{ width:'100%', marginTop:8, padding:'14px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.surfaceMuted, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft, cursor:'pointer' }}>🐞 Hiba bejelentése</button>;\n  return <>{btn}{open && <BugReportSheet T={T} onClose={() => setOpen(false)} shot={shot} />}</>;"
assert OLD8 in c, 'OLD8 not found'
c = c.replace(OLD8, NEW8)

# 5) Admin display: screenshot thumbnail in BugReportsCard
OLD9 = "          <div style={{ fontFamily:T.font, fontSize:14, color:T.ink, whiteSpace:'pre-wrap', wordBreak:'break-word' }}>{r.text}</div>\n          <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:6 }}>{r.version} · {r.screen} · {r.createdAt && r.createdAt.toDate ? r.createdAt.toDate().toLocaleString('hu-HU') : ''}</div>"
NEW9 = (
    "          <div style={{ fontFamily:T.font, fontSize:14, color:T.ink, whiteSpace:'pre-wrap', wordBreak:'break-word' }}>{r.text}</div>\n"
    "          {r.screenshot && <a href={r.screenshot} target=\"_blank\" rel=\"noopener noreferrer\" style={{ display:'block', marginTop:8 }}><img src={r.screenshot} alt=\"screenshot\" style={{ maxWidth:'100%', maxHeight:200, borderRadius:10, border:`1px solid ${T.border}`, cursor:'pointer', display:'block' }} /></a>}\n"
    "          <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:6 }}>{r.version} · {r.screen} · {r.createdAt && r.createdAt.toDate ? r.createdAt.toDate().toLocaleString('hu-HU') : ''}</div>"
)
assert OLD9 in c, 'OLD9 not found'
assert c.count(OLD9) == 1, 'OLD9 not unique'
c = c.replace(OLD9, NEW9)

# 6) version bump
OLDV = "const APP_VERSION = 'v9.821';"
NEWV = "const APP_VERSION = 'v9.822';"
assert OLDV in c, 'version not found'
assert c.count(OLDV) == 1, 'version not unique'
c = c.replace(OLDV, NEWV)

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(c)
print('patch applied OK')
