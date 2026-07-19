#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Pub keverés-űrlap redesign: az app design-nyelvén (EventForm minta) — teljes
# képernyős nézet AppBar-ral, kártya-szekciók, keret nélküli inputok; a
# "Ki keverte?" avataros profil-választó (mint az esemény Létrehozó), és a
# kártyán + sheeten is avatar jelenik meg a név mellett.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

# ── 1) DrinkForm teljes csere ──
FSTART = '// ── Pub: saját keverés űrlap (új / szerkesztés) ──'
FEND = '\n\nfunction BarScreen({ go, deepLink }) {'
assert src.count(FSTART) == 1
i1 = src.index(FSTART)
i2 = src.index(FEND, i1)

NEW_FORM = r'''// ── Pub: saját keverés űrlap (új / szerkesztés) — app design, EventForm mintára ──
function DrinkForm({ init, profiles, onSave, onCancel }) {
  const [name, setName] = React.useState(init.name || '');
  const [emoji, setEmoji] = React.useState(init.emoji || '🍹');
  const [str, setStr] = React.useState(init.str || 2);
  const [ing, setIng] = React.useState((init.ing || []).join('\n'));
  const [step, setStep] = React.useState(init.step || '');
  const [creator, setCreator] = React.useState(() => {
    if (init.byId) {
      const p = (profiles || []).find(x => x.id === init.byId);
      if (p) return { id: p.id, name: p.name, color: p.color, img: p.img || null };
      return { id: init.byId, name: init.by || '?', color: '#98A2B3', img: null };
    }
    return null;
  });
  const [note, setNote] = React.useState(init.note || '');
  const valid = name.trim().length > 0;
  const strColor = s => s >= 3 ? T.coral : s === 2 ? (T.yellow || '#F4C95A') : T.mint;
  const inpStyle = { width:'100%', boxSizing:'border-box', padding:'13px 14px', borderRadius:13, border:'none', background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none' };
  const label = txt => <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:8 }}>{txt}</div>;
  const card = { background:T.surface, borderRadius:18, padding:'16px', boxShadow:T.shadow, marginBottom:12 };
  const save = () => {
    if (!valid) return;
    onSave({ name:name.trim(), emoji:(emoji||'').trim()||'🍹', str, ing:ing.split('\n').map(s => s.trim()).filter(Boolean), step:step.trim(), by: creator ? (creator.name || '') : (init.byId ? '' : (init.by || '')), byId: creator ? creator.id : '', note:note.trim() });
  };
  return (
    <div style={{ position:'fixed', inset:0, zIndex:80, background:T.bg, display:'flex', flexDirection:'column' }}>
      <AppBar title={init.id ? 'Keverés szerkesztése' : 'Új keverés'} onBack={onCancel} />
      <div style={{ flex:1, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'16px 16px 32px', maxWidth:680, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>
        {/* Alapok */}
        <div style={card}>
          {label('Név')}
          <div style={{ display:'flex', gap:10 }}>
            <input value={emoji} onChange={e => setEmoji(e.target.value)} style={{ ...inpStyle, width:58, flexShrink:0, textAlign:'center', fontSize:22, padding:'11px 4px' }} />
            <input value={name} onChange={e => setName(e.target.value)} placeholder="Pl. Dini bombája" style={{ ...inpStyle, flex:1, width:'auto', minWidth:0 }} />
          </div>
          <div style={{ marginTop:14 }}>
            {label('Erősség')}
            <div style={{ display:'flex', gap:8 }}>
              {[[1,'Könnyű'],[2,'Közepes'],[3,'Erős']].map(([v,l]) => (
                <button key={v} onClick={() => setStr(v)} style={{ flex:1, padding:'11px 0', borderRadius:13, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:13, background: str === v ? strColor(v) : T.bg, color: str === v ? '#fff' : T.inkSoft, boxShadow: str === v ? `0 4px 12px ${strColor(v)}55` : 'none', transition:'all .15s' }}>{l}</button>
              ))}
            </div>
          </div>
        </div>
        {/* Recept */}
        <div style={card}>
          {label('Hozzávalók — soronként egy')}
          <textarea value={ing} onChange={e => setIng(e.target.value)} rows={4} placeholder={'4 cl vodka\n1 dl áfonyalé\nsok jég'} style={{ ...inpStyle, resize:'vertical', lineHeight:1.55 }} />
          <div style={{ marginTop:14 }}>
            {label('Elkészítés')}
            <textarea value={step} onChange={e => setStep(e.target.value)} rows={2} placeholder="Hogyan kevered ki?" style={{ ...inpStyle, resize:'vertical', lineHeight:1.55 }} />
          </div>
        </div>
        {/* Ki keverte — avataros választó */}
        {profiles.length > 0 && (
          <div style={card}>
            {label('Ki keverte?')}
            <div style={{ display:'flex', gap:14, overflowX:'auto', WebkitOverflowScrolling:'touch', paddingBottom:4, paddingTop:4 }}>
              {profiles.map(p => {
                const sel = creator && creator.id === p.id;
                return (
                  <div key={p.id} onClick={() => setCreator(sel ? null : { id: p.id, name: p.name, color: p.color, img: p.img || null })}
                    style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:4, flexShrink:0, cursor:'pointer', WebkitTapHighlightColor:'transparent', opacity: creator && !sel ? 0.35 : 1, transition:'opacity .15s' }}>
                    <div style={{ width:42, height:42, borderRadius:'50%', display:'grid', placeItems:'center', overflow:'hidden', background: p.img ? T.bg : (p.color||'#888'), outline: sel ? `2.5px solid ${p.color||T.mint}` : '2.5px solid transparent', outlineOffset:3, transition:'outline-color .15s' }}>
                      {p.img
                        ? <img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
                        : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff' }}>{(p.name||'?')[0].toUpperCase()}</span>
                      }
                    </div>
                    <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color: sel ? (p.color||T.mint) : T.inkSoft, textAlign:'center', maxWidth:52, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
        {/* Megjegyzés */}
        <div style={card}>
          {label('Megjegyzés — pl. melyik bulin készült')}
          <input value={note} onChange={e => setNote(e.target.value)} placeholder="Nem kötelező" style={inpStyle} />
        </div>
        {/* Gombok */}
        <div style={{ display:'flex', gap:10, marginTop:4 }}>
          <button onClick={onCancel} style={{ flex:1, padding:'15px', borderRadius:16, border:'none', background:T.surface, boxShadow:T.shadow, color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:15, cursor:'pointer' }}>Mégse</button>
          <button onClick={save} disabled={!valid} style={{ flex:2, padding:'15px', borderRadius:16, border:'none', background: valid ? T.mint : T.border, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor: valid ? 'pointer' : 'default', boxShadow: valid ? `0 4px 14px ${T.mint}66` : 'none', transition:'all .2s' }}>Mentés</button>
        </div>
      </div>
    </div>
  );
}'''

src = src[:i1] + NEW_FORM + src[i2:]

# ── 2) DrinkCard: "Keverte" sor avatarral ──
rep("""          {d.by ? <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11.5, color:T.inkSoft, marginTop:2, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>Keverte: {d.by}</div> : null}""",
"""          {(d.byId || d.by) ? (() => { const bp = profOf(d.byId) || (d.by ? { name: d.by } : null); return (
            <div style={{ display:'flex', alignItems:'center', gap:5, marginTop:3, minWidth:0 }}>
              <Avatar pr={bp} size={16} />
              <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11.5, color:T.inkSoft, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{(bp && bp.name) || ''}</span>
            </div>
          ); })() : null}""")

# ── 3) Sheet: "Keverte" sor avatarral ──
rep("""              {d.by ? <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12.5, color:T.inkSoft, marginTop:4 }}>Keverte: {d.by}</div> : null}""",
"""              {(d.byId || d.by) ? (() => { const bp = profOf(d.byId) || (d.by ? { name: d.by } : null); return (
                <div style={{ display:'flex', alignItems:'center', gap:6, marginTop:6 }}>
                  <Avatar pr={bp} size={20} />
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12.5, color:T.inkSoft }}>Keverte: {(bp && bp.name) || ''}</span>
                </div>
              ); })() : null}""")

# ── 4) Verziobump ──
rep("const APP_VERSION = 'v9.985';", "const APP_VERSION = 'v9.986';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — Pub form redesign applied')
