#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Wildcard admin szerkesztő: Firestore-backed wildcard lista (config/wildcards),
# admin tab (create/edit/delete/add/reset), runtime betöltés app-indításkor.
import io, sys

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

# 1) Firestore helperek a config IIFE végére
rep("""  window.onHiddenGames = function(cb) {
    return db.collection('config').doc('hiddenGames').onSnapshot(function(d) {
      cb(d.exists ? (d.data().ids || []) : []);
    });
  };
})();""",
"""  window.onHiddenGames = function(cb) {
    return db.collection('config').doc('hiddenGames').onSnapshot(function(d) {
      cb(d.exists ? (d.data().ids || []) : []);
    });
  };
  window.getWildcards = function() {
    return db.collection('config').doc('wildcards').get().then(function(d) {
      return d.exists ? (d.data().list || null) : null;
    }).catch(function() { return null; });
  };
  window.setWildcards = function(list) {
    return db.collection('config').doc('wildcards').set({ list: list }).catch(function(e) { console.warn('setWildcards', e); });
  };
})();""")

# 2) WILDCARDS -> WILDCARDS_DEFAULT + mutable lista + startup betöltés
rep("const WILDCARDS = [", "const WILDCARDS_DEFAULT = [")
rep("""  { emoji:'🤙', text:'Csak mutogatással lehet kommunikálni — aki szól, iszik!' },
];""",
"""  { emoji:'🤙', text:'Csak mutogatással lehet kommunikálni — aki szól, iszik!' },
];
let WILDCARDS = WILDCARDS_DEFAULT;
try {
  if (window.getWildcards) window.getWildcards().then(l => {
    if (Array.isArray(l) && l.length) WILDCARDS = l.filter(w => w && w.text);
  });
} catch(e) {}""")

# 3) Admin tab a listába
rep("['games','Játékok'],['stats','Statisztika']",
    "['games','Játékok'],['wildcards','Wildcard'],['stats','Statisztika']")

# 4) Tab render
rep("        {tab === 'games'    && <AdminGames />}",
    "        {tab === 'games'    && <AdminGames />}\n        {tab === 'wildcards' && <AdminWildcards />}")

# 5) AdminWildcards komponens az AdminTasks után
rep("""function EventLogScreen({ go, goEdit, deepLink }) {""",
"""function AdminWildcards() {
  const [list, setList] = React.useState(null);
  const [saving, setSaving] = React.useState(false);
  const [saved, setSaved] = React.useState(false);
  const [dirty, setDirty] = React.useState(false);
  const [confirmDel, setConfirmDel] = React.useState(null);
  const [confirmReset, setConfirmReset] = React.useState(false);
  React.useEffect(() => {
    (window.getWildcards ? window.getWildcards() : Promise.resolve(null)).then(l => {
      const src = (Array.isArray(l) && l.length) ? l : WILDCARDS_DEFAULT;
      setList(src.map(w => ({ emoji: w.emoji || '', text: w.text || '' })));
    }).catch(() => setList(WILDCARDS_DEFAULT.map(w => ({ emoji: w.emoji, text: w.text }))));
  }, []);
  const upd = (i, field, val) => { setList(l => l.map((w, j) => j === i ? { ...w, [field]: val } : w)); setDirty(true); setSaved(false); };
  const del = (i) => { setList(l => l.filter((_, j) => j !== i)); setConfirmDel(null); setDirty(true); setSaved(false); };
  const add = () => { setList(l => [...l, { emoji:'🃏', text:'' }]); setDirty(true); setSaved(false); };
  const persist = (clean) => {
    setSaving(true);
    (window.setWildcards ? window.setWildcards(clean) : Promise.resolve()).then(() => {
      WILDCARDS = clean.map(w => ({ ...w }));
      setList(clean.map(w => ({ ...w })));
      setSaving(false); setDirty(false); setConfirmReset(false); setSaved(true);
    }).catch(() => setSaving(false));
  };
  const save = () => {
    const clean = (list || []).map(w => ({ emoji: (w.emoji || '').trim() || '🃏', text: (w.text || '').trim() })).filter(w => w.text);
    if (!clean.length) return;
    persist(clean);
  };
  const reset = () => persist(WILDCARDS_DEFAULT.map(w => ({ emoji: w.emoji, text: w.text })));

  if (list === null) return <div style={{ textAlign:'center', padding:30, fontFamily:T.font, color:T.sub }}>Betöltés…</div>;
  const validCount = list.filter(w => (w.text || '').trim()).length;
  return (
    <div style={{ padding:16 }}>
      <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:4 }}>
        <BohIcon name="wildcard" size={20} />
        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>Wildcard kártyák</span>
        <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.mint, background:T.mintSoft, borderRadius:999, padding:'2px 8px' }}>{validCount} db</span>
      </div>
      <div style={{ fontFamily:T.font, fontSize:12.5, color:T.sub, marginBottom:12 }}>Ezek jelennek meg a wildcard körökben. Mentés után a többi készüléken az app következő indításakor töltődik be a friss lista.</div>
      <div style={{ display:'flex', flexDirection:'column', gap:8, marginBottom:14 }}>
        {list.map((w, i) => (
          <div key={i} style={{ background:T.surface, borderRadius:14, padding:'10px 12px', boxShadow:T.shadow, display:'flex', gap:8, alignItems:'flex-start' }}>
            <input value={w.emoji} onChange={e => upd(i, 'emoji', e.target.value)} placeholder="🃏" style={{ width:52, boxSizing:'border-box', padding:'9px 4px', borderRadius:10, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:18, textAlign:'center', color:T.ink, outline:'none', flexShrink:0 }} />
            <textarea value={w.text} onChange={e => upd(i, 'text', e.target.value)} placeholder="Wildcard szöveg…" rows={2} style={{ flex:1, boxSizing:'border-box', padding:'9px 10px', borderRadius:10, border:`1.5px solid ${(w.text||'').trim() ? T.border : T.coral}`, background:T.bg, fontFamily:T.font, fontSize:13, color:T.ink, outline:'none', resize:'vertical', minWidth:0 }} />
            <button onClick={() => { if (confirmDel === i) del(i); else setConfirmDel(i); }} style={{ padding:'8px 10px', borderRadius:10, border:'none', background: confirmDel === i ? T.coral : T.coralSoft, color: confirmDel === i ? '#fff' : T.coral, fontFamily:T.font, fontWeight:700, fontSize:12, cursor:'pointer', flexShrink:0, alignSelf:'center', display:'flex', alignItems:'center' }}>{confirmDel === i ? 'Biztos?' : <BohIcon name="trash" size={14} />}</button>
          </div>
        ))}
      </div>
      <button onClick={add} style={{ width:'100%', padding:'12px', borderRadius:14, border:`2px dashed ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft, cursor:'pointer', marginBottom:14 }}>+ Új wildcard</button>
      <div style={{ display:'flex', gap:8, alignItems:'center' }}>
        <button onClick={() => { if (confirmReset) reset(); else setConfirmReset(true); }} disabled={saving} style={{ padding:'11px 14px', borderRadius:12, border:'none', background: confirmReset ? T.coral : T.surfaceMuted, color: confirmReset ? '#fff' : T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer' }}>{confirmReset ? 'Biztos? Minden felülíródik!' : 'Alaphelyzet'}</button>
        <div style={{ flex:1 }} />
        {saved && !dirty && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.mint }}>Mentve ✓</span>}
        <button onClick={save} disabled={saving || !dirty || !validCount} style={{ padding:'12px 20px', borderRadius:12, border:'none', background: dirty && validCount ? T.mint : T.mintSoft, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor: dirty && validCount ? 'pointer' : 'default', opacity: saving ? 0.6 : 1 }}>Mentés</button>
      </div>
    </div>
  );
}

function EventLogScreen({ go, goEdit, deepLink }) {""")

# 6) Verziobump
rep("const APP_VERSION = 'v9.946';", "const APP_VERSION = 'v9.947';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — wildcard admin patch applied')
