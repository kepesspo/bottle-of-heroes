# v10.166 — tomeges kortyolasi-limit szerkeszto az Admin Profilok panelben
#
# A limit a profilra mentodik, ezert a Jatekmenet oldalrol kikerult (v10.165).
# Szerkeszteni eddig csak profilonkent kulon megnyitva lehetett — pedig ez
# tipikusan olyan, amit egyszer kell vegigmenni mindenkin. Ez a kartya egy
# gorgetessel engedi ugyanazt.
#
# Mentes a mezobol kilepeskor (blur), nem minden leutesre — kulonben minden
# beirt szamjegy kulon irast inditana.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── a celzott iro segedfuggveny vissza (a saveProfile nevet/szint is varna) ──
anchor = "  window.saveProfile = function(profile) {"
assert s.count(anchor) == 1
s = s.replace(anchor, """  window.setProfileDrinkLimit = function(profileId, limit) {
    if (!profileId) return Promise.resolve();
    var v = Number(limit) > 0 ? Number(limit) : firebase.firestore.FieldValue.delete();
    return db.collection('profiles').doc(profileId).set({ drinkLimit: v }, { merge: true })
      .catch(function(e) { console.warn('setProfileDrinkLimit', e); });
  };
""" + anchor)

# ── a kartya ──
CARD = '''// Tomeges kortyolasi-limit szerkeszto. A limit a profilon el, es tipikusan
// egyszer allitja be az ember mindenkinek — ezert egy listaban, nem profilonkent
// kulon megnyitva. Alapbol osszecsukva: ritkan nyulnak hozza.
function AdminDrinkLimits({ profiles, onSaved }) {
  const [open, setOpen] = React.useState(false);
  const [vals, setVals] = React.useState({});
  React.useEffect(() => {
    const m = {};
    (profiles || []).forEach(p => { m[p.id] = p.drinkLimit ? String(p.drinkLimit) : ''; });
    setVals(m);
  }, [profiles]);

  const commit = (id) => {
    const v = vals[id] || '';
    const before = (profiles || []).find(p => p.id === id);
    if (String(before && before.drinkLimit ? before.drinkLimit : '') === v) return;  // nem valtozott
    if (typeof window.setProfileDrinkLimit === 'function') {
      window.setProfileDrinkLimit(id, v).then(() => { onSaved && onSaved(); });
    }
  };
  const count = (profiles || []).filter(p => Number(vals[p.id]) > 0).length;

  return (
    <div style={{ background:T.surface, borderRadius:16, boxShadow:T.shadow, marginBottom:14, overflow:'hidden' }}>
      <button onClick={() => setOpen(o => !o)} style={{ width:'100%', display:'flex', alignItems:'center', gap:10,
        background:'transparent', border:'none', cursor:'pointer', padding:'14px 16px', textAlign:'left' }}>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>Kortyolási limitek</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:2 }}>
            Ha valaki eléri a sajátját, a kör végén figyelmeztetünk, és a neve mellé kerül egy 💧.
          </div>
        </div>
        {count > 0 && <span style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.mintDeep,
          background:T.mintSoft, borderRadius:999, padding:'3px 9px', flexShrink:0 }}>{count} beállítva</span>}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ flexShrink:0,
          transform: open ? 'rotate(0deg)' : 'rotate(-90deg)', transition:'transform .2s' }}>
          <path d="M6 9l6 6 6-6" stroke={T.inkMute} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
      {open && (
        <div style={{ padding:'0 16px 14px', display:'flex', flexDirection:'column', gap:8 }}>
          {(profiles || []).length === 0 ? (
            <div style={{ fontFamily:T.font, fontSize:13, color:T.sub }}>Még nincs profil.</div>
          ) : (profiles || []).map(p => (
            <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10, minHeight:52 }}>
              <div style={{ width:32, height:32, borderRadius:'50%', background:p.color || T.mint, flexShrink:0,
                display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff' }}>
                {(p.nickname || p.name || '?').charAt(0).toUpperCase()}
              </div>
              <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink,
                overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.nickname || p.name}</div>
              <input value={vals[p.id] == null ? '' : vals[p.id]}
                onChange={e => setVals(m => Object.assign({}, m, { [p.id]: e.target.value.replace(/[^0-9]/g, '') }))}
                onBlur={() => commit(p.id)} placeholder="nincs" inputMode="numeric" type="number"
                style={{ width:74, flexShrink:0, textAlign:'center', padding:'9px 6px', borderRadius:10,
                  border:`2px solid ${T.inkMute}28`, background:T.bgSoft, color:T.ink,
                  fontFamily:T.font, fontWeight:900, fontSize:15, outline:'none' }} />
              <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkMute, flexShrink:0 }}>korty</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

'''
mark = 'function AdminProfiles() {'
assert s.count(mark) == 1
s = s.replace(mark, CARD + mark)

# ── beillesztes a panelbe, a profil-lista ele ──
old = """      <button onClick={() => setShowForm(s => !s)} style={{ width:'100%', padding:'13px', borderRadius:14, border:`2px dashed ${T.mint}`,"""
assert s.count(old) == 1
s = s.replace(old, """      <AdminDrinkLimits profiles={profiles} onSaved={load} />
""" + old)

s = s.replace("const APP_VERSION = 'v10.165';", "const APP_VERSION = 'v10.166';", 1)
assert "v10.166" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
