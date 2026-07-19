#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Saját keveréseknél koktél/shot megkülönböztetés: Típus választó az űrlapon,
# Mind/Koktél/Shot szűrő a "Mi kevertük" listán, típus-jelvény a kártyán és a sheeten.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

# ── 1) DrinkForm: type state ──
rep("""  const [note, setNote] = React.useState(init.note || '');
  const valid = name.trim().length > 0;""",
"""  const [type, setType] = React.useState(init.type === 'shot' ? 'shot' : 'cocktail');
  const [note, setNote] = React.useState(init.note || '');
  const valid = name.trim().length > 0;""")

# ── 2) DrinkForm: type a mentett adatban ──
rep("onSave({ name:name.trim(), emoji:(emoji||'').trim()||'🍹', str, ing:",
    "onSave({ name:name.trim(), emoji:(emoji||'').trim()||'🍹', type, str, ing:")

# ── 3) DrinkForm: Típus választó az Alapok kártyában (az Erősség elé) ──
rep("""          <div style={{ marginTop:14 }}>
            {label('Erősség')}""",
"""          <div style={{ marginTop:14 }}>
            {label('Típus')}
            <div style={{ display:'flex', gap:8 }}>
              {[['cocktail','Koktél 🍹'],['shot','Shot 🥃']].map(([v,l]) => (
                <button key={v} onClick={() => { setType(v); setEmoji(em => (em === '🍹' || em === '🥃') ? (v === 'shot' ? '🥃' : '🍹') : em); }} style={{ flex:1, padding:'11px 0', borderRadius:13, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:13, background: type === v ? T.mint : T.bg, color: type === v ? '#fff' : T.inkSoft, boxShadow: type === v ? `0 4px 12px ${T.mint}55` : 'none', transition:'all .15s' }}>{l}</button>
              ))}
            </div>
          </div>
          <div style={{ marginTop:14 }}>
            {label('Erősség')}""")

# ── 4) BarScreen: szűrő state ──
rep("""  const [confirmDel, setConfirmDel] = React.useState(false);
  const db = (typeof firebase !== 'undefined') ? firebase.firestore() : null;""",
"""  const [confirmDel, setConfirmDel] = React.useState(false);
  const [ownFilter, setOwnFilter] = React.useState('all');
  const db = (typeof firebase !== 'undefined') ? firebase.firestore() : null;""")

# ── 5) Szűrt lista (az érmek a teljes listából számolódnak) ──
rep("""  const medalFor = {};
  ownSorted.filter(d => avgOf(d.id).n > 0).slice(0, 3).forEach((d, i) => { medalFor[d.id] = ['🥇','🥈','🥉'][i]; });""",
"""  const medalFor = {};
  ownSorted.filter(d => avgOf(d.id).n > 0).slice(0, 3).forEach((d, i) => { medalFor[d.id] = ['🥇','🥈','🥉'][i]; });
  const ownShown = ownFilter === 'all' ? ownSorted : ownSorted.filter(d => (d.type === 'shot' ? 'shot' : 'cocktail') === ownFilter);""")

# ── 6) Szűrő chipek a fejléc alá ──
rep("""          <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginBottom:10 }}>A DNR-eken készült keverések — koppints egy italra a részletekhez és az értékeléshez.</div>""",
"""          <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginBottom:10 }}>A DNR-eken készült keverések — koppints egy italra a részletekhez és az értékeléshez.</div>
          <div style={{ display:'flex', gap:7, marginBottom:12 }}>
            {[['all','Mind'],['cocktail','🍹 Koktél'],['shot','🥃 Shot']].map(([k,l]) => { const on = ownFilter === k; return (
              <button key={k} onClick={() => setOwnFilter(k)} style={{ padding:'7px 14px', borderRadius:999, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:12.5, background: on ? T.mint : T.surface, color: on ? '#fff' : T.ink, boxShadow: on ? `0 3px 0 ${T.mintDeep||T.mint}66, 0 6px 14px ${T.mint}33` : T.shadow }}>{l}</button>
            ); })}
          </div>""")

# ── 7) A lista a szűrt elemeket mutatja + üres szűrő üzenet ──
rep("""            <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
              {ownSorted.map(d => <DrinkCard key={d.id} d={d} medal={medalFor[d.id]} />)}
            </div>""",
"""            <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
              {ownShown.map(d => <DrinkCard key={d.id} d={d} medal={medalFor[d.id]} />)}
              {ownShown.length === 0 && <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, textAlign:'center', padding:'18px 0' }}>Ebben a kategóriában még nincs keverés.</div>}
            </div>""")

# ── 8) DrinkCard: típus-jelvény a név sorban (csak saját italnál) ──
rep("""            {medal && <span style={{ fontSize:15, lineHeight:1, flexShrink:0 }}>{medal}</span>}""",
"""            {medal && <span style={{ fontSize:15, lineHeight:1, flexShrink:0 }}>{medal}</span>}
            {d.custom && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:10, color:T.inkSoft, background:T.surfaceMuted, borderRadius:999, padding:'2px 8px', flexShrink:0 }}>{d.type === 'shot' ? '🥃 Shot' : '🍹 Koktél'}</span>}""")

# ── 9) Sheet: típus-jelvény az erősség mellett ──
rep("""                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:19, color:T.ink, lineHeight:1.15 }}>{d.name}</div>
                  <div style={{ marginTop:5 }}><StrDots s={d.str || 2} /></div>""",
"""                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:19, color:T.ink, lineHeight:1.15 }}>{d.name}</div>
                  <div style={{ marginTop:5, display:'flex', alignItems:'center', gap:8, flexWrap:'wrap' }}>
                    <StrDots s={d.str || 2} />
                    {d.custom && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:10.5, color:T.inkSoft, background:T.surfaceMuted, borderRadius:999, padding:'2px 8px' }}>{d.type === 'shot' ? '🥃 Shot' : '🍹 Koktél'}</span>}
                  </div>""")

# ── 10) Verziobump ──
rep("const APP_VERSION = 'v9.986';", "const APP_VERSION = 'v9.987';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — koktél/shot típus applied')
