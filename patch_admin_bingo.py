#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Admin Bingó vezérlők: kapcsoló a VB Bingó megjelenítéséhez (főképernyő banner),
# szerkeszthető cím (tematika) és bingó-mezők (emoji + szöveg). A beállítás a
# Firestore config/bingoConfig dokban él (enabled/title/items), a BingoScreen és a
# HomeScreen élőben olvassa; hiányzó/kevés (<24) mezőnél a beépített defaultra esik vissza.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

# ── 1) Firestore helperek (setWildcards után) ──
rep("""  window.setWildcards = function(list) {
    return db.collection('config').doc('wildcards').set({ list: list }).catch(function(e) { console.warn('setWildcards', e); });
  };
})();""",
"""  window.setWildcards = function(list) {
    return db.collection('config').doc('wildcards').set({ list: list }).catch(function(e) { console.warn('setWildcards', e); });
  };
  window.getBingoConfig = function() {
    return db.collection('config').doc('bingoConfig').get().then(function(d) {
      return d.exists ? d.data() : null;
    }).catch(function() { return null; });
  };
  window.setBingoConfig = function(cfg) {
    return db.collection('config').doc('bingoConfig').set(cfg).catch(function(e) { console.warn('setBingoConfig', e); });
  };
})();""")

# ── 2) bingoCardFor: opcionális n (mezőszám) ──
rep("""function bingoCardFor(pid) {
  // determinisztikus keverés a profil id-ből — mindenkinek saját, de stabil kártya
  let s = 2166136261;
  const key = 'boh-bingo-' + pid;
  for (let i = 0; i < key.length; i++) { s ^= key.charCodeAt(i); s = Math.imul(s, 16777619); }
  s >>>= 0; if (!s) s = 88172645;
  const rnd = () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
  const arr = BINGO_ITEMS.map((_, i) => i);""",
"""function bingoCardFor(pid, n) {
  // determinisztikus keverés a profil id-ből — mindenkinek saját, de stabil kártya
  const cnt = n || BINGO_ITEMS.length;
  let s = 2166136261;
  const key = 'boh-bingo-' + pid;
  for (let i = 0; i < key.length; i++) { s ^= key.charCodeAt(i); s = Math.imul(s, 16777619); }
  s >>>= 0; if (!s) s = 88172645;
  const rnd = () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
  const arr = Array.from({ length: cnt }, (_, i) => i);""")

# ── 3) BingoScreen: config feliratkozás + derivált ITEMS/cím ──
rep("""  const [celebrate, setCelebrate] = React.useState(null);
  const [confirmReset, setConfirmReset] = React.useState(false);
  const prevBingos = React.useRef(null);
  const db = (typeof firebase !== 'undefined') ? firebase.firestore() : null;

  React.useEffect(() => {
    if (typeof window.getProfiles === 'function') window.getProfiles().then(ps => setProfiles(ps || [])).catch(() => {});
    if (!db) { setLoaded(true); return; }
    const un = db.collection('config').doc('bingo').onSnapshot(d => { setMarksAll((d && d.exists && d.data()) || {}); setLoaded(true); }, () => setLoaded(true));
    return () => { try { un(); } catch(e) {} };
  }, []);""",
"""  const [celebrate, setCelebrate] = React.useState(null);
  const [confirmReset, setConfirmReset] = React.useState(false);
  const [cfg, setCfg] = React.useState(null);
  const prevBingos = React.useRef(null);
  const db = (typeof firebase !== 'undefined') ? firebase.firestore() : null;

  React.useEffect(() => {
    if (typeof window.getProfiles === 'function') window.getProfiles().then(ps => setProfiles(ps || [])).catch(() => {});
    if (!db) { setLoaded(true); return; }
    const un = db.collection('config').doc('bingo').onSnapshot(d => { setMarksAll((d && d.exists && d.data()) || {}); setLoaded(true); }, () => setLoaded(true));
    const un2 = db.collection('config').doc('bingoConfig').onSnapshot(d => setCfg((d && d.exists && d.data()) || null), () => {});
    return () => { try { un(); } catch(e) {} try { un2(); } catch(e) {} };
  }, []);

  const ITEMS = (cfg && Array.isArray(cfg.items) && cfg.items.length >= 24) ? cfg.items : BINGO_ITEMS;
  const bingoTitle = (cfg && cfg.title) ? cfg.title : 'VB Bingó';""")

# ── 4) BingoScreen: card az ITEMS hosszával, AppBar cím ──
rep("  const card = who ? bingoCardFor(who) : null;",
    "  const card = who ? bingoCardFor(who, ITEMS.length) : null;")

rep('      <AppBar title="VB Bingó ⚽" onBack={() => go(\'home\')} right={who ? (',
    '      <AppBar title={bingoTitle + " ⚽"} onBack={() => go(\'home\')} right={who ? (')

# ── 5) BingoScreen: a rács a konfigurált ITEMS-ből ──
rep("                const item = free ? null : BINGO_ITEMS[card[c < 12 ? c : c - 1]];",
    "                const item = free ? null : ITEMS[card[c < 12 ? c : c - 1]];")

# ── 6) HomeScreen: bingoConfig feliratkozás (a boxInfo effekt mellé) ──
rep("""  const [nextEvent, setNextEvent] = React.useState(null);
  const [boxInfo, setBoxInfo] = React.useState(null);""",
"""  const [nextEvent, setNextEvent] = React.useState(null);
  const [boxInfo, setBoxInfo] = React.useState(null);
  const [bingoCfg, setBingoCfg] = React.useState(null);
  React.useEffect(() => {
    if (typeof firebase === 'undefined') return;
    const un = firebase.firestore().collection('config').doc('bingoConfig').onSnapshot(d => setBingoCfg((d && d.exists && d.data()) || null), () => {});
    return () => { try { un(); } catch(e) {} };
  }, []);
  const bingoOn = !bingoCfg || bingoCfg.enabled !== false;
  const bingoLabel = (bingoCfg && bingoCfg.title) ? bingoCfg.title : 'VB Bingó';""")

# ── 7) HomeScreen: banner csak ha bingoOn, a cím a configból ──
rep("""            <button onClick={() => go('bingo')} style={{ position:'relative', overflow:'hidden', display:'flex', alignItems:'center', gap:12, border:'none', background:'linear-gradient(115deg, #1E7A46, #2FA35F 55%, #1E7A46)', borderRadius:18, padding:'13px 16px', cursor:'pointer', boxShadow:'0 4px 0 rgba(20,83,45,0.6), 0 11px 24px rgba(20,83,45,0.35)', transform:'rotate(0.5deg)', WebkitTapHighlightColor:'transparent', textAlign:'left' }}>
              <span style={{ fontSize:26, lineHeight:1 }}>⚽</span>
              <span style={{ flex:1, minWidth:0 }}>
                <span style={{ display:'block', fontFamily:T.font, fontWeight:900, fontSize:15.5, color:'#fff' }}>VB Bingó 🏆</span>
                <span style={{ display:'block', fontFamily:T.font, fontWeight:700, fontSize:10.5, color:'rgba(255,255,255,0.85)', marginTop:1 }}>X-eld ki, ami megtörténik a döntőben!</span>
              </span>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'rgba(255,255,255,0.9)' }}>›</span>
              <span style={{ position:'absolute', right:-18, top:-18, width:70, height:70, border:'2.5px solid rgba(255,255,255,0.16)', borderRadius:'50%', pointerEvents:'none' }} />
              <span style={{ position:'absolute', right:16, bottom:-30, width:60, height:60, border:'2.5px solid rgba(255,255,255,0.1)', borderRadius:'50%', pointerEvents:'none' }} />
            </button>""",
"""            {bingoOn && (
            <button onClick={() => go('bingo')} style={{ position:'relative', overflow:'hidden', display:'flex', alignItems:'center', gap:12, border:'none', background:'linear-gradient(115deg, #1E7A46, #2FA35F 55%, #1E7A46)', borderRadius:18, padding:'13px 16px', cursor:'pointer', boxShadow:'0 4px 0 rgba(20,83,45,0.6), 0 11px 24px rgba(20,83,45,0.35)', transform:'rotate(0.5deg)', WebkitTapHighlightColor:'transparent', textAlign:'left' }}>
              <span style={{ fontSize:26, lineHeight:1 }}>⚽</span>
              <span style={{ flex:1, minWidth:0 }}>
                <span style={{ display:'block', fontFamily:T.font, fontWeight:900, fontSize:15.5, color:'#fff' }}>{bingoLabel} 🏆</span>
                <span style={{ display:'block', fontFamily:T.font, fontWeight:700, fontSize:10.5, color:'rgba(255,255,255,0.85)', marginTop:1 }}>X-eld ki, ami megtörténik a döntőben!</span>
              </span>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'rgba(255,255,255,0.9)' }}>›</span>
              <span style={{ position:'absolute', right:-18, top:-18, width:70, height:70, border:'2.5px solid rgba(255,255,255,0.16)', borderRadius:'50%', pointerEvents:'none' }} />
              <span style={{ position:'absolute', right:16, bottom:-30, width:60, height:60, border:'2.5px solid rgba(255,255,255,0.1)', borderRadius:'50%', pointerEvents:'none' }} />
            </button>
            )}""")

# ── 8) AdminBingo komponens (az AdminWildcards elé) ──
rep("function AdminWildcards() {",
"""function AdminBingo() {
  const [enabled, setEnabled] = React.useState(true);
  const [title, setTitle] = React.useState('VB Bingó');
  const [items, setItems] = React.useState(null);
  const [saving, setSaving] = React.useState(false);
  const [saved, setSaved] = React.useState(false);
  const [dirty, setDirty] = React.useState(false);
  const [confirmReset, setConfirmReset] = React.useState(false);
  React.useEffect(() => {
    (window.getBingoConfig ? window.getBingoConfig() : Promise.resolve(null)).then(c => {
      setEnabled(c ? c.enabled !== false : true);
      setTitle((c && c.title) || 'VB Bingó');
      setItems((c && Array.isArray(c.items) && c.items.length) ? c.items.map(it => ({ e: it.e || '', t: it.t || '' })) : BINGO_ITEMS.map(it => ({ e: it.e, t: it.t })));
    }).catch(() => { setItems(BINGO_ITEMS.map(it => ({ e: it.e, t: it.t }))); });
  }, []);
  const markDirty = () => { setDirty(true); setSaved(false); };
  const updItem = (i, field, val) => { setItems(l => l.map((w, j) => j === i ? { ...w, [field]: val } : w)); markDirty(); };
  const delItem = (i) => { setItems(l => l.filter((_, j) => j !== i)); markDirty(); };
  const addItem = () => { setItems(l => [...l, { e: '⚽', t: '' }]); markDirty(); };
  const toggleEnabled = () => { setEnabled(v => !v); markDirty(); };
  const setTitleV = v => { setTitle(v); markDirty(); };

  const persist = (en, ti, its) => {
    setSaving(true);
    const clean = (its || []).map(w => ({ e: (w.e || '').trim() || '⚽', t: (w.t || '').trim() })).filter(w => w.t);
    (window.setBingoConfig ? window.setBingoConfig({ enabled: en, title: (ti || '').trim() || 'VB Bingó', items: clean }) : Promise.resolve())
      .then(() => { setItems(clean.map(w => ({ ...w }))); setSaving(false); setDirty(false); setSaved(true); setConfirmReset(false); })
      .catch(() => setSaving(false));
  };
  const save = () => persist(enabled, title, items);
  const reset = () => { const d = BINGO_ITEMS.map(it => ({ e: it.e, t: it.t })); setEnabled(true); setTitle('VB Bingó'); setItems(d); persist(true, 'VB Bingó', d); };

  if (items === null) return <div style={{ textAlign:'center', padding:30, fontFamily:T.font, color:T.sub }}>Betöltés…</div>;
  const validCount = items.filter(w => (w.t || '').trim()).length;
  const tooFew = validCount < 24;
  return (
    <div style={{ padding:16 }}>
      <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:4 }}>
        <span style={{ fontSize:20, lineHeight:1 }}>⚽</span>
        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>VB Bingó</span>
        <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color: tooFew ? T.coral : T.mint, background: tooFew ? T.coralSoft : T.mintSoft, borderRadius:999, padding:'2px 8px' }}>{validCount} mező</span>
      </div>
      <div style={{ fontFamily:T.font, fontSize:12.5, color:T.sub, marginBottom:12 }}>A kapcsoló ki-be teszi a főképernyő bingó gombját. A cím és a mezők szabadon szerkeszthetők. A kártya 24 mezőt sorsol ki (középen fix DÖNTŐ), ezért legalább 24 mező kell — kevesebbnél a beépített lista marad érvényben.</div>

      {/* Megjelenítés kapcsoló */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
        <div>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>Megjelenítés a főképernyőn</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>{enabled ? 'Látszik a bingó gomb' : 'El van rejtve'}</div>
        </div>
        <Toggle on={enabled} onChange={toggleEnabled} />
      </div>

      {/* Cím / tematika */}
      <div style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:7 }}>Cím / tematika</div>
        <input value={title} onChange={e => setTitleV(e.target.value)} placeholder="VB Bingó" style={{ width:'100%', boxSizing:'border-box', padding:'10px 12px', borderRadius:10, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />
      </div>

      {tooFew && <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.coral, background:T.coralSoft, borderRadius:10, padding:'8px 12px', marginBottom:10 }}>Legalább 24 mező kell — jelenleg {validCount}. Mentésig/24-ig a beépített lista marad.</div>}

      {/* Mezők */}
      <div style={{ display:'flex', flexDirection:'column', gap:7, marginBottom:12 }}>
        {items.map((w, i) => (
          <div key={i} style={{ display:'flex', gap:7, alignItems:'center', background:T.surface, borderRadius:12, padding:'7px 9px', boxShadow:T.shadow }}>
            <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkMute, width:20, textAlign:'center', flexShrink:0 }}>{i+1}</span>
            <input value={w.e} onChange={e => updItem(i, 'e', e.target.value)} placeholder="⚽" style={{ width:46, boxSizing:'border-box', padding:'8px 4px', borderRadius:9, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:17, textAlign:'center', color:T.ink, outline:'none', flexShrink:0 }} />
            <input value={w.t} onChange={e => updItem(i, 't', e.target.value)} placeholder="Esemény szövege…" style={{ flex:1, minWidth:0, boxSizing:'border-box', padding:'9px 10px', borderRadius:9, border:`1.5px solid ${(w.t||'').trim() ? T.border : T.coral}`, background:T.bg, fontFamily:T.font, fontSize:13, color:T.ink, outline:'none' }} />
            <button onClick={() => delItem(i)} style={{ padding:'8px 9px', borderRadius:9, border:'none', background:T.coralSoft, color:T.coral, cursor:'pointer', flexShrink:0, display:'flex', alignItems:'center' }}><BohIcon name="trash" size={13} /></button>
          </div>
        ))}
      </div>
      <button onClick={addItem} style={{ width:'100%', padding:'12px', borderRadius:14, border:`2px dashed ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft, cursor:'pointer', marginBottom:14 }}>+ Új mező</button>

      <div style={{ display:'flex', gap:8, alignItems:'center' }}>
        <button onClick={() => { if (confirmReset) reset(); else setConfirmReset(true); }} disabled={saving} style={{ padding:'11px 14px', borderRadius:12, border:'none', background: confirmReset ? T.coral : T.surfaceMuted, color: confirmReset ? '#fff' : T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer' }}>{confirmReset ? 'Biztos? Alaphelyzet!' : 'Alaphelyzet'}</button>
        <div style={{ flex:1 }} />
        {saved && !dirty && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.mint }}>Mentve ✓</span>}
        <button onClick={save} disabled={saving || !dirty} style={{ padding:'12px 20px', borderRadius:12, border:'none', background: dirty ? T.mint : T.mintSoft, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor: dirty ? 'pointer' : 'default', opacity: saving ? 0.6 : 1 }}>Mentés</button>
      </div>
    </div>
  );
}

function AdminWildcards() {""")

# ── 9) Admin tab: Bingó (a Wildcard után) ──
rep("['wildcards','Wildcard'],['stats','Statisztika']",
    "['wildcards','Wildcard'],['bingo','Bingó'],['stats','Statisztika']")

rep("        {tab === 'wildcards' && <AdminWildcards />}",
    "        {tab === 'wildcards' && <AdminWildcards />}\n        {tab === 'bingo' && <AdminBingo />}")

# ── 10) Verziobump ──
rep("const APP_VERSION = 'v9.990';", "const APP_VERSION = 'v9.991';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — admin bingo + mitval fix applied')
