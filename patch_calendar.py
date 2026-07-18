#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Naptár + meghívó integráció: "Naptárhoz adom" (Google Naptár template URL, egy
# koppintással előkitöltve — az emlékeztetőt a naptár kezeli) + felturbózott meghívó-megosztás.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

# ── 1) Modul-szintű Google Naptár URL helper az EventLogScreen elé ──
rep("function EventLogScreen({ go, goEdit, deepLink }) {",
"""// Google Naptár "esemény hozzáadása" template URL — nincs OAuth, egy koppintással
// előkitölti a naptárat; az emlékeztetőt maga a naptár adja.
function bohGCalUrl(ev) {
  const pad = n => String(n).padStart(2, '0');
  const fmt = (d, allDay) => {
    const dt = new Date(d);
    return allDay
      ? '' + dt.getFullYear() + pad(dt.getMonth() + 1) + pad(dt.getDate())
      : '' + dt.getUTCFullYear() + pad(dt.getUTCMonth() + 1) + pad(dt.getUTCDate()) + 'T' + pad(dt.getUTCHours()) + pad(dt.getUTCMinutes()) + '00Z';
  };
  const start = new Date(ev.date);
  let end;
  if (ev.dateTo) { end = new Date(ev.dateTo); if (ev.allDay) end.setDate(end.getDate() + 1); }
  else { end = new Date(start); if (ev.allDay) end.setDate(end.getDate() + 1); else end.setHours(end.getHours() + 3); }
  const dates = ev.allDay ? (fmt(start, true) + '/' + fmt(end, true)) : (fmt(start) + '/' + fmt(end));
  let deep = '';
  try { deep = location.origin + location.pathname + '?screen=events&event=' + ev.id; } catch(e) {}
  const params = new URLSearchParams({
    action: 'TEMPLATE',
    text: ev.title || 'Esemény',
    dates,
    location: ev.location || '',
    details: 'Bottle of Heroes esemény' + (deep ? ' — jelezz vissza: ' + deep : ''),
  });
  return 'https://calendar.google.com/calendar/render?' + params.toString();
}

function EventLogScreen({ go, goEdit, deepLink }) {""")

# ── 2) shareEvent → rendes meghívó-szöveg ──
rep("""  function shareEvent(sev) {
    const url = location.origin + location.pathname + '?screen=events&event=' + sev.id;
    if (navigator.share) {
      navigator.share({ title: sev.title, url }).catch(() => {});
    } else if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(() => { setShareCopied(true); setTimeout(() => setShareCopied(false), 2000); }).catch(() => {});
    }
  }""",
"""  function shareEvent(sev) {
    const url = location.origin + location.pathname + '?screen=events&event=' + sev.id;
    let dateStr = '';
    try {
      dateStr = sev.date ? new Date(sev.date).toLocaleString('hu-HU', sev.allDay ? { month:'long', day:'numeric' } : { month:'long', day:'numeric', hour:'2-digit', minute:'2-digit' }) : '';
    } catch(e) {}
    const invite = `${sev.emoji || '🎉'} ${sev.title}` + (dateStr ? `\\n📅 ${dateStr}` : '') + (sev.location ? `\\n📍 ${sev.location}` : '') + `\\n\\nJelezz vissza:`;
    if (navigator.share) {
      navigator.share({ title: sev.title, text: invite, url }).catch(() => {});
    } else if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(invite + '\\n' + url).then(() => { setShareCopied(true); setTimeout(() => setShareCopied(false), 2000); }).catch(() => {});
    }
  }""")

# ── 3) Naptár + Meghívó gombsor a részletek nézetben ──
rep("""          {/* Share */}
          <button onClick={() => shareEvent(ev)} style={{ width:'100%', padding:'13px', borderRadius:14, border:'none', background: shareCopied ? T.mint : T.surface, boxShadow:T.shadow, fontFamily:T.font, fontWeight:800, fontSize:14, color: shareCopied ? '#fff' : T.ink, cursor:'pointer', marginBottom:12, display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
            {shareCopied ? 'Link másolva ✓' : <React.Fragment><BohIcon name="share" size={14} style={{ marginRight:5 }} />Megosztás</React.Fragment>}
          </button>""",
"""          {/* Naptár + Meghívó */}
          <div style={{ display:'flex', gap:10, marginBottom:12 }}>
            {ev.date && !ev.cancelled && (
              <button onClick={() => { try { window.open(bohGCalUrl(ev), '_blank', 'noopener'); } catch(e) {} }} style={{ flex:1, padding:'13px', borderRadius:14, border:'none', background:T.surface, boxShadow:T.shadow, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:7 }}>
                <span style={{ fontSize:15, lineHeight:1 }}>📅</span> Naptárhoz
              </button>
            )}
            <button onClick={() => shareEvent(ev)} style={{ flex:1, padding:'13px', borderRadius:14, border:'none', background: shareCopied ? T.mint : T.surface, boxShadow:T.shadow, fontFamily:T.font, fontWeight:800, fontSize:14, color: shareCopied ? '#fff' : T.ink, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:7 }}>
              {shareCopied ? 'Másolva ✓' : <React.Fragment><BohIcon name="share" size={14} style={{ marginRight:3 }} />Meghívó</React.Fragment>}
            </button>
          </div>""")

# ── 4) Verziobump ──
rep("const APP_VERSION = 'v9.976';", "const APP_VERSION = 'v9.977';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — calendar + invite applied')
