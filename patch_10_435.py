# v10.435 — Gender Reveal: Kisfiú/Kislány, telefonon távirányító, a vetítőről nincs kvíz-indítás
p = 'app.src.html'
s = open(p, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.434';", "const APP_VERSION = 'v10.435';")

# ── 1. Kisfiú / Kislány
rep("boy:  { word:'FIÚ!',  name:'Fiú',  emoji:'💙'", "boy:  { word:'KISFIÚ!',  name:'Kisfiú',  emoji:'💙'")
rep("girl: { word:'LÁNY!', name:'Lány', emoji:'💗'", "girl: { word:'KISLÁNY!', name:'Kislány', emoji:'💗'")
# a hosszabb szó a régi méreten kilógna (8 betű × 22vw)
rep("<div data-reveal-word style={{ fontFamily:T.font, fontWeight:900, fontSize:'min(30vh, 22vw)',",
    "<div data-reveal-word style={{ fontFamily:T.font, fontWeight:900, fontSize:'min(26vh, 13vw)', whiteSpace:'nowrap',")

# ── 2. közös vetítő-vezérlés + telefonos távirányító
rep("const REVEAL_SLOT_OPTS = [1, 2, 3];", """const REVEAL_SLOT_OPTS = [1, 2, 3];
// Telefon (rövidebb oldal < 500 px): a Vetítő szerep ott TÁVIRÁNYÍTÓ, nem vetít (v10.435).
const REVEAL_PHONE_MAX = 500;""")

rep("""function RevealProjector({ title, cfg, onExit }) {""",
"""// ── Vetítő-vezérlés: KÖZÖS dokumentum (v10.435) ─────────────────────────────────────
// `config/revealProjector = { secs, slots, paused, next }` — a laptopon futó vetítő ÉS a
// telefonos távirányító ugyanazt írja és olvassa. A `next` jelölő: minden ÚJ érték egy
// lépés a vetítőn. ⚠️ A vetítő SAJÁT „Következő" gombja nem írja a jelölőt (csak helyben
// lép) — különben a visszaérkező pillanatkép még egyet léptetne.
function revealCtlWrite(patch) { const db = revealDb(); if (db) db.collection('config').doc('revealProjector').set(patch, { merge:true }).catch(() => {}); }
function revealIsPhone(vp) { return Math.min(vp.w, vp.h) < REVEAL_PHONE_MAX; }
function RevealProjectorHost({ title, cfg, onExit }) {
  const vp = useRevealViewport();
  return revealIsPhone(vp) ? <RevealRemote onExit={onExit} /> : <RevealProjector title={title} cfg={cfg} onExit={onExit} />;
}
// Telefonon a vetítés nem fér el (és nem is ott nézik) — csak a gombok kellenek.
function RevealRemote({ onExit }) {
  const ctl = useRevealDoc('revealProjector');
  const { list: photos } = useRevealPhotos(false);
  const v = ctl.v || {};
  const secs = REVEAL_SECS.includes(+v.secs) ? +v.secs : 5;
  const slots = REVEAL_SLOT_OPTS.includes(+v.slots) ? +v.slots : 3;
  const paused = !!v.paused;
  const [msg, setMsg] = React.useState('');
  const flash = m => { setMsg(m); setTimeout(() => setMsg(''), 1500); };
  const card = { width:'100%', maxWidth:440, background:T.surface, borderRadius:20, padding:'16px', boxShadow:T.shadow, boxSizing:'border-box' };
  const label = t => <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, letterSpacing:'0.08em', color:T.inkSoft, marginBottom:10, textTransform:'uppercase' }}>{t}</div>;
  const segWrap = { display:'flex', gap:6, padding:4, borderRadius:14, background:T.bg };
  const seg = on => ({ flex:1, padding:'12px 6px', borderRadius:11, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:15, background: on ? T.mint : 'transparent', color: on ? '#fff' : T.ink });
  return (
    <div data-reveal-remote style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Vetítő" onBack={onExit} />
      <div style={{ flex:1, overflowY:'auto', display:'flex', flexDirection:'column', alignItems:'center', gap:14, padding:'18px 16px calc(24px + env(safe-area-inset-bottom))', boxSizing:'border-box' }}>
        <div style={{ ...card, textAlign:'center' }}>
          <div aria-hidden="true" style={{ fontSize:30, lineHeight:1 }}>📽️</div>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, marginTop:6 }}>Távirányító</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, lineHeight:1.45, marginTop:4 }}>A vetítést a kivetítőre kötött laptop mutatja — innen állíthatod.</div>
          <div data-reveal-remote-count style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.ink, marginTop:8 }}>{photos.filter(x => x.src || x.kind === 'wish').length} tétel a vetítőn</div>
        </div>
        <div style={card}>
          {label('Képváltás')}
          <div style={segWrap}>{REVEAL_SECS.map(n => <button key={n} data-reveal-remote-secs={n} aria-pressed={secs === n} onClick={() => revealCtlWrite({ secs:n })} style={seg(secs === n)}>{n} mp</button>)}</div>
        </div>
        <div style={card}>
          {label('Polaroidok egyszerre')}
          <div style={segWrap}>{REVEAL_SLOT_OPTS.map(n => <button key={n} data-reveal-remote-slots={n} aria-pressed={slots === n} onClick={() => revealCtlWrite({ slots:n })} style={seg(slots === n)}>{n}</button>)}</div>
        </div>
        <div style={{ ...card, display:'flex', gap:10 }}>
          <button data-reveal-remote-pause onClick={() => revealCtlWrite({ paused: !paused })}
            style={{ flex:1, padding:'16px 8px', borderRadius:14, border:`1.5px solid ${T.border}`, cursor:'pointer', background: paused ? T.mintSoft : 'transparent', fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink }}>{paused ? '▶ Folytatás' : '⏸ Szünet'}</button>
          <button data-reveal-remote-next onClick={() => { revealCtlWrite({ next: revealToken() }); flash('Következő kép'); }}
            style={{ flex:1.4, padding:'16px 8px', borderRadius:14, border:'none', cursor:'pointer', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff' }}>Következő ›</button>
        </div>
        {msg && <div data-reveal-remote-msg style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.mint }}>{msg}</div>}
      </div>
    </div>
  );
}

function RevealProjector({ title, cfg, onExit }) {""")

rep("""  const [paused, setPaused] = React.useState(false);
  const [ui, setUi] = React.useState(true);
  const [fs, setFs] = React.useState(false);""",
"""  const [paused, setPaused] = React.useState(false);
  const [ui, setUi] = React.useState(true);
  const [fs, setFs] = React.useState(false);
  // a KÖZÖS vezérlés (telefonos távirányító): beállítások + „következő" jelölő
  const ctl = useRevealDoc('revealProjector');
  React.useEffect(() => {
    const v = ctl.v || {};
    if (REVEAL_SECS.includes(+v.secs)) setSecs(+v.secs);
    if (REVEAL_SLOT_OPTS.includes(+v.slots)) setSlotPref(+v.slots);
    if (typeof v.paused === 'boolean') setPaused(v.paused);
  }, [ctl.v]);
  const pausedRef = React.useRef(false); pausedRef.current = paused;
  const togglePause = () => { const v = !pausedRef.current; setPaused(v); revealCtlWrite({ paused:v }); };
  const pickSecs = n => { setSecs(n); revealStore('boh_reveal_secs', String(n)); revealCtlWrite({ secs:n }); };
  const pickSlots = n => { setSlotPref(n); revealStore('boh_reveal_slots', String(n)); revealCtlWrite({ slots:n }); };""")

# a „következő" jelölő: az első pillanatképet csak megjegyezzük
rep("""  // ── polaroid-asztal: a helyek és ki van rajtuk ──""",
"""  const nextSeen = React.useRef(undefined);
  React.useEffect(() => {
    if (!ctl.loaded) return;
    const n = (ctl.v || {}).next || null;
    if (nextSeen.current === undefined) { nextSeen.current = n; return; }
    if (n && n !== nextSeen.current) { nextSeen.current = n; seq.next(); }
  }, [ctl.v, ctl.loaded]);

  // ── polaroid-asztal: a helyek és ki van rajtuk ──""")

rep("else if (e.key === ' ') { e.preventDefault(); if (qz.on) qz.step(1); else setPaused(p => !p); }",
    "else if (e.key === ' ') { e.preventDefault(); if (qz.on) qz.step(1); else togglePause(); }")
rep("""<button data-reveal-pause onClick={() => setPaused(p => !p)} style={chip(paused)}>""",
    """<button data-reveal-pause onClick={togglePause} style={chip(paused)}>""")
rep("""{REVEAL_SECS.map(n => <button key={n} data-reveal-secs={n} onClick={() => { setSecs(n); revealStore('boh_reveal_secs', String(n)); }} style={chip(secs === n)}>{n} mp</button>)}""",
    """{REVEAL_SECS.map(n => <button key={n} data-reveal-secs={n} onClick={() => pickSecs(n)} style={chip(secs === n)}>{n} mp</button>)}""")
rep("""onClick={() => { setSlotPref(n); revealStore('boh_reveal_slots', String(n)); }} style={chip(slotPref === n)}>""",
    """onClick={() => pickSlots(n)} style={chip(slotPref === n)}>""")

# ── 3. a Babakvízt a vetítőről NEM lehet indítani (a Szülők indítják)
rep("""        <button data-reveal-quizbtn onClick={() => qstate ? revealQuizWrite({ phase:'idle' }) : quizStep(1)} style={chip(!!qstate)}>🍼 Babakvíz</button>
""", "")

# szerep-választó: telefonon távirányító
rep("{ id:'projector', emoji:'📽️', name:'Vetítő', sub:'Laptop a kivetítőn — polaroid-fal, üzenetek, Babakvíz és a nagy leleplezés.' },",
    "{ id:'projector', emoji:'📽️', name:'Vetítő', sub:'Laptop a kivetítőn — polaroid-fal, üzenetek, Babakvíz és a nagy leleplezés. Telefonon távirányító.' },")
rep("if (ok && role === 'projector') return <RevealProjector title={title} cfg={cfg.v} onExit={() => setRole(null)} />;",
    "if (ok && role === 'projector') return <RevealProjectorHost title={title} cfg={cfg.v} onExit={() => setRole(null)} />;")
open(p, 'w', encoding='utf-8').write(s)
print('ok')

# ── a jelvény és a sarok-óra a felső gombsor ALÁ (látható sávnál rácsúszott)
s = open(p, encoding='utf-8').read()
rep("data-reveal-resultbadge style={{ position:'absolute', top: narrow ? 56 : '3vh',",
    "data-reveal-resultbadge style={{ position:'absolute', top: narrow ? 56 : 'max(3vh, 74px)',")
rep("data-reveal-corner style={{ position:'absolute', top: narrow ? 56 : '3vh',",
    "data-reveal-corner style={{ position:'absolute', top: narrow ? 56 : 'max(3vh, 74px)',")
open(p, 'w', encoding='utf-8').write(s)
print('ok2')
