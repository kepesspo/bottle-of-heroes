# v10.438 — Gender Reveal: a vetítőn nincs beállítás (minden a Szülőknél), és a
# leleplezés-visszaszámláló / eredmény-jelvény fent KÖZÉPEN áll.
import re
P = 'app.src.html'
s = open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:120])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.437'", "const APP_VERSION = 'v10.438'")

# ── 1. Telefonos Vetítő: nem távirányító, csak egy tájékoztató ───────────────────────
rep("""function RevealProjectorHost({ title, cfg, onExit }) {
  const vp = useRevealViewport();
  return revealIsPhone(vp) ? <RevealRemote onExit={onExit} /> : <RevealProjector title={title} cfg={cfg} onExit={onExit} />;
}
// Telefonon a vetítés nem fér el (és nem is ott nézik) — csak a gombok kellenek.
function RevealRemote({ onExit }) {
  const ctl = useRevealDoc('revealProjector');""",
"""function RevealProjectorHost({ title, cfg, onExit }) {
  const vp = useRevealViewport();
  return revealIsPhone(vp) ? <RevealPhoneNote onExit={onExit} /> : <RevealProjector title={title} cfg={cfg} onExit={onExit} />;
}
// Telefonon a vetítés nem fér el (és nem is ott nézik). A beállítások (v10.438 óta) a
// Szülők részen vannak — itt csak elmondjuk, hova kell menni.
function RevealPhoneNote({ onExit }) {
  return (
    <div data-reveal-phonenote style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Vetítő" onBack={onExit} />
      <div style={{ flex:1, overflowY:'auto', display:'flex', flexDirection:'column', alignItems:'center', padding:'22px 16px', boxSizing:'border-box' }}>
        <div style={{ width:'100%', maxWidth:440, background:T.surface, borderRadius:20, padding:'22px 18px', boxShadow:T.shadow, boxSizing:'border-box', textAlign:'center' }}>
          <div aria-hidden="true" style={{ fontSize:34, lineHeight:1 }}>📽️</div>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, marginTop:8 }}>A vetítő a laptopon fut</div>
          <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, lineHeight:1.5, marginTop:6 }}>Nyisd meg a Vetítőt a kivetítőre kötött gépen. A beállításokat (képváltás, polaroidok, szünet, következő kép) a <b>Szülők</b> részen találod.</div>
        </div>
      </div>
    </div>
  );
}
// A vetítő MINDEN beállítása (v10.438): a Szülők nézetben, a szülői kód mögött.
function RevealProjectorPanel() {
  const ctl = useRevealDoc('revealProjector');""")

# a régi távirányító törzse → beágyazható panel (AppBar és saját görgetés nélkül)
rep("""  const seg = on => ({ flex:1, padding:'12px 6px', borderRadius:11, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:15, background: on ? T.mint : 'transparent', color: on ? '#fff' : T.ink });
  return (
    <div data-reveal-remote style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Vetítő" onBack={onExit} />
      <div style={{ flex:1, overflowY:'auto', display:'flex', flexDirection:'column', alignItems:'center', gap:14, padding:'18px 16px calc(24px + env(safe-area-inset-bottom))', boxSizing:'border-box' }}>
        <div style={{ ...card, textAlign:'center' }}>
          <div aria-hidden="true" style={{ fontSize:30, lineHeight:1 }}>📽️</div>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, marginTop:6 }}>Távirányító</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, lineHeight:1.45, marginTop:4 }}>A vetítést a kivetítőre kötött laptop mutatja — innen állíthatod.</div>
          <div data-reveal-remote-count""",
"""  const seg = on => ({ flex:1, padding:'12px 6px', borderRadius:11, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:15, background: on ? T.mint : 'transparent', color: on ? '#fff' : T.ink });
  const qr = v.qr !== false;
  return (
    <div data-reveal-parentctl style={{ width:'100%', maxWidth:440, display:'flex', flexDirection:'column', alignItems:'center', gap:14 }}>
        <div style={{ ...card, textAlign:'center' }}>
          <div aria-hidden="true" style={{ fontSize:30, lineHeight:1 }}>📽️</div>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, marginTop:6 }}>Vetítő beállításai</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, lineHeight:1.45, marginTop:4 }}>A vetítést a kivetítőre kötött laptop mutatja — innen állíthatod.</div>
          <div data-reveal-ctl-count""")
rep("<div data-reveal-remote-tally", "<div data-reveal-ctl-tally")
rep("data-reveal-remote-secs={n}", "data-reveal-ctl-secs={n}")
rep("data-reveal-remote-slots={n}", "data-reveal-ctl-slots={n}")
rep("""          <button data-reveal-remote-pause onClick""", """          <button data-reveal-ctl-pause onClick""")
rep("""          <button data-reveal-remote-next onClick""", """          <button data-reveal-ctl-next onClick""")
rep("""        {msg && <div data-reveal-remote-msg style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.mint }}>{msg}</div>}
      </div>
    </div>
  );
}""", """        <div style={card}>
          {label('Vendég QR-kód a vetítőn')}
          <div style={segWrap}>{[[true, 'Látszik'], [false, 'Rejtve']].map(([on, t]) => <button key={t} data-reveal-ctl-qr={on ? '1' : '0'} aria-pressed={qr === on} onClick={() => revealCtlWrite({ qr:on })} style={seg(qr === on)}>{t}</button>)}</div>
        </div>
        {msg && <div data-reveal-ctl-msg style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.mint }}>{msg}</div>}
    </div>
  );
}""")

# ── 2. A vetítő csak KÖVETI a közös dokumentumot ─────────────────────────────────────
rep("""    if (typeof v.paused === 'boolean') setPaused(v.paused);
  }, [ctl.v]);""", """    if (typeof v.paused === 'boolean') setPaused(v.paused);
    if (typeof v.qr === 'boolean') setShowQr(v.qr);
    // a laptop megjegyzi az utolsó beállítást (ha a dokumentum egyszer üresen jönne)
    if (REVEAL_SECS.includes(+v.secs)) revealStore('boh_reveal_secs', String(+v.secs));
    if (REVEAL_SLOT_OPTS.includes(+v.slots)) revealStore('boh_reveal_slots', String(+v.slots));
  }, [ctl.v]);""")
rep("""  const pickSecs = n => { setSecs(n); revealStore('boh_reveal_secs', String(n)); revealCtlWrite({ secs:n }); };
  const pickSlots = n => { setSlotPref(n); revealStore('boh_reveal_slots', String(n)); revealCtlWrite({ slots:n }); };
""", "")
rep("""  const replay = () => { const v = rstate.v || {}; if (v.phase === 'reveal') setShow({ run:'replay' + Date.now(), test:!!v.test, result:v.result, videoUrl:v.videoUrl || '' }); };
""", "")

# a kvíz-lapozó gombsor kikerül (a Szülők lapoznak; a billentyűk maradnak)
rep("""      {qstate && !show && (
        <div data-reveal-quiznav style={{ position:'absolute', left:0, right:0, bottom:0, zIndex:60, display:'flex', justifyContent:'center', gap:10, padding:'14px 16px', flexWrap:'wrap',
          opacity: ui ? 1 : 0, pointerEvents: ui ? 'auto' : 'none', transition:'opacity .4s' }}>
          {!(qstate.phase === 'q' && !qstate.idx) && <button data-reveal-quizprev onClick={() => quizStep(-1)} style={chip(false)}>‹ Előző</button>}
          <button data-reveal-quiznext onClick={() => quizStep(1)} style={chip(true)}>{revealQuizNextLabel(qstate)}</button>
          <button data-reveal-quizexit onClick={() => revealQuizWrite({ phase:'idle' })} style={chip(false)}>✕ Kilépés</button>
        </div>
      )}
""", "")

# a gombsorból kikerül minden beállítás: marad a Vissza, a darabszám, a Videó és a Teljes képernyő
rep("""        {REVEAL_SECS.map(n => <button key={n} data-reveal-secs={n} onClick={() => pickSecs(n)} style={chip(secs === n)}>{n} mp</button>)}
        <span aria-hidden="true" style={{ flexShrink:0, width:1.5, alignSelf:'stretch', margin:'4px 2px', background:'#EFE2D2' }} />
        {REVEAL_SLOT_OPTS.map(n => <button key={n} data-reveal-slotsbtn={n} aria-label={n + ' polaroid egyszerre'} title={n + ' polaroid egyszerre'} onClick={() => pickSlots(n)} style={chip(slotPref === n)}>🖼 {n}</button>)}
        <div style={{ flex:1, minWidth:8 }} />""", """        <div style={{ flex:1, minWidth:8 }} />""")
rep("""        {qrUrl && !narrow && <button data-reveal-qrbtn onClick={() => { const v = !showQr; setShowQr(v); revealStore('boh_reveal_qr', v ? '1' : '0'); }} style={chip(showQr)}>QR</button>}
""", "")
rep("""        {rstate.v && rstate.v.phase === 'reveal' && !show && <button data-reveal-replay onClick={replay} style={chip(false)}>↻ Leleplezés újra</button>}
        <button data-reveal-pause onClick={togglePause} style={chip(paused)}>{paused ? '▶ Folytatás' : '⏸ Szünet'}</button>
        <button data-reveal-next onClick={() => qstate ? quizStep(1) : seq.next()} style={chip(false)}>Következő ›</button>
""", """        {paused && <span data-reveal-paused style={{ flexShrink:0, whiteSpace:'nowrap', fontFamily:T.font, fontWeight:800, fontSize:13, color:REVEAL_INK, opacity:0.7 }}>⏸ Szünet</span>}
""")
rep("""  const [showQr, setShowQr] = React.useState(() => revealStore('boh_reveal_qr') !== '0');""",
    """  const [showQr, setShowQr] = React.useState(true);""")

# ── 3. A leleplezés fent KÖZÉPEN; a polaroid-fal alatta kezdődik ─────────────────────
rep("""  const boardH = meterOn ? vp.h * REVEAL_METER_ROOM : vp.h;""",
"""  const boardH = meterOn ? vp.h * REVEAL_METER_ROOM : vp.h;
  // ⚠️ A felül középen álló jelvény / visszaszámláló a középső lap tetejére esne: a fal az
  // ALJA alatt kezdődik (mért érték — a szöveg mérete vh-függő).
  const topRef = React.useRef(null);
  const [topEdge, setTopEdge] = React.useState(0);
  React.useLayoutEffect(() => {
    const e = topRef.current;
    const v = e ? Math.round(e.offsetTop + e.offsetHeight + 10) : 0;
    if (v !== topEdge) setTopEdge(v);
  });""")
rep("""      <div data-reveal-board data-slots={nSlots} style={{ position:'absolute', inset:0, zIndex:1, isolation:'isolate' }}>
        {slots.map((s, i) => { const it = s && byId[s.id]; if (!it) return null;
          return <RevealBoardCard key={s.key} item={it} g={revealCardGeom(i, nSlots, vp.w, boardH, it, s.key)}""",
"""      <div data-reveal-board data-slots={nSlots} style={{ position:'absolute', left:0, right:0, top:topEdge, height:Math.max(1, boardH - topEdge), zIndex:1, isolation:'isolate' }}>
        {slots.map((s, i) => { const it = s && byId[s.id]; if (!it) return null;
          return <RevealBoardCard key={s.key} item={it} g={revealCardGeom(i, nSlots, vp.w, Math.max(1, boardH - topEdge), it, s.key)}""")
rep("""        <div data-reveal-resultbadge style={{ position:'absolute', top: narrow ? 56 : 'max(3vh, 74px)', right:'2.4vw', zIndex:45,""",
    """        <div ref={topRef} data-reveal-resultbadge style={{ position:'absolute', top: narrow ? 56 : 'max(3vh, 74px)', left:'50%', transform:'translateX(-50%)', whiteSpace:'nowrap', zIndex:45,""")
rep("""        <div data-reveal-corner style={{ position:'absolute', top: narrow ? 56 : 'max(3vh, 74px)', right:'2.4vw', zIndex:45, padding: narrow ? '8px 14px' : '1.2vh 1.6vw', borderRadius:18, textAlign:'right',""",
    """        <div ref={topRef} data-reveal-corner style={{ position:'absolute', top: narrow ? 56 : 'max(3vh, 74px)', left:'50%', transform:'translateX(-50%)', whiteSpace:'nowrap', zIndex:45, padding: narrow ? '8px 14px' : '1.2vh 2.2vw', borderRadius:18, textAlign:'center',""")

# ── 4. Szülők: a vetítő beállításai a leleplezés és a Babakvíz között ────────────────
rep("""        {secret.loaded && sec.code && ok && <div data-reveal-parentquiz""",
    """        {secret.loaded && sec.code && ok && <RevealProjectorPanel />}
        {secret.loaded && sec.code && ok && <div data-reveal-parentquiz""")
rep("a leleplezést és a Babakvízt a szülők kezelik, ezzel a kóddal.",
    "a leleplezést, a Babakvízt és a vetítő beállításait a szülők kezelik, ezzel a kóddal.")
rep("polaroid-fal, üzenetek, Babakvíz és a nagy leleplezés. Telefonon távirányító.' }",
    "polaroid-fal, üzenetek, Babakvíz és a nagy leleplezés. Beállítás nincs rajta — az a Szülőknél van.' }")
rep("sub:'Külön kóddal — a nagy leleplezés és a Babakvíz. Az eredményt ők sem látják.' }",
    "sub:'Külön kóddal — a nagy leleplezés, a Babakvíz és a vetítő beállításai. Az eredményt ők sem látják.' }")

# ── 5. Admin felirat ─────────────────────────────────────────────────────────────────
rep("Visszaszámláló a vetítő jobb felső sarkában", "Visszaszámláló a vetítő tetején, középen")

assert 'RevealRemote' not in s and 'data-reveal-remote' not in s
assert 'data-reveal-quiznav' not in s and 'data-reveal-slotsbtn' not in s and 'pickSecs' not in s
open(P, 'w', encoding='utf-8').write(s)
print('ok')
